from pathlib import Path
import re
import subprocess as sp
import sys
from typing import cast

MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'
REPO_URI = 'git@github.com:{{ cookiecutter.github_username }}/{{ cookiecutter.directory_name }}.git'
GIT_COMMAND_ARGS = (('init',), ('add', '.'), ('commit', '-m', 'Start of project', '--signoff'),
                    ('remote', 'add', 'origin', REPO_URI))


def main() -> int:
    module_name = '{{ cookiecutter.module_name }}'
    if not re.match(MODULE_REGEX, module_name):
        print(f'ERROR: {module_name} is not a valid Python module name!', file=sys.stderr)
        return 1
    packages = cast(tuple[str, ...], tuple())
    dev_packages: tuple[str, ...] = ('commitizen', 'mypy', 'rope', 'ruff', 'yapf')
    docs_packages: tuple[str, ...] = ('doc8', 'docutils', 'esbonio', 'restructuredtext-lint',
                                      'sphinx', 'tomlkit')
    test_packages: tuple[str, ...] = ('coveralls', 'mock', 'pytest', 'pytest-cov', 'pytest-mock')
    if {{cookiecutter.want_main}}:  # type: ignore[name-defined] # noqa: F821
        packages += ('click>=8.1.3,!=8.1.4', 'loguru')
        docs_packages += ('sphinx-click',)
    else:
        main_py = Path(module_name) / 'main.py'
        main_py.unlink()
    if {{cookiecutter.want_requests}}:  # type: ignore[name-defined] # noqa: F821
        dev_packages += ('types-requests',)
        packages += ('requests',)
        test_packages += ('requests-mock',)
    for args in (packages, ('-G', 'dev') + tuple(sorted(dev_packages)),
                 ('-G', 'docs') + tuple(sorted(docs_packages)),
                 ('-G', 'tests') + tuple(sorted(test_packages))):
        if not args:
            continue
        sp.run(('poetry', 'add') + args, check=True)
    sp.run(('poetry', 'install', '--with=dev,docs,tests', '--all-extras'), check=True)
    sp.run(('yarn',), check=True)
    sp.run(('yarn', 'format'), check=True)
    with open('.vscode/dictionary.txt') as f:
        words = f.readlines()
    words.append('{{ cookiecutter.module_name }}\n')
    words.append('{{cookiecutter.directory_name}}\n')
    words.sort()
    with open('.vscode/dictionary.txt', 'w') as f:
        f.writelines(words)
    sp.run(('yarn', 'clean-dict'), check=True)
    for args in GIT_COMMAND_ARGS:
        sp.run(('git',) + args, check=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
