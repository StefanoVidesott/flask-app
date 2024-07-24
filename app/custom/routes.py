from flask import Blueprint
from custom.models import User
from custom.handlers import *

app = Blueprint('app', __name__)

@app.route('/')
def index():
    context = {
    }
    page = TestPage()._compile(global_context=context)
    page_code = "\n".join(r.tag for r in page._style_requirements) + "\n\n" + "\n".join(r.tag for r in page._script_requirements) + "\n\n" + page._code
    return page_code

#enddef

@app.route('/users')
def users():
    _template = "<h1>User list</h1>"
    _template += "<ul>"
    for user in User.get_all():
        _template += f"<li>{user.username}</li>"
    #endfor
    _template += "</ul>"
    return _template
#enddef
