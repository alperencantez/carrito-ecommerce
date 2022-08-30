from tests.configtest import client, invalid_reqs_valid_post_get, json


def test_signup(client):
    res = client.get("/")
    assert res.status_code == 200
    
    data = {
        "email": "test@mail.com",
        "password": "123456789",
        "is_seller": True,
    }

    res_post = client.post("/", data=json.dumps(data))
    
    assert type(data["is_seller"]) is bool
    assert res_post.status_code == 200


def test_signup_invalid_requests(client):
    invalid_reqs_valid_post_get(client, "/")