from PIL import Image
from resizeimage import resizeimage


def resizeImage(img_path, width=768, height=1024):

    try:
        with open(img_path, 'r+b') as f:
            with Image.open(f) as image:
                cover = resizeimage.resize_cover(
                    image, [width, height], validate=False)
                cover.save(img_path, image.format)
        return True
    except Exception:
        return False
