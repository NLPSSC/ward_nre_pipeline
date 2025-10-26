# Task: Define get(...) method with overrides

## Task Definition

Create a series of methods with the name `get` to retrieve the value for a specified environment variable.

- The method name is `get`
- `get` takes the following parameters:
  - A required unnamed parameter, `key: str`, used to call `os.getenv(key, None)`
  - An optional named parameter, `required`, which can be one of the following:
    - `Literal["exists"]`
    - `Callable[[Optional[str]], bool]`
    - None
- If `required` is "exists", the method
  - raises an EnvironmentError if the environment variable does not exist and
  - returns a `str` otherwise.
- If `required` is a callable, the method
  - raises an EnvironmentError if the callable returns False and 
  - returns a `str` otherwise.
- If `required` is None, the method returns an `Optional[str]`

## Instructions

- Clear the file `/workspace/src/nre_pipeline/_experimental/get_test.py` before writing.
- Create a series of methods with the name `get` in the file `/workspace/src/nre_pipeline/_experimental/get_test.py` that defines the primary method with overrides for the given use cases.
- All methods must be named `get` with varying parameters to handle the different `required` cases.
- The return type should be consistent with the `required` parameter's behavior.
- Do not consider any existing code already present in `/workspace/src/nre_pipeline/_experimental/get_test.py`; overwrite existing code.