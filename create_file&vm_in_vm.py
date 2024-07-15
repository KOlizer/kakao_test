from flask import Flask, request, jsonify
import hmac
import hashlib
from github import Github
import requests
import os
import subprocess
import json
from datetime import datetime  # datetime 모듈 추가

app = Flask(__name__)

# GitHub Personal Access Token
GITHUB_TOKEN = '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'
WEBHOOK_SECRET = 'syu_1234'

# 저장소 정보
SOURCE_REPO = 'KOlizer/Orign-copy'  # 포크된 리포지토리 이름
DEST_REPO = 'syu-admin/Orign'  # 원본 리포지토리 이름
FILE_PATH = '/home/ubuntu/push_to_github/test_rejection'  # 업로드할 파일 경로 (vm에 맞게 변경)
FILE_NAME_IN_REPO = os.path.basename(FILE_PATH)  # 리포지토리에 저장될 파일 이름 (로컬 파일 경로에서 추출)
COMMIT_MESSAGE = f'Add {FILE_NAME_IN_REPO} using PyGithub'  # 커밋 메시지 
PR_TITLE = f'{FILE_NAME_IN_REPO} 추가'  # PR 제목 
PR_BODY = f'{FILE_NAME_IN_REPO}의 요청사항: '  # PR 내용
BRANCH_NAME = 'main'  # 포크된 저장소의 브랜치 이름
REPO_DIR = '/home/ubuntu/Orign-copy'  # 로컬 Git 리포지토리 경로
PR_HISTORY_FILE = '/home/ubuntu/pull_request_history.json'  # PR 내역 저장 파일 경로

# 깃허브에 인증
g = Github(GITHUB_TOKEN)
repo_user = g.get_repo(SOURCE_REPO)

# 파일 읽기
with open(FILE_PATH, 'r', encoding='utf-8') as file:
    content = file.read()

# 파일 업로드
try:
    existing_file = repo_user.get_contents(FILE_NAME_IN_REPO, ref=BRANCH_NAME)
    repo_user.update_file(existing_file.path, COMMIT_MESSAGE, content, existing_file.sha, branch=BRANCH_NAME)
    print("File updated successfully in forked repository")
except:
    repo_user.create_file(FILE_NAME_IN_REPO, COMMIT_MESSAGE, content, branch=BRANCH_NAME)
    print("File uploaded successfully to forked repository")

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

# 원본 리포지토리와 포크된 리포지토리 동기화 함수
def sync_fork_with_upstream():
    def run_command(command, cwd=None):
        print(f"Running command: {command} in {cwd}")
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True, cwd=cwd)
        if result.returncode != 0:
            print(f"Error running command: {command}")
            print(f"Error: {result.stderr}")
        else:
            print(result.stdout)
    
    # Git 리포지토리의 루트 디렉토리로 이동하여 명령 실행
    git_dir = REPO_DIR  # Git 리포지토리 경로로 변경
    
    # 원격 설정
    origin_url_with_token = f"https://{GITHUB_TOKEN}@github.com/KOlizer/Orign-copy.git"
    upstream_url = f"https://{GITHUB_TOKEN}@github.com/syu-admin/Orign.git"

    run_command(f"git remote set-url origin {origin_url_with_token}", cwd=git_dir)
    run_command(f"git remote set-url upstream {upstream_url}", cwd=git_dir)
    
    # 원본 리포지토리에서 변경 사항 가져오기
    run_command("git fetch upstream", cwd=git_dir)
    
    # 로컬 브랜치로 체크아웃
    run_command("git checkout main", cwd=git_dir)
    
    # 원본 리포지토리의 변경 사항으로 리베이스
    run_command("git reset --hard upstream/main", cwd=git_dir)
    
    # 변경 사항 푸시
    run_command("git push origin main --force", cwd=git_dir)

# PR 코멘트 가져오기
def get_pr_comments(pr_number):
    url = f'https://api.github.com/repos/{DEST_REPO}/issues/{pr_number}/comments'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# PR 내역 저장 함수
def save_pr_history(pr_data, comments):
    history = {
        'pr_number': pr_data['number'],
        'title': pr_data['title'],
        'user': pr_data['user']['login'],
        'state': pr_data['state'],
        'merged': pr_data['merged'],
        'closed_at': pr_data['closed_at'],
        'comments': comments,
        'timestamp': datetime.now().isoformat(),
        'merge_commit_message': pr_data.get('merge_commit_message', ''),
    }
    if os.path.exists(PR_HISTORY_FILE):
        with open(PR_HISTORY_FILE, 'r', encoding='utf-8') as file:
            try:
                pr_history = json.load(file)
            except json.JSONDecodeError:
                pr_history = []
    else:
        pr_history = []
    pr_history.append(history)
    with open(PR_HISTORY_FILE, 'w', encoding='utf-8') as file:
        json.dump(pr_history, file, ensure_ascii=False, indent=4)
    print("PR history saved.")

# 웹훅 시그니처 검증 함수
def verify_signature(payload, signature):
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha1)
    generated_signature = 'sha1=' + mac.hexdigest()
    print(f"Signature from GitHub: {signature}")
    print(f"Generated signature: {generated_signature}")
    return hmac.compare_digest(generated_signature, signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    signature = request.headers.get('X-Hub-Signature')

    # 웹훅 시그니처 검증
    if not verify_signature(payload, signature):
        return jsonify({'message': 'Invalid signature'}), 400

    event = request.headers.get('X-GitHub-Event')
    if event == 'pull_request':
        pr_data = request.json
        action = pr_data['action']
        merged = pr_data['pull_request']['merged']
        pr_number = pr_data['number']

        # PR이 거절되었고 병합되지 않았을 때 동기화
        if action == 'closed' and not merged:
            print("PR이 거절되었습니다. 포크된 리포지토리를 원본 리포지토리와 동기화합니다.")
            comments = get_pr_comments(pr_number)
            for comment in comments:
                print(f"Comment by {comment['user']['login']}: {comment['body']}")
            save_pr_history(pr_data['pull_request'], comments)
            sync_fork_with_upstream()
        
        # PR이 병합되었을 때 동기화
        if action == 'closed' and merged:
            print("PR이 병합되었습니다. 로컬 리포지토리를 원본 리포지토리와 동기화합니다.")
            comments = get_pr_comments(pr_number)
            for comment in comments:
                print(f"Comment by {comment['user']['login']}: {comment['body']}")
            pr_data['pull_request']['merge_commit_message'] = pr_data['pull_request']['merge_commit_message'] if 'merge_commit_message' in pr_data['pull_request'] else ''
            save_pr_history(pr_data['pull_request'], comments)
            sync_fork_with_upstream()

    return jsonify({'message': 'Success'}), 200

# PR 생성 및 모니터링
try:
    pr = create_pull_request(fork_owner, DEST_REPO, PR_TITLE, PR_BODY, BRANCH_NAME, base_branch)
    pr_number = pr['number']
    print(f"PR 생성 완료: {pr['html_url']}")
except requests.exceptions.HTTPError as err:
    print(f"HTTP 오류 발생: {err}")
    print(f"응답 내용: {err.response.json()}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
