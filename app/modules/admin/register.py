from flask import jsonify, request, current_app, session
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import exc
from models import db, Users, FCM_Access_Token
from werkzeug.security import generate_password_hash
from datetime import datetime
import hashlib
import qrcode
import os

# Add custom helper modules
from app.utils.img_resize import resizeImage
from app.utils.upload_img import uploadImage
from app.utils.str_to_img import str_to_img


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
    qr_filename = 'qrcode.png'
    filepath = os.path.join(
        current_app.config['IMG_DIR'], hashed_username)
    os.mkdir(filepath)
    qr_code_filepath = os.path.join(filepath, qr_filename)
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
            current_app.logger.info('Failed to add new user: ' + str(e))
            status = 0
    else:
        status = 0

    return jsonify({"status": status})


def login():
    # Return directly if the user has authenticated
    if current_user.is_authenticated:
        is_vendor = session.get('is_vendor', -1)
        if is_vendor != -1:
            status = 1
        else:
            status = -1
        return jsonify({
            'status': status,
            'is_vendor': is_vendor
        })

    password = str(request.form.get('password', ''))
    email = str(request.form.get('email', ''))
    device_id = str(request.form.get('deviceID', ''))

    # Return if any of the POST parameter is empty
    if not(password and email):
        return jsonify({'status': 0})

    # Get user account and FCM ID using email
    user = db.session.query(
        Users, FCM_Access_Token
    ).outerjoin(
        FCM_Access_Token,
        db.and_(
            Users.id_user == FCM_Access_Token.id_user,
            FCM_Access_Token.access_token == device_id
        )
    ).filter(
        Users.email == email
    ).first()

    # Login verification
    if user:
        if user.Users.check_password(password):
            # If the user does not have FCM Access Token
            # Add new record
            if not user.FCM_Access_Token:
                try:
                    FCM_token = FCM_Access_Token(
                        id_user=user.Users.id_user,
                        access_token=device_id
                    )
                    db.session.add(FCM_token)
                    db.session.commit()
                except exc.IntegrityError:
                    current_app.logger.info(
                        "Unable to add FCM Token due to integrity issue")
                except Exception as e:
                    current_app.logger.info(
                        "Failed to add FCM Toekn: " + str(e))
                    return jsonify({
                        'status': -1,
                        'is_vendor': -1
                    })
            login_user(user.Users)
            session['id_user'] = user.Users.id_user_hash
            session['is_vendor'] = user.Users.is_vendor
            return jsonify({
                'status': 1,
                'is_vendor': user.Users.is_vendor
            })
        else:
            return jsonify({
                'status': -1,
                'is_vendor': -1
            })
    else:
        return jsonify({
            'status': -1,
            'is_vendor': -1
        })


@login_required
def logout():
    try:
        session.clear()
        logout_user()
        status = 1
    except Exception:
        status = 0

    return jsonify({'status': status})


@login_required
def getQRcode():
    hashed_vendor_id = str(session.get('id_user'))
    if hashed_vendor_id:
        url = db.session.query(
            Users.qrcode_url
        ).filter(
            Users.id_user_hash == hashed_vendor_id
        ).scalar()

        if url:
            status = 1
        else:
            status = -1
            url = ''
    else:
        status = 0
        url = ''

    return jsonify({
        'url': url,
        'status': status
    })


@login_required
def uploadProfileImg():
    img_file = str(request.form.get('file', ''))
    hashed_vendor_id = str(session.get('id_user'))
    status = 0

    if img_file and hashed_vendor_id:
        user = db.session.query(
            Users
        ).filter(
            Users.id_user_hash == hashed_vendor_id
        ).scalar()

        if user:
            # Create new filename
            filename = 'profileimg.png'

            # Create tmp file directory for image
            filepath = os.path.join(
                current_app.config['IMG_DIR'], hashed_vendor_id)
            os.mkdir(filepath)
            full_img_filename = os.path.join(filepath, filename)

            if str_to_img(img_file, full_img_filename):
                # Resize the image
                if (resizeImage(img_path=full_img_filename, width=1080, height=1920)):
                    S3_FILE_PATH = hashed_vendor_id + "/" + filename
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

    return jsonify({'status': status})
