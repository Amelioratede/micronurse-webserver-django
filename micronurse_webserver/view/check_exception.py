from rest_framework.exceptions import APIException


class CheckException(APIException):
    def __init__(self, status: int, result_code: int, message: str):
        self.status = status
        self.result_code = result_code
        self.detail = message
