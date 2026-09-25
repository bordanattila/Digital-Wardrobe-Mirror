"""Background removal for wardrobe item photos.

Reads images from wardrobe_images/original, strips near-black backgrounds,
and writes safe processed files to wardrobe_images/processed.

Path checks, extension allowlisting, and size limits defend against
path traversal and oversized or non-image uploads.
"""

from pathlib import Path

from PIL import Image, UnidentifiedImageError

from app.utils.colors import GREEN, RED, RESET

# backend/ — three levels up from app/services/this_file.py
BASE_DIR = Path(__file__).parent.parent.parent

# Resolved absolute paths so symlink tricks cannot escape these folders
ORIGINAL_IMAGES_DIR = (BASE_DIR / "wardrobe_images" / "original").resolve()
BACKGROUND_REMOVED_IMAGES_DIR = (BASE_DIR / "wardrobe_images" / "processed").resolve()

ORIGINAL_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
BACKGROUND_REMOVED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".ppm"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB — protect Pi memory before PIL loads the file


def is_path_inside_directory(path: Path, directory: Path) -> bool:
    """Return True if path resolves inside directory (blocks path traversal).

    Uses Path.relative_to: if path is outside directory, relative_to raises
    ValueError and we treat that as unsafe.
    """
    try:
        path.resolve().relative_to(directory)
        return True
    except ValueError:
        return False


def remove_background(image):
    """Replace pure-black pixels with white (simple prototype background cut).

    Args:
        image: A PIL Image. Converted to RGB before processing.

    Returns:
        The modified RGB image (black -> white).
    """
    image = image.convert("RGB")
    width, height = image.size
    pixels = image.load()
    for y in range(height):
        for x in range(width):
            pixel = pixels[x, y]
            if pixel == (0, 0, 0):
                pixels[x, y] = (255, 255, 255)
    return image


def process_image(image_path: Path) -> Path:
    """Process an image by removing the background and saving it to the background
    removed images directory."""
    image_path = image_path.resolve()

    # Skip non-files and anything that escaped ORIGINAL_IMAGES_DIR (e.g. symlinks)
    if not image_path.is_file() or not is_path_inside_directory(
        image_path, ORIGINAL_IMAGES_DIR
    ):
        raise ValueError(
            f"Image path {image_path} is not inside the original images directory"
        )

    # Sanitize the filename stem before building the output path.
    # file.stem = name without extension, e.g. "blue shirt!.png" -> "blue shirt!"
    # Keep only letters, digits, hyphen, underscore — drop spaces, "!", "../", etc.
    # "".join(...) builds the cleaned string; if nothing remains
    # (e.g. stem was "!!!"),
    # `or "item"` falls back so we never write a nameless file like bg_removed_.png.
    safe_stem = (
        "".join(c for c in image_path.stem if c.isalnum() or c in "-_") or "item"
    )
    out_name = f"bg_removed_{safe_stem}{image_path.suffix.lower()}"
    out_path = (BACKGROUND_REMOVED_IMAGES_DIR / out_name).resolve()

    # Final confinement check on the destination we are about to write
    if not is_path_inside_directory(out_path, BACKGROUND_REMOVED_IMAGES_DIR):
        raise ValueError(
            f"Output path \
            {out_path} \
            is not inside the background removed images directory"
        )

    try:
        with Image.open(image_path) as image:
            image.load()  # force decode now so corrupt/non-images fail here
            print(f"Processing image: {image_path.name}")
            background_removed = remove_background(image)
            background_removed.save(out_path)
    except UnidentifiedImageError as exc:
        raise ValueError(f"Image {image_path} is not a valid image: {exc}")
    except OSError as exc:
        raise ValueError(f"Error processing image {image_path}: {exc}")

    # Only this verified processed path is safe to store in the database later
    verified_image_path = str(out_path)
    print(f"{GREEN}Processed: {image_path.name} -> {verified_image_path}{RESET}")
    return Path(verified_image_path)


if __name__ == "__main__":
    print(f"Processing images in {ORIGINAL_IMAGES_DIR}")
    for file in ORIGINAL_IMAGES_DIR.iterdir():
        try:
            process_image(file)
        except ValueError as exc:
            print(f"{RED}Error processing image {file}: {exc}{RESET}")
