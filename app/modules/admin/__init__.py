from flask import Blueprint

# Import all the view function
from app.modules.admin.register import register, login, logout, getQRcode, uploadProfileImg
from app.modules.admin.getInfo import getVendor

# Define the blueprint name
module = Blueprint('admin', __name__)


module.add_url_rule('/admin/register',
                    view_func=register, methods=['POST'])
module.add_url_rule('/admin/login',
                    view_func=login, methods=['POST'])
module.add_url_rule('/admin/logout',
                    view_func=logout, methods=['GET'])
module.add_url_rule('/admin/getQRcode',
                    view_func=getQRcode, methods=['GET'])
module.add_url_rule('/admin/uploadProfileImg',
                    view_func=uploadProfileImg, methods=['POST'])
module.add_url_rule('/admin/getVendor/<vendor_id>',
                    view_func=getVendor, methods=['GET'])
