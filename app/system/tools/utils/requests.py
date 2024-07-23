from typing import Any, Union, Callable, Dict, List, Tuple, TypeVar
from flask import request
from . import common

import json

T = TypeVar("T")

class DefaultToNone:
    """Makes sure that if the value doesn't exist or is invalid it defaults to None, otherwhise will cast to the given type with the given caster method"""

    def __init__(self, caster):
        self.caster = caster
    #enddef
#endclass


def get_request_argument(
    argument_name: str,
    caster: Callable[[Any], T],

    arg_container: Any = {},
    default: Union[T, None] = None,
    caster_positional_arguments: List[Any] = [],
    caster_keyword_arguments: Dict[str, Any] = {},
) -> Union[T, None]:
    """Get an argument from a request object argument container passed in `arg_container`.

    Will cast its value using the given `caster` method and fall back to the given `default`.

    Example:
    ```
        import json
        container = request.args.to_dict() # even if to_dict() is called, values would be still strings
        received_args = get_request_argument("plant_types", json.loads, arg_container = container, default = {"carrot": "vegetable"})
        # received_args will be whatever value there was on the url parameter `plant_types`, if any, otherwhise will fall back to `default`
    ```
    """

    var = arg_container.get(argument_name, default)
    caster_lambda = lambda variable: caster(variable, *caster_positional_arguments, **caster_keyword_arguments)
    return common.castVariable(var, caster=caster_lambda, default=default) if var else default
#enddef


def get_request_args(
    args,
    arg_container: str = "url-args", # convert to Literal["url-args", "json-body", "form-data"] from python 3.8 onwards
    default = None
) -> Union[Any, bool, Tuple[Any, ...], Dict[str, Any], None]:
    """Get an argument (or list/dict of arguments) from a taken from a request object argument container selected in `arg_container`.

    Will cast its value using the given `default` type and fall back (if necessary) to the given `default`.

    Example 1:
    ```
        arguments = ["id", "name", "surname"]
        received_args = get_request_args(arguments, arg_container = "form-data", default = None)
        # received_args will be a list
    ```

    Example 2:
    ```
        # key -> Argument name; value -> Argument default
        arguments = {"id": 0, "name": "John", "surname": DefaultToNone(str)}
        received_args = get_request_args(arguments, arg_container = "json-body", default = None)
        # received_args will be a dict
    ```

    Example 3:
    ```
        received_arg = get_request_args("id", arg_container = "url-args", default = -1)
        # received_arg will be a single value
    ```
    """

    arg_container_list = ["url-args", "json-body", "form-data"]
    if arg_container not in arg_container_list:
        raise ValueError(f"Invalid 'arg_container' argument ('{arg_container}'); must be one of {arg_container_list}")
    #endif
    result = None

    if isinstance(args, str):
        if arg_container == "url-args":
            request_args = request.args.to_dict()
        elif arg_container == "json-body":
            request_args = request.json
        elif arg_container == "form-data":
            request_args = request.form.to_dict()
        else:
            request_args = {}
        #endif

        result = request_args.get(args, default)

        if isinstance(default, DefaultToNone):
            default_type = default.caster
            default = None
        else:
            default_type = type(default)
        #endif

        if default_type == bool:
            if result in ["true", "True"]:
                result = True
            elif result in ["false", "False"]:
                result = False
            else:
                result = default
            #endif

        elif default_type in [int, float]:
            try:
                result = default_type(result) # dynamically cast the value by using the type of the default
            except ValueError:
                result = default
            #endtry

        elif default_type in [list, tuple, dict] and arg_container == "url-args":
            try:
                result = json.loads(result)

                if default_type == tuple:
                    result = tuple(result)
                #endif
            except:
                result = default
            #endtry

        else:
            result = result if (result != "" and result != None) else default
        #endif

    elif isinstance(args, list):
        result = []
        for arg in args:
            result.append(get_request_args(arg, arg_container = arg_container))
        #endfor

    elif isinstance(args, dict):
        result = {}
        for arg, default in args.items():
            result[arg] = get_request_args(arg, arg_container = arg_container, default = default)
        #endfor
    #endif

    return result
#enddef

