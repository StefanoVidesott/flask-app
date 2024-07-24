from system.utils.web_elements import htmllib
from system.utils.web_elements import bases
from system.utils.web_elements.requirements import ScriptLoading, ScriptRequirement, StyleRequirement

from typing import Any, Dict, List

class TestPage(bases.BaseWrapper):

    _body_template = htmllib.tagDIV(
        children=[
            htmllib.tagH1(
                "Page Title"
            ),
            htmllib.tagP(
                "This is a test page."
            )
        ]
    )

    _template = htmllib.Page(
        htmllib.tagBODY(_body_template)
    )

    _script_requirements = [
        ScriptRequirement(
            name = "body-js",
            path = "/assets/scripts/body_script.js",
            loading_technique = ScriptLoading.DEFER
        )
    ]

    _style_requirements = [
        StyleRequirement(
            name = "ob-widget-app-doppelmayr-css",
            path = "/assets/doppelmayr_app/styles/style.css"
        )
    ]

    def __init__(self) -> None:
        pass
    #enddef

    def _compile(self, global_context: Dict[str, Any] = {}) -> bases.HTMLData:
        compiled_self = self._compile_self(
            global_context = global_context
        )

        return bases.HTMLData(
            compiled_self,
            script_requirements = self._script_requirements,
            style_requirements  = self._style_requirements
        )
    #enddef

    def _compile_self(self, global_context: Dict[str, Any] = {}) -> str:
        local_context = {
        }

        return self._template.render(
            global_context = global_context,
            local_context = local_context
        )
    #enddef
#endclass
