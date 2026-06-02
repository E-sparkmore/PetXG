from . import script

def main(save_path):
    pet = script.PetMain(save_path)
    pet.exec()
if __name__ == '__main__':
    main(None)