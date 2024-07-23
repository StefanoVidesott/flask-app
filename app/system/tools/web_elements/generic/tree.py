import json
from typing import Any, Dict, List, Union

from app.system.tools.web_elements import htmllib
from app.system.tools.web_elements.bases import BaseElement, BaseWidget, HTMLData
from app.system.tools.web_elements.requirements import CSS_COMMON, JS_COMMON, Resource, ScriptLoading, ScriptRequirement, StyleRequirement
from app.system.tools.web_elements.structural import OneTimeWidget


class Tree(BaseWidget):

    # structure defining "expand all" and "collapse all" buttons
    _expansion_controls = htmllib.tagDIV(
        attrs = {
            "class": "ob-tree-expansion-controls",
        },
        children = [
            # main label
            htmllib.tagLABEL(
                htmllib.local_var("translations.all_nodes")
            ),

            # "expand all" button
            htmllib.tagBUTTON(
                attrs = {
                    "class": "ob-btn btn",
                    "name":  "open-all-nodes-btn",
                    "title": "open all nodes",
                },
                children = [htmllib.local_var("translations.open")],
            ),

            # "collapse all" button
            htmllib.tagBUTTON(
                attrs = {
                    "class": "ob-btn btn",
                    "name":  "close-all-nodes-btn",
                    "title": "close all nodes",
                },
                children = [htmllib.local_var("translations.close")],
            ),
        ],
    )


    # structure defining the search bar
    # NOTE: there is no "submit search" button, as the search
    #       is done client-side and will be auto-executed once
    #       the user stops writing in the input
    _search_controls = htmllib.tagDIV(
        attrs = {
            "class": "ob-tree-search-controls",
        },
        children = [
            # search bar container
            htmllib.tagDIV(
                attrs = {
                    "class": "ob-tree-search-container",
                },
                children = [
                    # actual search input
                    htmllib.tagINPUT(
                        attrs = {
                            "class": "ob-tree-searchbar",
                            "name":  "search-bar",
                            "type":  "text",
                            "placeholder": htmllib.local_var("translations.search"),
                        },
                    ),

                    # submit button
                    htmllib.tagBUTTON(
                        attrs = {
                            "class": "ob-tree-searchreset",
                            "name":  "search-reset",
                            "type":  "button",
                        },
                        children = [
                            # clear icon
                            htmllib.tagI(
                                attrs = {
                                    "class": "material-symbols-outlined"
                                },
                                children = ["clear"],
                            ),
                        ],
                    ),
                ],
            ),

            # result container
            htmllib.tagDIV(
                attrs = {
                    "class": "ob-tree-search-matches",
                    "name":  "search-matches-container",
                    "style": "display: none;",
                },
                children = [
                    # container for the number of results of a search
                    htmllib.tagLABEL(
                        attrs = {
                            "name": "search-matches",
                        }
                    ),

                    htmllib.tagLABEL(htmllib.local_var("translations.results")),
                ],
            ),
        ],
    )


    # structure defining the buttons to save/discard changes made
    # NOTE: keep as list, to speed up the addition/deletion of buttons
    _save_discard_buttons = [
        htmllib.tagBUTTON(
            attrs = {
                "class": "btn btn-danger",
                "name": "discard_changes_btn",
                "title": "discard changes (reload)"
            },
            data = {
                "confirm-string": htmllib.local_var("translations.discard_confirm"),
            },
            children = [htmllib.local_var("translations.discard_changes")],
        ),

        htmllib.tagBUTTON(
            attrs = {
                "class": "btn btn-success",
                "name": "save_changes_btn",
                "title": "save changes"
            },
            data = {
                "confirm-string": htmllib.local_var("translations.save_confirm"),
            },
            children = [htmllib.local_var("translations.save_changes")],
        ),
    ]


    # structure defining the reload button
    _reload_buttons = [
        htmllib.tagBUTTON(
            attrs = {
                "class": "btn",
                "name": "reload_btn",
                "title": "reload",
            },
            children = [
                htmllib.tagI(
                    attrs = {
                        "class": "material-symbols-outlined",
                    },
                    children = ["refresh"],
                ),
            ],
        ),
    ]


    # main template structure
    template = htmllib.tagDIV(
        attrs = {
            "class": htmllib.local_var("container_class"),
        },
        data = {
            "id":              htmllib.local_var("tree.id"),
            "url":             htmllib.local_var("tree.url"),
            "config-override": htmllib.local_var("tree.config_override"),
            "flag":            htmllib.local_var("tree.flags"),
        },
        children = [
            # tree legend, is user-defined
            htmllib.tagDIV(
                attrs = {
                    "class": "ob-tree-legend",
                },
                children = [htmllib.local_var("legend")],
            ),

            htmllib.tagHR(),

            # top container for controls
            htmllib.tagDIV(
                attrs = {
                    "class": "ob-tree-top-bar",
                },
                children = [
                    # save/discard changes container, content will be set in _compile_self
                    htmllib.tagDIV(
                        attrs = {
                            "class": "ob-tree-save-controls",
                        },
                        children = [htmllib.local_var("save_control_buttons")],
                    ),

                    # general tree controls
                    htmllib.tagDIV(
                        attrs = {
                            "class": "ob-tree-controls",
                        },
                        children = [
                            _expansion_controls,

                            htmllib.tagDIV(
                                attrs = {
                                    "class": "vr",
                                },
                            ),

                            _search_controls,
                        ],
                    ),
                ],
            ),

            # container for API results
            htmllib.tagDIV(
                attrs = {
                    "name": "error-container",
                    "class": "ob-tree-error-container",
                },
            ),

            # actual tree container
            htmllib.tagDIV(
                attrs = {
                    "name": "main",
                    "class": "ob-tree-main",
                },
            ),
        ],
    )


    _script_requirements: List[ScriptRequirement] = [
        JS_COMMON["ob-utils-js"],
        ScriptRequirement(
            name = "ob-widget-tree-js",
            path = "/web/static/lib/openbridge/widget_tree/widget_tree.js",
        ),
        ScriptRequirement(
            name = "ob-widget-tree-jstree-js",
            path = "/web/static/lib/openbridge/widget_tree/jstree_3_3_16/dist/jstree.min.js",
            loading_technique = ScriptLoading.PRELOAD,
        ),
    ]


    _style_requirements: List[StyleRequirement] = [
        StyleRequirement(
            name = "ob-widget-tree-css",
            path = "/web/static/lib/openbridge/widget_tree/widget_tree.css",
        ),
        StyleRequirement(
            name = "ob-widget-tree-jstree-css",
            path = "/web/static/lib/openbridge/widget_tree/jstree_3_3_16/dist/themes/default/style.min.css",
            preload_resources = [
                Resource("/web/static/lib/openbridge/widget_tree/jstree_3_3_16/dist/themes/default/32px.png",     "image", "image/png"),
                Resource("/web/static/lib/openbridge/widget_tree/jstree_3_3_16/dist/themes/default/40px.png",     "image", "image/png"),
                Resource("/web/static/lib/openbridge/widget_tree/jstree_3_3_16/dist/themes/default/throbber.gif", "image", "image/gif"),
            ],
        ),
    ]


    def __init__(
        self,
        url:                str,
        tag_id:             str  = "",
        tree_legend:        Union[str, BaseElement]  = "",

        async_load:         bool = False,
        can_upload:         bool = False,
        edit_record:        bool = False,
        add_record:         bool = False,
        delete_record:      bool = False,
        move_record:        bool = False,

        class_list:         List[str] = [],
        label_translations: dict = {
            "save_changes":    "Save",
            "discard_changes": "Discard",
            "save_confirm":    "Confirm saving?",
            "discard_confirm": "Confirm discard?",
            "search":    "Search...",
            "results":   "results",
            "all_nodes": "All nodes",
            "open":      "open",
            "close":     "close",
        },
        config_override: Union[str, dict] = {}
    ) -> None:
        self.url                = url
        self.tag_id             = tag_id if tag_id.strip() else f"ob-tree-{id(self)}"
        self.tree_legend        = tree_legend
        self.flags              = {
            "async_load":    async_load,
            "can_upload":    can_upload,
            "edit_record":   edit_record,
            "add_record":    add_record,
            "delete_record": delete_record,
            "move_record":   move_record,
        }
        self.class_list         = class_list
        self.label_translations = label_translations

        if isinstance(config_override, dict):
            try:
                json.dumps(config_override)
            except TypeError:
                raise ValueError(f"Invalid dict for config_override: '{config_override}', must be json serializable")
            #endtry
        elif isinstance(config_override, str):
            try:
                json.loads(config_override)
            except TypeError:
                raise ValueError(f"Invalid string for config_override: '{config_override}', must be json deserializable")
            #endtry
        else:
            raise ValueError(f"Invalid object for config_override: '{config_override}'; expected <str | dict>; got {config_override.__class__.__name__}")
        #endif

        self.config_override = config_override
    #enddef


    def _compile(self, global_context: Dict[str, Any] = {}) -> HTMLData:

        if isinstance(self.tree_legend, BaseElement):
            compiled_tree_legend = self.tree_legend._compile(
                global_context = global_context
            )
        elif isinstance(self.tree_legend, str):
            compiled_tree_legend = OneTimeWidget(self.tree_legend)._compile(
                global_context = global_context
            )
        else:
            raise ValueError(f"invalid object set in tree_legend: '{self.tree_legend}'; expected <str | BaseElement>; got <{self.tree_legend.__class__.__name__}>")
        #endif

        compiled_self = self._compile_self(
            global_context = global_context,
            compiled_tree_legend_string = compiled_tree_legend._code,
        )

        return HTMLData(
            compiled_self,
            script_requirements = self._script_requirements + compiled_tree_legend._script_requirements,
            style_requirements  = self._style_requirements  + compiled_tree_legend._style_requirements,
        )
    #enddef


    def _compile_self(self, global_context: Dict[str, Any] = {}, compiled_tree_legend_string: str = "") -> str:

        config_override_string = self.config_override if isinstance(self.config_override, str) else json.dumps(self.config_override)

        save_control_buttons = self._save_discard_buttons if self.flags["can_upload"] else self._reload_buttons

        local_context = {
            "translations": {
                "save_changes":    self.label_translations.get("save_changes",    "N/A"),
                "discard_changes": self.label_translations.get("discard_changes", "N/A"),
                "save_confirm":    self.label_translations.get("save_confirm",    "N/A"),
                "discard_confirm": self.label_translations.get("discard_confirm", "N/A"),
                "search":          self.label_translations.get("search",          "N/A"),
                "results":         self.label_translations.get("results",         "N/A"),
                "all_nodes":       self.label_translations.get("all_nodes",       "N/A"),
                "open":            self.label_translations.get("open",            "N/A"),
                "close":           self.label_translations.get("close",           "N/A"),
            },
            "tree": {
                "id":              self.tag_id,
                "url":             self.url,
                "config_override": config_override_string,
                "flags": {
                    key: str(value).lower() # convert flags to strings
                    for key, value in self.flags.items()
                },
            },
            "legend":               compiled_tree_legend_string,
            "container_class":      " ".join(["ob-tree"] + self.class_list),
            "save_control_buttons": save_control_buttons,
        }

        return self.template.render(
            global_context = global_context,
            local_context = local_context,
        )
    #enddef
#endclass
