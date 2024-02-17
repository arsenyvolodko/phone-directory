class ValidationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

    ERROR_MESSAGE = "Error: Incorrect {} format: {}. Expected format: {}"


class PhoneValidationError(ValidationError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NameValidationError(ValidationError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
