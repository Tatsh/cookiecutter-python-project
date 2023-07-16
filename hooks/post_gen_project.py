# pylint: disable=using-constant-test,unhashable-member,undefined-variable
from pathlib import Path
import re
import subprocess as sp
import sys

MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'
REPO_URI = 'git@github.com:{{ cookiecutter.github_username }}/{{ cookiecutter.directory_name }}.git'
GIT_COMMAND_ARGS = (('init',), ('add', '.'), ('commit', '-m', 'Start of project', '--signoff'),
                    ('remote', 'add', 'origin', REPO_URI))

YARN_COMMAND_ARGS = (('add', '-D', 'cspell', 'markdownlint-cli2', 'prettier-plugin-sort-json',
                      'prettier-plugin-toml'), ('format',))


def main() -> int:
    module_name = '{{ cookiecutter.module_name }}'
    if not re.match(MODULE_REGEX, module_name):
        print(f'ERROR: {module_name} is not a valid Python module name!', file=sys.stderr)
        return 1
    packages: tuple[str, ...] = ('loguru',)
    dev_packages: tuple[str, ...] = ('mypy', 'pylint', 'pylint-quotes', 'rope', 'toml', 'yapf')
    docs_packages: tuple[str, ...] = ('docutils', 'esbonio', 'sphinx', 'toml')
    test_packages: tuple[str, ...] = ('coveralls', 'mock', 'pytest', 'pytest-mock')
    if {{cookiecutter.want_main}}:  # type: ignore[name-defined]
        packages += ('click>=8.1.3,!=8.1.4',)
        docs_packages += ('sphinx-click',)
    else:
        main_py = Path(module_name) / 'main.py'
        main_py.unlink()
    if {{cookiecutter.want_requests}}:  # type: ignore[name-defined]
        dev_packages += ('types-requests',)
        packages += ('requests',)
        test_packages += ('requests-mock',)
    for args in (packages, ('-G', 'dev') + dev_packages, ('-G', 'docs') + docs_packages,
                 ('-G', 'tests') + test_packages):
        sp.run(('poetry', 'add') + args, check=True)
    sp.run(('poetry', 'install', '--with=dev', '--with=docs', '--with=tests'), check=True)
    for args in YARN_COMMAND_ARGS:
        sp.run(('yarn',) + args, check=True)
    for args in GIT_COMMAND_ARGS:
        sp.run(('git',) + args, check=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
