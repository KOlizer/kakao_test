from github import Github
import requests
import os

# GitHub Personal Access Token
GITHUB_TOKEN = 'My_Token'

# 저장소 정보
SOURCE_REPO = 'KOlizer/Orign-copy'  # 포크된 리포지토리 이름
DEST_REPO = 'syu-admin/Orign'  # 원본 리포지토리 이름
FILE_PATH = '/path/to/vm_info/lsh-vm.txt'  # 업로드할 파일 경로 (vm에 맞게 변경)
FILE_NAME_IN_REPO = os.path.basename(FILE_PATH)  # 리포지토리에 저장될 파일 이름 (로컬 파일 경로에서 추출)
COMMIT_MESSAGE = f'Add {FILE_NAME_IN_REPO} using PyGithub'  # 커밋 메시지 
PR_TITLE = f'{FILE_NAME_IN_REPO} 추가'  # PR 제목 
PR_BODY = f'{FILE_NAME_IN_REPO}의 요청사항: {}'  # PR 내용
BRANCH_NAME = 'main'  # 포크된 저장소의 브랜치 이름

# 깃허브에 인증
g = Github(GITHUB_TOKEN)
repo = g.get_repo(SOURCE_REPO)

# 파일 읽기
with open(FILE_PATH, 'r', encoding='utf-8') as file:
    content = file.read()

# 파일 업로드
try:
    repo.create_file(FILE_NAME_IN_REPO, COMMIT_MESSAGE, content, branch=BRANCH_NAME)
    print("File uploaded successfully to forked repository")
except Exception as e:
    print(f"Error uploading file: {e}")

# PR 생성 함수
def create_pull_request(fork_repo, base_repo, title, body, branch_name):
    url = f'https://api.github.com/repos/{base_repo}/pulls'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'title': title,
        'body': body,
        'head': f'{fork_repo.split("/")[0]}:{branch_name}',  # 사용자명:브랜치명 형식
        'base': 'main'
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

# PR 생성
try:
    pr = create_pull_request(SOURCE_REPO, DEST_REPO, PR_TITLE, PR_BODY, BRANCH_NAME)
    print(f"PR 생성 완료: {pr['html_url']}")
except requests.exceptions.HTTPError as err:
    print(f"HTTP 오류 발생: {err}")
    print(f"응답 내용: {err.response.json()}")
