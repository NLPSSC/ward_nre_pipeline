import os
from typing import Any, Literal, Optional, Callable, TypeAlias, cast

from nre_pipeline.common.env_vars.exceptions import (
    BooleanEnvironmentError,
    KeyMissingEnvironmentError,
    PositiveIntEnvironmentError,
    StrValidationEnvironmentError,
)

TValidator: TypeAlias = Optional[Callable[[Optional[str]], bool]]
TEnvRetVal: TypeAlias = str | Literal["undefined"]

ACCEPTED_TRUE_VALUES = ["true", True, "1", "yes"]
ACCEPTED_FALSE_VALUES = ["false", False, "0", "no"]
ALL_ACCEPTED_BOOL_VALUES = ACCEPTED_TRUE_VALUES + ACCEPTED_FALSE_VALUES


def default_str_is_valid(x) -> bool:
    return x is not None and len(x) > 0


def default_bool_is_valid(x) -> bool:
    is_not_none = x is not None
    within_accepted_values = _is_bool_equivalent(x)
    return is_not_none and within_accepted_values


def _is_bool_equivalent(x):
    _x = x
    if isinstance(x, tuple) and len(x) > 1:
        _x = x[0]
    return (
        _x in ALL_ACCEPTED_BOOL_VALUES
        or str(_x).lower().strip("'").strip('"') in ALL_ACCEPTED_BOOL_VALUES
    )


def default_positive_int_is_valid(x: Any) -> bool:
    is_not_none = x is not None
    is_number = isinstance(x, int) or (isinstance(x, str) and x.isdigit())
    is_gt_zero = int(x) > 0 if is_number else False
    return (is_not_none and is_number and is_gt_zero) is True


def _convert_none_to_undefined(value: Optional[str]) -> TEnvRetVal:
    return "undefined" if (value == "None" or value is None) else value


def _convert_undefined_to_none(value: TEnvRetVal) -> Optional[str]:
    return None if value == "undefined" else value


def get_env(
    key: str,
    validator: TValidator = None,
) -> TEnvRetVal:
    """
    Retrieve the value for a specified environment variable.
    - If validator is a callable: raises EnvironmentError if callable returns False, returns str otherwise.
    - If validator is None: returns Optional[str].
    """

    if validator is None:
        validator = default_str_is_valid

    if key not in os.environ:
        raise KeyMissingEnvironmentError(key)
    value: TEnvRetVal = _convert_none_to_undefined(os.getenv(key, None))

    # validator is a callable
    if callable(validator):
        if not validator(value):
            raise StrValidationEnvironmentError(key, value)
        return value
    # validator is None
    
    return value


def get_env_as_positive_integer(key, validator: TValidator = None) -> Optional[int]:

    if validator is None:
        validator = default_positive_int_is_valid

    try:
        val: Optional[str] = get_env(key, validator=validator)
    except StrValidationEnvironmentError as sve:
        raise PositiveIntEnvironmentError(sve.key, sve.value)

    if validator is None and val is None:
        return None

    if validator and not validator(val):
        raise PositiveIntEnvironmentError(key, val)
    assert val is not None
    return int(val)


def get_env_as_bool(key, validator: TValidator = None) -> Optional[bool]:

    if validator is None:
        validator = default_bool_is_valid

    try:
        val: Optional[str] = get_env(key, validator=validator)
    except StrValidationEnvironmentError as sve:
        raise BooleanEnvironmentError(sve.key, sve.value)
    bool_val = None

    if validator is None and val is None:
        return None

    if validator and not validator(val):
        raise BooleanEnvironmentError(key, val)
    bool_val = any(True for v in ACCEPTED_TRUE_VALUES if str(val).lower() == str(v).lower())

    return bool_val
