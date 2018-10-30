from flask import jsonify, request
from sqlalchemy import exc
from datetime import datetime
from models import db, Vendors, Users
import hashlib


def register_vendor():
    password = request.form['password']
    email = request.form['email']
    vendor_name = request.form['name']

    # Return if any of the POST parameter is empty
    if not(len(password) and len(email) and len(vendor_name)):
        return jsonify({'status': 0})

    # Hash the vendor name and email
    unhashed_vendor_name = "email:" + email + ";" + "vendor_name:" + vendor_name
    hashed_vendor_name = hashlib.sha512(
        unhashed_vendor_name.encode('UTF-8')).hexdigest()

    # Hash the password
    hashed_password = hashlib.sha512(
        password.encode('UTF-8')).hexdigest()

    timestamp = datetime.utcnow().replace(microsecond=0)

    vendor = Vendors(
        password=hashed_password,
        email=email,
        vendor_name=vendor_name,
        id_vendor_hash=hashed_vendor_name,
        create_timestamp=timestamp
    )

    status = 1
    try:
        db.session.add(vendor)
        db.session.commit()
    except exc.IntegrityError:
        status = -1
    except Exception:
        status = 0

    return jsonify({"status": status})


def register_user():
    password = str(request.form['password'])
    email = str(request.form['email'])
    username = str(request.form['name'])

    # Return if any of the POST parameter is empty
    if not(len(password) and len(email) and len(username)):
        return jsonify({'status': 0})

    # Hash the vendor name and email
    unhashed_username = "email:" + email + ";" + "vendor_name:" + username
    hashed_username = hashlib.sha512(
        unhashed_username.encode('UTF-8')).hexdigest()

    # Hash the password
    hashed_password = hashlib.sha512(
        password.encode('UTF-8')).hexdigest()

    timestamp = datetime.utcnow().replace(microsecond=0)

    user = Users(
        password=hashed_password,
        email=email,
        vendor_name=username,
        id_vendor_hash=hashed_username,
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
