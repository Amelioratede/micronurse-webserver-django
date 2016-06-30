from rest_framework.exceptions import APIException


class CheckException(APIException):
    def __init__(self, status_code: int, result_code: int, message: str):
        self.status_code = status_code
        self.result_code = result_code
        self.detail = message
