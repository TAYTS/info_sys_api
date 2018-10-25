from flask import Blueprint

# Import all the view function
from app.modules.core.views import hello

# Define the blueprint name
module = Blueprint('core', __name__)


module.add_url_rule('/', view_func=hello)
