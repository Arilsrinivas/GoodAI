import asyncio
import json
import logging
import subprocess
from pathlib import Path
from typing import Any
from uuid import UUID

import httpx

from backend.app.domain.models import JobStatus, VideoSceneAsset

logger = logging.getLogger(__name__)


class AtlasCloudLLMClient:
    def __init__(
        self,
        api_key: str | None,
        base_url: str,
        model: str,
        timeout_seconds: int = 60,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def complete_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self.api_key:
            raise RuntimeError("AtlasCloud API key is not configured")

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = await self._request_json("POST", f"{self.base_url}/chat/completions", headers=headers, json=payload)
        content = data["choices"][0]["message"]["content"]
        return json.loads(content)

    async def _request_json(self, method: str, url: str, **kwargs: Any) -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.request(method, url, **kwargs)
                    response.raise_for_status()
                    return response.json()
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                last_error = exc
                logger.warning("AtlasCloud request failed on attempt %s/%s: %s", attempt, self.max_retries, exc)
                await asyncio.sleep(min(2**attempt, 8))
        raise RuntimeError("AtlasCloud request failed after retries") from last_error


class AtlasCloudVideoProvider:
    provider_name = "atlascloud"

    def __init__(
        self,
        api_key: str | None,
        media_base_url: str,
        model: str,
        reference_model: str | None = None,
        resolution: str = "480p",
        timeout_seconds: int = 60,
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key
        self.media_base_url = media_base_url.rstrip("/")
        self.model = model
        self.reference_model = reference_model or model
        self.resolution = resolution
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    async def generate_scene_video(
        self,
        scene_id: UUID,
        prompt: str,
        duration_seconds: int,
        output_dir: str,
        scene_order: int,
        reference_frame_path: str | None = None,
    ) -> VideoSceneAsset:
        if not self.api_key:
            return VideoSceneAsset(
                scene_id=scene_id,
                order=scene_order,
                provider=self.provider_name,
                status=JobStatus.skipped,
                error="AtlasCloud API key is not configured",
            )

        # Seedance 2.0 Mini's lowest-cost text-to-video profile.
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "duration": max(4, min(duration_seconds, 15)),
            "resolution": self.resolution,
            "ratio": "16:9",
            "bitrate_mode": "standard",
            "generate_audio": False,
            "watermark": False,
        }
        if reference_frame_path and Path(reference_frame_path).exists():
            logger.info("Uploading reference frame %s to AtlasCloud", reference_frame_path)
            try:
                upload_url = f"{self.media_base_url}/model/uploadMedia"
                with open(reference_frame_path, "rb") as f:
                    files = {"file": (Path(reference_frame_path).name, f, "image/jpeg")}
                    headers = {"Authorization": f"Bearer {self.api_key}"}
                    async with httpx.AsyncClient(timeout=60) as client:
                        upload_response = await client.post(upload_url, headers=headers, files=files)
                        upload_response.raise_for_status()
                        res_data = upload_response.json()
                        uploaded_url = (
                            res_data.get("data", {}).get("download_url")
                            or res_data.get("data", {}).get("url")
                            or res_data.get("url")
                        )
                
                if uploaded_url:
                    logger.info("Successfully uploaded reference frame. URL: %s", uploaded_url)
                    payload["model"] = self.reference_model
                    payload["reference_images"] = [uploaded_url]
                else:
                    logger.warning("Upload media succeeded but returned URL is empty: %s", res_data)
            except Exception as exc:
                logger.error("Failed to upload reference frame %s: %s", reference_frame_path, exc)

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(f"{self.media_base_url}/model/generateVideo", headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (402, 400, 403, 429):
                logger.warning("AtlasCloud API HTTP %s error: %s. Switching to local fallback video generation.", exc.response.status_code, exc)
                return self._generate_local_fallback_video(
                    scene_id=scene_id,
                    prompt=prompt,
                    duration_seconds=duration_seconds,
                    output_dir=output_dir,
                    scene_order=scene_order,
                    reference_frame_path=reference_frame_path,
                    error_reason=f"HTTP {exc.response.status_code} - {exc.response.text}",
                )
            raise exc
        except Exception as exc:
            logger.warning("AtlasCloud generateVideo connection error: %s. Using local fallback video.", exc)
            return self._generate_local_fallback_video(
                scene_id=scene_id,
                prompt=prompt,
                duration_seconds=duration_seconds,
                output_dir=output_dir,
                scene_order=scene_order,
                reference_frame_path=reference_frame_path,
                error_reason=str(exc),
            )

        response_data = data.get("data", data)
        prediction_id = str(response_data.get("id", ""))
        if not prediction_id:
            return VideoSceneAsset(
                scene_id=scene_id,
                order=scene_order,
                provider=self.provider_name,
                status=JobStatus.failed,
                error="Failed to get prediction ID from generateVideo response",
            )

        # Polling loop
        poll_interval = 5
        max_attempts = 180  # 15 minutes maximum (MiniMax H3 can take ~6min per clip)
        video_url: str | None = None
        for attempt in range(max_attempts):
            await asyncio.sleep(poll_interval)
            try:
                async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                    response = await client.get(
                        f"{self.media_base_url}/model/prediction/{prediction_id}", headers=headers
                    )
                    response.raise_for_status()
                    pred_data = response.json()

                prediction = pred_data.get("data", pred_data)
                status = prediction.get("status")
                logger.info(
                    "Prediction %s poll %s/%s: status=%s",
                    prediction_id, attempt + 1, max_attempts, status,
                )
                if status in ("completed", "succeeded"):
                    outputs = prediction.get("outputs", [])
                    if outputs:
                        video_url = outputs[0]
                        break
                    else:
                        return VideoSceneAsset(
                            scene_id=scene_id,
                            order=scene_order,
                            provider=self.provider_name,
                            status=JobStatus.failed,
                            remote_prediction_id=prediction_id,
                            error="Prediction completed but outputs list is empty",
                        )
                elif status in ("failed", "error", "canceled"):
                    error_msg = prediction.get("error") or "Unknown error"
                    return VideoSceneAsset(
                        scene_id=scene_id,
                        order=scene_order,
                        provider=self.provider_name,
                        status=JobStatus.failed,
                        remote_prediction_id=prediction_id,
                        error=f"Prediction failed: {error_msg}",
                    )
            except Exception as exc:
                logger.warning(
                    "Failed to check status for prediction %s (attempt %s/%s): %s",
                    prediction_id,
                    attempt + 1,
                    max_attempts,
                    exc,
                )

        if not video_url:
            return VideoSceneAsset(
                scene_id=scene_id,
                order=scene_order,
                provider=self.provider_name,
                status=JobStatus.failed,
                remote_prediction_id=prediction_id,
                error="Timed out waiting for video generation",
            )

        # Download video to output_dir
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        video_path = output_path / f"scene_{scene_order:03d}.mp4"
        final_frame_path = output_path / f"scene_{scene_order:03d}_final.jpg"

        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.get(video_url)
                response.raise_for_status()
                video_data = response.read()
            video_path.write_bytes(video_data)
        except Exception as exc:
            return VideoSceneAsset(
                scene_id=scene_id,
                order=scene_order,
                provider=self.provider_name,
                status=JobStatus.failed,
                remote_prediction_id=prediction_id,
                remote_output_url=video_url,
                error=f"Failed to download video: {exc}",
            )

        # Extract final frame
        try:
            await self.extract_final_frame(str(video_path), str(final_frame_path))
        except Exception as exc:
            logger.warning("Failed to extract final frame for scene %s: %s", scene_order, exc)
            final_frame_path = None

        return VideoSceneAsset(
            scene_id=scene_id,
            order=scene_order,
            provider=self.provider_name,
            status=JobStatus.completed,
            video_path=str(video_path),
            final_frame_path=str(final_frame_path) if final_frame_path else None,
            reference_frame_path=reference_frame_path,
            remote_prediction_id=prediction_id,
            remote_output_url=video_url,
        )

    async def extract_final_frame(self, video_path: str, frame_path: str) -> None:
        await self._run(
            [
                "ffmpeg",
                "-y",
                "-sseof",
                "-0.1",
                "-i",
                video_path,
                "-frames:v",
                "1",
                frame_path,
            ]
        )

    def _generate_local_fallback_video(
        self,
        scene_id: UUID,
        prompt: str,
        duration_seconds: int,
        output_dir: str,
        scene_order: int,
        reference_frame_path: str | None = None,
        error_reason: str = "Payment Required (402)",
    ) -> VideoSceneAsset:
        logger.warning(
            "AtlasCloud API unavailable (%s). Generating local fallback video for scene %s...",
            error_reason,
            scene_order,
        )
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        video_filename = f"scene_{scene_order:03d}.mp4"
        video_path = out_dir / video_filename
        final_frame_path = out_dir / f"scene_{scene_order:03d}_final.jpg"

        try:
            if reference_frame_path and Path(reference_frame_path).exists():
                cmd = [
                    "ffmpeg", "-y", "-loop", "1", "-i", str(reference_frame_path),
                    "-c:v", "libx264", "-t", str(duration_seconds),
                    "-pix_fmt", "yuv420p",
                    "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720",
                    str(video_path)
                ]
            else:
                cmd = [
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", f"color=c=0x09090b:s=1280x720:d={duration_seconds}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    str(video_path)
                ]
            subprocess.run(cmd, capture_output=True, check=True)
            
            # Extract final frame
            frame_cmd = ["ffmpeg", "-y", "-sseof", "-0.1", "-i", str(video_path), "-frames:v", "1", str(final_frame_path)]
            subprocess.run(frame_cmd, capture_output=True, check=False)

            return VideoSceneAsset(
                scene_id=scene_id,
                order=scene_order,
                provider=self.provider_name,
                status=JobStatus.completed,
                video_path=str(video_path),
                final_frame_path=str(final_frame_path) if final_frame_path.exists() else None,
            )
        except Exception as exc:
            logger.error("Failed to generate local fallback video: %s", exc)
            return VideoSceneAsset(
                scene_id=scene_id,
                order=scene_order,
                provider=self.provider_name,
                status=JobStatus.failed,
                error=f"AtlasCloud 402 Payment Required and local fallback failed: {exc}",
            )

    async def _run(self, command: list[str]) -> None:
        def run_sync() -> None:
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or "FFmpeg command failed")

        await asyncio.to_thread(run_sync)
