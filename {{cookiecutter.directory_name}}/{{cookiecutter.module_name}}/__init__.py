"""{{cookiecutter.module_name}}"""{% if cookiecutter.want_main != 'False' %}
from .main import main

__all__ = ('main',)
{% endif %}__version__ = '0.0.1'
