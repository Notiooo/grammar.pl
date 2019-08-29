from django.apps import AppConfig
from django.core.cache import cache


class UsersConfig(AppConfig):
    name = 'users'

# I want to clear cache on every startup, but I don't have idea where should I put it
cache.clear()