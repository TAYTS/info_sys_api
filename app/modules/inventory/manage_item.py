from flask import jsonify, request, current_app, session
from flask_login import login_required
from sqlalchemy import exc
from models import db, Users, Items
from werkzeug.utils import secure_filename
from datetime import datetime
from PIL import Image
import os

# Add custom helper modules
from app.utils.validate_file_ext import allowed_ext
from app.utils.img_resize import resizeImage
from app.utils.upload_img import uploadImage


@login_required
def add_item():
    hashed_vendor_id = str(session.get('id_user'))
    item_name = str(request.form.get('item_name', ''))
    description = str(request.form.get('description', ''))
    category = str(request.form.get('category', ''))
    price = float(request.form.get('price', 0.0))
    timestamp = datetime.utcnow().replace(microsecond=0)

    if (hashed_vendor_id and item_name and price):
        # Get the user
        user = db.session.query(
            Users
        ).filter(
            Users.id_user_hash == hashed_vendor_id
        ).scalar()

        if user:
            item = Items(
                id_user=user.id_user,
                item_name=item_name,
                description=description,
                category=category,
                price=price,
                create_timestamp=timestamp
            )

            try:
                db.session.add(item)
                db.session.commit()
                status = 1
            except exc.IntegrityError:
                status = -1
            except Exception as e:
                current_app.logger.info("Failed to add new item: " + str(e))
                status = 0
        else:
            status = 0
    else:
        status = 0

    return jsonify({'status': status})


@login_required
def remove_items():
    hashed_vendor_id = str(session.get('id_user'))
    item_name = request.form.get('item_name', '')
    status = 0
    if item_name and hashed_vendor_id:
        vendor_id = db.session.query(
            Users.id_user
        ).filter(
            Users.id_user_hash == hashed_vendor_id
        ).scalar()
        if vendor_id:
            try:
                status = db.session.query(
                    Items
                ).filter(
                    Items.id_user == vendor_id,
                    Items.item_name == item_name
                ).delete(synchronize_session=False)
                db.session.commit()
            except Exception as e:
                current_app.logger.info('Failed to remove items: ' + str(e))

    return jsonify({'status': status})


@login_required
def edit_item():
    hashed_vendor_id = str(session.get('id_user'))
    item_name = str(request.form.get('item_name', ''))
    description = str(request.form.get('description', ''))
    category = str(request.form.get('category', ''))
    price = float(request.form.get('price', 0.0))
    status = 0

    if item_name and hashed_vendor_id:
        vendor_id = db.session.query(
            Users.id_user
        ).filter(
            Users.id_user_hash == hashed_vendor_id
        ).scalar()
        if vendor_id:
            try:
                item = db.session.query(
                    Items
                ).filter(
                    Items.id_user == vendor_id,
                    Items.item_name == item_name
                ).scalar()

                item.description = description
                item.category = category
                item.price = price
                db.session.commit()
                status = 1
            except exc.IntegrityError:
                status = -1
            except Exception as e:
                current_app.logger.info("Failed to edit item: " + str(e))

    return jsonify({'status': status})


@login_required
def uploadItemImg():
    hashed_vendor_id = str(session.get('id_user'))
    item_name = str(request.form.get('item_name', ''))
    img_file = request.files.get('file', '')
    status = 0

    if hashed_vendor_id and item_name and img_file:
        if allowed_ext(img_file.filename):
            vendor_item = db.session.query(
                Users.id_user, Items
            ).join(
                Items,
                Items.id_user == Users.id_user
            ).filter(
                Users.id_user_hash == hashed_vendor_id,
                Items.item_name == item_name
            ).first()

            if vendor_item:
                # Create new filename
                filename = secure_filename(item_name) + '.png'

                # Save the image to tmp directory
                img_file = Image.open(img_file)
                filepath = os.path.join(
                    current_app.config['IMG_DIR'], hashed_vendor_id)
                os.mkdir(filepath)
                full_img_filename = os.path.join(filepath, filename)
                img_file.save(full_img_filename)

                # Resize the image
                if (resizeImage(img_path=full_img_filename, width=768, height=1024)):
                    S3_FILE_PATH = hashed_vendor_id + "/" + filename
                    # Upload the file to S3
                    if uploadImage(localpath=full_img_filename, S3path=S3_FILE_PATH):
                        vendor_item[1].image_url = S3_FILE_PATH
                        try:
                            db.session.commit()
                            status = 1
                        except Exception as e:
                            current_app.logger.info(
                                "Failed to save the profile_img_url: " + str(e))

    return jsonify({'status': status})
