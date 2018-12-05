from flask import current_app
import phonenumbers


def validate_phone(phone_no):
    parsed_phone_no = ''
    try:
        phone_no_obj = phonenumbers.parse(phone_no, 'SG')

        if phonenumbers.is_valid_number(phone_no_obj):
            parsed_phone_no = phonenumbers.format_number(
                phone_no_obj,
                phonenumbers.PhoneNumberFormat.E164
            )
    except Exception as e:
        current_app.logger.info("Unable to parse phone number: " + str(e))

    return parsed_phone_no
