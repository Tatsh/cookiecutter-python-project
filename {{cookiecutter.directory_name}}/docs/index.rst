{{ cookiecutter.human_project_name }}
=====================================

{% if cookiecutter.want_main %}
Commands
--------

.. click:: {{ cookiecutter.module_name }}.main:main
  :prog: {{ cookiecutter.main_cli_name }}
  :nested: full
{% endif %}

Library
-------
.. automodule:: {{ cookiecutter.module_name }}.name_of_module
   :members:

Submodule
---------
.. automodule:: {{ cookiecutter.module_name }}.submodule
   :members:

Typing
------
.. automodule:: {{ cookiecutter.module_name }}.typing
   :members:

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
