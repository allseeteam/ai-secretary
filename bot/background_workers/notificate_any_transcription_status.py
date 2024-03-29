import logging

from telegram.ext import Application

from database import (
    get_details_for_any_transcription_with_given_status,
    update_transcription_details_by_id,
)


async def notificate_any_transcription_status(application: Application) -> None:
    for transcription_status in [
        "Transcribed"
    ]:
        transcription_chat_id_and_title = get_details_for_any_transcription_with_given_status(
            transcription_status=transcription_status,
            details_to_get=["id", "chat_id", "title"]
        )
    
        if transcription_chat_id_and_title:
            transcription_id = transcription_chat_id_and_title['id']
            transcription_chat_id = transcription_chat_id_and_title['chat_id']
            transcription_title = transcription_chat_id_and_title['title']

            try:
                await application.bot.send_message(
                    chat_id=transcription_chat_id,
                    text=f"Ваша транскрипция {transcription_title} успешно завершена!",
                )

                update_transcription_details_by_id(
                    transcription_id,
                    {'status': "Transcribed and notified"}
                )

                logging.info(f"Sent notification to {transcription_chat_id}")

            except Exception as e:
                update_transcription_details_by_id(
                    transcription_id,
                    {'status': "Transcribed and failed to notify"}
                )

                logging.error(f"Error saving {transcription_id} file path: {e}")
