from flask import Blueprint

# Import all the view function
from app.modules.sales.order import submit_order, getOrders, getTasks, jobDone

# Define the blueprint name
module = Blueprint('sales', __name__)


module.add_url_rule('/sales/submit',
                    view_func=submit_order, methods=['POST'])
module.add_url_rule('/sales/getOrders',
                    view_func=getOrders, methods=['GET'])
module.add_url_rule('/sales/getTasks',
                    view_func=getTasks, methods=['GET'])
module.add_url_rule('/sales/removeTasks',
                    view_func=jobDone, methods=['POST'])
