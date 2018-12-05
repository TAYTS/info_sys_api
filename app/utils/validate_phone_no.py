import phonenumbers


def validate_phone(phone_no):
    phone_no_obj = phonenumbers.parse(phone_no, 'SG')
    parsed_phone_no = ''

    if phonenumbers.is_valid_number(phone_no_obj):
        parsed_phone_no = phonenumbers.format_number(
            phone_no_obj,
            phonenumbers.PhoneNumberFormat.E164
        )

    return parsed_phone_no
