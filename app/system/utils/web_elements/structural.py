from typing import Any, Dict, List, Union

from system.utils.web_elements import htmllib
from system.utils.web_elements.bases import BaseContainer, BaseElement, BaseWidget, BaseWrapper, HTMLData
from system.utils.web_elements.requirements import CSS_COMMON, JS_COMMON, Resource, ScriptLoading, ScriptRequirement, StyleRequirement

# NOTE: there may be unused imports, they're kept in case they're needed when adding new structural elements

##############
# CONTAINERS #
#region ######

class Column(BaseContainer):
    template = htmllib.tagDIV(
        htmllib.local_var("children"),
        attrs = {
            "class": htmllib.local_var("class_list"),
            "id": htmllib.local_var("id"),
        }
    )


    def __init__(self, children: List[BaseElement], class_list: List[str] = [], tag_id: Union[str, None] = None) -> None:
        super().__init__(children)

        self.tag_id = tag_id
        self.class_list = class_list
    #enddef


    def _compile_self(self, global_context: Dict[str, Any] = {}, compiled_children_strings: List[str] = []) -> str:
        local_context = {
            "children": compiled_children_strings,
            "class_list": " ".join(["ob-column"] + self.class_list),
            "id": self.tag_id,
        }

        return self.template.render(
            global_context = global_context,
            local_context = local_context,
        )
    #enddef
#endclass


class Row(BaseContainer):
    template = htmllib.tagDIV(
        htmllib.local_var("children"),
        attrs = {
            "class": htmllib.local_var("class_list"),
            "id": htmllib.local_var("id"),
        }
    )


    def __init__(self, children: List[BaseElement], class_list: List[str] = [], tag_id: Union[str, None] = None) -> None:
        super().__init__(children)

        self.tag_id = tag_id
        self.class_list = class_list
    #enddef


    def _compile_self(self, global_context: Dict[str, Any] = {}, compiled_children_strings: List[str] = []) -> str:
        local_context = {
            "children": compiled_children_strings,
            "class_list": " ".join(["ob-row"] + self.class_list),
            "id": self.tag_id
        }

        return self.template.render(
            global_context = global_context,
            local_context = local_context,
        )
    #endclass
#endclass

##################
# END CONTAINERS #
#endregion #######



###########
# WIDGETS #
#region ###

class Label(BaseWidget):
    template = htmllib.tagSPAN(
        htmllib.local_var("content"),
        attrs = {
            "class": htmllib.local_var("class_list"),
        },
    )

    _default_classes = ["ob-label"]


    def __init__(self, content: str, class_list: List[str] = [], override_default_class: bool = False) -> None:
        super().__init__()

        self._class_list = class_list
        self._override_default_class = override_default_class

        self.content = content
    #enddef


    def _compile_self(self, global_context: Dict[str, Any] = {}) -> str:
        local_context = {
            "class_list": " ".join(self._class_list if self._override_default_class else self._default_classes + self._class_list),
            "content": self.content,
        }

        return self.template.render(
            global_context = global_context,
            local_context = local_context,
        )
    #enddef
#endclass


class OneTimeWidget(BaseWidget):
    template = htmllib.Raw(htmllib.local_var("text"))


    def __init__(self, code: str, script_requirements: List[str] = [], style_requirements: List[str] = []) -> None:
        self._text = code
        self._script_requirements = script_requirements
        self._style_requirements  = style_requirements
    #enddef
#endclass

###############
# END WIDGETS #
#endregion ####



############
# WRAPPERS #
#endregion #

class Card(BaseWrapper):
    template = htmllib.tagDIV(
        children = [
            htmllib.tagH1(htmllib.local_var("title")),
            htmllib.tagDIV(htmllib.local_var("content")),
        ],
        attrs = {
            "class": htmllib.local_var("class_list"),
        }
    )

    _default_classes = ["ob-card"]


    def __init__(self, title: str, child: BaseElement, class_list: List[str] = []) -> None:
        super().__init__(child)

        self._class_list = class_list
        self.title = title
    #enddef


    def _compile_self(self, global_context: Dict[str, Any] = {}, compiled_child_string: str = "") -> str:
        local_context = {
            "content": compiled_child_string,
            "title": self.title,
            "class_list": " ".join(self._default_classes + self._class_list),
        }

        return self.template.render(
            global_context = global_context,
            local_context = local_context,
        )
    #enddef
#endclass


class Section(BaseWrapper):
    template = htmllib.tagSECTION(
        children = [
            htmllib.tagH1(htmllib.local_var("title")),
            htmllib.tagDIV(htmllib.local_var("content"))
        ],
        attrs = {
            "class": htmllib.local_var("class_list"),
        }
    )

    _default_classes = ["ob-section"]


    def __init__(self, title: str, child: BaseElement, class_list: List[str] = []) -> None:
        super().__init__(child)

        self._class_list = class_list
        self.title = title
    #enddef


    def _compile_self(self, global_context: Dict[str, Any] = {}, compiled_child_string: str = "") -> str:
        local_context = {
            "content": compiled_child_string,
            "title": self.title,
            "class_list": " ".join(self._default_classes + self._class_list),
        }

        return self.template.render(
            global_context = global_context,
            local_context = local_context,
        )
    #enddef
#endclass

################
# END WRAPPERS #
#endregion #####
