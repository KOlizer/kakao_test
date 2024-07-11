import requests

# GitHub Personal Access Token
GITHUB_TOKEN = 'My_Token' # 포크된 리포지토리 토큰

# 저장소 정보
SOURCE_REPO = 'KOlizer/Orign-copy' # 출발지: 포크된 리포지토리 이름
DEST_REPO = 'syu-admin/Orign' # 목적지: 원본 리포지토리
BRANCH_NAME = 'main'  # 포크된 저장소의 브랜치 이름, 우리는 main 고정
PR_TITLE = 'Add lsh-vm.txt' # PR 타이틀, 
PR_BODY = 'This PR adds the lsh-vm.txt file from Orign-copy repository.' # PR 내용, 사용자 요청사항 쓰면 될듯

def create_pull_request(fork_repo, base_repo, title, body, branch_name): # PR 생성 함수
    url = f'https://api.github.com/repos/{base_repo}/pulls'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'title': title,
        'body': body,
        'head': f'{fork_repo.split("/")[0]}:{branch_name}',  # 사용자명 ["Kolizer", "Orign-copy'], Kolizer:main 표현
        'base': 'main'
    }
    response = requests.post(url, json=data, headers=headers) #PR 생성할 Github의 엔드포인트 URL
    response.raise_for_status() # HTTP 응답 상태 검사
    return response.json() # 성공적으로 PR이 생성되면PR에 대한 정보를 JSON 형식으로 반환

# PR 생성
try:
    pr = create_pull_request(SOURCE_REPO, DEST_REPO, PR_TITLE, PR_BODY, BRANCH_NAME)
    print(f"PR 생성 완료: {pr['html_url']}")
except requests.exceptions.HTTPError as err:
    print(f"HTTP 오류 발생: {err}")
    print(f"응답 내용: {err.response.json()}")
