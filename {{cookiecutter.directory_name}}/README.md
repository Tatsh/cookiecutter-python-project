# {{cookiecutter.human_project_name}}

[![QA](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.directory_name}}/actions/workflows/qa.yml/badge.svg)](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.directory_name}}/actions/workflows/qa.yml)
[![Tests](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.directory_name}}/actions/workflows/tests.yml/badge.svg)](https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.directory_name}}/actions/workflows/tests.yml)
[![Coverage Status](https://coveralls.io/repos/github/{{cookiecutter.github_username}}/{{cookiecutter.directory_name}}/badge.svg?branch=master)](https://coveralls.io/github/{{cookiecutter.github_username}}/{{cookiecutter.directory_name}}?branch=master)
[![Documentation Status](https://readthedocs.org/projects/{{cookiecutter.directory_name}}/badge/?version=latest)](https://{{cookiecutter.directory_name}}.readthedocs.io/en/latest/?badge=latest)
![PyPI - Version](https://img.shields.io/pypi/v/{{cookiecutter.directory_name}})
![GitHub tag (with filter)](https://img.shields.io/github/v/tag/{{cookiecutter.github_username}}/{{cookiecutter.directory_name}})
![GitHub](https://img.shields.io/github/license/{{cookiecutter.github_username}}/{{cookiecutter.directory_name}})
![GitHub commits since latest release (by SemVer including pre-releases)](https://img.shields.io/github/commits-since/{{cookiecutter.github_username}}/{{cookiecutter.directory_name}}/v0.0.1/master)

{{cookiecutter.readme.description}}

## Installation

```shell
pip install {{cookiecutter.directory_name}}
```{% if cookiecutter.want_main %}

## Command line usage

```shell
{{cookiecutter.main_cli_name}}
```
{% endif %}
