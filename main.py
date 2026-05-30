import PetPackageXG
from pathlib import Path

cwd = Path(__file__).parent
PetPackageXG.main(cwd.as_posix())
