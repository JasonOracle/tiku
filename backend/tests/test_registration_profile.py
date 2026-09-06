"""v1.3 注册资料回归测试：昵称/性别/手机号/职务/邮箱 + 唯一性校验 + 个人资料接口"""
from app.models.user import User


def _register(client, **overrides):
    payload = {
        "username": "stu_profile",
        "password": "stupass123",
        "nickname": "小明同学",
        "gender": "male",
        "phone": "13900000001",
        "position": "学生",
        "email": "xiaoming@test.com",
    }
    payload.update(overrides)
    return client.post("/api/v1/auth/register", json=payload)


def test_register_full_profile_success(client):
    """全字段注册成功, 登录返回完整资料"""
    r = _register(client)
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["nickname"] == "小明同学"
    assert data["gender"] == "male"
    assert data["phone"] == "13900000001"
    assert data["position"] == "学生"
    assert data["email"] == "xiaoming@test.com"

    # 登录返回资料
    login = client.post("/api/v1/auth/login", json={"username": "stu_profile", "password": "stupass123"})
    assert login.status_code == 200
    user = login.json()["data"]["user"]
    assert user["nickname"] == "小明同学"
    assert user["phone"] == "13900000001"

    # GET /users/me 返回资料
    token = login.json()["data"]["token"]
    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["data"]["nickname"] == "小明同学"


def test_register_missing_nickname_rejected(client):
    """缺昵称 → 400 中文提示"""
    r = _register(client, nickname="")
    assert r.status_code == 400
    assert "昵称" in r.json()["detail"]


def test_register_missing_gender_rejected(client):
    """缺性别 → 400"""
    r = _register(client, gender="")
    assert r.status_code == 400
    assert "性别" in r.json()["detail"]


def test_register_invalid_phone_rejected(client):
    """手机号格式错误 → 400"""
    for bad in ["12345", "23900000001", "1390000000a"]:
        r = _register(client, phone=bad)
        assert r.status_code == 400, bad
        assert "手机号" in r.json()["detail"]


def test_register_duplicate_phone_rejected(client):
    """手机号全局唯一 → 重复注册 400"""
    assert _register(client).status_code == 201
    r = _register(client, username="stu_other", nickname="另一位")
    assert r.status_code == 400
    assert "手机号" in r.json()["detail"]


def test_register_duplicate_username_rejected(client):
    """用户名唯一 → 重复 400"""
    assert _register(client).status_code == 201
    r = _register(client, phone="13900000002")
    assert r.status_code == 400
    assert "用户名" in r.json()["detail"]


def test_register_optional_fields_default_empty(client):
    """职务/邮箱选填, 缺省可注册"""
    r = _register(client, position=None, email=None, username="stu_min", phone="13900000003")
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["position"] in ("", None)
    assert data["email"] in ("", None)


def test_legacy_user_display_fallback(client, db_session):
    """老用户无昵称时, B端数据 nickname=None, 前端回退 username (后端契约)"""
    legacy = User(username="legacy_user", password_hash="x", nickname=None)
    db_session.add(legacy)
    db_session.commit()
    client.post("/api/v1/admin/auth/init", json={"username": "admin_p", "password": "adminpassword"})
    token = client.post("/api/v1/admin/auth/login", json={"username": "admin_p", "password": "adminpassword"}).json()["data"]["token"]
    users = client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"}).json()["data"]
    legacy_item = [u for u in users["items"] if u["username"] == "legacy_user"][0]
    assert legacy_item["nickname"] is None
    assert legacy_item["phone"] is None
