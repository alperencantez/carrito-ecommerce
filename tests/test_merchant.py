from tests.configtest import client, invalid_reqs_valid_post_get, json, current_user


# This file contains tests for "/merchant/edit" and "merchant/pending"
def test_merchant_edit(client):
    with client:
        client.post("/signin", data={"email": "andyprout@yandex.ru", "password": "alperen"})

        res_get = client.get("/merchant/edit")
        res_sub_get = client.get("merchant/pending")

        if current_user.is_authenticated:
            assert res_get.status_code == 200
            assert res_sub_get.status_code == 200
        else:
            assert res_get.status_code == 302
            assert res_sub_get.status_code == 302

        # POST
        data = {
            "name": "product",
            "price": 456,
            "image": "product-img.jpg",
            "desc": "Description",
            "seller": 2,
        }   

        res_post = client.post("/merchant/edit", data=json.dumps(data))

        assert type(data["name"]) is str
        assert type(data["price"]) is int
        assert type(data["image"]) is str
        assert type(data["desc"]) is str
        assert type(data["seller"]) is int

        assert res_post.status_code == 200
 

def test_merchant_edit_invalid_requests(client):
    invalid_reqs_valid_post_get(client, "/merchant/edit")
    invalid_reqs_valid_post_get(client, "/merchant/pending")

    post = client.post("merchant/pending")
    assert post.status_code == 405
