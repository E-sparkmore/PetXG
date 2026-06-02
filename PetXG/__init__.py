from .deps import *
from . import pet_label, audio_ui, ai_chat, config, resource, styles, ai_ui, tools
from .__version__ import __title__, __description__, __version__
from .script import main

__all__ = ["main", "pet_label", "audio_ui", "ai_chat", "config", "styles"]