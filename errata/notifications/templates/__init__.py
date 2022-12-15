import os

import jinja2


# Set templates home folder.
_TEMPLATES_DIR = os.path.dirname(__file__)

# Set codegen template engine.
_CODEGEN_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(_TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(),
    trim_blocks=True
)

# Set template loading function.
get_template = _CODEGEN_ENV.get_template
