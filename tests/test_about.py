from tests.configtest import client
from flask_login import current_user


def test_home(client):
    res = client.get("/about")

    if current_user == None:
        assert res.status_code == 302
    else:
        assert res.status_code == 200    


def test_home_invalid_requests(client):
    invalid_methods = []

    invalid_methods.append(client.post("/about"))
    invalid_methods.append(client.put("/about"))
    invalid_methods.append(client.patch("/about"))
    invalid_methods.append(client.delete("/about"))
    
    for invalid in invalid_methods:    
        assert invalid.status_code == 405