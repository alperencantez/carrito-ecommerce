from tests.configtest import current_user, client, invalid_reqs_valid_post_get


def test_signout(client):
    with client:
        get_unauthorized = client.get("/signout")
        assert get_unauthorized.status_code == 302

        # authenticated user logs in
        client.post("/signin", data={"email": "andyprout@yandex.ru", "password": "alperen"})

        if current_user.is_authenticated:
            get_req = client.get("/signin")
            assert get_req.status_code == 302


def test_signout_invalid_requests(client):
    invalid_reqs_valid_post_get(client, "/signout")
    post_req = client.post("/signout")
    assert post_req.status_code == 405