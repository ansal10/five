

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'five',
        'HOST': 'localhost',
        'PORT': '5432',
        'USERNAME': 'ansal'
    }
}

FIREBASE_API_KEY = "AAAAapKlL5w:APA91bHp8965bkq8rFhnoZh1ESl-W-OEQPCa8Sm_8QRMfeIQNJv3WZ_OA8rMil6mdcfLzff2hj16O5EXPbsVoOALgcDxGlirNDwuKUgvbzob9jdxRUCg-wScKGkR-XrkAViIv_R71Bzl"

DEBUG = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'INFO',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/five.log',
            'maxBytes': 1024*1024*50, # 50 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'fiveapp':{
            'handlers':['file'],
            'propogate': True,
            'level': 'INFO'
        }
    },
}
