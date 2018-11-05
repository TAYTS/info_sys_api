from flask import Blueprint

# Import all the view function
from app.modules.inventory.manage_item import add_item, remove_items, edit_item, uploadItemImg
from app.modules.inventory.item_info import getItemInfo, listItem

# Define the blueprint name
module = Blueprint('inventory', __name__)


module.add_url_rule('/inventory/add',
                    view_func=add_item, methods=['POST'])
module.add_url_rule('/inventory/remove',
                    view_func=remove_items, methods=['POST'])
module.add_url_rule('/inventory/update',
                    view_func=edit_item, methods=['POST'])
module.add_url_rule('/inventory/uploadImg',
                    view_func=uploadItemImg, methods=['POST'])
module.add_url_rule('/inventory/getItem/<vendor_id>/<item_name>',
                    view_func=getItemInfo, methods=['GET'])
module.add_url_rule('/inventory/listItem/<vendor_id>',
                    view_func=listItem, methods=['GET'])
