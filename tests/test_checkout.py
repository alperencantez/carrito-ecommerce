from tests.configtest import invalid_reqs_valid_post_get, client, current_user


# This file contains tests for "/checkout" and "/checkout/success"
def test_checkout(client):
    with client:
        get_unauthorized = client.get("/checkout")
        get_success_unauthorized = client.get("/checkout/success")

        assert get_unauthorized.status_code == 302
        assert get_success_unauthorized.status_code == 302

        # authorized user logs in
        client.post("/signin", data={"email": "andyprout@yandex.ru", "password": "alperen"})

        if current_user.is_authenticated:
            get_req = client.get("/checkout")
            get_success_req = client.get("/checkout/success")

            assert get_req.status_code == 200
            assert get_success_req.status_code == 302

        post_req = client.post("/checkout")
        assert post_req.status_code == 200


def test_checkout_invalid_requests(client):
    invalid_reqs_valid_post_get(client, "/checkout")

    invalid_reqs_valid_post_get(client, "/checkout/success")
    sub_post = client.post("/checkout/success")
    assert sub_post.status_code == 405