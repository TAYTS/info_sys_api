from flask import Blueprint

# Import all the view function
from app.modules.admin.register import register_vendor, register_user

# Define the blueprint name
module = Blueprint('admin', __name__)


module.add_url_rule('/admin/register_vendor', view_func=register_vendor, methods=['POST'])
module.add_url_rule('/admin/register_user', view_func=register_user, methods=['POST'])
