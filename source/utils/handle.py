class CustomResponse:
    def __init__(self, status, message, data):
        self.status = status
        self.message = message

        if data is not None:
            self.data = data