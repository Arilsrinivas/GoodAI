import asyncio
import subprocess
from pathlib import Path
from uuid import UUID

from backend.app.domain.models import JobStatus, VideoSceneAsset


class StubVideoProvider:
    provider_name = "stub"

    async def generate_scene_video(
        self,
        scene_id: UUID,
        prompt: str,
        duration_seconds: int,
        output_dir: str,
        scene_order: int,
        reference_frame_path: str | None = None,
    ) -> VideoSceneAsset:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        video_path = output / f"scene_{scene_order:03d}.mp4"
        final_frame_path = output / f"scene_{scene_order:03d}_final.jpg"
        await self._run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c=0x172026:s=1280x720:d={duration_seconds}:r=24",
                "-vf",
                f"drawtext=text='Scene {scene_order}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
                "-pix_fmt",
                "yuv420p",
                str(video_path),
            ]
        )
        await self.extract_final_frame(str(video_path), str(final_frame_path))
        return VideoSceneAsset(
            scene_id=scene_id,
            order=scene_order,
            provider=self.provider_name,
            status=JobStatus.completed,
            video_path=str(video_path),
            final_frame_path=str(final_frame_path),
            reference_frame_path=reference_frame_path,
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

    async def _run(self, command: list[str]) -> None:
        def run_sync() -> None:
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or "FFmpeg command failed")

        await asyncio.to_thread(run_sync)
