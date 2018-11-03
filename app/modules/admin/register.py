from flask import jsonify, request, current_app
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import exc
from models import db, Users
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from PIL import Image
import hashlib
import qrcode
import os

# Add custom helper modules
from app.utils.validate_file_ext import allowed_ext
from app.utils.img_resize import resizeImage
from app.utils.upload_img import uploadImage


def register():
    password = str(request.form.get('password', ''))
    email = str(request.form.get('email', ''))
    username = str(request.form.get('username', ''))
    is_vendor = int(request.form.get('is_vendor', 0))

    # Return if any of the POST parameter is empty
    if not(password and email and username):
        return jsonify({'status': 0})

    # Hash the username and email
    unhashed_username = 'email:' + email + ';' + 'username:' + username
    hashed_username = hashlib.sha512(
        unhashed_username.encode('UTF-8')).hexdigest()

    # Generate QR code using the hashed username
    qr_code = qrcode.make(hashed_username)
    qr_filename = hashed_username + '_qrcode.png'
    qr_code_filepath = current_app.config['IMG_DIR'] + qr_filename
    qr_code.save(qr_code_filepath)

    S3_FILE_PATH = hashed_username + "/" + qr_filename

    if uploadImage(localpath=qr_code_filepath, S3path=S3_FILE_PATH):
        # Hash the password
        hashed_password = generate_password_hash(password)
        timestamp = datetime.utcnow().replace(microsecond=0)

        user = Users(
            password=hashed_password,
            email=email,
            username=username,
            qrcode_url=S3_FILE_PATH,
            profile_img_url='',
            id_user_hash=hashed_username,
            is_vendor=is_vendor,
            create_timestamp=timestamp
        )

        try:
            db.session.add(user)
            db.session.commit()
            status = 1
        except exc.IntegrityError:
            status = -1
        except Exception as e:
            current_app.logger.info(e)
            status = 0
    else:
        status = 0

    return jsonify({"status": status})


def login():
    # Return directly if the user has authenticated
    if current_user.is_authenticated:
        return jsonify({'status': 1})

    password = str(request.form.get('password', ''))
    email = str(request.form.get('email', ''))
    remember = int(request.form.get('remember', 0))

    # Return if any of the POST parameter is empty
    if not(password and email):
        return jsonify({'status': 0})

    # Get user using email
    user = db.session.query(
        Users
    ).filter(
        Users.email == email
    ).scalar()

    # Login verification
    if user:
        if user.check_password(password):
            login_user(user, remember=remember, duration=timedelta(minutes=30))
            return jsonify({'status': 1})
        else:
            return jsonify({'status': -1})
    else:
        return jsonify({'status': -1})


@login_required
def logout():
    try:
        logout_user()
        status = 1
    except Exception:
        status = 0

    return jsonify({'status': status})


@login_required
def getQRcode():
    email = str(request.form.get('email', ''))

    if not email:
        status = 0
        url = ''
    else:
        url = db.session.query(
            Users.qrcode_url
        ).filter(
            Users.email == email
        ).scalar()

        if url:
            status = 1
        else:
            status = -1
            url = ''

    return jsonify({
        'url': url,
        'status': status
    })


@login_required
def uploadProfileImg():
    img_file = request.files.get('file', '')
    email = str(request.form.get('email', ''))
    status = 0

    if img_file and email:
        # Verify the uploaded file extension before processing it
        if allowed_ext(img_file.filename):
            user = db.session.query(
                Users
            ).filter(
                Users.email == email
            ).scalar()

            if user:
                # Create new filename
                hashed_username = user.id_user_hash
                filename = hashed_username + '_profileimg.png'

                # Save the image to tmp directory
                img_file = Image.open(img_file)
                full_img_filename = os.path.join(
                    current_app.config['IMG_DIR'], filename)
                img_file.save(full_img_filename)

                # Resize the image
                if (resizeImage(img_path=full_img_filename, width=1080, height=1920)):
                    S3_FILE_PATH = hashed_username + "/" + filename
                    # Upload the file to S3
                    if uploadImage(localpath=full_img_filename, S3path=S3_FILE_PATH):
                        user.profile_img_url = S3_FILE_PATH
                        try:
                            db.session.commit()
                            status = 1
                        except Exception as e:
                            current_app.logger.info(
                                "Failed to save the profile_img_url: " + str(e))
            else:
                status = -1
        else:
            status = -1
    else:
        status = -1

    return jsonify({'status': status})
