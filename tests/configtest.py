import pytest
import json
from flask_login import LoginManager, current_user, login_user
from app.config import app


test_app = app
test_app.config.update({
    "TESTING": True,
})


@pytest.fixture
def client():
    return app.test_client()


def invalid_reqs_valid_post_get(client, path):
    invalid_methods = []

    invalid_methods.append(client.put(path))
    invalid_methods.append(client.patch(path))
    invalid_methods.append(client.delete(path))
    
    for invalid in invalid_methods:    
        assert invalid.status_code == 405
