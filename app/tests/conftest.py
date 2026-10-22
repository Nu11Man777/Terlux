import pytest

from terlux import create_app


@pytest.fixture
def app():
    application = create_app()
    application.config.update(TESTING=True, SECRET_KEY="test")
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def catalog(app):
    return app.extensions["catalog"]
