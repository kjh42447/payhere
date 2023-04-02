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
        "username": "john",
        "password": "testpassword"
    }

    # 회원 정보 조회
    response = client.get("/users")

    # 응답 코드 확인
    assert response.status_code == 200
    
    # 응답 데이터 확인
    response_data = json.loads(response.text)
    print(response_data)
    
    # 로그인 API 호출
    response = client.post("/token", data=login_data)
    
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
    assert decoded_token == {"username": "john"}
