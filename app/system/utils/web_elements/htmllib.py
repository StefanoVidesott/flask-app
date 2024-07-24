import collections.abc
import json
import re
from copy import deepcopy
from typing import Any, Callable, Dict, List, Sequence, Union

from system.tools import utils

INDENT = 2

# TYPE ALIASES
################
CONTEXT         = Dict[str, Any]
ITEM            = Union["HTMLElement", str, Sequence, Callable[[CONTEXT, CONTEXT], Union["HTMLElement", str, Sequence]]]
ATTRIBUTE_VALUE = Union["ATTRIBUTE_DICT", str, bool, Callable[[CONTEXT, CONTEXT], Union["ATTRIBUTE_DICT", str, bool]]]
ATTRIBUTE_DICT  = Dict[str, ATTRIBUTE_VALUE]
JSON_SERIALIZABLE = Union[
    Dict[str, "JSON_SERIALIZABLE"],
    List["JSON_SERIALIZABLE"],
    str, int, float, bool, None
]


# CUSTOM ERRORS
#################

class HTMLError(Exception):                  pass
class HTMLStructuralError(HTMLError):        pass
class HTMLAttributeEncodingError(HTMLError): pass
class HTMLContextKeyError(HTMLError):        pass


# UTILS
#########

def _render_item(
    item: ITEM,
    global_context: CONTEXT = {},
    local_context:  CONTEXT = {},
    indent: int = 0,
    whitespace_sensitive: bool = False,
) -> str:
    output = ""

    if isinstance(item, HTMLElement):
        output += item.render(
            global_context = global_context,
            local_context = local_context,
            indent  = indent,
            whitespace_sensitive = whitespace_sensitive,
        )
    elif callable(item):
        output += _render_item(
            item           = item(global_context, local_context),
            global_context = global_context,
            local_context  = local_context,
            indent         = indent,
            whitespace_sensitive = whitespace_sensitive,
        )
    elif isinstance(item, collections.abc.Sequence) and not isinstance(item, str):
        # need to check that is not a string as a string is itself a sequence
        output += _render_list(
            item_list      = list(item),
            global_context = global_context,
            local_context  = local_context,
            indent         = indent,
            whitespace_sensitive = whitespace_sensitive,
        )
    else: # assume it's string
        # .format call removed as it would create too many problems,
        # now to use formatted strings based on local/global context
        # use Raw object with format_content flag set to True
        string = str(item)

        # Write content
        if not whitespace_sensitive:
            for line in string.splitlines(True):
                output += "{indent}{line}".format(
                    indent = " " * indent,
                    line = line
                )
            #endfor
        else:
            output += string
        #endif
    #endif

    return output
#enddef


def _render_list(
    item_list: list,
    global_context: CONTEXT = {},
    local_context: CONTEXT = {},
    indent: int = 0,
    whitespace_sensitive: bool = False,
) -> str:
    output = ""

    for index, child in enumerate(item_list):
        if index != 0 and not whitespace_sensitive: output += "\n"

        output += _render_item(
            item = child,
            global_context = global_context,
            local_context = local_context,
            indent = indent,
            whitespace_sensitive = whitespace_sensitive,
        )
    #endfor

    return output
#enddef


def escape_html_text(text: str) -> str:
    """Escapes the given text to be HTML-safe"""

    escape_characters = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
    }

    for char, escaped in escape_characters.items():
        text = text.replace(char, escaped)
    # endfor

    return text
# enddef


def encode_attribute_key(key: str) -> str:
    """Converts any attribute key to its relative HTML-specification-compliant counterpart.

    E.g.: a key ```helloWorld``` will be converted to ```hello-world```
    """

    # based on these standards
    # HTML standard for data-attributes: https://html.spec.whatwg.org/multipage/dom.html#dom-dataset
    # HTML standard for naming: https://www.w3.org/TR/xml/#NT-Name

    # the function replaces for each match the first group (the uppercase letter) with a hyphen ('-') followed by the
    # same letter in lowercase
    replacement_function: Callable[[re.Match], str] = lambda match: f"-{str(match.group(1)).lower()}"

    return re.sub(
        pattern = "(?<=[a-z0-9])([A-Z])",
        repl    = replacement_function,
        string  = key
    )
#enddef


def encode_attribute_value(key: str, value: ATTRIBUTE_VALUE, concatenator: str = ".", global_context: CONTEXT = {}, local_context: CONTEXT = {}) -> str:
    """Flattens any subdict or list present in the value given, or present in any function call in the value given, recursively to have a list of HTML-compliant attributes.

    E.g.: a starting value of
    ```
    {
        "a": "hello",
        "b": True,
        "c": {
            "x": [1,2,3],
            "y": {
                "z": 12,
            },
        },
        "d": lambda g, l: [1, True, "hello"],
    }
    ```
    will return the following HTML-compliant string:
    ```
    "a='hello' b c.x.0='1' c.x.1='2' c.x.2='3' c.y.z='12' d.0='1' d.1 d.2='hello'"
    ```
    """

    encoded_attribute = ""

    if isinstance(value, dict):
        encoded_items = []

        for subkey, subvalue in value.items():
            encoded_items.append(
                encode_attribute_value(
                    key   = f"{key}{concatenator}{subkey}",
                    value = subvalue,
                    concatenator   = concatenator,
                    global_context = global_context,
                    local_context  = local_context
                )
            )
        #endfor

        encode_result = " ".join(encoded_items).strip()
        if encode_result: encoded_attribute = encode_result

    elif isinstance(value, list):
        encoded_items = []

        for index, item in enumerate(value):
            encoded_items.append(
                encode_attribute_value(
                    key   = f"{key}{concatenator}{index}",
                    value = item,
                    concatenator   = concatenator,
                    global_context = global_context,
                    local_context  = local_context
                )
            )
        #endfor

        encode_result = " ".join(encoded_items).strip()
        if encode_result: encoded_attribute = encode_result

    elif callable(value):
        function_value = encode_attribute_value(
            key   = key,
            value = value(global_context, local_context),
            concatenator   = concatenator,
            global_context = global_context,
            local_context  = local_context
        )

        if function_value: encoded_attribute = function_value

    elif isinstance(value, bool):
        if value: encoded_attribute = key

    else:
        value = str(value).strip() # force item to be string
        # don't add the key if there is no value as browsers will interpret it as a boolean value
        if value: encoded_attribute = f"{key}='{escape_html_text(value)}'"
    #endif

    return encoded_attribute.strip()
#enddef


def encode_tag_attributes(
    data: ATTRIBUTE_DICT,
    prefix: str = "",
    concatenator: str = ".",
    global_context: CONTEXT = {},
    local_context:  CONTEXT = {},
    is_data_attribute: bool = False,
) -> str:
    """Given a dictionary of attributes generate the string going into the tag definition.

    `global_context` and `local_context` are namespaces passed to dictionary values that are functions that can be called,
    once they are called the return value of those functions will be put as the value of the tag.

    If the value is None or "" (empty string), the tag will not be renderd.
    """

    encoded_attributes = []

    for key, value in data.items():
        # following the directives defined in https://html.spec.whatwg.org/multipage/dom.html#dom-dataset

        if "-" in key:
            raise HTMLAttributeEncodingError("tag attribute name cannot containt hypens ('-') characters")
        #endif

        key_string = encode_attribute_key(key)

        if prefix:
            key_string = f"{prefix}{concatenator}{key_string}"
        #endif

        if is_data_attribute:
            key_string = f"data-{key_string}"
        #endif

        formatted_string = encode_attribute_value(
            # add concatenator only if the prefix is actually present
            key   = key_string,
            value = value,
            concatenator   = concatenator,
            global_context = global_context,
            local_context  = local_context
        ).strip()

        if formatted_string:
            encoded_attributes.append(formatted_string)
        #endif
    #endfor

    return " ".join(encoded_attributes)
#enddef


def global_var(key: str, default: Any = None) -> Callable[[CONTEXT, CONTEXT], Any]:
    """global_context variable getter used as children of tags or as values of attributes, will be called at render-time.

    The `key` attribute is a string representing the "path" of the value in the global_context dictionary,
    writing `global_var("text.value")` will do the same as `global_context["text"]["value"]` returning the `default` if
    at any point the value cannot be found.
    """

    return lambda ctx_global, ctx_local: utils.common.get_dict_subattribute(ctx_global, key, default)
#enddef

def local_var(key: str, default: Any = None) -> Callable[[CONTEXT, CONTEXT], Any]:
    """local_context variable getter used as children of tags or as values of attributes, will be called at render-time.

    The `key` attribute is a string representing the "path" of the value in the local_context dictionary,
    writing `global_var("text.value")` will do the same as `local_context["text"]["value"]` returning the `default` if
    at any point the value cannot be found.
    """

    return lambda ctx_global, ctx_local: utils.common.get_dict_subattribute(ctx_local, key, default)
#enddef


# CLASSES
###########

class HTMLElementMeta(type):
    """Type of the Tag. (type(Tag) == HTMLElementMeta)"""
#endclass


class HTMLElement(object, metaclass=HTMLElementMeta):
    """Base HTML element class to make any tag, calling an istance of an element will return a modified clone of itself plus the arguments given.

    By default the tag name is the classname in lowercase and, if it starts with "tag", it removes it, the name can be overwritten
    using the `tag_name_override` attribute.

    A tag can be self-closing, meaning that it can't have children and will auto close.
    A tag can be whitespace sensitive, meaning that it won't add nor delete any spacing/return characters to its content.
    A tag can be escaping content, meaning that all of its content will be escaped to not be interpreted by an HTML interpreter.

    Default attributes and data-attributes can be set in the class definition.
    This class should be used to create new classes representing the desired tag.
    """

    self_closing:         bool = False
    escape_content:       bool = False # do not escape while rendering
    whitespace_sensitive: bool = False
    tag_name_override:    Union[str, None] = None
    default_attributes:   Dict[str, Union[str, bool]] = {}
    default_data:         Dict[str, Union[str, bool]] = {}

    def __init__(
        self,
        *args,
        children: list = [],
        escape_content:       bool = False,
        whitespace_sensitive: bool = False,
        attrs: ATTRIBUTE_DICT = {},
        data:  ATTRIBUTE_DICT = {},
    ) -> None:
        """Creates an instance of this tag, children can be defined (provided the tag isn't self-closing) in the positional arguments or in the `children` parameter.

        A child can be:
            - another instance of HTMLElement
            - a list
            - a function taking two dictionaries (`global_context` and `local_context`) as input and returning a string
            - a string

        Attributes and data-attributes can be set in their respective dicitonary parameters, an attribute can be:
            - a string
            - a bool (which will be considered as a flag if the value is `True`)
            - a function taking two dictionaries (`global_context` and `local_context`) as input and returning a string
        """

        if self.self_closing and len(list(args) + children):
            raise HTMLStructuralError("Self closing tag can't have children")
        #endif

        # set safe flag for escaping
        self.escape_content = escape_content
        self.whitespace_sensitive = whitespace_sensitive

        self.children = list(args) + children

        # set tag attributes
        self.attributes = {
            **self.default_attributes,
            **attrs
        }

        # set tag data-attributes
        self.data = {
            **self.default_data,
            **data
        }
    #enddef

    def __call__(
        self,
        *args,
        children: list = [],
        escape_content:       bool = False,
        whitespace_sensitive: bool = False,
        attrs: ATTRIBUTE_DICT = {},
        data:  ATTRIBUTE_DICT = {},
    ) -> "HTMLElement":
        """Clones this instance of this tag and modifies it, children can be defined (provided the tag isn't self-closing) in the positional arguments or in the `children` parameter.

        A child can be:
            - another instance of HTMLElement
            - a list
            - a function taking two dictionaries (`global_context` and `local_context`) as input and returning a string
            - a string

        Attributes and data-attributes can be set in their respective dicitonary parameters, an attribute can be:
            - a string
            - a bool (which will be considered as a flag if the value is `True`)
            - a function taking two dictionaries (`global_context` and `local_context`) as input and returning a string
        """

        clone = self.copy()

        if clone.self_closing and (list(args) + children):
            raise HTMLStructuralError("Self closing tag can't have children")
        #endif

        clone.escape_content = escape_content
        clone.whitespace_sensitive = whitespace_sensitive
        clone.children = list(args) + children
        clone.attributes = {**attrs}
        clone.data = {**data}

        return clone
    #enddef

    def __repr__(self) -> str:
        return f"<{self.name} attrs={self.attributes} data={self.data}>"
    #enddef

    def __str__(self) -> str:
        return self.render()
    #enddef


    def copy(self):
        """Clones this tag and returns its deep copy"""

        return deepcopy(self)
    #enddef

    def render(
        self,
        global_context: CONTEXT = {},
        local_context: CONTEXT = {},
        indent: int = 0,
        whitespace_sensitive: bool = False,
    ) -> str:
        """Renders this tag and returns its string representation.

        global and local context are two namespaces in which variables can be stored to be used in rendering.
        """

        output = ""

        # attributes encoding
        self_attributes_string = (
            (" " + encode_tag_attributes(self.attributes, global_context = global_context, local_context = local_context))
            if self.attributes
            else ""
        )

        self_data_attributes_string = (
            (" " + encode_tag_attributes(self.data, global_context = global_context, local_context = local_context, is_data_attribute = True))
            if self.data
            else ""
        )

        self_indent = (" " * indent) if not whitespace_sensitive else ""

        if self.self_closing:
            output += "{indent}<{tag}{attributes}{data_attributes}/>".format(
                indent = self_indent,
                tag    = self.name,
                attributes      = self_attributes_string,
                data_attributes = self_data_attributes_string
            )
        else:
            output += "{indent}<{tag}{attributes}{data_attributes}>".format(
                indent = self_indent,
                tag    = self.name,
                attributes      = self_attributes_string,
                data_attributes = self_data_attributes_string
            )

            content = ""

            # adding chilren
            if self.children:
                if not whitespace_sensitive: content += "\n"

                # Write content
                content += _render_list(
                    item_list      = self.children,
                    global_context = global_context,
                    local_context  = local_context,
                    indent         = indent + INDENT,
                    # must pass the flag as if this tag is whitespace sensitive from this point onwards all tags must not modify the spaces
                    whitespace_sensitive = whitespace_sensitive or self.whitespace_sensitive,
                )

                if not whitespace_sensitive: content += "\n"
            #endif

            # can escape text here as all the children are already rendered
            output += escape_html_text(content) if self.escape_content else content

            output += "{indent}</{tag}>".format(
                indent = self_indent,
                tag = self.name
            )
        #endif

        return output
    #enddef


    @property
    def name(self) -> str:
        if self.tag_name_override:
            return self.tag_name_override
        else:
            self_name = self.__class__.__name__

            if self_name.startswith("tag"):
                self_name = self_name[3:]
            #endif

            return self_name.lower()
        #endif
    #enddef
#endclass


class JSONData(HTMLElement):
    """SCRIPT element, to be used when storing JSON data, will accept only text or functions as input."""

    tag_name_override = "script"
    default_attributes = {"type": "application/json"}


    def __init__(
        self,
        json_data: Union[str, JSON_SERIALIZABLE, Callable[[CONTEXT, CONTEXT], JSON_SERIALIZABLE]],
        json_call_kwargs: Dict[str, Any] = {},
        attrs: ATTRIBUTE_DICT = {},
        data:  ATTRIBUTE_DICT = {},
    ) -> None:
        if not callable(json_data):
            if isinstance(json_data, str):
                try:
                    json.loads(json_data, **json_call_kwargs)
                except TypeError as exception:
                    raise HTMLStructuralError("JSONData data content is not a valid JSON string") from exception
                #endtry
            else:
                try:
                    json.dumps(json_data, **json_call_kwargs)
                except TypeError as exception:
                    raise HTMLStructuralError("JSONData data content is not JSON serializable") from exception
                #endtry
            #endif
        #endif

        self.json_data = json_data
        self.json_call_kwargs = json_call_kwargs

        super().__init__(
            attrs=attrs,
            data=data,
        )
    #enddef

    def __call__(
        self,
        json_data: Union[str, JSON_SERIALIZABLE, Callable[[CONTEXT, CONTEXT], JSON_SERIALIZABLE]],
        json_call_kwargs: Dict[str, Any] = {},
        attrs: ATTRIBUTE_DICT = {},
        data:  ATTRIBUTE_DICT = {},
    ) -> "JSONData":
        clone = self.copy()

        if not callable(json_data):
            if isinstance(json_data, str):
                try:
                    json.loads(json_data, **json_call_kwargs)
                except TypeError as exception:
                    raise HTMLStructuralError("JSONData data content is not a valid JSON string") from exception
                #endtry
            else:
                try:
                    json.dumps(json_data, **json_call_kwargs)
                except TypeError as exception:
                    raise HTMLStructuralError("JSONData data content is not JSON serializable") from exception
                #endtry
            #endif
        #endif

        clone.json_data = json_data
        clone.json_call_kwargs = json_call_kwargs
        clone.attributes = {**attrs}
        clone.data = {**data}

        return clone
    #enddef

    def render(
        self,
        indent: int = 0,
        global_context: CONTEXT = {},
        local_context: CONTEXT = {},
        whitespace_sensitive: bool = False,
    ) -> str:
        temp_data = self.json_data

        if callable(self.json_data):
            temp_data = self.json_data(global_context, local_context)
        #endif

        if isinstance(temp_data, str):
            # if the try block is successful then don't alter the string as it's already valid
            try:
                json.loads(temp_data, **self.json_call_kwargs)
            except TypeError as exception:
                raise HTMLStructuralError("JSONData data content is not a valid JSON string") from exception
            #endtry
        else:
            try:
                temp_data = json.dumps(temp_data, **self.json_call_kwargs)
            except TypeError as exception:
                raise HTMLStructuralError("JSONData data content is not JSON serializable") from exception
            #endtry
        #endif

        self.children = [temp_data]

        return super().render(
            global_context = global_context,
            local_context  = local_context,
            indent         = indent,
            whitespace_sensitive = whitespace_sensitive,
        )
    #enddef
#endclass


class Raw(HTMLElement):
    """Raw element, to be used when creating custom hand-made tags, will accept only text or functions as input."""

    def __init__(
        self,
        *args,
        text: List[Union[str, Callable[[CONTEXT, CONTEXT], str]]] = [],
        separator: str = " ",
        escape_content:       bool = False,
        whitespace_sensitive: bool = False,
        format_content:       bool = False,
    ) -> None:
        self.code = list(args) + text
        self.separator = separator
        self.escape_content = escape_content
        self.whitespace_sensitive = whitespace_sensitive
        self.format_content = format_content
    #enddef

    def __call__(
        self,
        *args,
        text: List[Union[str, Callable[[CONTEXT, CONTEXT], str]]] = [],
        separator: str = " ",
        escape_content:       bool = False,
        whitespace_sensitive: bool = False,
        format_content:       bool = False,
    ) -> "Raw":
        clone = self.copy()

        clone.code = list(args) + text
        clone.separator = separator
        clone.escape_content = escape_content
        clone.whitespace_sensitive = whitespace_sensitive
        clone.format_content = format_content

        return clone
    #enddef

    def render(
        self,
        indent: int = 0,
        global_context: CONTEXT = {},
        local_context: CONTEXT = {},
        whitespace_sensitive: bool = False,
    ) -> str:
        rendered_string = ""

        for index, item in enumerate(self.code):
            if isinstance(item, HTMLElement):
                # add raise on HTMLElement as it is callable and calling it would return a copy of itself
                raise HTMLStructuralError("Can't render HTMLElements inside Raw Element")
            #endif

            if callable(item):
                temp_data = item(global_context, local_context)

                if not isinstance(temp_data, str):
                    raise HTMLStructuralError(f"Non-string value returned by function in argument {index}")
                #endif

                rendered_string += temp_data
            else:
                rendered_string += str(item)
            #endif
        #endfor

        if self.format_content:
            try:
                rendered_string = rendered_string.format(
                    ctx_global = global_context,
                    ctx_local = local_context
                )
            except KeyError as exception:
                raise HTMLContextKeyError(f"Key '{exception.args[0]}' not found in global/local context")
            #endtry
        #endif

        if self.escape_content:
            rendered_string = escape_html_text(rendered_string)
        #endif

        return _render_item(
            item           = rendered_string,
            global_context = global_context,
            local_context  = local_context,
            indent         = indent,
            whitespace_sensitive = whitespace_sensitive,
        )
    #enddef
#endclass


class Page(HTMLElement):
    """Helper tag to create basic HTML document, is basically an html tag, only difference is that will prefix `<!DOCTYPE html>\\n` to its content"""

    tag_name_override = "html"

    def render(
        self,
        indent: int = 0,
        global_context: CONTEXT = {},
        local_context: CONTEXT = {},
        whitespace_sensitive: bool = False,
    ) -> str:
        return "<!DOCTYPE html>\n" + super().render(
            indent = indent,
            global_context = global_context,
            local_context = local_context,
            whitespace_sensitive = whitespace_sensitive,
        )
    #enddef
#enddef


class SelfClosingTag(HTMLElement):
    """Helper class to mark all self closing tags"""

    self_closing = True
#endclass


# ELEMENT LIST
#region ########

class tagA           (HTMLElement): pass
class tagABBR        (HTMLElement): pass
class tagADDRESS     (HTMLElement): pass
class tagARTICLE     (HTMLElement): pass
class tagASIDE       (HTMLElement): pass
class tagAUDIO       (HTMLElement): pass
class tagB           (HTMLElement): pass
class tagBDI         (HTMLElement): pass
class tagBDO         (HTMLElement): pass
class tagBLOCKQUOTE  (HTMLElement): pass
class tagBODY        (HTMLElement): pass
class tagBUTTON      (HTMLElement): pass
class tagCANVAS      (HTMLElement): pass
class tagCAPTION     (HTMLElement): pass
class tagCITE        (HTMLElement): pass
class tagCODE        (HTMLElement): pass
class tagCOLGROUP    (HTMLElement): pass
class tagDATA        (HTMLElement): pass
class tagDATALIST    (HTMLElement): pass
class tagDD          (HTMLElement): pass
class tagDEL         (HTMLElement): pass
class tagDETAILS     (HTMLElement): pass
class tagDFN         (HTMLElement): pass
class tagDIALOG      (HTMLElement): pass
class tagDIV         (HTMLElement): pass
class tagDL          (HTMLElement): pass
class tagDT          (HTMLElement): pass
class tagEM          (HTMLElement): pass
class tagFENCEDFRAME (HTMLElement): pass
class tagFIELDSET    (HTMLElement): pass
class tagFIGCAPTION  (HTMLElement): pass
class tagFIGURE      (HTMLElement): pass
class tagFOOTER      (HTMLElement): pass
class tagH1          (HTMLElement): pass
class tagH2          (HTMLElement): pass
class tagH3          (HTMLElement): pass
class tagH4          (HTMLElement): pass
class tagH5          (HTMLElement): pass
class tagH6          (HTMLElement): pass
class tagHEAD        (HTMLElement): pass
class tagHEADER      (HTMLElement): pass
class tagHGROUP      (HTMLElement): pass
class tagHTML        (HTMLElement): pass
class tagI           (HTMLElement): pass
class tagIFRAME      (HTMLElement): pass
class tagINS         (HTMLElement): pass
class tagKBD         (HTMLElement): pass
class tagLABEL       (HTMLElement): pass
class tagLEGEND      (HTMLElement): pass
class tagLI          (HTMLElement): pass
class tagMAIN        (HTMLElement): pass
class tagMAP         (HTMLElement): pass
class tagMARK        (HTMLElement): pass
class tagMENU        (HTMLElement): pass
class tagMETER       (HTMLElement): pass
class tagNAV         (HTMLElement): pass
class tagNOSCRIPT    (HTMLElement): pass
class tagOBJECT      (HTMLElement): pass
class tagOL          (HTMLElement): pass
class tagOPTGROUP    (HTMLElement): pass
class tagOPTION      (HTMLElement): pass
class tagOUTPUT      (HTMLElement): pass
class tagP           (HTMLElement): pass
class tagPICTURE     (HTMLElement): pass
class tagPORTAL      (HTMLElement): pass
class tagPRE         (HTMLElement): pass
class tagPROGRESS    (HTMLElement): pass
class tagQ           (HTMLElement): pass
class tagRP          (HTMLElement): pass
class tagRT          (HTMLElement): pass
class tagRUBY        (HTMLElement): pass
class tagS           (HTMLElement): pass
class tagSAMP        (HTMLElement): pass
class tagSEARCH      (HTMLElement): pass
class tagSECTION     (HTMLElement): pass
class tagSELECT      (HTMLElement): pass
class tagSLOT        (HTMLElement): pass
class tagSMALL       (HTMLElement): pass
class tagSPAN        (HTMLElement): pass
class tagSTRONG      (HTMLElement): pass
class tagSUB         (HTMLElement): pass
class tagSUMMARY     (HTMLElement): pass
class tagSUP         (HTMLElement): pass
class tagTABLE       (HTMLElement): pass
class tagTBODY       (HTMLElement): pass
class tagTD          (HTMLElement): pass
class tagTEMPLATE    (HTMLElement): pass
class tagTEXTAREA    (HTMLElement): pass
class tagTFOOT       (HTMLElement): pass
class tagTH          (HTMLElement): pass
class tagTHEAD       (HTMLElement): pass
class tagTIME        (HTMLElement): pass
class tagTITLE       (HTMLElement): pass
class tagTR          (HTMLElement): pass
class tagU           (HTMLElement): pass
class tagUL          (HTMLElement): pass
class tagVAR         (HTMLElement): pass
class tagVIDEO       (HTMLElement): pass

class tagSCRIPT(HTMLElement):
    default_attributes = {"type": "text/javascript"}
#endclass

class tagSTYLE(HTMLElement):
    default_attributes = {"type": "text/css"}
#endclass

class tagFORM(HTMLElement):
    default_attributes = {"method": "POST"}
#endclass

class tagAREA   (SelfClosingTag): pass
class tagBASE   (SelfClosingTag): pass
class tagBR     (SelfClosingTag): pass
class tagCOL    (SelfClosingTag): pass
class tagEMBED  (SelfClosingTag): pass
class tagHR     (SelfClosingTag): pass
class tagIMG    (SelfClosingTag): pass
class tagINPUT  (SelfClosingTag): pass
class tagLINK   (SelfClosingTag): pass
class tagMETA   (SelfClosingTag): pass
class tagSOURCE (SelfClosingTag): pass
class tagTRACK  (SelfClosingTag): pass
class tagWBR    (SelfClosingTag): pass

#endregion

__all__ = [
    "HTMLError",
    "escape_html_text",
    "encode_attribute_key",
    "encode_attribute_value",
    "encode_tag_attributes",
    "global_var",
    "local_var",

    "SelfClosingTag",
    "HTMLElement",
    "JSONData",
    "Raw",
    "Page",

    "tagA",
    "tagABBR",
    "tagADDRESS",
    "tagARTICLE",
    "tagASIDE",
    "tagAUDIO",
    "tagB",
    "tagBDI",
    "tagBDO",
    "tagBLOCKQUOTE",
    "tagBODY",
    "tagBUTTON",
    "tagCANVAS",
    "tagCAPTION",
    "tagCITE",
    "tagCODE",
    "tagCOLGROUP",
    "tagDATA",
    "tagDATALIST",
    "tagDD",
    "tagDEL",
    "tagDETAILS",
    "tagDFN",
    "tagDIALOG",
    "tagDIV",
    "tagDL",
    "tagDT",
    "tagEM",
    "tagFENCEDFRAME",
    "tagFIELDSET",
    "tagFIGCAPTION",
    "tagFIGURE",
    "tagFOOTER",
    "tagH1",
    "tagH2",
    "tagH3",
    "tagH4",
    "tagH5",
    "tagH6",
    "tagHEAD",
    "tagHEADER",
    "tagHGROUP",
    "tagHTML",
    "tagI",
    "tagIFRAME",
    "tagINS",
    "tagKBD",
    "tagLABEL",
    "tagLEGEND",
    "tagLI",
    "tagMAIN",
    "tagMAP",
    "tagMARK",
    "tagMENU",
    "tagMETER",
    "tagNAV",
    "tagNOSCRIPT",
    "tagOBJECT",
    "tagOL",
    "tagOPTGROUP",
    "tagOPTION",
    "tagOUTPUT",
    "tagP",
    "tagPICTURE",
    "tagPORTAL",
    "tagPRE",
    "tagPROGRESS",
    "tagQ",
    "tagRP",
    "tagRT",
    "tagRUBY",
    "tagS",
    "tagSAMP",
    "tagSEARCH",
    "tagSECTION",
    "tagSELECT",
    "tagSLOT",
    "tagSMALL",
    "tagSPAN",
    "tagSTRONG",
    "tagSUB",
    "tagSUMMARY",
    "tagSUP",
    "tagTABLE",
    "tagTBODY",
    "tagTD",
    "tagTEMPLATE",
    "tagTEXTAREA",
    "tagTFOOT",
    "tagTH",
    "tagTHEAD",
    "tagTIME",
    "tagTITLE",
    "tagTR",
    "tagU",
    "tagUL",
    "tagVAR",
    "tagVIDEO",
    "tagSCRIPT",
    "tagSTYLE",
    "tagFORM",
    "tagAREA",
    "tagBASE",
    "tagBR",
    "tagCOL",
    "tagEMBED",
    "tagHR",
    "tagIMG",
    "tagINPUT",
    "tagLINK",
    "tagMETA",
    "tagSOURCE",
    "tagTRACK",
    "tagWBR",
]
