import os
import tempfile

# We want DocHub to run in DEBUG=True by default so a user cloning the repo
# can run the app without any configuration and still have some DEBUG info.
# However, we don't want to run the tests in DEBUG=True mode, so we override
if "DEBUG" not in os.environ:
    os.environ["DEBUG"] = "False"

    # We do not want to run in DEBUG=False without an explicit SECRET_KEY
    # (it's too risky to forget setting it in production)
    # But we allow the exception in the tests (and only in the tests)
    if "SECRET_KEY" not in os.environ:
        os.environ["SECRET_KEY"] = "this-is-a-secret-key-to-be-used-in-tests"

from www.settings import *

CELERY_ALWAYS_EAGER = True  # Skip the Celery daemon

# all tasks will be executed locally by blocking until the task returns.
# apply_async() and Task.delay() will return an EagerResult instance,
# which emulates the API and behavior of AsyncResult,
# except the result is already evaluated.

# Required if we don't want to build the collected static files upfront
# (which is not possible desirable to do before each test run)
WHITENOISE_MANIFEST_STRICT = False

UPLOAD_DIR = tempfile.mkdtemp()
