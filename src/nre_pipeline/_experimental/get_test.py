import os
from typing import Optional, Callable, Literal, TypeAlias, overload

TRequired: TypeAlias = Literal["exists"]
TValidator: TypeAlias = Callable[[Optional[str]], bool]


# Overload for required = "exists"
@overload
def get(key: str, required: TRequired) -> str: ...


# Overload for required = Callable[[Optional[str]], bool]
@overload
def get(key: str, required: TValidator) -> str: ...


# Overload for required = None
@overload
def get(key: str, required: None = None) -> Optional[str]: ...


def get(
    key: str,
    required: "TRequired | TValidator | None" = None,
) -> Optional[str]:
    """
    Retrieve the value for a specified environment variable.
    - If required is "exists": raises EnvironmentError if not set, returns str otherwise.
    - If required is a callable: raises EnvironmentError if callable returns False, returns str otherwise.
    - If required is None: returns Optional[str].
    """
    value = os.getenv(key, None)
    # required = "exists"
    if required == "exists":
        if value is None:
            raise EnvironmentError(f"Environment variable '{key}' does not exist.")
        return value
    # required is a callable
    if callable(required):
        if not required(value):
            raise EnvironmentError(
                f"Validation failed for environment variable '{key}' with value '{value}'"
            )
        return value
    # required is None
    return value


if __name__ == "__main__":

    os.environ["TEST_VAR"] = "123"
    assert get("TEST_VAR", required="exists") == "123"
    assert get("TEST_VAR", required=lambda x: x == "123") == "123"
    assert get("NON_EXISTENT_VAR") is None

    try:
        get("NON_EXISTENT_VAR", required="exists")
    except EnvironmentError as ex:
        assert str(ex) == "Environment variable 'NON_EXISTENT_VAR' does not exist."
    else:
        raise AssertionError("Expected EnvironmentError for missing variable with required='exists'")
    
    try:
        get("NON_EXISTENT_VAR", required=lambda x: x == "123")
    except EnvironmentError as ex:
        assert str(ex) == "Validation failed for environment variable 'NON_EXISTENT_VAR' with value 'None'"
    else:
        raise AssertionError("Expected EnvironmentError for missing variable with required=lambda")