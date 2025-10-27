import pytest
from typing import List, cast
import pytest


@pytest.fixture(params=[3, 2, 1])
def countdown(request: pytest.FixtureRequest) -> int:
    return cast(int, request.param)


@pytest.fixture()
def logr():
    def _local_logr(msg: str, *args):
        args_list: List[str] = [str(a) for a in list(args)]
        print(msg.format(*args_list))

    return _local_logr
