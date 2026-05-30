import PetXG
from pathlib import Path

cwd = Path(__file__).parent
PetXG.main(cwd.as_posix())
