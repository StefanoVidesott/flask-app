from system.tools.web_elements import htmllib
from system.tools.web_elements import bases
from system.tools.web_elements.requirements import ScriptLoading, ScriptRequirement, StyleRequirement

from typing import Any, Dict, List


class TestPage(bases.BaseWrapper):
    """Main page for the Doppelmayr app. It contains the navigation bar, the header and the content. The content is a wrapper for the specific page content."""

    _body_template = htmllib.tagDIV(
        children=[
            htmllib.tagSPAN(
                "Hello World"
            )
        ]
    )

    _template = htmllib.Page(
        htmllib.tagBODY(_body_template)
    )

    _script_requirements = [
        # ScriptRequirement(
        #     name = "ob-widget-app-doppelmayr-js",
        #     path = "/assets/doppelmayr_app/scripts/script.js",
        #     loading_technique = ScriptLoading.DEFER
        # )
    ]

    _style_requirements = [
        # StyleRequirement(
        #     name = "ob-widget-app-doppelmayr-css",
        #     path = "/assets/doppelmayr_app/styles/style.css"
        # )
    ]

    def __init__(self) -> None:
        """Initialize the page with the content. The content is a wrapper for the specific page content."""
        pass
    #enddef

    def _compile(self, global_context: Dict[str, Any] = {}) -> bases.HTMLData:
        """Compile the page. It compiles the navigation bar, the header and the content."""

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
        """Method called to render the template itself given the global_context and the child compiled string, useful to set the local_context"""

        local_context = {
        }

        return self._template.render(
            global_context = global_context,
            local_context = local_context
        )
    #enddef
#endclass
