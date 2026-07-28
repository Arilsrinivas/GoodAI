import asyncio
import json
import subprocess
import os
import logging
from pathlib import Path
from uuid import UUID

from backend.app.application.ports import StoryPlanRepository, VideoProvider
from backend.app.domain.models import JobStatus, MovieExport, StoryPlan, VideoSceneAsset

logger = logging.getLogger(__name__)


class VideoExportService:
    def __init__(
        self,
        repository: StoryPlanRepository,
        video_provider: VideoProvider,
        storage_dir: Path,
        tts_client: object | None = None,
    ) -> None:
        self.repository = repository
        self.video_provider = video_provider
        self.storage_dir = storage_dir
        self.tts_client = tts_client

    async def initialize_export(self, plan_id: UUID) -> MovieExport:
        plan = await self.repository.get(plan_id)
        if plan is None:
            raise ValueError("Story plan not found")

        export_dir = self.storage_dir / "exports" / str(plan.id)
        video_assets = [
            VideoSceneAsset(
                scene_id=scene.id,
                order=scene.order,
                provider=self.video_provider.provider_name,
                status=JobStatus.pending,
            )
            for scene in plan.scenes
        ]

        export = MovieExport(
            plan_id=plan.id,
            export_dir=str(export_dir),
            status=JobStatus.processing,
            narration_path=str(export_dir / "narration.txt"),
            subtitles_path=str(export_dir / "subtitles.srt"),
            json_path=str(export_dir / "story_plan.json"),
            timeline_path=str(export_dir / "timeline.json"),
            prompt_history_path=str(export_dir / "prompt_history.json"),
            character_database_path=str(export_dir / "characters.json"),
            location_database_path=str(export_dir / "locations.json"),
            scene_database_path=str(export_dir / "scenes.json"),
            metadata_path=str(export_dir / "metadata.json"),
            final_movie_path=None,
            video_assets=video_assets,
            warnings=[],
        )
        await self.repository.save_export(export)
        return export

    async def generate_export(self, plan_id: UUID) -> MovieExport:
        try:
            plan = await self.repository.get(plan_id)
            if plan is None:
                raise ValueError("Story plan not found")

            export_dir = self.storage_dir / "exports" / str(plan.id)
            videos_dir = export_dir / "videos"
            export_dir.mkdir(parents=True, exist_ok=True)
            videos_dir.mkdir(parents=True, exist_ok=True)

            existing_export = await self.repository.get_export(plan_id)
            if existing_export and existing_export.video_assets:
                video_assets = existing_export.video_assets
            else:
                video_assets = [
                    VideoSceneAsset(
                        scene_id=scene.id,
                        order=scene.order,
                        provider=self.video_provider.provider_name,
                        status=JobStatus.pending,
                    )
                    for scene in plan.scenes
                ]

            reference_frame_path: str | None = None
            for idx, scene in enumerate(plan.scenes):
                # Update status of this scene to processing and save
                video_assets[idx].status = JobStatus.processing
                intermediate_export = MovieExport(
                    plan_id=plan.id,
                    export_dir=str(export_dir),
                    status=JobStatus.processing,
                    narration_path=str(export_dir / "narration.txt"),
                    subtitles_path=str(export_dir / "subtitles.srt"),
                    json_path=str(export_dir / "story_plan.json"),
                    timeline_path=str(export_dir / "timeline.json"),
                    prompt_history_path=str(export_dir / "prompt_history.json"),
                    character_database_path=str(export_dir / "characters.json"),
                    location_database_path=str(export_dir / "locations.json"),
                    scene_database_path=str(export_dir / "scenes.json"),
                    metadata_path=str(export_dir / "metadata.json"),
                    final_movie_path=None,
                    video_assets=video_assets,
                    warnings=[],
                )
                await self.repository.save_export(intermediate_export)

                asset = await self.video_provider.generate_scene_video(
                    scene.id,
                    scene.prompt,
                    scene.duration_seconds,
                    str(videos_dir),
                    scene.order,
                    reference_frame_path=reference_frame_path,
                )

                # Narration audio synthesis and merging if configured
                if (
                    asset.status == JobStatus.completed
                    and asset.video_path
                    and self.tts_client
                    and getattr(self.tts_client, "is_configured", False)
                    and scene.narration
                ):
                    try:
                        logger.info("Generating TTS audio for scene %s", scene.order)
                        audio_bytes = await self.tts_client.generate_tts_audio(scene.narration)
                        audio_format = getattr(self.tts_client, "audio_format", "pcm_s16le")
                        audio_extension = "mp3" if audio_format == "mp3" else "raw"
                        audio_path = videos_dir / f"scene_{scene.order:03d}_narration.{audio_extension}"
                        audio_path.write_bytes(audio_bytes)

                        def get_stream_duration(file_p: str) -> float:
                            ffprobe_cmd = [
                                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "default=noprint_wrappers=1:nokey=1", str(file_p)
                            ]
                            res = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
                            return float(res.stdout.strip())

                        temp_video_path = videos_dir / f"scene_{scene.order:03d}_temp.mp4"
                        
                        def run_ffmpeg_merge():
                            v_dur = get_stream_duration(asset.video_path)
                            a_dur = get_stream_duration(audio_path)
                            
                            if a_dur > v_dur:
                                freeze_dur = a_dur - v_dur + 0.3
                                cmd = [
                                    "ffmpeg", "-y",
                                    "-i", asset.video_path,
                                    "-i", str(audio_path),
                                    "-filter_complex", f"[0:v]tpad=stop_mode=clone:stop_duration={freeze_dur:.2f}[v]",
                                    "-map", "[v]",
                                    "-map", "1:a:0",
                                    "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
                                    "-c:a", "aac",
                                    str(temp_video_path),
                                ]
                            else:
                                cmd = [
                                    "ffmpeg", "-y",
                                    "-i", asset.video_path,
                                    "-i", str(audio_path),
                                    "-c:v", "copy",
                                    "-c:a", "aac",
                                    "-map", "0:v:0",
                                    "-map", "1:a:0",
                                    "-shortest",
                                    str(temp_video_path),
                                ]
                            subprocess.run(cmd, capture_output=True, check=True)

                        await asyncio.to_thread(run_ffmpeg_merge)

                        if temp_video_path.exists():
                            os.replace(temp_video_path, asset.video_path)
                            logger.info("Successfully merged narration audio into scene %s video with freeze-frame hold", scene.order)
                    except Exception as exc:
                        logger.warning("Failed to generate/merge narration audio for scene %s: %s", scene.order, exc)

                video_assets[idx] = asset
                reference_frame_path = asset.final_frame_path or reference_frame_path

                # Save intermediate status after finishing this scene
                intermediate_export.video_assets = video_assets
                await self.repository.save_export(intermediate_export)

            narration_path = self._write_text(export_dir / "narration.txt", self._narration_text(plan))
            subtitles_path = self._write_text(export_dir / "subtitles.srt", self._subtitles(plan))
            json_path = self._write_text(export_dir / "story_plan.json", plan.model_dump_json(indent=2))
            timeline_path = self._write_text(export_dir / "timeline.json", json.dumps([item.model_dump(mode="json") for item in plan.timeline], indent=2))
            prompt_history_path = self._write_text(export_dir / "prompt_history.json", json.dumps(self._prompt_history(plan), indent=2))
            character_database_path = self._write_text(export_dir / "characters.json", json.dumps([item.model_dump(mode="json") for item in plan.characters], indent=2))
            location_database_path = self._write_text(export_dir / "locations.json", json.dumps([item.model_dump(mode="json") for item in plan.locations], indent=2))
            scene_database_path = self._write_text(export_dir / "scenes.json", json.dumps([item.model_dump(mode="json") for item in plan.scenes], indent=2))
            metadata_path = self._write_text(export_dir / "metadata.json", json.dumps(plan.metadata | {"export_provider": self.video_provider.provider_name}, indent=2))

            character_bible_path = self._write_text(export_dir / "character_bible.md", self._character_bible_md(plan))
            location_bible_path = self._write_text(export_dir / "location_bible.md", self._location_bible_md(plan))
            shot_list_path = self._write_text(export_dir / "shot_list.json", json.dumps([item.model_dump(mode="json") for item in plan.shots], indent=2))
            voice_script_ssml_path = self._write_text(export_dir / "voice_script.ssml", self._voice_ssml(plan))
            sfx_plan_path = self._write_text(export_dir / "sfx_plan.json", json.dumps([item.model_dump(mode="json") for item in plan.sfx_plan], indent=2))
            music_plan_path = self._write_text(export_dir / "music_plan.json", json.dumps([item.model_dump(mode="json") for item in plan.music_plan], indent=2))
            storyboard_html_path = self._write_text(export_dir / "storyboard.html", self._storyboard_html(plan))

            completed_videos = [asset.video_path for asset in video_assets if asset.status == JobStatus.completed and asset.video_path]
            final_movie_path = None
            warnings: list[str] = []
            if completed_videos:
                final_movie_path = str(export_dir / "final_movie.mp4")
                await self._stitch_videos(completed_videos, final_movie_path, export_dir)
            else:
                warnings.append("No completed scene videos were available to stitch.")

            export = MovieExport(
                plan_id=plan.id,
                export_dir=str(export_dir),
                status=JobStatus.completed if final_movie_path else JobStatus.skipped,
                narration_path=narration_path,
                subtitles_path=subtitles_path,
                json_path=json_path,
                timeline_path=timeline_path,
                prompt_history_path=prompt_history_path,
                character_database_path=character_database_path,
                location_database_path=location_database_path,
                scene_database_path=scene_database_path,
                metadata_path=metadata_path,
                character_bible_path=character_bible_path,
                location_bible_path=location_bible_path,
                shot_list_path=shot_list_path,
                voice_script_ssml_path=voice_script_ssml_path,
                sfx_plan_path=sfx_plan_path,
                music_plan_path=music_plan_path,
                storyboard_html_path=storyboard_html_path,
                final_movie_path=final_movie_path,
                video_assets=video_assets,
                warnings=warnings,
            )
            await self.repository.save_export(export)
            return export
        except Exception as exc:
            logger.exception("Background export task failed for plan %s", plan_id)
            existing = await self.repository.get_export(plan_id)
            if existing:
                existing.status = JobStatus.failed
                existing.warnings.append(f"Export failed: {str(exc)}")
                await self.repository.save_export(existing)
            raise

    def _write_text(self, path: Path, content: str) -> str:
        path.write_text(content, encoding="utf-8")
        return str(path)

    def _narration_text(self, plan: StoryPlan) -> str:
        return "\n\n".join(f"Scene {scene.order}: {scene.narration}" for scene in plan.scenes)

    def _subtitles(self, plan: StoryPlan) -> str:
        entries: list[str] = []
        current_seconds = 0
        for index, scene in enumerate(plan.scenes, start=1):
            start = current_seconds
            end = current_seconds + scene.duration_seconds
            entries.append(f"{index}\n{self._srt_time(start)} --> {self._srt_time(end)}\n{scene.narration}\n")
            current_seconds = end
        return "\n".join(entries)

    def _srt_time(self, seconds: int) -> str:
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},000"

    def _prompt_history(self, plan: StoryPlan) -> list[dict[str, str | int]]:
        return [
            {
                "scene_order": scene.order,
                "prompt": scene.prompt,
                "negative_prompt": scene.negative_prompt,
                "ending_frame": scene.ending_frame,
            }
            for scene in plan.scenes
        ]

    def _character_bible_md(self, plan: StoryPlan) -> str:
        lines = [f"# Character Bible - {plan.title}\n"]
        for c in plan.characters:
            lines.append(f"## {c.name}")
            if c.aliases:
                lines.append(f"**Aliases:** {', '.join(c.aliases)}")
            lines.append(f"- **Age:** {c.age or 'Unknown'}")
            lines.append(f"- **Gender:** {c.gender or 'Unknown'}")
            lines.append(f"- **Height:** {c.height or 'N/A'}")
            lines.append(f"- **Body Type:** {c.body_type or 'N/A'}")
            lines.append(f"- **Face Shape:** {c.face_shape or 'N/A'}")
            lines.append(f"- **Eye Colour:** {c.eye_colour or 'N/A'}")
            lines.append(f"- **Hair:** {c.hair or 'N/A'} ({c.hairstyle or 'Standard'})")
            lines.append(f"- **Skin Tone:** {c.skin_tone or 'N/A'}")
            lines.append(f"- **Clothing:** {c.clothing or 'N/A'}")
            lines.append(f"- **Power Level:** {c.power_level or 'Normal'}")
            lines.append(f"- **Abilities:** {', '.join(c.abilities) if c.abilities else 'None'}")
            lines.append(f"- **Voice:** {c.voice or 'N/A'}\n")
        return "\n".join(lines)

    def _location_bible_md(self, plan: StoryPlan) -> str:
        lines = [f"# Location Bible - {plan.title}\n"]
        for l in plan.locations:
            lines.append(f"## {l.name}")
            lines.append(f"- **Architecture:** {l.architecture or 'N/A'}")
            lines.append(f"- **Lighting:** {l.lighting or 'N/A'}")
            lines.append(f"- **Weather:** {l.weather or 'N/A'}")
            lines.append(f"- **Season:** {l.season or 'N/A'}")
            lines.append(f"- **Time of Day:** {l.time_of_day or 'N/A'}")
            lines.append(f"- **Textures:** {l.textures or 'N/A'}")
            lines.append(f"- **Vegetation:** {l.vegetation or 'N/A'}")
            lines.append(f"- **Props:** {', '.join(l.props) if l.props else 'None'}")
            lines.append(f"- **Colour Palette:** {l.colour_palette or 'N/A'}\n")
        return "\n".join(lines)

    def _voice_ssml(self, plan: StoryPlan) -> str:
        lines = ['<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">']
        for item in plan.voice_script:
            lines.append(f'  <!-- Scene {item.scene_order} - {item.speaker} -->')
            lines.append(f'  <p><s>{item.text}</s></p>')
        lines.append('</speak>')
        return "\n".join(lines)

    def _storyboard_html(self, plan: StoryPlan) -> str:
        rows = []
        for s in plan.scenes:
            rows.append(f"""
            <div style="border: 1px solid #3f3f46; border-radius: 8px; padding: 16px; margin-bottom: 16px; background: #18181b; color: #f4f4f5;">
                <h3 style="color: #f59e0b;">Scene {s.order}: {s.title}</h3>
                <p><strong>Narration:</strong> {s.narration}</p>
                <p><strong>Camera:</strong> {s.camera}</p>
                <p><strong>Prompt:</strong> {s.prompt}</p>
                <p><strong>Duration:</strong> {s.duration_seconds}s</p>
            </div>
            """)
        return f"""<!DOCTYPE html>
<html>
<head><title>Storyboard - {plan.title}</title></head>
<body style="background: #09090b; color: #f4f4f5; font-family: sans-serif; padding: 24px;">
    <h1>{plan.title} - Storyboard</h1>
    {"".join(rows)}
</body>
</html>"""

    async def _stitch_videos(self, video_paths: list[str], final_movie_path: str, export_dir: Path) -> None:
        concat_path = export_dir / "concat.txt"
        concat_path.write_text(
            "\n".join(f"file '{Path(path).resolve().as_posix()}'" for path in video_paths),
            encoding="utf-8",
        )

        def run_sync() -> None:
            completed = subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path), "-c", "copy", final_movie_path],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or "FFmpeg stitching failed")

        await asyncio.to_thread(run_sync)
