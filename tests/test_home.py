from tests.configtest import client, invalid_reqs_valid_post_get, current_user


def test_home(client):
    res = client.get("/home")

    if current_user == None:
        assert res.status_code == 302
    else:
        assert res.status_code == 200    


def test_home_invalid_requests(client):
    invalid_reqs_valid_post_get(client, "/home")
    
    post = client.post("/home")
    assert post.status_code == 405
    
