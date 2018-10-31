from flask import jsonify, request
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import exc
from models import db, Users
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import hashlib


def register():
    password = str(request.form.get('password', ''))
    email = str(request.form.get('email', ''))
    username = str(request.form.get('username', ''))
    is_vendor = int(request.form.get('is_vendor', 0))

    # Return if any of the POST parameter is empty
    if not(password and email and username):
        return jsonify({'status': 0})

    # Hash the username and email
    unhashed_username = "email:" + email + ";" + "username:" + username
    hashed_username = hashlib.sha512(
        unhashed_username.encode('UTF-8')).hexdigest()

    # Hash the password
    hashed_password = generate_password_hash(password)

    timestamp = datetime.utcnow().replace(microsecond=0)

    user = Users(
        password=hashed_password,
        email=email,
        username=username,
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
    except Exception:
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
