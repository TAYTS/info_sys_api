from flask import jsonify, request, current_app
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import exc
from models import db, Users
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import hashlib
import qrcode
import boto3
import os


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
    qr_code_filepath = current_app.config['IMG_DIR'] + hashed_username + '.png'
    qr_code.save(qr_code_filepath)

    # Upload to S3 bucket
    S3_BUCKET = current_app.config['S3_BUCKET']
    S3_KEY = current_app.config['S3_KEY']
    S3_SECRET = current_app.config['S3_SECRET_ACCESS_KEY']
    S3_FILE_PATH = hashed_username + "/" + hashed_username + '.png'

    # Create the instance connection to the S3 bucket
    s3 = boto3.client(
        's3',
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET
    )

    # Upload the file to the S3 bucket
    try:
        s3.upload_file(
            Bucket=S3_BUCKET,
            Filename=qr_code_filepath,
            Key=S3_FILE_PATH
        )
    except Exception as e:
        current_app.logger.info('Upload QR code error: ' + str(e))
    finally:
        # Remove the local QR code image
        os.remove(qr_code_filepath)

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

    status = 1
    try:
        db.session.add(user)
        db.session.commit()
    except exc.IntegrityError:
        status = -1
    except Exception as e:
        current_app.logger.info(e)
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
