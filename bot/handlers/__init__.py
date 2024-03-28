from .change_menu import handle_change_menu_callback_query
from .discuss_transcription import handle_discuss_transcription
from .new_transcription import handle_add_new_transcription
from .start import handle_start


__all__ = [
    'handle_start',
    'handle_change_menu_callback_query',
    'handle_add_new_transcription',
    'handle_discuss_transcription'
]
