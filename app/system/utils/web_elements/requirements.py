from enum import Flag
from typing import Dict, List, Set, Union

from system.utils.web_elements import htmllib

# GENERAL NOTE: Link-preload can be used on script, css and genral resources to be loaded before they're used
#               here this feature will be used only with scripts, and with resources of style requirements.
#               Some guidelines on loading:
#               - Styles:
#                   - Style should be after scripts
#                   - If a style has some resources to preload they will be put before scripts and before the css.
#               - Scripts
#                   - If a script has some resources to preload they will be put before scripts and before the css.
#                   - If a script has the PRELOAD flag it will have at the top of the document (after resources) a tag
#                       link with the preload flag active and have the actual script tag at the bottom of the document
#                   - If a script has the the DEFER/ASYNC flag it will be put at the top of the document (after resources)
#                       as a normal script tag with its relative flag on
#
#               So the final structure will be:
#               1. resources to preload (if any)
#               2. stylesheets
#               3. script preload of those scripts which have the PRELOAD flag
#               4. script tags of those scripts which have the NORMAL/ASYNC/DEFER flag
#               5. rest of HTML document
#               6. script tags of those scripts which have the PRELOAD flag
#
#               Docs on preloads: https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/preload
#

###########
# CLASSES #
#region ###

class ScriptLoading(Flag):
    # NOTE: the Flag class is the same as Enum, with the only difference being it supports
    #       binary operators thus to be single options the value must be powers of 2.
    #       If (for example) the ASYNC flag would be 3 it would be interpreted as
    #       a combination of NORMAL and DEFER (since 1 + 2 = 3).
    #       So passing a flag as `ScriptLoading.DEFER | ScriptLoading.ASYNC` will return
    #       `ScriptLoading.ASYNC_DEFER`
    #       docs @ https://docs.python.org/3.7/library/enum.html#flag
    NORMAL  = 1
    DEFER   = 2
    ASYNC   = 4
    PRELOAD = 8
    ASYNC_DEFER = DEFER | ASYNC
#endclass

# NOTE: __hash__ and __eq__ methods are defined on each class to make possible the use of "set" to make the sorting faster

class Resource:
    """A resource that needs preloading, it is a part of a Style/Script Requirement

    Generates a link tag with the `rel="preload"` attribute
    """

    allowed_content_types = [
        "fetch",
        "font",
        "image",
        "script",
        "style",
        "track",
    ]

    def __init__(self, path: str, content_type: str, mime_type: Union[str, None] = None) -> None:
        # TYPE CHECK
        if not isinstance(path, str):
            raise TypeError(f"Invalid type for argument 'path'; expected <str>; got <{path.__class__.__name__}>")
        #endif

        if not isinstance(content_type, str) or content_type not in self.allowed_content_types:
            raise TypeError(f"Invalid type for argument 'content_type'; expected <str: {' | '.join(self.allowed_content_types)}>; got <{content_type.__class__.__name__}>")
        #endif

        if (mime_type is not None) and not isinstance(mime_type, str):
            raise TypeError(f"Invalid type for argument 'mime_type'; expected <str | None>; got <{mime_type.__class__.__name__}>")
        #endif

        self.path = path
        self.content_type = content_type
        self.mime_type    = mime_type
    #enddef


    def __hash__(self) -> int:
        return hash(self.path)
    #enddef


    def __eq__(self, other) -> bool:
        return hash(self) == hash(other)
    #enddef


    @property
    def tag(self) -> str:
        return htmllib.tagLINK(
            attrs = {
                "rel":  "preload",
                "href": self.path,
                "as":   self.content_type,
                # adding it as empty string will completely remove it from being rendered
                "type": self.mime_type if self.mime_type != None else "",
                # adding this as default, documentation at
                # https://developer.mozilla.org/en-US/docs/Web/HTML/Element/link#crossorigin
                "crossorigin": "anonymous",
            },
        ).render()
    #enddef
#endclass


class ScriptRequirement:
    def __init__(
        self,
        name: str,
        path: str,

        priority: int = 50,
        loading_technique: ScriptLoading = ScriptLoading.ASYNC_DEFER,
        preload_resources: List[Resource] = [],
    ) -> None:
        # TYPE CHECK
        if not isinstance(name, str):
            raise TypeError(f"Invalid type for argument 'name'; expected <str>; got <{name.__class__.__name__}>")
        #endif

        if not isinstance(path, str):
            raise TypeError(f"Invalid type for argument 'path'; expected <str>; got <{path.__class__.__name__}>")
        #endif

        if not isinstance(priority, int):
            raise TypeError(f"Invalid type for argument 'priority'; expected <int>; got <{priority.__class__.__name__}>")
        #endif

        if not isinstance(loading_technique, ScriptLoading):
            raise TypeError(f"Invalid type for argument 'loading_technique'; expected <ScriptLoading>; got <{loading_technique.__class__.__name__}>")
        #endif

        if not isinstance(preload_resources, list):
            raise TypeError(f"Invalid type for argument 'preload_resources'; expected <list>; got <{preload_resources.__class__.__name__}>")
        elif not all(isinstance(list_item, Resource) for list_item in preload_resources):
            raise TypeError(f"Invalid list content for argument 'preload_resources'; all items must be <Resource>")
        #endif

        self.name = name
        self.path = path
        self.priority          = priority
        self.loading_technique = loading_technique
        self.preload_resources = preload_resources
    #enddef


    def __str__(self) -> str:
        return f"{self.__qualname__}(name='{self.name}', path='{self.path}', priority='{self.priority}', loading='{self.loading_technique}', preload='{self.preload_resources}')"
    #enddef


    def __hash__(self) -> int:
        return hash(self.path)
    #enddef


    def __eq__(self, other) -> bool:
        return hash(self) == hash(other)
    #enddef


    @property
    def tag(self) -> str:
        return htmllib.tagSCRIPT(
            attrs = {
                "src": self.path,
                "defer": (self.loading_technique == ScriptLoading.DEFER) or (self.loading_technique == ScriptLoading.ASYNC_DEFER),
                "async": (self.loading_technique == ScriptLoading.ASYNC) or (self.loading_technique == ScriptLoading.ASYNC_DEFER),
            },
        ).render()
    #enddef


    @property
    def resource_tag_list(self) -> List[str]:
        return [resource.tag for resource in self.preload_resources]
    #enddef
#endclass


class StyleRequirement:
    def __init__(
        self,
        name: str,
        path: str,

        priority: int = 50,
        preload_resources: List[Resource] = [],
    ) -> None:
        # TYPE CHECK
        if not isinstance(name, str):
            raise TypeError(f"Invalid type for argument 'name'; expected <str>; got <{name.__class__.__name__}>")
        #endif

        if not isinstance(path, str):
            raise TypeError(f"Invalid type for argument 'path'; expected <str>; got <{path.__class__.__name__}>")
        #endif

        if not isinstance(priority, int):
            raise TypeError(f"Invalid type for argument 'priority'; expected <int>; got <{priority.__class__.__name__}>")
        #endif

        if not isinstance(preload_resources, list):
            raise TypeError(f"Invalid type for argument 'preload_resources'; expected <list>; got <{preload_resources.__class__.__name__}>")
        elif not all(isinstance(list_item, Resource) for list_item in preload_resources):
            raise TypeError(f"Invalid list content for argument 'preload_resources'; all items must be <Resource>")
        #endif

        self.name = name
        self.path = path
        self.priority          = priority
        self.preload_resources = preload_resources
    #enddef


    def __str__(self) -> str:
        return f"{self.__qualname__}(name='{self.name}', path='{self.path}', priority='{self.priority}', preload='{self.preload_resources}')"
    #enddef


    def __hash__(self) -> int:
        return hash(self.path)
    #enddef


    def __eq__(self, other) -> bool:
        return hash(self) == hash(other)
    #enddef

    @property
    def tag(self) -> str:
        return htmllib.tagLINK(
            attrs = {
                "rel": "stylesheet",
                "href": self.path,
            },
        ).render()
    #enddef


    @property
    def resource_tag_list(self) -> List[str]:
        return [resource.tag for resource in self.preload_resources]
    #enddef
#endclass


class PageResourceData:
    def __init__(
        self,
        resource_preload:    Set[Resource]          = set(),
        style_requirements:  Set[StyleRequirement]  = set(),
        script_requirements: Set[ScriptRequirement] = set(),
    ) -> None:
        self.resource_preload    = resource_preload
        self.style_requirements  = style_requirements
        self.script_requirements = script_requirements
    #enddef


    # SCRIPTS

    def add_script(self, script_requirement: ScriptRequirement) -> None:
        if not isinstance(script_requirement, ScriptRequirement):
            raise TypeError(f"Invalid type for argument 'script_requirement'; expected <ScriptRequirement>; got <{script_requirement.__class__.__name__}>")
        #endif

        if script_requirement in self.script_requirements:
            # NOTE: order of operation matters, if self.script_requirements is last then the object that will be put inside current_script_requirement
            #       will be the object that is inside self.script_requirements

            # here can safely use pop() as there is only one element
            current_script_requirement = (set([script_requirement]) & self.script_requirements).pop()

            if script_requirement.priority > current_script_requirement.priority:
                self.script_requirements.difference_update(set([current_script_requirement])) # remove old script
                self.script_requirements.add(script_requirement) # add new one

                self.add_resource_list(script_requirement.preload_resources, overwrite = True)
            else:
                self.add_resource_list(script_requirement.preload_resources)
            #endif
        else:
            self.script_requirements.add(script_requirement)
            self.add_resource_list(script_requirement.preload_resources)
        #endif
    #enddef


    def add_script_list(self, script_requirement_list: List[ScriptRequirement]) -> None:
        if not isinstance(script_requirement_list, list):
            raise TypeError(f"Invalid type for argument 'script_requirement_list'; expected <list>; got <{script_requirement_list.__class__.__name__}>")
        elif not all(isinstance(list_item, ScriptRequirement) for list_item in script_requirement_list):
            raise TypeError(f"Invalid list content for argument 'script_requirement_list'; all items must be <ScriptRequirement>")
        #endif

        for script_requirement in script_requirement_list:
            self.add_script(script_requirement)
        #endfor
    #enddef


    # STYLESHEETS

    def add_style(self, style_requirement: StyleRequirement) -> None:
        if not isinstance(style_requirement, StyleRequirement):
            raise TypeError(f"Invalid type for argument 'style_requirement'; expected <StyleRequirement>; got <{style_requirement.__class__.__name__}>")
        #endif

        if style_requirement in self.style_requirements:
            # NOTE: order of operation matters, if self.style_requirements is last then the object that will be put inside current_style_requirement
            #       will be the object that is inside self.style_requirements

            # here can safely use pop() as there is only one element
            current_style_requirement = (set([style_requirement]) & self.style_requirements).pop()

            if style_requirement.priority > current_style_requirement.priority:
                self.style_requirements.difference_update(set([current_style_requirement])) # remove old script
                self.style_requirements.add(style_requirement) # add new one

                self.add_resource_list(style_requirement.preload_resources, overwrite = True)
            else:
                self.add_resource_list(style_requirement.preload_resources)
            #endif
        else:
            self.style_requirements.add(style_requirement)
            self.add_resource_list(style_requirement.preload_resources)
        #endif
    #enddef


    def add_style_list(self, style_requirement_list: List[StyleRequirement]) -> None:
        if not isinstance(style_requirement_list, list):
            raise TypeError(f"Invalid type for argument 'style_requirement_list'; expected <list>; got <{style_requirement_list.__class__.__name__}>")
        elif not all(isinstance(list_item, StyleRequirement) for list_item in style_requirement_list):
            raise TypeError(f"Invalid list content for argument 'style_requirement_list'; all items must be <StyleRequirement>")
        #endif

        for style_requirement in style_requirement_list:
            self.add_style(style_requirement)
        #endfor
    #enddef


    # GENERAL RESOURCES

    def add_resource(self, new_resource: Resource, overwrite: bool = False) -> None:
        if not isinstance(new_resource, Resource):
            raise TypeError(f"Invalid type for argument 'new_resource'; expected <Resource>; got <{new_resource.__class__.__name__}>")
        #endif

        if overwrite:
            # NOTE: here can safely use the difference update without taking the item that is inside resource_preload
            #       as the hash is defined by only the path
            self.resource_preload.difference_update(set([new_resource])) # remove old resource
            self.resource_preload.add(new_resource) # add new one
        else:
            self.resource_preload.add(new_resource)
        #endif
    #enddef


    def add_resource_list(self, resource_list: List[Resource], overwrite: bool = False) -> None:
        if not isinstance(resource_list, list):
            raise TypeError(f"Invalid type for argument 'resource_list'; expected <list>; got <{resource_list.__class__.__name__}>")
        elif not all(isinstance(list_item, Resource) for list_item in resource_list):
            raise TypeError(f"Invalid list content for argument 'resource_list'; all items must be <Resource>")
        #endif

        for resource_requirement in resource_list:
            self.add_resource(resource_requirement, overwrite = overwrite)
        #endfor
    #enddef
#endclass

###############
# END CLASSES #
#endregion ####


JS_COMMON: Dict[str, ScriptRequirement] = {
    "ob-general-js": ScriptRequirement(
        name = "ob-general",
        path = "/web/static/lib/scripts/ob_general.js",
        priority = 40,
    ),
    "ob-utils-js": ScriptRequirement(
        name = "ob-utils",
        path = "/web/static/lib/openbridge/utils/utils.js",
        priority = 30,
    ),
}


CSS_COMMON: Dict[str, StyleRequirement] = {
    "ob-general-css": StyleRequirement(
        "ob-general",
        "/web/static/lib/css/ob_general.css",
    ),
}
