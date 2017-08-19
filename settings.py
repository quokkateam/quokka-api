import sys

LOGGING = {
  'handlers': {
    'console': {
      'level': 'INFO',
      'class': 'logging.StreamHandler',
      'stream': sys.stdout
    }
  },
  'loggers': {
    'quokka': {
      'handlers': ['console']
    }
  }
}