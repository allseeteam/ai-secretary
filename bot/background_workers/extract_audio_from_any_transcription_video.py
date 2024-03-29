import logging
import os

from moviepy.video.io.VideoFileClip import VideoFileClip

from database import (
    get_details_for_any_transcription_with_given_status,
    update_transcription_details_by_id
)


async def extract_audio_from_video(video_path: str, audio_path: str) -> None:
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)

    with VideoFileClip(video_path) as video:
        video.audio.write_audiofile(audio_path, )


async def extract_audio_from_any_transcription_video():
    transcription_id_and_video_file_path = get_details_for_any_transcription_with_given_status(
        transcription_status="Awaiting to audio extraction",
        details_to_get=["id", "uploaded_file_id", "video_file_path"]
    )

    if transcription_id_and_video_file_path:
        transcription_id = transcription_id_and_video_file_path["id"]
        uploaded_file_id = transcription_id_and_video_file_path["uploaded_file_id"]
        video_file_path = transcription_id_and_video_file_path["video_file_path"]

        try:
            video_file_path_parts = video_file_path.split("/")
            audio_file_path = "/".join(
                video_file_path_parts[:-2]
                +
                ["music", f"{uploaded_file_id}.mp3"]
            )

            update_transcription_details_by_id(
                transcription_id,
                {
                    "status": "Extracting audio from video"
                }
            )

            await extract_audio_from_video(video_file_path, audio_file_path)

            update_transcription_details_by_id(
                transcription_id,
                {
                    "audio_file_path": audio_file_path,
                    "status": "Awaiting upload to transcription API"
                }
            )

        except Exception as e:
            logging.error(f"Failed to extract audio from transcription with id {transcription_id}: {e}")
