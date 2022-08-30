from tests.configtest import current_user, client, invalid_reqs_valid_post_get


# This file contains tests for "/products", "/products/details", "/products/cart" respectively
def test_product(client):
    with client:
        get_unauthorized = client.get("/products")
        get_sub_unauthorized = client.get("/products/details")
        get_cart_unauthorized = client.get("/products/cart")

        assert get_unauthorized.status_code == 302
        assert get_sub_unauthorized.status_code == 302
        assert get_cart_unauthorized.status_code == 302

        # authorized user logs in
        client.post("/signin", data={"email": "andyprout@yandex.ru", "password": "alperen"})

        if current_user.is_authenticated:
            get_req = client.get("/products")
            get_sub_req = client.get("/products/details")
            get_cart_req = client.get("/products/cart")

            assert get_req.status_code == 200
            assert get_sub_req.status_code == 200
            assert get_cart_req.status_code == 200

        post_req = client.post("/products")
        post_sub_req = client.post("/products/details")
        post_cart_req = client.post("/products/cart")

        assert post_req.status_code == 200
        assert post_sub_req.status_code == 200
        assert post_cart_req.status_code == 302


def test_products_invalid_requests(client):
    invalid_reqs_valid_post_get(client, "/products")
    invalid_reqs_valid_post_get(client, "/products/details")
    invalid_reqs_valid_post_get(client, "/products/cart")

