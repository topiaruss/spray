from jinja2 import Environment
from spray import templating

# To setup custom filters, we need to establish an environment
env = Environment()

# Add the custom filters
env.filters['urlformat'] = templating.urlformat
env.filters['buttonformat'] = templating.buttonformat
