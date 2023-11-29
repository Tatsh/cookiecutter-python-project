#!/usr/bin/env python
from pathlib import Path
from typing import Any
import json
import re

from deepdiff import DeepDiff
import click
import toml

__all__ = ('main',)

# Errors
E_FILE_NOT_FOUND = 'E0001: File not found: {}'
E_DEPRECATED_SETTINGS_FILE = 'E0002: File should not exist: {}. Move these settings to {}'
E_LIST_MISSING_VALUE = 'E0003: {}: {} missing "{}"'
E_UNEXPECTED_EMPTY = 'E0004: {}: {} is empty'
E_CANNOT_PARSE_JSON_FILE = ('E0005: {}: failed to parse JSON. Comments in JSON files are not '
                            'allowed.')
E_UNEXPECTED_EMPTY_JSON = 'E0006: {}: Unexpected empty JSON file.'
E_DOCS_CONF_PY_MISSING_LINE = 'E0007: docs/conf.py: expected to have line "{}"'
E_DOCS_CONF_PY_MISSING_LINE_CONTAINING = ('E0008: docs/conf.py: expected to have line containing '
                                          '"{}"')
E_UNEXPECTED_VALUE = 'E0009: {}: Expected "{}" to be `{}`'
E_CANNOT_PARSE_TOML_FILE = 'E0010: {}: failed to parse TOML.'
E_UNEXPECTED_EMPTY_TOML = 'E0011: {}: Unexpected empty TOML file.'
E_KEY_NOT_PRESENT_OR_INVALID = 'E0011: {}: "{}" key is not present or is invalid.'
E_PYPROJECT_PACKAGE_JSON_VERSION_MISMATCH = ('E0012: package.json version and pyproject.toml '
                                             'version differ.')
E_KEY_NOT_PRESENT = 'E0013: {}: "{}" key is not present.'
E_MIGRATE_TO_RUFF = 'E0014: Pylint settings detected. Migrate to Ruff.'
E_UNEXPECTED_KEY = 'E0015: {}: "{}" key should not be present.'

EXPECTED_FILES = ('.github/workflows/close-inactive.yml', '.github/workflows/qa.yml', '.gitignore',
                  '.markdownlint.json', '.prettierignore', '.readthedocs.yaml',
                  '.rtfd-requirements.txt', '.vscode/cspell.json', '.vscode/dictionary.txt',
                  '.vscode/extensions.json', '.vscode/launch.json', '.vscode/settings.json',
                  'CHANGELOG.md', 'LICENSE.txt', 'README.md', '_config.yml', 'docs/conf.py',
                  'docs/index.rst', 'package.json', 'poetry.lock', 'pyproject.toml',
                  'tests/conftest.py', 'yarn.lock')
UNEXPECTED_FILES = {
    '.prettierrc': 'package.json',
    '.style.yapf': 'pyproject.toml',
    'mypy.ini': 'pyproject.toml'
}
CSPELL_EXPECTED_KEYS = ('dictionaryDefinitions', 'enableGlobDot', 'enabledLanguageIds',
                        'ignorePaths', 'languageSettings')
CSPELL_EXPECTED_IGNORE_PATHS = ('*.log', '.coverage', '.directory', '.git', '.mypy_cache',
                                '.vscode/extensions.json', '__pycache__', '_build/**', 'build/**',
                                'dist/**', 'htmlcov/**')
VSCODE_SETTINGS_JSON_EXPECTED_KEY_VALUES = {
    '[python]': {
        'editor.defaultFormatter': 'eeyore.yapf',
        'editor.tabSize': 4
    },
    'cSpell.enabled': True,
    'editor.defaultFormatter': 'esbenp.prettier-vscode',
    'editor.formatOnPaste': True,
    'editor.formatOnSave': True,
    'editor.formatOnType': True,
    'editor.inlayHints.enabled': 'offUnlessPressed',
    'editor.insertSpaces': True,
    'editor.rulers': [100],
    'editor.tabSize': 2,
    'editor.wordWrapColumn': 100,
    'eslint.lintTask.enable': True,
    'files.insertFinalNewline': True,
    'files.trimFinalNewlines': True,
    'files.trimTrailingWhitespace': True,
    'python.analysis.autoImportCompletions': True,
    'python.analysis.completeFunctionParens': True,
    'python.analysis.importFormat': 'relative',
    'python.analysis.indexing': True,
    'python.analysis.inlayHints.functionReturnTypes': True,
    'python.analysis.inlayHints.pytestParameters': True,
    'python.analysis.inlayHints.variableTypes': True,
    'python.analysis.packageIndexDepths': [{
        'depth': 100,
        'name': ''
    }],
    'python.analysis.stubPath': '.stubs',
    'python.analysis.typeCheckingMode': 'strict',
    'python.languageServer': 'Pylance',
    'yaml.format.printWidth': 100,
}
VSCODE_SETTINGS_JSON_UNEXPECTED_KEYS = {
    'python.formatting.provider', 'python.linting.flake8Enabled', 'python.linting.pylintEnabled'
}
DOCS_CONF_PY_EXPECTED_LINES = (
    '^import toml', "with open(f'{dirname(__file__)}/../pyproject.toml') as f:",
    '^copyright: Final[str] = str(datetime.now().year)',
    "^project: Final[str] = PROJECT['tool']['poetry']['name']",
    "^version: Final[str] = PROJECT['tool']['poetry']['version']",
    "^release: Final[str] = f'v{version}'",
    "['sphinx_click'] if PROJECT['tool']['poetry'].get('scripts') else [])")
MARKDOWN_JSON_EXPECTED_KEY_VALUES = {
    'default': True,
    'line-length': {
        'code_blocks': False,
        'line_length': 100
    }
}
PACKAGE_JSON_EXPECTED_KEYS = ('contributors', 'devDependencies', 'license', 'name', 'prettier',
                              'repository', 'scripts', 'version')
PACKAGE_JSON_EXPECTED_SCRIPT_VALUES = {
    'check-formatting':
        "yarn prettier -c . && poetry run yapf -prd . && "
        "markdownlint-cli2 '**/*.md' '#node_modules'",
    'check-spelling': 'cspell --no-progress .',
    'clean-dict':
        "r=(); while IFS=$\\n read -r w; do ! rg --no-config -qi. -g "
        "'!.vscode/dictionary.txt' -m 1 \"$w\" . && r+=(\"$w\"); done < ./.vscode/dictionary.txt; "
        "j=$(printf \"|%s\" \"${r[@]}\"); j=\"^(${j:1})$\"; grep -Ev \"${j}\" "
        "./.vscode/dictionary.txt > new && mv new ./.vscode/dictionary.txt",
    'fix-pluggy': "touch \"$(poetry run python -c 'import inspect, os, pluggy; "
                  "print(os.path.dirname(inspect.getabsfile(pluggy)))')/py.typed\"",
    'format': "yarn prettier -w . && poetry run yapf -pri . && "
              "markdownlint-cli2 --fix '**/*.md' '#node_modules'",
    'mypy': 'yarn fix-pluggy && poetry run mypy .',
    'qa': 'yarn mypy && yarn ruff && yarn check-spelling && yarn check-formatting',
    'ruff': 'poetry run ruff .',
    'test': 'poetry run pytest'
}
PACKAGE_JSON_EXPECTED_PRETTIER_PLUGIN_VALUES = {
    '@prettier/plugin-xml', 'prettier-plugin-ini', 'prettier-plugin-sort-json',
    'prettier-plugin-toml'
}
PYPROJECT_EXPECTED_POETRY_KEYS = ('authors', 'classifiers', 'description', 'documentation',
                                  'homepage', 'keywords', 'license', 'name', 'packages', 'readme',
                                  'version')
PYPROJECT_EXPECTED_TOOL_KEYS = ('poetry', 'mypy', 'pytest', 'ruff', 'yapf')


def log_key_not_present_expected_value(filename: str, key: str, value: str) -> None:
    click.echo(f'{E_KEY_NOT_PRESENT.format(filename, key)} Should be: `{value}`')


def read_json_file(workdir: Path, filepath: str) -> Any:
    json_file = workdir.joinpath(filepath)
    data = None
    if (exists := json_file.exists()):
        try:
            data = json.loads(json_file.read_text())
        except json.JSONDecodeError:
            click.echo(E_CANNOT_PARSE_JSON_FILE.format(json_file))
    if exists and not data:
        click.echo(E_UNEXPECTED_EMPTY_JSON.format(json_file))
    return data


def read_toml_file(workdir: Path, filepath: str) -> Any:
    toml_file = workdir.joinpath(filepath)
    data = None
    if (exists := toml_file.exists()):
        try:
            data = toml.loads(toml_file.read_text())
        except toml.TomlDecodeError:
            click.echo(E_CANNOT_PARSE_TOML_FILE.format(toml_file))
    if exists and not data:
        click.echo(E_UNEXPECTED_EMPTY_TOML.format(toml_file))
    return data


def check_expected_files(workdir: Path) -> None:
    for filename in EXPECTED_FILES:
        if not workdir.joinpath(filename).exists():
            click.echo(E_FILE_NOT_FOUND.format(filename))
    for filename, new_location in UNEXPECTED_FILES.items():
        if workdir.joinpath(filename).exists():
            click.echo(E_DEPRECATED_SETTINGS_FILE.format(filename, new_location))


def check_cspell_json(workdir: Path) -> None:
    if (data := read_json_file(workdir, '.vscode/cspell.json')):
        for key in CSPELL_EXPECTED_KEYS:
            if key not in data:
                click.echo(E_KEY_NOT_PRESENT.format('.vscode/cspell.json', key))
        if 'enableGlobDot' in data and not data['enableGlobDot']:
            click.echo(E_KEY_NOT_PRESENT_OR_INVALID.format('.vscode/cspell.json', 'enableGlobDot'))
        if 'dictionaryDefinitions' in data:
            if data['dictionaryDefinitions'][0]['name'] != 'main':
                click.echo(
                    E_UNEXPECTED_VALUE.format('.vscode/cspell.json',
                                              'dictionaryDefinitions[0].name', 'main'))
            if data['dictionaryDefinitions'][0]['path'] != 'dictionary.txt':
                click.echo(
                    E_UNEXPECTED_VALUE.format('.vscode/cspell.json',
                                              'dictionaryDefinitions[0].path', 'dictionary.txt'))
        if 'ignorePaths' in data:
            for item in CSPELL_EXPECTED_IGNORE_PATHS:
                if item not in data['ignorePaths']:
                    click.echo(
                        E_LIST_MISSING_VALUE.format('.vscode/cspell.json', 'ignorePaths', item))
        if 'enabledLanguageIds' in data and not data['enabledLanguageIds']:
            click.echo(E_UNEXPECTED_EMPTY)
        # TODO Check languages in enabledLanguageIds
        if 'languageSettings' in data:
            if not data['languageSettings']:
                click.echo(E_UNEXPECTED_EMPTY.format('.vscode/cspell.json', 'languageSettings'))
            if 'dictionaries' not in data['languageSettings'][0]:
                click.echo(E_KEY_NOT_PRESENT.format('.vscode/cspell.json', 'dictionaries'))
            elif 'main' not in data['languageSettings'][0]['dictionaries']:
                click.echo(
                    E_LIST_MISSING_VALUE.format('.vscode/cspell.json',
                                                'languageSettings[0].dictionaries', 'main'))
            if 'languageId' not in data['languageSettings'][0]:
                click.echo(E_KEY_NOT_PRESENT.format('.vscode/cspell.json', 'languageId'))
            elif data['languageSettings'][0]['languageId'] != '*':
                click.echo(
                    E_UNEXPECTED_VALUE.format('.vscode/cspell.json',
                                              'languageSettings[0].languageId', '*'))


def check_vscode_settings_json(workdir: Path) -> None:
    if (data := read_json_file(workdir, '.vscode/settings.json')):
        for key, value in VSCODE_SETTINGS_JSON_EXPECTED_KEY_VALUES.items():
            if key not in data:
                log_key_not_present_expected_value('.vscode/settings.json', key, json.dumps(value))
            elif DeepDiff(data[key], value):
                click.echo(
                    E_UNEXPECTED_VALUE.format('.vscode/settings.json', key, json.dumps(value)))
        for key in VSCODE_SETTINGS_JSON_UNEXPECTED_KEYS:
            if key in data:
                click.echo(E_UNEXPECTED_KEY.format('.vscode/settings.json', key))


def check_docs_conf_py(workdir: Path) -> None:
    docs_conf_py = workdir.joinpath('docs/conf.py')
    if docs_conf_py.exists():
        contents = docs_conf_py.read_text().splitlines()
        for line in DOCS_CONF_PY_EXPECTED_LINES:
            if line.startswith('^') and not any(x.startswith(line[1:]) for x in contents):
                click.echo(E_DOCS_CONF_PY_MISSING_LINE.format(line[1:]))
            elif not any(line[1:] in x for x in contents):
                click.echo(E_DOCS_CONF_PY_MISSING_LINE_CONTAINING.format(line))


def check_markdownlint_json(workdir: Path) -> None:
    if (data := read_json_file(workdir, '.markdownlint.json')):
        for key, value in MARKDOWN_JSON_EXPECTED_KEY_VALUES.items():
            if key not in data:
                log_key_not_present_expected_value('.markdownlint.json', key, json.dumps(value))
            elif DeepDiff(data[key], value):
                click.echo(E_UNEXPECTED_VALUE.format('.markdownlint.json', key, value))


def check_package_json(workdir: Path, no_pluggy: bool = False) -> None:
    package_json_version = None
    if (data := read_json_file(workdir, 'package.json')):
        for key in PACKAGE_JSON_EXPECTED_KEYS:
            if key not in data:
                click.echo(E_KEY_NOT_PRESENT.format('package.json', key))
        if 'version' in data:
            package_json_version = data['version']
        if 'scripts' in data:
            for key, value in PACKAGE_JSON_EXPECTED_SCRIPT_VALUES.items():
                new_value = value
                if no_pluggy:
                    if key == 'fix-pluggy':
                        continue
                    if key == 'mypy':
                        new_value = re.sub(r'^yarn fix-pluggy && ', '', value)
                if key not in data['scripts']:
                    log_key_not_present_expected_value('package.json', f'scripts.{key}',
                                                       json.dumps(new_value))
                elif data['scripts'][key] != new_value:
                    click.echo(
                        E_UNEXPECTED_VALUE.format('package.json', f'scripts.{key}',
                                                  json.dumps(new_value)))
        try:
            for plugin in PACKAGE_JSON_EXPECTED_PRETTIER_PLUGIN_VALUES:
                if plugin not in data['prettier']['plugins']:
                    click.echo(
                        E_LIST_MISSING_VALUE.format('package.json', 'prettier.plugins', plugin))
        except KeyError:
            click.echo(E_KEY_NOT_PRESENT.format('prettier.plugins'), err=True)
        if ((data := read_toml_file(workdir, 'pyproject.toml')) and 'tool' in data
                and 'poetry' in data['tool']):
            poetry = data['tool']['poetry']
            if ('version' in poetry and poetry['version'] is not None
                    and package_json_version is not None
                    and package_json_version != poetry['version']):
                click.echo(E_PYPROJECT_PACKAGE_JSON_VERSION_MISMATCH)


def check_pyproject_toml(workdir: Path) -> None:
    if (data := read_toml_file(workdir, 'pyproject.toml')):
        if 'tool' in data:
            tool = data['tool']
            for key in PYPROJECT_EXPECTED_TOOL_KEYS:
                if key not in tool:
                    click.echo(E_KEY_NOT_PRESENT.format('pyproject.toml', f'tool.{key}'))
            if 'poetry' in tool:
                poetry = tool['poetry']
                for key in PYPROJECT_EXPECTED_POETRY_KEYS:
                    if key not in poetry:
                        click.echo(E_KEY_NOT_PRESENT.format('pyproject.toml', f'tool.poetry.{key}'))
        else:
            click.echo(E_KEY_NOT_PRESENT_OR_INVALID.format('pyproject.toml', 'tool'))


def check_pylint(workdir: Path) -> None:
    if (workdir / '.pylintrc').exists():
        click.echo(E_MIGRATE_TO_RUFF)
        return
    if (data := read_toml_file(workdir, 'pyproject.toml')):
        try:
            if 'pylint' in data['tool']:
                click.echo(E_MIGRATE_TO_RUFF)
        except KeyError:
            pass


@click.command()
@click.argument('workdir',
                default='.',
                type=click.Path(exists=True, file_okay=False, resolve_path=True, path_type=Path))
@click.option('-P', '--no-pluggy', default=False, is_flag=True)
def main(workdir: Path, no_pluggy: bool) -> None:
    check_expected_files(workdir)
    check_cspell_json(workdir)
    check_vscode_settings_json(workdir)
    check_markdownlint_json(workdir)
    check_package_json(workdir, no_pluggy=no_pluggy)
    check_pyproject_toml(workdir)
    check_pylint(workdir)


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
