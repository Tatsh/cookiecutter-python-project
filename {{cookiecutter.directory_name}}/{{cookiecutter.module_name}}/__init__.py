"""{{cookiecutter.module_name}}"""{% if cookiecutter.want_main != 'False' %}
from .main import main

__all__ = ('main',)
{% endif %}
