"""Updates the version based on git tag."""
import re
import subprocess


VERSION = subprocess.check_output(
    'git describe --abbrev=0'.split(),
    text=True
).rstrip()


with open('pupyl.py') as MAIN_MODULE, \
        open('setup.py') as SETUP_MODULE:
    FILE_MODULE = MAIN_MODULE.read()
    SETUP_FILE = SETUP_MODULE.read()

    NEW_VERSION = f"__version__ = '{VERSION}'"

    MAIN_MODULE_MODIFIED = re.sub(
        r'^.*\b(\w*__version__\w*)\b.*',
        NEW_VERSION,
        FILE_MODULE,
        flags=re.MULTILINE
    )

    SETUP_MODULE_MODIFIED = re.sub(
        r'^.*\b(\w*version\w*)\b.*',
        f'    version="{VERSION[1:].replace("rc", "rc0")}",',
        SETUP_FILE,
        flags=re.MULTILINE
    )


with open('pupyl.py', 'w') as MAIN_MODULE, \
        open('setup.py', 'w') as SETUP_MODULE:
    MAIN_MODULE.write(MAIN_MODULE_MODIFIED)
    SETUP_MODULE.write(SETUP_MODULE_MODIFIED)
