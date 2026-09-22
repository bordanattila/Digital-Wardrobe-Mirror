from PIL import Image
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
# Image directory at root/backend/wardrobe_images/original
ORIGINAL_IMAGES_DIR = BASE_DIR / "wardrobe_images" / "original"
# Image directory at root/backend/wardrobe_images/processed
BACKGROUND_REMOVED_IMAGES_DIR = BASE_DIR / "wardrobe_images" / "processed"
# Create the directories if they don't exist
ORIGINAL_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
BACKGROUND_REMOVED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


def remove_background(image):
    # Convert the image to RGB
    image = image.convert("RGB")
    # Get the width and height of the image
    width, height = image.size
    # Get the pixels of the image
    pixels = image.load()
    # Remove the background of the image
    for y in range(height):
        for x in range(width):
            # Get the pixel
            pixel = pixels[x, y]
            # If the pixel is black, set it to white
            if pixel == (0, 0, 0):
                pixels[x, y] = (255, 255, 255)
    return image


# Process images in the original directory
if __name__ == "__main__":
    print(f"Processing images in {ORIGINAL_IMAGES_DIR}")
    for file in ORIGINAL_IMAGES_DIR.iterdir():
        if not file.is_file():
            continue

        with Image.open(file) as image:
            print(f"Processing image: {file.name}")
            background_removed_image = remove_background(image)
            background_removed_image.save(BACKGROUND_REMOVED_IMAGES_DIR / f"bg_removed_{file.name}")

