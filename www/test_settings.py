import tempfile

from www.config import *

CELERY_ALWAYS_EAGER = True  # Skip the Celery daemon

# all tasks will be executed locally by blocking until the task returns.
# apply_async() and Task.delay() will return an EagerResult instance,
# which emulates the API and behavior of AsyncResult,
# except the result is already evaluated.


UPLOAD_DIR = tempfile.mkdtemp()
