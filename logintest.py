import json
from fastapi.testclient import TestClient

from main import app, decode_token

client = TestClient(app)

def test_login():
    # 임시로 사용할 유저 정보
    fake_users_db = {
        "john": {
            "username": "john",
            "full_name": "John Doe",
            "email": "john.doe@example.com",
            "hashed_password": "$2b$12$HtMSr0CR.tuM5kkzV7bYOuGTXzV77oAb.s5JfuZl5Q5e5r7XuOP5O",  # testpassword
            "disabled": False,
        },
    }
    
    # 로그인 정보 생성
    login_data = {
    "username": "kjh42447@gmail.com",
    "password": "testpassword1!"
    }

    # 회원 정보 조회
    response = client.get("/users")

    # 응답 코드 확인
    assert response.status_code == 200
    
    # 응답 데이터 확인
    response_data = json.loads(response.text)
    print(response_data)
    
    # 로그인 API 호출
    response = client.post("/login", data=login_data)
    
    # 응답 코드 확인
    assert response.status_code == 200
    
    # 응답 데이터 확인
    response_data = json.loads(response.text)
    assert "access_token" in response_data
    assert "token_type" in response_data
    assert response_data["token_type"] == "bearer"
    
    # 발급된 토큰 디코딩
    token = response_data["access_token"]
    decoded_token = decode_token(token)
    assert decoded_token == {"email": "kjh42447@gmail.com", "user_id": 2}

# def test_create_expenses():
#     # 가짜 데이터 생성
#     fake_cost = 1000
#     fake_comment = "Test Comment"
#     fake_user_id = 2
#     fake_expenses = {"cost": fake_cost, "comment": fake_comment, "user_id": fake_user_id}
    
#     # 로그인 API 호출
#     login_data = {
#     "username": "kjh42447@gmail.com",
#     "password": "testpassword1!"
#     }
#     response = client.post("/login", data=login_data)
#     token = response.json()["access_token"]

#     # API 호출
#     print(decode_token(token))
#     response = client.post("/expenses", json=fake_expenses, headers={"Authorization": f"Bearer {token}"})
#     headers={"Authorization": f"Bearer {token}"}
#     print(headers)
#     print(response.json())

#     # 응답 상태 코드 확인
#     assert response.status_code == 200
    
#     # 응답 내용 확인
#     response_json = response.json()
#     assert response_json["cost"] == fake_cost
#     assert response_json["comment"] == fake_comment
#     assert response_json["user_id"] == fake_user_id

def test_patch_expenses():
    # 가짜 데이터 생성
    fake_expenses_id = 1
    fake_cost = 1000
    fake_comment = "Test Comment"
    fake_user_id = 2
    fake_expenses = {"expenses_id": fake_expenses_id, "cost": fake_cost, "comment": fake_comment, "user_id": fake_user_id}
    
    # 로그인 API 호출
    login_data = {
    "username": "kjh42447@gmail.com",
    "password": "testpassword1!"
    }
    response = client.post("/login", data=login_data)
    token = response.json()["access_token"]

    # API 호출
    print(decode_token(token))
    response = client.patch("/expenses", json=fake_expenses, headers={"Authorization": f"Bearer {token}"})
    headers={"Authorization": f"Bearer {token}"}
    print(headers)
    print(response.json())

    # 응답 상태 코드 확인
    assert response.status_code == 200
    
    # 응답 내용 확인
    response_json = response.json()
    assert response_json["cost"] == fake_cost
    assert response_json["comment"] == fake_comment
    assert response_json["user_id"] == fake_user_id