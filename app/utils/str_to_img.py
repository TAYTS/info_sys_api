from flask import current_app
import base64
import os


def str_to_img(img_str, filepath):
    current_app.logger.info("image string: " + img_str)
    try:
        imgdata = base64.b64decode(img_str)
        with open(filepath, 'wb') as f:
            f.write(imgdata)
        return True
    except Exception as e:
        current_app.logger.info(
            "Failed to convert image string to binary file: " + str(e))
        os.rmdir(filepath[:filepath.rindex('/')])
        return False
