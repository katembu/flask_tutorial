# filters.py

import jinja2
import flask

blueprint = flask.Blueprint('filters', __name__)


# using the method
@jinja2.contextfilter
def filter2(context, value):
    return 2

blueprint.add_app_template_filter(filter2)
