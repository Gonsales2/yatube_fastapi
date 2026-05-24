from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.di.providers import all_providers


def create_container():
    return make_async_container(*all_providers)


container = create_container()
