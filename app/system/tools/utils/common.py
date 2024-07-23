from typing import Any, Union, Callable, Dict, Tuple, TypeVar, get_type_hints
from decimal import Decimal
from inspect import signature, _empty

import datetime

T = TypeVar("T")


DEFAULT_JSON_CASTERS = {
    str(object):            repr,
    str(int):               int,
    str(float):             float,
    str(Decimal):           float,
    str(datetime.date):     datetime.date.isoformat,
    str(datetime.datetime): datetime.datetime.isoformat,
}


def castVariable(
    var:     Any,
    caster:  Callable[[Any], T],
    default: Union[T, None] = None
) -> Union[T, None]:
    """Tries to cast a variable with the given caster, if an error is thrown will return `default`"""

    res = default
    try:
        res = caster(var)
    finally:
        return res
    #endtry
#enddef


def autoCastVariable(
    var:         Any,
    caster_dict: Dict[str, Union[Callable[[Any], T], Tuple[Callable[[Any], T], T]]] = DEFAULT_JSON_CASTERS,
    default:     Union[T, None] = None
) -> Union[T, None]:
    """Tries to cast a variable with a caster selected from the given dict trying each entry in `var.__class__.__mro__` from the first to the last.

    If none of the classes in the mro is contained in th `caster_dict` it will return `default`.
    If `var.__class__.__mro__` is not a tuple or a list it will return `default`.

    Example:
    ```
        caster_dict = {
            str(object): repr,
            str(int): str,
            str(float): int
        }
        foo = autoCastVariable(12.5, caster_dict = caster_dict)
        # foo will be casted to int, as its mro is (float, object)

        bar = autoCastVariable(12, caster_dict = caster_dict)
        # bar will be casted to str, as its mro is (int, object)

        # anything that doesn't have float or int in its mro list will be casted with repr, as all objects derive from object
    ```
    """

    res = default
    mro = getattr(
        getattr(var, "__class__", object),
        "__mro__",
        []
    )

    if isinstance(mro, (list, tuple)):
        # mro is a tuple with the first attribute being the class of the object itself, and the last being "object"
        for object_type in mro:
            # encapsulate everything in a try to catch all possible breaking points
            # string casting and basically every other method can be breaking
            try:
                if str(object_type) in caster_dict.keys():
                    caster = caster_dict[str(object_type)]

                    if isinstance(caster, tuple):
                        res = castVariable(var, caster=caster[0], default=caster[1])
                        break
                    elif callable(caster):
                        res = castVariable(var, caster=caster)
                        break
                    #endif
                #endif
            except:
                pass # res remains default
            #entry
        #endfor
    #endif

    return res
#enddef


def objectFromDict(data: dict) -> object:
    """Generates an object starting from a python dict object, recursively translating each dict into an object with its keys as its attributes.

    Example:
    ```
        my_dict = {"bar": 1, "baz": 2}
        foo = objectFromDict(my_dict)
        # now it is possible to access "bar" and "baz" directly using foo:
        print(foo.bar, foo.baz)
    ```
    """

    class obj(object):
        def __init__(self, d: dict):
            for key, value in d.items():
                if isinstance(value, (list, tuple)):
                    setattr(self, key, [obj(x) if isinstance(x, dict) else x for x in value])
                else:
                    setattr(self, key, obj(value) if isinstance(value, dict) else value)
                #endif
            #endfor
        #enddef
    #endclass

    return obj(data)
#enddef


def get_object_subattribute(obj: Any, key: str, default: Any = None) -> Any:
    """Get a nested value from any object using a string key.

    For example: `x = get_object_subattribute(obj = foo, key = "bar.baz")`
    is the same as doing: `x = foo.bar.baz`.
    """

    if not isinstance(key, str):
        raise ValueError(f"invalid key type: expected string but got {key.__class__.__name__}")
    #endif

    key_list = key.split(".")
    if len(key_list) > 1:
        # skip the last key as it will be retrieved after this if
        for temp_key in key_list[:-1]:
            obj = getattr(obj, temp_key, object())
        #endfor
    #endif

    return getattr(obj, key_list[-1], default)
#enddef


def get_dict_subattribute(obj: dict, key: str, default: Any = None) -> Any:
    """Get a nested value from any dict using a string key.

    For example: `x = get_dict_subattribute(obj = foo, key = "bar.baz")`
    is the same as doing: `x = foo["bar"]["baz"]`.
    """

    if not isinstance(key, str):
        raise ValueError(f"invalid key type: expected string but got {key.__class__.__name__}")
    #endif

    key_list = key.split(".")
    if len(key_list) > 1:
        # skip the last key as it will be retrieved after this if
        for temp_key in key_list[:-1]:
            obj = obj.get(temp_key, {})
        #endfor
    #endif

    return obj.get(key_list[-1], default)
#enddef


def get_first_not_none(*args) -> Any:
    """From the list of arguments returns the first not None, if all are None it will return None"""

    try:
        return next(item for item in args if item is not None)
    except StopIteration:
        return None
    #endtry
#enddef


def variable_type_check(variable: Any, required_type: Any, skip_on_error: bool = False) -> bool:
    """check variable type based on type passed.

    Subscripted types (present in typing module) if passed directly to `isinstance` will throw an error,
    all types present in typing module have an `__origin__` variable in which is stored a class that can be used in checks.
    That class is more generic, so for example `variable_type_check({"hello": 12}, typing.Dict[str, str])` will still match.

    Depending on what is passed as type can raise an error, setting the `skip_parameter_on_error` flag
    sets the action to take (skip and assume correct or crash)
    """

    if required_type == Any: return True

    # IMPORTANT NOTE:
    # in isinstance check can't be used anything from typing module, except for Union, there is a need to automate the generic class retrveving
    # as in all typing class there is a __origin__ variable in which is stored a class that can be used in checks.

    # NOTE: the "isinstance" call must remain inside the try/except block
    try:
        if hasattr(required_type, "__origin__") and required_type.__origin__ == Union:
            # __args__ contains the arguments of the Union, so use those in isinstance call
            valid = isinstance(variable, required_type.__args__)
        elif hasattr(required_type, "__origin__"):
            valid = isinstance(variable, required_type.__origin__)
        else:
            valid = isinstance(variable, required_type)
        #endif
    except:
        if not skip_on_error: raise # pass trhough error
    #endtry

    return valid
#enddef


def type_check(
    _function: Callable,
    check_positional: bool = True,
    check_keyword:    bool = True,
    check_return:     bool = False,
    skip_parameter_on_error: bool = False,
) -> Callable:
    """Checks parameters and return type at runtime based on the function signature

    Subscripted types (present in typing module) if passed directly to `isinstance` will throw an error,
    all types present in typing module have an `__origin__` variable in which is stored a class that can be used in checks.
    That class is more generic, so for example `variable_type_check({"hello": 12}, typing.Dict[str, str])` will still match.

    `check_positional`: sets wether to check positional parameters
    `check_keyword`:    sets wether to check keyword parameters
    `check_return`:     sets wether to check return parameters

    Type checking is done by `common.variable_type_check` and depending on what is passed as type it can raise an error,
    setting the `skip_parameter_on_error` flag sets the action to take (skip and assume correct or crash)
    """

    def _type_check(*args, **kwargs) -> Any:
        function_signature  = signature(_function)
        function_type_hints = get_type_hints(_function)

        # TODO: FIX TYPING CHECK FOR ALL CORNER CASES

        # NOTE:
        #   - inspect.signature returns a general signature object, if there is a late-evaluation type hint,
        #       it won't intepret it, but will separate the arguments into positiona, keyword, etc.
        #       [https://peps.python.org/pep-0649/]
        #   - typing.get_type_hints won't separate arguments but will intepret late-evaluation type hints,
        #       it is needed as the type will be passed to isinstance call, that mandatorily needs a class.
        #       [https://docs.python.org/3.7/library/typing.html#typing.get_type_hints]


        # FROM python.org DOCUMENTATION [https://docs.python.org/3.7/library/inspect.html#inspect.Parameter.kind]:
        #   POSITIONAL_ONLY
        #       Value must be supplied as a positional argument.
        #       Python has no explicit syntax for defining positional-only parameters, but many built-in and
        #        extension module functions (especially those that accept only one or two parameters) accept them.
        #
        #   POSITIONAL_OR_KEYWORD
        #       Value may be supplied as either a keyword or positional argument (this is
        #        the standard binding behaviour for functions implemented in Python.)
        #
        #   VAR_POSITIONAL
        #       A tuple of positional arguments that aren’t bound to any other parameter.
        #       This corresponds to a *args parameter in a Python function definition.
        #
        #   KEYWORD_ONLY
        #       Value must be supplied as a keyword argument. Keyword only parameters are those
        #        which appear after a * or *args entry in a Python function definition.
        #
        #   VAR_KEYWORD
        #       A dict of keyword arguments that aren’t bound to any other parameter.
        #       This corresponds to a **kwargs parameter in a Python function definition.

        # in this function will be checked only POSITIONAL and KEYWORD arguments, as VAR_POSITIONAL and VAR_keyword are general


        if check_positional:
            for index, parameter_value in enumerate(args):
                parameter_name = list(function_signature.parameters.keys())[index] # get parameter name
                parameter_type = function_type_hints.get(parameter_name, _empty)   # get parameter annotation

                # if the parameter has no type hint (_empty) then skip and assume it's correct
                if (parameter_type != _empty and not variable_type_check(parameter_value, parameter_type, skip_parameter_on_error)):
                    raise TypeError(f"Invalid positioanl argument type for '{parameter_name}': expected {parameter_type}; got {type(parameter_value)}")
                #endif
            #endfor
        #endif

        if check_keyword:
            for index, (parameter_name, parameter_value) in enumerate(kwargs.items()):
                if parameter_name not in function_signature.parameters.keys(): continue # skip

                parameter_type = function_type_hints.get(parameter_name, _empty)

                # if the parameter has no type hint (_empty) then skip and assume it's correct
                if (parameter_type != _empty and not variable_type_check(parameter_value, parameter_type, skip_parameter_on_error)):
                    raise TypeError(f"Invalid keword argument type for '{parameter_name}': expected {parameter_type}; got {type(parameter_value)}")
                #endif
            #endfor
        #endif

        return_value = _function(*args, **kwargs)

        # check return
        if check_return:
            return_type = function_signature.return_annotation

            if not variable_type_check(return_value, return_type, skip_parameter_on_error):
                raise TypeError(f"Invalid return type for function '{_function.__name__}': expected {return_type}; got {type(return_value)}")
            #endif
        #endif

        return return_value
    #enddef

    return _type_check
#enddef
