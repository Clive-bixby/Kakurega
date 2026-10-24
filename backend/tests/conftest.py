import os
import tempfile

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.database import Base
from app.main import create_app


@pytest.fixture
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.remove(path)
    settings = Settings(
        app_name="Kakurega API",
        environment="test",
        debug=True,
        database_url=f"sqlite:///{path}",
    )
    app = create_app(settings)
    with TestClient(app) as client:
        with app.state.engine.begin() as connection:
            Base.metadata.create_all(bind=connection)
        yield client
    app.state.engine.dispose()
    try:
        if os.path.exists(path):
            os.remove(path)
    except PermissionError:
        pass
