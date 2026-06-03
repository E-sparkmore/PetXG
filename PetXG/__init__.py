from .setting.deps import *
from . import pet_label, audio_ui, resource, agent, setting
from .__version__ import __title__, __description__, __version__
from .script import main, PetMain

__all__ = ["main", "pet_label", "audio_ui", "agent", "setting"]