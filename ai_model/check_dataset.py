
from pathlib import Path
from PIL import Image

dataset = Path("dataset")

valid_extensions = {".jpg", ".jpeg", ".png"}

for category in ["e_waste", "natural_waste"]:
    folder = dataset / category

    print(f"\nChecking {category}:")

    if not folder.exists():
        print("ERROR: Folder not found!")
        continue

    for file in folder.iterdir():

        if file.suffix.lower() not in valid_extensions:
            print("SKIPPED:", file.name)
            continue

        try:
            with Image.open(file) as img:
                img.verify()

            if file.stat().st_size == 0:
                print("EMPTY:", file.name)
            else:
                print("VALID:", file.name)

        except Exception as error:
            print("INVALID:", file.name, error)
