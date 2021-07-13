LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
    },
    'formatters': {
        'colored': {
            '()': 'project.contrib.logging.formaters.ColoredExtraFormatter',
            'format': '%(log_color)s[%(levelname)s] %(asctime)s :: %(message)s',
            'log_colors': {
                'DEBUG': 'bold_black',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        }
    },
    'handlers': {
        'console_colored': {
            'class': 'colorlog.StreamHandler',
            'formatter': 'colored',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console_colored'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
