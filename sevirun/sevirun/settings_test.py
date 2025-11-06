from .settings import *

# Base de datos temporal para tests
import tempfile, os
tmpdir = tempfile.gettempdir()
TEST_DB_PATH = os.path.join(tmpdir, 'sevirun_test_db.sqlite3')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': TEST_DB_PATH,
    }
}