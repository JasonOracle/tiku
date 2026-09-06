def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_c_user_register_and_login(client):
    # 注册 C端用户 (v1.3: 需带昵称/性别/手机号)
    reg_res = client.post("/api/v1/auth/register", json={
        "username": "student_test",
        "password": "password123",
        "nickname": "测试学员",
        "gender": "male",
        "phone": "13900020001"
    })
    assert reg_res.status_code == 201
    assert reg_res.json()["data"]["username"] == "student_test"

    # 重复注册测试
    reg_repeat = client.post("/api/v1/auth/register", json={
        "username": "student_test",
        "password": "password123",
        "nickname": "测试学员",
        "gender": "male",
        "phone": "13900020002"
    })
    assert reg_repeat.status_code == 400

    # 登录测试
    login_res = client.post("/api/v1/auth/login", json={
        "username": "student_test",
        "password": "password123"
    })
    assert login_res.status_code == 200
    assert "token" in login_res.json()["data"]

def test_b_admin_init_and_login(client):
    # 初始化管理员
    init_res = client.post("/api/v1/admin/auth/init", json={
        "username": "admin_test",
        "password": "adminpassword"
    })
    assert init_res.status_code == 201
    assert init_res.json()["data"]["username"] == "admin_test"

    # 管理员登录
    login_res = client.post("/api/v1/admin/auth/login", json={
        "username": "admin_test",
        "password": "adminpassword"
    })
    assert login_res.status_code == 200
    assert "token" in login_res.json()["data"]
