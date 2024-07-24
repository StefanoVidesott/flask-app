from typing import Any, Dict, List

from system.utils.web_elements import htmllib
from system.utils.web_elements.requirements import ScriptRequirement, StyleRequirement

CSS_CLASS_PREFIX = "openbridge"


class HTMLData:
    """Holds data of a block of HTML code, as well as its style/javascript file requirements"""

    def __init__(
        self,
        code: str,

        script_requirements: List[ScriptRequirement] = [],
        style_requirements:  List[StyleRequirement]  = [],
    ) -> None:
        self._code = code
        self._script_requirements = script_requirements
        self._style_requirements  = style_requirements
    #enddef
#endclass



class BaseElement:
    """Base object used as a base for every element, holds very basic informations shared between every sub-object

    This class should be subclassed to make a specific element
    """

    _script_requirements = []
    _style_requirements = []
    template = None


    def _compile(self, global_context: Dict[str, Any] = {}) -> HTMLData:
        raise NotImplementedError()
    #enddef
#endclass



class BaseContainer(BaseElement):
    """Base object that can contain one or more children

    This class should be subclassed to make a specific container and to change its appearance and/or behaviour
    """

    template = htmllib.tagDIV(
        htmllib.local_var("children")
    )


    def __init__(self, children: List[BaseElement]) -> None:
        self._children  = children
    #enddef


    def _compile(self, global_context: Dict[str, Any] = {}) -> HTMLData:
        compiled_strings = []

        # copy the lists, so that when modifying won't touch the original ones
        script_requirements = [*self._script_requirements]
        style_requirements  = [*self._style_requirements]

        for child in self._children:
            compiled_child = child._compile(global_context=global_context)

            compiled_strings.append(compiled_child._code)
            script_requirements.extend(compiled_child._script_requirements)
            style_requirements.extend(compiled_child._style_requirements)
        #endfor

        # calling compile_self as most of the times there's the need for setting just the `local_context` variable
        # to render the content correctly, so the surrounding section of the _compile_self call can be generalized.
        compiled_self = self._compile_self(
            global_context = global_context,
            compiled_children_strings = compiled_strings,
        )

        return HTMLData(
            compiled_self,
            script_requirements = script_requirements,
            style_requirements  = style_requirements,
        )
    #enddef


    def _compile_self(self, global_context: Dict[str, Any] = {}, compiled_children_strings: List[str] = []) -> str:
        """Method called to render the template itself given the global_context and the children compiled strings, useful to set the local_context"""

        local_context = {
            "children": compiled_children_strings
        }

        return self.template.render(
            global_context = global_context,
            local_context = local_context,
        )
    #enddef
#endclass



class BaseWrapper(BaseElement):
    """Base object that can contain only one child

    This class should be subclassed to make a specific wrapper and to change its appearance and/or behaviour
    """

    template = htmllib.tagDIV(
        htmllib.local_var("child")
    )


    def __init__(self, child: BaseElement) -> None:
        self._child = child
    #enddef


    def _compile(self, global_context: Dict[str, Any] = {}) -> HTMLData:
        compiled_child = self._child._compile(
            global_context = global_context
        )

        # calling compile_self as most of the times there's the need for setting just the `local_context` variable
        # to render the content correctly, so the surrounding section of the _compile_self call can be generalized.
        compiled_self = self._compile_self(
            global_context = global_context,
            compiled_child_string = compiled_child._code,
        )

        return HTMLData(
            compiled_self,
            script_requirements = self._script_requirements + compiled_child._script_requirements,
            style_requirements  = self._style_requirements  + compiled_child._style_requirements,
        )
    #enddef


    def _compile_self(self, global_context: Dict[str, Any] = {}, compiled_child_string: str = "") -> str:
        """Method called to render the template itself given the global_context and the child compiled string, useful to set the local_context"""

        local_context = {
            "child": compiled_child_string
        }

        return self.template.render(
            global_context = global_context,
            local_context = local_context,
        )
    #enddef
#endclass



class BaseWidget(BaseElement):
    """Base object that displays data, can't have any children at all

    This class should be subclassed to make a specific widget and to change its appearance and/or behaviour
    """

    template = htmllib.tagSPAN(
        htmllib.local_var("text")
    )


    def __init__(self, text: str = "") -> None:
        self._text = text
    #enddef


    def _compile(self, global_context: Dict[str, Any] = {}) -> HTMLData:

        # here the _compile_self call is present just to maintain a certain consistency between classes, but the scope is the same.
        return HTMLData(
            self._compile_self(global_context=global_context),
            script_requirements = self._script_requirements,
            style_requirements  = self._style_requirements
        )
    #enddef


    def _compile_self(self, global_context: Dict[str, Any] = {}) -> str:
        """Method called to render the template itself given the global_context, useful to set the local_context"""

        local_context = {
            "text": self._text
        }

        return self.template.render(
            global_context = global_context,
            local_context = local_context,
        )
    #enddef
#endclass
