from flask import current_app


def allowed_ext(filename):
    allow = '.' in filename and filename.rsplit(
        '.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

    return allow
