import requests
from bs4 import BeautifulSoup

def get_clusters(auth_token: str, project_id: str, region: str):
    url = f"https://kubernetes.{region}.kakaoapis.com/v4/projects/{project_id}/clusters"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # HTTP 오류 발생 시 예외를 던집니다.
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching clusters: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # 액세스 토큰과 프로젝트 ID, 지역 설정
    access_token = 'gAAAAABmf1gbpPnpSpAauorq0SsE5ETwRL7kacIMKdM06RMfmWG5e7l9sDLUKp1z9OUz6gS5r2Myd3a173quheG6GoZE6HJix-aVa1P7OUKiu7_gPnI0Sr1Bp6HmU6DO4iTVTrqe8sbphMCA3FEUstj6Djquau5OCN2DxHVlx1q2qP8wLqZP22GkGoE4sVc3xQYmaQov_bij'
    project_id = '5883f6b1b1914d8d8e44b5026578e0be'
    region = 'kr-central-2'

    # 클러스터 목록 조회
    clusters = get_clusters(access_token, project_id, region)
    if clusters:
        for cluster in clusters.get('items', []):
            print(f"Cluster Name: {cluster['name']}, Cluster ID: {cluster['id']}")
    else:
        print("Failed to fetch clusters.")
