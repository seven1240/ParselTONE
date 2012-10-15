LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'djangoesque': {
            'format': '[%(asctime)s] %(levelname)8s (%(name)s) %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'djangoesque'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers':['null'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'parseltone': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
        },
    }
}

