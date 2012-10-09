from jinja2 import Environment
from spray import templating

# To setup custom filters, we need to establish an environment
env = Environment()

# Add the custom filters
env.filters['urlformat'] = templating.urlformat
env.filters['buttonformat'] = templating.buttonformat
env.filters['featuretext'] = templating.featuretext

# Plaintext alternatives
ptenv = Environment()

# Add the custom filters
ptenv.filters['urlformat'] = templating.urlformat_to_plain
ptenv.filters['buttonformat'] = templating.buttonformat_to_plain
ptenv.filters['featuretext'] = templating.featuretext_to_plain
