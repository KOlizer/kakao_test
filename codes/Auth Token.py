import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_token(access_key_id, secret_key):
    url = "https://iam.kakaocloud.com/identity/v3/auth/tokens"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "auth": {
            "identity": {
                "methods": ["application_credential"],
                "application_credential": {
                    "id": access_key_id,
                    "secret": secret_key
                }
            }
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        return response.headers.get('X-Subject-Token')
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def get_projects(auth_token, user_id):
    url = f"https://iam.kakaocloud.com/identity/v3/users/{user_id}/projects"
    headers = {
        "X-Auth-Token": auth_token
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('projects')
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")






if __name__ == "__main__":
    # 액세스 키와 보안 액세스 키 설정
    access_key_id = '80a979153fe34362ac6e8301ea307099'
    secret_key = 'dc8f8b9c7d5a1aff39d304779a60207057c71325a9160628a177cba2e58380820d6ae4'
    user_id = 'ce276c0c8ae346f8873f8a72f137e1a1'


    # 인증 토큰 발급
    auth_token = get_token(access_key_id, secret_key)
    print(f"Auth Token: {auth_token}")

    # 프로젝트 목록 조회
    projects = get_projects(auth_token, user_id)
    for project in projects:
        print(f"Project ID: {project['id']}, Project Name: {project['name']}")

    project_id = "5883f6b1b1914d8d8e44b5026578e0be"
    cluster_endpoint = "https://51d9835d-8e18-4b80-920c-3098961b5ff3-public.ke.kr-central-2.kakaocloud.com:443"
    region = "kr-central-2"

