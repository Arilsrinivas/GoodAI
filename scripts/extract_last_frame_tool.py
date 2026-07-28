#!/usr/bin/env python3
import asyncio
import argparse
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("extract_last_frame_tool")

# Default API URL
ATLASCLOUD_API_KEY = os.getenv("ATLASCLOUD_API_KEY")
MEDIA_BASE_URL = os.getenv("ATLASCLOUD_MEDIA_BASE_URL", "https://api.atlascloud.ai/api/v1")
DEFAULT_MODEL = os.getenv("ATLASCLOUD_VIDEO_MODEL", "kling-v2.0")

def run_ffmpeg(command: list[str]) -> None:
    logger.info("Running FFmpeg: %s", " ".join(command))
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "FFmpeg command failed")

def extract_final_frame(video_path: str, frame_path: str) -> None:
    logger.info("Extracting final frame from %s to %s", video_path, frame_path)
    run_ffmpeg([
        "ffmpeg",
        "-y",
        "-sseof",
        "-0.1",
        "-i",
        video_path,
        "-frames:v",
        "1",
        frame_path
    ])

async def upload_reference_frame(frame_path: str, api_key: str, media_base_url: str) -> str:
    upload_url = f"{media_base_url}/model/uploadMedia"
    logger.info("Uploading reference frame %s to %s", frame_path, upload_url)
    
    with open(frame_path, "rb") as f:
        files = {"file": (Path(frame_path).name, f, "image/jpeg")}
        headers = {"Authorization": f"Bearer {api_key}"}
        
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(upload_url, headers=headers, files=files)
            response.raise_for_status()
            res_data = response.json()
            
            uploaded_url = res_data.get("data", {}).get("url") or res_data.get("url")
            if not uploaded_url:
                raise ValueError(f"Upload media response did not contain url: {res_data}")
            
            logger.info("Uploaded reference frame successfully. URL: %s", uploaded_url)
            return uploaded_url

async def generate_next_scene(
    prompt: str,
    duration: int,
    image_url: str,
    model: str,
    api_key: str,
    media_base_url: str
) -> str:
    url = f"{media_base_url}/model/generateVideo"
    logger.info("Requesting video generation from %s using model %s", url, model)
    
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "image": image_url,
        "reference_image": image_url,
        "image_url": image_url,
        "images": [image_url]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res_data = response.json()
        
        prediction_id = res_data.get("data", {}).get("id") or res_data.get("id")
        if not prediction_id:
            raise ValueError(f"Generation request did not return a prediction ID: {res_data}")
        
        logger.info("Generation job queued successfully. Prediction ID: %s", prediction_id)
        return str(prediction_id)

async def poll_prediction_status(
    prediction_id: str,
    api_key: str,
    media_base_url: str,
    poll_interval: int = 5,
    max_attempts: int = 60
) -> str:
    url = f"{media_base_url}/model/prediction/{prediction_id}"
    logger.info("Polling prediction status from %s", url)
    headers = {"Authorization": f"Bearer {api_key}"}
    
    for attempt in range(1, max_attempts + 1):
        await asyncio.sleep(poll_interval)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                pred_data = response.json()
                
            status = pred_data.get("status")
            logger.info("Attempt %d/%d: Status = %s", attempt, max_attempts, status)
            
            if status == "completed":
                outputs = pred_data.get("outputs", [])
                if outputs:
                    return str(outputs[0])
                else:
                    raise ValueError(f"Prediction completed but outputs list is empty: {pred_data}")
            elif status == "failed":
                error_msg = pred_data.get("error") or "Unknown error"
                raise RuntimeError(f"Prediction failed: {error_msg}")
        except Exception as exc:
            logger.warning("Error fetching prediction status on attempt %d: %s", attempt, exc)
            
    raise TimeoutError("Timed out waiting for video generation")

async def download_video(video_url: str, destination_path: str) -> None:
    logger.info("Downloading video from %s to %s", video_url, destination_path)
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.get(video_url)
        response.raise_for_status()
        video_data = response.read()
    
    Path(destination_path).write_bytes(video_data)
    logger.info("Video downloaded successfully!")

async def main_async() -> None:
    parser = argparse.ArgumentParser(
        description="Extracts the last frame of a video, uploads it to AtlasCloud, and triggers the next scene generation."
    )
    parser.add_argument("--video-path", required=True, help="Path to the generated video file for the previous scene")
    parser.add_argument("--output-dir", required=True, help="Directory to save extracted frame and next scene video")
    parser.add_argument("--next-prompt", required=True, help="Prompt text for the next scene")
    parser.add_argument("--next-duration", type=int, default=10, help="Duration of the next scene (seconds)")
    parser.add_argument("--next-scene-order", type=int, default=2, help="Order index of the next scene")
    parser.add_argument("--api-key", default=ATLASCLOUD_API_KEY, help="AtlasCloud API key (defaults to ATLASCLOUD_API_KEY env var)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model identifier to use for next video generation")
    
    args = parser.parse_args()
    
    if not args.api_key:
        logger.error("API Key not found. Please provide --api-key or set the ATLASCLOUD_API_KEY environment variable.")
        sys.exit(1)
        
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Extract the last frame
    frame_path = output_path / f"scene_{args.next_scene_order-1:03d}_final.jpg"
    try:
        extract_final_frame(args.video_path, str(frame_path))
    except Exception as exc:
        logger.error("Failed to extract final frame: %s", exc)
        sys.exit(1)
        
    # 2. Upload reference frame
    try:
        uploaded_url = await upload_reference_frame(str(frame_path), args.api_key, MEDIA_BASE_URL)
    except Exception as exc:
        logger.error("Failed to upload reference frame: %s", exc)
        sys.exit(1)
        
    # 3. Generate next scene video
    try:
        prediction_id = await generate_next_scene(
            prompt=args.next_prompt,
            duration=args.next_duration,
            image_url=uploaded_url,
            model=args.model,
            api_key=args.api_key,
            media_base_url=MEDIA_BASE_URL
        )
    except Exception as exc:
        logger.error("Failed to trigger video generation: %s", exc)
        sys.exit(1)
        
    # 4. Poll status
    try:
        video_url = await poll_prediction_status(prediction_id, args.api_key, MEDIA_BASE_URL)
    except Exception as exc:
        logger.error("Failed waiting for video completion: %s", exc)
        sys.exit(1)
        
    # 5. Download the new video
    next_video_path = output_path / f"scene_{args.next_scene_order:03d}.mp4"
    try:
        await download_video(video_url, str(next_video_path))
    except Exception as exc:
        logger.error("Failed downloading generated video: %s", exc)
        sys.exit(1)

    logger.info("Tool completed successfully! Next scene video generated at: %s", next_video_path)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
