"""
Entrypoint module, in case you use `python -m nibetaseries`.


Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""

if __name__ == "__main__":
    raise RuntimeError("NiBetaSeries/cli/run.py should not be run directly;\n"
                       "Please `pip install` NiBetaSeries and use the `nibs` command")
