import re  # noqa: INP001
import sys

MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'


def main() -> int:
    module_name = '{{ cookiecutter.module_name }}'
    if not re.match(MODULE_REGEX, module_name):
        print(f'ERROR: {module_name} is not a valid Python module name!', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
