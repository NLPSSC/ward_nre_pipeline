from typing import Any, Optional


class KeyMissingEnvironmentError(EnvironmentError):
    def __init__(self, key: str) -> None:
        super().__init__(f"Environment variable '{key}' does not exist.")


class ValueMissingEnvironmentError(EnvironmentError):
    def __init__(self, key: str) -> None:
        super().__init__(f"Value for environment variable '{key}' does not exist.")


class MethodValidationEnvirontmentError(EnvironmentError):
    def __init__(
        self, key: str, value: Any, validation_description: Optional[str] = None
    ) -> None:
        super().__init__(
            f"Method validation for key='{key}' and value='{value}' failed: {validation_description}."
        )


class StrValidationEnvironmentError(MethodValidationEnvirontmentError):
    def __init__(
        self, key: str, value: Any, validation_description: Optional[str] = None
    ) -> None:
        super().__init__(key, value, validation_description or "default_str_is_valid")


class PositiveIntEnvironmentError(MethodValidationEnvirontmentError):
    def __init__(
        self, key: str, value: Any, validation_description: Optional[str] = None
    ) -> None:
        super().__init__(
            key, value, validation_description or "default_positive_int_is_valid"
        )


class BooleanEnvironmentError(MethodValidationEnvirontmentError):
    def __init__(
        self, key: str, value: Any, validation_description: Optional[str] = None
    ) -> None:
        super().__init__(key, value, validation_description or "default_bool_is_valid")
