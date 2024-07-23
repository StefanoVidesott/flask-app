from typing import Any, Union, Callable, Dict, Tuple, TypeVar
from . import common

import json

T = TypeVar("T")

def objectFromJSONString(data: str) -> object:
    """Generates an object starting from a JSON string, recursively translating each dict into an object with its keys as its attributes.

    Example:
    ```
        json_string = "{"bar": [1,2], "baz": "spam"}"
        foo = objectFromJSONString(json_string)
        # now it is possible to access "bar" and "baz" directly using foo:
        print(foo.bar, foo.baz)
    ```
    """

    class obj(object):
        def __init__(self, dict_: dict):
            self.__dict__.update(dict_)
        #enddef

        def __repr__(self) -> str:
            return f"<{' '.join(f'{key}={repr(val)}' for key, val in self.__dict__.items() if key[0] != '_')}>"
        #enddef
    #endclass

    return json.loads(data, object_hook = obj)
#enddef


def JSONStringFromDict(
    data: dict,
    caster_dict: Dict[str, Union[Callable[[Any], T], Tuple[Callable[[Any], T], T]]] = common.DEFAULT_JSON_CASTERS
) -> str:
    """Generates a JSON string starting from a valid python object. Can auto cast some variables given in the `caster_dict` parameter

    Example:
    ```
        my_dict = {"bar": [1,2], "baz": "spam"}
        foo = JSONStringFromDict(my_dict)
        # now foo will be a string representing my_dict: "{"bar": [1,2], "baz": "spam"}"
    ```
    """

    return json.dumps(data, default=(lambda variable: common.autoCastVariable(variable, caster_dict = caster_dict)))
#enddef


def JSONifyDict(
    data: dict,
    caster_dict: Dict[str, Union[Callable[[Any], T], Tuple[Callable[[Any], T], T]]] = common.DEFAULT_JSON_CASTERS
) -> object:
    """Sanitizes an object preparing it fo being sent as a JSON string, making it usable in python as an object

    Example:
    ```
        my_dict = {"bar": [1,2], "baz": "hello!", "foo": MyCustomObject}
        spam = JSONifyDict(my_dict) # assuming the usage of default caster_dict
        # now spam will be a dict that can be represented as json: {"bar": [1,2], "baz": "hello!", "foo": "<MyCustomObject object at 0x7f58f61db828>"}
    ```
    """

    return json.loads(
        JSONStringFromDict(data, caster_dict=caster_dict)
    )
#enddef

