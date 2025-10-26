import os
from typing import Optional
import pytest
from dotenv import load_dotenv
import random
import string

load_dotenv("/workspace/.nre_pipeline.env")
from nre_pipeline.common.env_vars.env_getter import (
    default_str_is_valid,
    default_bool_is_valid,
    default_positive_int_is_valid,
    get_env,
    get_env_as_int,
    get_env_as_bool,
    ACCEPTED_TRUE_VALUES,
    ACCEPTED_FALSE_VALUES,
    ALL_ACCEPTED_BOOL_VALUES,
    ValidValidationType,
)  # type: ignore


from nre_pipeline.common.env_vars.exceptions import (
    KeyMissingEnvironmentError,
    ValueMissingEnvironmentError,
    MethodValidationEnvirontmentError,
    StrValidationEnvironmentError,
    PositiveIntEnvironmentError,
    BooleanEnvironmentError,
)

###############################################################################
# str Value generator
###############################################################################


@pytest.fixture()
def random_str_value():
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=random.randint(10, 20))
    )


@pytest.fixture()
def valid_str_value(random_str_value):
    return random_str_value


@pytest.fixture()
def invalid_str_value():
    return None


###############################################################################
# bool Value generator
###############################################################################


def _bool_variant_generator(val):
    if isinstance(val, str):
        if val.isdigit():
            # if this is a digit, yield a number and string form
            yield from (val, int(val))
        else:
            # not a number, yield different case variants
            yield from (val.upper(), val.lower(), val.title())
    else:
        # if not a string, just yield the value
        yield val


@pytest.fixture(params=ACCEPTED_TRUE_VALUES)
def TRUE_value(request):
    yield from _bool_variant_generator(request.param)


@pytest.fixture(params=ACCEPTED_FALSE_VALUES)
def FALSE_value(request):
    yield from _bool_variant_generator(request.param)


@pytest.fixture(params=["-1", "2", "never", "always"])
def invalid_bool_values(request):
    yield from ((x, None) for x in _bool_variant_generator(request.param))


@pytest.fixture()
def valid_bool_values(TRUE_value, FALSE_value):
    """Valid values within environment variables for bools

    Args:
        request (_type_): _description_

    Yields:
        Tuple[Any, Any]: parameter, represented boolean
    """
    yield TRUE_value, True
    yield FALSE_value, False


###############################################################################
# Positive Integer Value Fixtures
###############################################################################


@pytest.fixture(params=[1, 10, 100, 1000, 10000])
def valid_pos_int(request):
    yield request.param


@pytest.fixture(params=[-1, 0, "a", "-"])
def invalid_pos_int(request):
    yield request.param


###############################################################################
# Validation Fixtures
###############################################################################


@pytest.fixture(params=["exists", default_str_is_valid, None])
def str_validation_methods(request):
    yield request.param


@pytest.fixture(params=["exists", default_positive_int_is_valid, None])
def int_validation_methods(request):
    yield request.param


@pytest.fixture(params=["exists", default_bool_is_valid, None])
def bool_validation_methods(request):
    yield request.param


###############################################################################
# Testing Fixtures
###############################################################################


def validate_method__key_missing(_method_to_eval, _key):
    try:
        assert _key not in os.environ
        _method_to_eval(_key)
    except KeyMissingEnvironmentError as ex:
        assert str(ex) == f"Environment variable '{_key}' does not exist."
    else:
        assert False, f"Expected KeyMissingEnvironmentError for key '{_key}'"


def generate_values_to_eval(_values_for_eval):
    valid_values = [(v, True) for v in _values_for_eval["valid_values"]]
    invalid_values = [(v, False) for v in _values_for_eval["invalid_values"]]
    return valid_values + invalid_values


###############################################################################
# Environment Variable Key Fixture
###############################################################################


@pytest.fixture()
def key_name_builder():
    def build_key_name_from_type(type_name: str) -> str:
        key = f"TEST_ENV_{type_name.upper()}"
        assert (
            key not in os.environ
        ), f"Generated key already exists in environment variables ({key})"
        return key

    return build_key_name_from_type


###############################################################################
# Test default validators
###############################################################################


def test_default_str_is_valid(valid_str_value, invalid_str_value):
    assert default_str_is_valid(valid_str_value)
    assert not default_str_is_valid(invalid_str_value)


def test_default_bool_is_valid(valid_bool_values, invalid_bool_values):
    valid_test = valid_bool_values
    if isinstance(valid_test, tuple) and len(valid_test) == 2 and isinstance(valid_test[1], bool):
        valid_test = valid_test[0]
    assert default_bool_is_valid(valid_test)

    valid_test = invalid_bool_values
    if isinstance(valid_test, tuple) and len(valid_test) == 2 and valid_test[1] is None:
        valid_test = valid_test[0]
    assert not default_bool_is_valid(valid_test)
        


def test_default_positive_int_is_valid(valid_pos_int, invalid_pos_int):
    assert default_positive_int_is_valid(valid_pos_int)
    assert not default_positive_int_is_valid(invalid_pos_int)
        


###############################################################################
# Testing get_env
###############################################################################


@pytest.fixture(
    params={
        "str": {
            "test_method": get_env,
            "test_cases": {
                "valid_values": valid_str_value,
                "invalid_values": invalid_str_value,
            },
            "validation_approach": str_validation_methods,
            "failed_validation_with_method_exception": StrValidationEnvironmentError,
        },
        "positive_int": {
            "test_method": get_env_as_int,
            "test_cases": {
                "valid_values": valid_pos_int,
                "invalid_values": invalid_pos_int,
            },
            "validation_approach": int_validation_methods,
            "failed_validation_with_method_exception": PositiveIntEnvironmentError,
        },
        "boolean": {
            "test_method": get_env_as_bool,
            "test_cases": {
                "valid_values": valid_bool_values,
                "invalid_values": invalid_bool_values,
            },
            "validation_approach": bool_validation_methods,
            "failed_validation_with_method_exception": BooleanEnvironmentError,
        },
    }
)
def test_permutations(request, key_name_builder):

    for test_case, test_params in request.param.items():

        env_key = key_name_builder(test_case)
        method_to_eval = test_params["test_method"]  # e.g., get_env
        validation_methods = test_params[
            "validation_approach"
        ]  # e.g., exists, default_str_is_valid, None

        def validate_method__key_exists(
            _validation_method: ValidValidationType, _expected, _expect_to_succeed
        ):
            try:
                os.environ[env_key] = _expected
                _actual = method_to_eval(env_key, required=_validation_method)
                assert _actual == _expected and _expect_to_succeed is True
            except ValueMissingEnvironmentError as _vee:
                assert _validation_method == "exists" and _expect_to_succeed is False
                assert (
                    str(_vee)
                    == f"Value for environment variable '{env_key}' does not exist."
                )
            except MethodValidationEnvirontmentError as _mee:
                assert callable(_validation_method) and _expect_to_succeed is False
                assert isinstance(
                    _mee, test_params["failed_validation_with_method_exception"]
                )  # noqa
                assert str(_mee).startswith(
                    f"Method validation for key='{env_key}' and value='{_actual}' failed: "
                )
            finally:
                del os.environ[env_key]
                validate_method__key_missing(method_to_eval, env_key)

        for val_to_eval, expect_to_succeed in generate_values_to_eval(
            test_params["test_cases"]
        ):
            for validation_method in validation_methods:
                validate_method__key_exists(
                    validation_method, val_to_eval, expect_to_succeed
                )
