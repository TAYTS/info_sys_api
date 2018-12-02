from flask import current_app
from pyfcm import FCMNotification
from models import db, FCM_Access_Token


def push_notification(title, body, id_vendor):
    api_key = current_app.config['FSM_API_KEY']
    push_service = FCMNotification(api_key=api_key)

    token_query = db.session.query(
        FCM_Access_Token
    ).filter(
        FCM_Access_Token.id_user == id_vendor
    )

    token_list = token_query.all()
    registration_ids = []
    for token in token_list:
        registration_ids.append(token.access_token)

    message_title = title
    message_body = body
    results = push_service.notify_multiple_devices(
        registration_ids=registration_ids,
        message_title=message_title,
        message_body=message_body
    ).get('results', [])

    # Remove the unused token if there is any
    reject_token = []
    for idx in range(len(results)):
        if 'error' in results[idx]:
            reject_token.append(registration_ids[idx])

    if reject_token:
        token_query = token_query.filter(
            FCM_Access_Token.access_token.in_(reject_token)
        ).delete(synchronize_session=False)
        db.session.commit()
