from flask import current_app
from pyfcm import FCMNotification


def push_notification(title, body):
    api_key = current_app.config['FSM_API_KEY']
    push_service = FCMNotification(api_key=api_key)

    registration_id = 'dW_i98gdA9E:APA91bERvKntGP-r9ghZmHFxFYZHMDzTaCsWKFI6_Gt5joaXQzweMgN99et8gX1n5BIojWnFU9mZQK958DPZrZY3NbnvJ2SAGQOU5WQBkZmzKjU3Av_i-3jfAqFhaQAV1_B8Xu8WPhHe'
    message_title = title
    message_body = body
    result = push_service.notify_single_device(
        registration_id=registration_id,
        message_title=message_title,
        message_body=message_body
    )

    return result.get('success')
