import os
import pytest
from dotenv import load_dotenv
import random
import string

load_dotenv("/workspace/.nre_pipeline.env")
from nre_pipeline.common.env_vars.env_getter import (  # type: ignore
    default_str_is_valid,
    default_bool_is_valid,
    _is_bool_equivalent,
    default_positive_int_is_valid,
    get_env,
    get_env_as_positive_integer,
    get_env_as_bool,
    ACCEPTED_TRUE_VALUES,
    ACCEPTED_FALSE_VALUES,
    _convert_undefined_to_none,
)  # type: ignore


from nre_pipeline.common.env_vars.exceptions import (  # type: ignore
    KeyMissingEnvironmentError,
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
    vals_to_yield = []
    if isinstance(val, str):
        if val.isdigit():
            # if this is a digit, yield a number and string form
            vals_to_yield.append(val)
            vals_to_yield.append(int(val))
        else:
            # not a number, yield different case variants
            vals_to_yield.append(val.upper())
            vals_to_yield.append(val.lower())
            vals_to_yield.append(val.title())
    else:
        # if not a string, just yield the value
        vals_to_yield.append(val)

    return vals_to_yield


@pytest.fixture(params=ACCEPTED_TRUE_VALUES)
def TRUE_value(request):
    return _bool_variant_generator(request.param)


@pytest.fixture(params=ACCEPTED_FALSE_VALUES)
def FALSE_value(request):
    return _bool_variant_generator(request.param)


@pytest.fixture(params=["-1", "2", "never", "always"])
def invalid_bool_values(request):
    for x in _bool_variant_generator(request.param):
        yield x


@pytest.fixture(params=[(TRUE_value, True), (FALSE_value, False)])
def valid_bool_values(request):
    """Valid values within environment variables for bools

    Args:
        request (_type_): _description_

    Yields:
        Tuple[Any, Any]: parameter, represented boolean
    """

    yield request.param


def _convert_bool_tuple_to_test_bool_val(x):
    if isinstance(x, tuple) and len(x) > 1 and isinstance(x[1], bool):
        return x[0]
    return x


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


@pytest.fixture(params=[default_str_is_valid, None])
def str_validation_method(request):
    yield request.param


@pytest.fixture(params=[default_positive_int_is_valid, None])
def int_validation_method(request):
    yield request.param


@pytest.fixture(params=[default_bool_is_valid, None])
def bool_validation_method(request):
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


def validate_method__key_exists(
    _env_key,
    _method_to_eval,
    _validation_method,
    _expected,
    _expect_to_succeed,
    _failed_validation_with_method_exception,
):
    try:
        if _expected is not None:
            os.environ[_env_key] = str(_expected)
        else:
            os.environ[_env_key] = ""
        _actual = "<_method_to_eval not yet called>"
        _actual = _method_to_eval(_env_key, validator=_validation_method)
        _expected_test_val = _expected
        if isinstance(_expected, tuple) and len(_expected) > 0:
            _expected_test_val = _expected[0]
        _actual_test_val = _actual
        if isinstance(_actual, tuple) and len(_actual) > 0:
            _actual_test_val = _actual[0]

        # if the expected and actual values are actually a bool equivalent, compare as bools
        if _is_bool_equivalent(_expected_test_val) and _is_bool_equivalent(
            _actual_test_val
        ):
            _expected_as_bool = default_bool_is_valid(_expected_test_val)
            _actual_as_bool = default_bool_is_valid(_actual_test_val)
            is_equal = _actual_as_bool == _expected_as_bool
            if _expect_to_succeed:
                assert (
                    is_equal
                ), f"Expected to succeed, but actual ({_actual_as_bool}) != expected ({_expected_as_bool})"
            else:
                assert (
                    not is_equal
                ), f"Expected to fail, but actual ({_actual_as_bool}) == expected ({_expected_as_bool})"
        else:
            is_equal = _actual_test_val == _expected_test_val
            if _expect_to_succeed:
                assert (
                    is_equal
                ), f"Expected to succeed, but actual ({_actual_test_val}) != expected ({_expected_test_val})"
            else:
                assert (
                    not is_equal
                ), f"Expected to fail, but actual ({_actual_test_val}) == expected ({_expected_test_val})"

    except MethodValidationEnvirontmentError as _mee:
        assert (
            _expect_to_succeed is False
            and isinstance(_mee, _failed_validation_with_method_exception)
            and str(_mee).startswith(
                f"Method validation for key='{_env_key}' and value="
            )
        )
    finally:
        os.environ.pop(_env_key, None)
        validate_method__key_missing(_method_to_eval, _env_key)


def permutation_test_handler(key_name_builder, test_cases):
    for test_params in test_cases:
        validation_approach = test_params["validation_approach"]
        valid_test_value = test_params["test_cases"]["valid_values"]  # type: ignore
        invalid_test_value = test_params["test_cases"]["invalid_values"]  # type: ignore

        env_key = key_name_builder(test_params["type"])
        method_to_eval = test_params["test_method"]
        failed_validation_with_method_exception = test_params[
            "failed_validation_with_method_exception"
        ]

        # check to drop to actual bool value if tuple

        validate_method__key_exists(
            env_key,
            method_to_eval,
            validation_approach,
            _convert_bool_tuple_to_test_bool_val(valid_test_value),
            True,
            failed_validation_with_method_exception,
        )

        validate_method__key_exists(
            env_key,
            method_to_eval,
            validation_approach,
            _convert_bool_tuple_to_test_bool_val(invalid_test_value),
            False,
            failed_validation_with_method_exception,
        )


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
    valid_string_is_valid = default_str_is_valid(valid_str_value)
    invalid_string_is_invalid = not default_str_is_valid(invalid_str_value)
    assert valid_string_is_valid and invalid_string_is_invalid


def test_default_bool_is_valid(valid_bool_values, invalid_bool_values):
    for valid_test in valid_bool_values:
        if (
            isinstance(valid_test, tuple)
            and len(valid_test) == 2
            and isinstance(valid_test[1], bool)
        ):
            valid_test = valid_test[0]
        assert default_bool_is_valid(valid_test)

    for invalid_valid_test in invalid_bool_values:
        if (
            isinstance(invalid_valid_test, tuple)
            and len(invalid_valid_test) == 2
            and invalid_valid_test[1] is None
        ):
            invalid_valid_test = invalid_valid_test[0]
        assert not default_bool_is_valid(invalid_valid_test)


def test_default_positive_int_is_valid(valid_pos_int, invalid_pos_int):
    assert default_positive_int_is_valid(
        valid_pos_int
    ) and not default_positive_int_is_valid(invalid_pos_int)


###############################################################################
# Testing get_env
###############################################################################


def test_str_permutations(
    key_name_builder,
    valid_pos_int,
    invalid_pos_int,
    int_validation_method,
):
    test_cases = [
        {
            "type": "str",
            "test_method": get_env,
            "test_cases": {
                "valid_values": valid_str_value,
                "invalid_values": invalid_str_value,
            },
            "validation_approach": str_validation_method,
            "failed_validation_with_method_exception": StrValidationEnvironmentError,
        }
    ]

    permutation_test_handler(key_name_builder, test_cases)


def test_bool_permutations(
    key_name_builder,
    valid_pos_int,
    invalid_pos_int,
    int_validation_method,
):

    test_cases = [
        {
            "type": "boolean",
            "test_method": get_env_as_bool,
            "test_cases": {
                "valid_values": valid_bool_values,
                "invalid_values": invalid_bool_values,
            },
            "validation_approach": bool_validation_method,
            "failed_validation_with_method_exception": BooleanEnvironmentError,
        }
    ]

    permutation_test_handler(key_name_builder, test_cases)


def test_positive_int_permutations(
    key_name_builder,
    valid_pos_int,
    invalid_pos_int,
    int_validation_method,
):
    test_cases = [
        {
            "type": "positive_int",
            "test_method": get_env_as_positive_integer,
            "test_cases": {
                "valid_values": valid_pos_int,
                "invalid_values": invalid_pos_int,
            },
            "validation_approach": int_validation_method,
            "failed_validation_with_method_exception": PositiveIntEnvironmentError,
        }
    ]

    permutation_test_handler(key_name_builder, test_cases)
