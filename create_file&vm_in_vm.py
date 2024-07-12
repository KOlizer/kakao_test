from github import Github
import requests
import os

# GitHub Personal Access Token
GITHUB_TOKEN = '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'

# 저장소 정보
SOURCE_REPO = 'KOlizer/Orign-copy'  # 포크된 리포지토리 이름
DEST_REPO = 'syu-admin/Orign'  # 원본 리포지토리 이름
FILE_PATH = '/home/ubuntu/push_to_github/test_rejection'  # 업로드할 파일 경로 (vm에 맞게 변경)
FILE_NAME_IN_REPO = os.path.basename(FILE_PATH)  # 리포지토리에 저장될 파일 이름 (로컬 파일 경로에서 추출)
COMMIT_MESSAGE = f'Add {FILE_NAME_IN_REPO} using PyGithub'  # 커밋 메시지 
PR_TITLE = f'{FILE_NAME_IN_REPO} 추가'  # PR 제목 
PR_BODY = f'{FILE_NAME_IN_REPO}의 요청사항: '  # PR 내용
BRANCH_NAME = 'main'  # 포크된 저장소의 브랜치 이름

# 깃허브에 인증
g = Github(GITHUB_TOKEN)
repo_user = g.get_repo(SOURCE_REPO)

# 파일 읽기
with open(FILE_PATH, 'r', encoding='utf-8') as file:
    content = file.read()

# 파일 업로드
try:
    repo_user.create_file(FILE_NAME_IN_REPO, COMMIT_MESSAGE, content, branch=BRANCH_NAME)
    print("File uploaded successfully to forked repository")
except Exception as e:
    print(f"Error uploading file: {e}")

# 포크된 리포지토리의 소유자 확인
fork_owner = repo_user.owner.login
print(f"Forked repository owner: {fork_owner}")

# 포크된 리포지토리의 브랜치들 확인
branches = repo_user.get_branches()
branch_names = [branch.name for branch in branches]
print(f"Available branches in forked repository: {branch_names}")

# 원본 리포지토리의 기본 브랜치
base_branch = 'main'

# PR 생성 함수
def create_pull_request(fork_owner, base_repo, title, body, head_branch, base_branch):
    url = f'https://api.github.com/repos/{base_repo}/pulls'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'title': title,
        'body': body,
        'head': f'{fork_owner}:{head_branch}',  # 사용자명:브랜치명 형식
        'base': base_branch  # 원본 리포지토리의 기본 브랜치
    }
    print(f"Creating PR with data: {data}")  # 로깅 추가
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

# PR 생성 및 모니터링
try:
    pr = create_pull_request(fork_owner, DEST_REPO, PR_TITLE, PR_BODY, BRANCH_NAME, base_branch)
    pr_number = pr['number']
    print(f"PR 생성 완료: {pr['html_url']}")
except requests.exceptions.HTTPError as err:
    print(f"HTTP 오류 발생: {err}")
    print(f"응답 내용: {err.response.json()}")
