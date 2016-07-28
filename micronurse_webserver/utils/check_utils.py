def check_phone_num(phone_num: str):
    for c in phone_num:
        if '0' <= c <= '9':
            continue
        else:
            return False
    return True


CHECK_SUCCESS = 0
PASSWORD_LENGTH_ILLEGAL = 1
PASSWORD_FORMAT_ILLEGAL = 2


def check_password(password: str):
    if len(password) < 6 or len(password) > 20:
        return PASSWORD_LENGTH_ILLEGAL
    return CHECK_SUCCESS
