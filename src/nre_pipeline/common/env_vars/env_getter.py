import os
from typing import Any, Optional, Callable, Literal, TypeAlias, overload

from nre_pipeline.common.env_vars.exceptions import (
    BooleanEnvironmentError,
    KeyMissingEnvironmentError,
    PositiveIntEnvironmentError,
    ValueMissingEnvironmentError,
    StrValidationEnvironmentError,
)

TRequired: TypeAlias = Literal["exists"]
TValidator: TypeAlias = Callable[[Optional[str]], bool]

ACCEPTED_TRUE_VALUES = ["true", True, "1", "yes"]
ACCEPTED_FALSE_VALUES = ["false", False, "0", "no"]
ALL_ACCEPTED_BOOL_VALUES = ACCEPTED_TRUE_VALUES + ACCEPTED_FALSE_VALUES

ValidValidationType: TypeAlias = TRequired | TValidator | None


def default_str_is_valid(x) -> bool:
    return x is not None and len(x) > 0


def default_bool_is_valid(x) -> bool:
    is_not_none = x is not None
    within_accepted_values = x in ALL_ACCEPTED_BOOL_VALUES or x.lower().strip("'").strip('"') in ALL_ACCEPTED_BOOL_VALUES
    return is_not_none and within_accepted_values


def default_positive_int_is_valid(x: Any) -> bool:
    is_not_none = x is not None
    is_number = isinstance(x, int) or (isinstance(x, str) and x.isdigit())
    is_gt_zero = int(x) > 0 if is_number else False
    return (is_not_none and is_number and is_gt_zero) is True


# Overload for required = "exists"
@overload
def get_env(key: str, required: TRequired | TValidator = "exists") -> str: ...


# Overload for required = None
@overload
def get_env(key: str, required: None = None) -> Optional[str]: ...


def get_env(
    key: str,
    required: TRequired | TValidator | None = None,
) -> Optional[str]:
    """
    Retrieve the value for a specified environment variable.
    - If required is "exists": raises EnvironmentError if not set, returns str otherwise.
    - If required is a callable: raises EnvironmentError if callable returns False, returns str otherwise.
    - If required is None: returns Optional[str].
    """
    if key not in os.environ:
        raise KeyMissingEnvironmentError(key)
    value = os.getenv(key, None)
    # required = "exists"
    if required == "exists":
        if value is None:
            raise ValueMissingEnvironmentError(key)
        return value
    # required is a callable
    if callable(required):
        if not required(value):
            raise StrValidationEnvironmentError(key, value)
        return value
    # required is None
    return value


def get_env_as_int(
    key, required: TRequired | TValidator | None = "exists"
) -> Optional[int]:
    val: Optional[str] = get_env(key, required=required)

    if required is None and val is None:
        return None

    if required == "exists":
        required = default_positive_int_is_valid

    assert required is not None
    if not required(val):
        raise PositiveIntEnvironmentError(key, val)
    assert val is not None
    return int(val)


def get_env_as_bool(
    key, required: TRequired | TValidator | None = "exists"
) -> Optional[bool]:
    val: Optional[str] = get_env(key, required=required)
    bool_val = None

    if required is None and val is None:
        return None

    if required == "exists":
        required = default_bool_is_valid

    assert required is not None
    if not required(val):
        raise BooleanEnvironmentError(key, val)
    bool_val = val in ("true", "1")

    return bool_val
