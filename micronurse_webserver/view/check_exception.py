from rest_framework.exceptions import APIException


class CheckException(APIException):
    def __init__(self, result_code: int, message: str, status: int=422):
        self.status = status
        self.result_code = result_code
        self.detail = message
