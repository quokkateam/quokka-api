import os

ENV = os.environ.get('ENV') or 'dev'


def env():
  return ENV


def is_test():
  return ENV == 'test'


def is_dev():
  return ENV == 'dev'


def is_prod():
  return ENV == 'prod'