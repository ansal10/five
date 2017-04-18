import os

env = os.getenv('ENV', 'development')

if env == 'development':
    from development import *
elif env == 'production':
    from production import *
elif env == 'test' or env == 'testing':
    from test import *
else:
    from development import *


SECONDS = 300

MIN_BUILD_VERSION_FOR_FORCE_UPDATE = 1.2