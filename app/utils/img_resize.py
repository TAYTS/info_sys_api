from PIL import Image


def resizeImage(img_path, width=768, height=1024):

    try:
        with open(img_path, 'r+b') as f:
            with Image.open(f) as image:
                new_img = image.resize((width, height), Image.ANTIALIAS)
                new_img.save(img_path, image.format)
        return True
    except Exception:
        return False
