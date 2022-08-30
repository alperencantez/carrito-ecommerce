from tests.configtest import client, current_user, invalid_reqs_valid_post_get


def test_signin(client):
    with client:
        # get as anonymous user
        res = client.get("/signin")
        assert res.status_code == 200
        
        # authenticated user logs in
        res_post = client.post("/signin", data={"email": "andyprout@yandex.ru", "password": "alperen"}) 
        assert res_post.status_code == 302
        
        if current_user.is_authenticated:
            assert res_post.status_code == 302

            res_get = client.get("/signin")
            assert res_get.status_code == 302
        else:
            assert res_post.status_code == 200    


def test_signin_invalid_requests(client):
    invalid_reqs_valid_post_get(client, "/signin")