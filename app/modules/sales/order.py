from flask import jsonify, request, current_app, session
from flask_login import login_required
from models import db, Items, Users, Tasks
from datetime import datetime
import json

# Add custom helper modules
from app.utils.push_notificaiton import push_notification


@login_required
def submit_order():
    content = json.loads(request.data)
    orders = json.loads(content.get('orders', []))
    hashed_customer_id = str(session.get('id_user'))
    hashed_vendor_id = content.get('vendor_id', '')
    table_id = content.get('table_id', 0)
    timestamp = datetime.utcnow().replace(microsecond=0)

    if orders and hashed_vendor_id and table_id and hashed_customer_id:
        item_list = [x['item_name'] for x in orders]
        item_count = {}
        for x in orders:
            item_count[x['item_name']] = x['qty']

        customer = db.aliased(Users)
        query = db.session.query(
            Items, customer
        ).join(
            Users,
            Users.id_user == Items.id_user
        ).outerjoin(
            customer,
            customer.id_user_hash == hashed_customer_id
        ).filter(
            Users.id_user_hash == hashed_vendor_id,
            Items.item_name.in_(item_list)
        ).all()

        if query:
            tasks = []
            for x in query:
                task = Tasks(
                    id_user=x[0].id_user,
                    id_cust=x[1].id_user if x[1].id_user else -1,
                    id_item=x[0].id_item,
                    id_table=table_id,
                    order_count=item_count.get(x[0].item_name),
                    create_timestamp=timestamp
                )
                x[0].order_count += item_count.get(x[0].item_name)
                tasks.append(task)
            try:
                db.session.add_all(tasks)
                db.session.commit()
                # Send push notification to the Vendor
                push_notification(
                    title="New Order",
                    body="Your have new order!",
                    id_vendor=hashed_vendor_id
                )
                status = 1
            except Exception as e:
                current_app.logger.info("Failed to add order: " + str(e))
                status = 0
        else:
            status = 0
    else:
        status = 0

    return jsonify({'status': status})


@login_required
def getOrders():
    hashed_user_id = str(session.get('id_user'))
    order_list = db.session.query(
        Tasks, Items
    ).join(
        Users,
        Tasks.id_cust == Users.id_user
    ).join(
        Items,
        Tasks.id_item == Items.id_item
    ).filter(
        Users.id_user_hash == hashed_user_id
    ).order_by(
        Tasks.create_timestamp
    ).all()

    orders = []
    if order_list:
        for order in order_list:
            tmp = {
                'item_name': order[1].item_name,
                'qty': order[0].order_count
            }
            orders.append(tmp)

    return jsonify({'orders': orders})


@login_required
def getTasks():
    hashed_vendor_id = str(session.get('id_user'))
    tasks = db.session.query(
        Tasks, Items
    ).join(
        Users,
        Tasks.id_user == Users.id_user
    ).join(
        Items,
        Tasks.id_item == Items.id_item
    ).filter(
        Users.id_user_hash == hashed_vendor_id
    ).order_by(
        Tasks.create_timestamp
    ).all()

    jobs = []
    if tasks:
        for task in tasks:
            job = {
                'task_id': task[0].id_task,
                'item_name': task[1].item_name,
                'qty': task[0].order_count,
                'table_id': task[0].id_table
            }
            jobs.append(job)

    return jsonify({'jobs': jobs})


@login_required
def jobDone():
    hashed_vendor_id = str(session.get('id_user'))
    task_id = request.form.get('task_id')
    status = 0

    if task_id and hashed_vendor_id:
        try:
            status = db.session.query(
                Tasks
            ).filter(
                Users.id_user_hash == hashed_vendor_id,
                Tasks.id_user == Users.id_user,
                Tasks.id_task == task_id
            ).delete(synchronize_session=False)
            db.session.commit()
        except Exception as e:
            current_app.logger.info("Failed to remove task: " + str(e))

    return jsonify({'status': status})
