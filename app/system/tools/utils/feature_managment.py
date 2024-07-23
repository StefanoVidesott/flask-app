import inspect
import sys
from typing import Any, Callable, Union

from flask_restx import Resource

from app import app, db
from app.system.models.BaseModel import BaseModel

# GLOBALS
# 0 = no log; 1 = normal calls log; 2 = calls with a leading _ log; 3 = all calls log
VERBOSITY_LEVEL    = app.config.get("CORE_FUNCTIONALITY_MANAGER_LOG_LEVEL", 0)
# 0 = attribute name and caller name; 1 = file, module and line number; 2 = code context
DEBUG_DETAIL_LEVEL = app.config.get("CORE_FUNCTIONALITY_MANAGER_DEBUG_CALL_DETAIL_LEVEL", 0)


# custom error
class NotConfiguredError(Exception): pass


class ManagedBaseModel:

    class ManagedFunctionalityType(type):
        def __getattribute__(self, name: str) -> None:
            if VERBOSITY_LEVEL > 0:

                # verbosity check
                if   VERBOSITY_LEVEL == 1 and name.startswith("_"):  return
                elif VERBOSITY_LEVEL == 2 and name.startswith("__"): return

                log_message = ""
                cls = super().__getattribute__("__class__")

                caller_frame      = sys._getframe(1)
                caller_frame_info = inspect.getframeinfo(caller_frame, context=5) # get 5 lines of context (2 above and 2 below)

                module = inspect.getmodule(caller_frame)
                path   = inspect.getfile(caller_frame)

                code_context             = caller_frame_info.code_context
                code_context_index       = caller_frame_info.index
                code_context_line_number = caller_frame_info.lineno
                caller_name              = caller_frame_info.function

                if DEBUG_DETAIL_LEVEL >= 0:
                    log_message  = f"[FEATURE MANAGMENT] \"{cls.__name__}.{name}\" invoked by \"{caller_name}\""

                    if DEBUG_DETAIL_LEVEL >= 1:
                        log_message += f"\n| FILE \"{path}\", module \"{module}\", line {code_context_line_number}"

                        if DEBUG_DETAIL_LEVEL >= 2:
                            log_message += "\n"

                            if code_context and code_context_index:
                                context_line_number_start = code_context_line_number - code_context_index
                                max_line_number_length    = len(str(code_context_line_number + context_line_number_start))

                                for index, line in enumerate(code_context):
                                    log_line_number = str(context_line_number_start + index).rjust(max_line_number_length)

                                    if index == code_context_index:
                                        log_message += f"|>{log_line_number}<|{line}"
                                    else:
                                        log_message += f"| {log_line_number} |{line}"
                                    #endif
                                #endfor
                            else:
                                log_message += "UNABLE TO RETRIEVE code_context"
                            #endif
                        #endif
                    #endif
                #endif

                app.logger.debug(log_message)
            #endif

            return None
        #enddef


        def __setattr__(self, name: str, value: Any) -> None:
            return object.__getattribute__(self, "__getattribute__")(name)
        #enddef
    #endclass

    def __new__(
        cls,
        flag: Union[bool, None]=None,
        on_access: Callable[[str], None]=lambda name:None
    ):
        if flag:
            return BaseModel
        else:
            class ManagedFunctionalityDerived(metaclass=ManagedBaseModel.ManagedFunctionalityType):
                def __getattribute__(_self, name):
                    object.__getattribute__(ManagedBaseModel.ManagedFunctionalityType, "__getattribute__")(_self, name)
                    on_access(name)
                #enddef
            #endclass

            return ManagedFunctionalityDerived
        #endif
    #enddef
#endclass


class ManagedResource:

    class ManagedResourceBase:
        def get(self, *args, **kwargs):
            raise NotConfiguredError("Api is not configured")
        #enddef

        def head(self, *args, **kwargs):
            raise NotConfiguredError("Api is not configured")
        #enddef

        def post(self, *args, **kwargs):
            raise NotConfiguredError("Api is not configured")
        #enddef

        def put(self, *args, **kwargs):
            raise NotConfiguredError("Api is not configured")
        #enddef

        def delete(self, *args, **kwargs):
            raise NotConfiguredError("Api is not configured")
        #enddef

        def connect(self, *args, **kwargs):
            raise NotConfiguredError("Api is not configured")
        #enddef

        def options(self, *args, **kwargs):
            raise NotConfiguredError("Api is not configured")
        #enddef

        def trace(self, *args, **kwargs):
            raise NotConfiguredError("Api is not configured")
        #enddef

        def patch(self, *args, **kwargs):
            raise NotConfiguredError("Api is not configured")
        #enddef
    #endclass


    def __new__(
        cls,
        flag: Union[bool, None]=None,
        on_access: Callable[[str], None]=lambda name:None
    ):
        if flag:
            return Resource
        else:
            return cls.ManagedResourceBase
        #endif
    #enddef
#endclass


def disable_if(_function, condition: bool = False):
    def func(*args, **kwargs): raise NotConfiguredError("method is not configured")

    if condition: return func
    else:         return _function
#enddef
