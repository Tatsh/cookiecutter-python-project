from pathlib import Path
import re
import subprocess as sp
import sys

MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'
REPO_URI = 'git@github.com:{{ cookiecutter.github_username }}/{{ cookiecutter.directory_name }}.git'

module_name = '{{ cookiecutter.module_name }}'
want_main = {{cookiecutter.want_main}}
packages = ('loguru', )
dev_packages = ('mypy', 'pylint', 'pylint-quotes', 'rope', 'toml', 'yapf')
docs_packages = ('sphinx', )
test_packages = ('coveralls', 'mock', 'pytest', 'pytest-mock')
git_command_args = (('init', ), ('add', '.'),
                    ('commit', '-m', 'Start of project',
                     '--signoff'), ('remote', 'add', 'origin', REPO_URI))
yarn_command_args = (('add', '-D', 'cspell', 'prettier', 'prettier-plugin-ini',
                      'prettier-plugin-toml'), ('format', ))

if not re.match(MODULE_REGEX, module_name):
    print(f'ERROR: {module_name} is not a valid Python module name!',
          file=sys.stderr)
    sys.exit(1)
if want_main:
    packages += ('click', )
else:
    main_py = Path(module_name) / 'main.py'
    main_py.unlink()
if {{cookiecutter.want_requests}}:
    packages += ('requests', )
    dev_packages += ('types-requests', )
    test_packages += ('requests-mock', )
poetry_add_command_args = (packages, ('-G', 'dev') + dev_packages,
                           ('-G', 'docs') + docs_packages,
                           ('-G', 'test') + test_packages)
for args in poetry_add_command_args:
    sp.run(('poetry', 'add') + args, check=True)
sp.run(('poetry', 'install', '--with=dev', '--with=docs', '--with=test'), check=True)
for args in yarn_command_args:
    sp.run(('yarn', ) + args, check=True)
for args in git_command_args:
    sp.run(('git', ) + args, check=True)
