import os
import subprocess
import hmac
import hashlib
from datetime import datetime
import json
import requests
from github import Github
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# GitHub Personal Access Token
GITHUB_TOKEN = 'gefM'  # 실제 토큰 값
WEBHOOK_SECRET = 'syu_1234'

# 저장소 정보
SOURCE_REPO = 'KOlizer/Orign-copy'  # 포크된 리포지토리 이름
DEST_REPO = 'syu-admin/Orign'  # 원본 리포지토리 이름
FILE_PATH = '/home/ubuntu/push_to_github/test_rejection'  # 업로드할 파일 경로 (vm에 맞게 변경)
FILE_NAME_IN_REPO = os.path.basename(FILE_PATH)  # 리포지토리에 저장될 파일 이름 (로컬 파일 경로에서 추출)
COMMIT_MESSAGE = f'Add {FILE_NAME_IN_REPO} using PyGithub'  # 커밋 메시지
PR_TITLE = f'{FILE_NAME_IN_REPO} 추가'  # PR 제목
PR_BODY = f'{FILE_NAME_IN_REPO}을 추가했을 때 자원 상황 \n 퍼블릭 아이피 개수: 50/100개 \n 저장공간: 500/1000GB'
BRANCH_NAME = 'main'  # 포크된 저장소의 브랜치 이름
base_branch = 'main'  # 원본 리포지토리의 기본 브랜치
REPO_DIR = '/home/ubuntu/Orign-copy'  # 로컬 Git 리포지토리 경로
PR_HISTORY_FILE = '/home/ubuntu/pull_request_history.json'  # PR 내역 저장 파일 경로
DENY_COMMENTS_FILE = '/home/ubuntu/deny_comments.json'  # 원하는 파일 경로로 변경

# 깃허브에 인증
g = Github(GITHUB_TOKEN)
repo_user = g.get_repo(SOURCE_REPO)
fork_owner = repo_user.owner.login  # 포크된 리포지토리의 소유자 확인

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

    print("\n Github 동기화 작업을 시작합니다 (Orign-copy & Orign)\n")

    print("봇 리포지토리 origin으로 등록")
    run_command(f"git remote set-url origin {origin_url_with_token}", cwd=git_dir)

    print("원본 리포지토리를 upstream으로 등록")
    run_command(f"git remote add upstream {upstream_url}", cwd=git_dir)

    print("upstream 패치")
    run_command("git fetch upstream", cwd=git_dir)

    print("메인 브랜치 체크아웃")
    run_command("git checkout main", cwd=git_dir)

    print("포크된 리포지토리를 원본 리포지토리와 동기화")
    run_command("git rebase upstream/main", cwd=git_dir)

    print("변경 사항 푸시")
    run_command("git push origin main --force", cwd=git_dir)

# 파일 업로드 함수 (프론트에서 파일 받아오는 걸로 추가해야됨)
def upload_file_to_github(): 
    with open(FILE_PATH, 'r', encoding='utf-8') as file: #FILE_PATH 파일 content에 저장
        content = file.read()

    try:
        existing_file = repo_user.get_contents(FILE_NAME_IN_REPO, ref=BRANCH_NAME)
        repo_user.update_file(existing_file.path, COMMIT_MESSAGE, content, existing_file.sha, branch=BRANCH_NAME)
        print("파일을 성공적으로 업로드했습니다.")
    except:
        repo_user.create_file(FILE_NAME_IN_REPO, COMMIT_MESSAGE, content, branch=BRANCH_NAME)
        print("File uploaded successfully to forked repository \n")

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
    print(f"생성하는데 사용된 PR 데이터: {data} \n")  # 로깅 추가
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

# PR 정보 가져오기
def get_pr_info(pr_number):
    url = f'https://api.github.com/repos/{DEST_REPO}/pulls/{pr_number}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# PR 코멘트 가져오기
def get_pr_comments(pr_number):
    url = f'https://api.github.com/repos/{DEST_REPO}/issues/{pr_number}/comments'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    comments = response.json()

    # 필요한 정보만 포함한 댓글 리스트 생성
    filtered_comments = [
        {
            'created_at': comment['created_at'],
            'updated_at': comment['updated_at'],
            'author_association': comment['author_association'],
            'body': comment['body']
        }
        for comment in comments
    ]

    return filtered_comments

# PR에 코멘트 추가 함수
def add_comment_to_pr(pr_number, comment_body):
    url = f'https://api.github.com/repos/{DEST_REPO}/issues/{pr_number}/comments'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'body': comment_body
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    print(f"PR #{pr_number}에 코멘트가 추가되었습니다.")

# /deny 명령의 코멘트 저장 함수
def save_deny_comment(pr_number, comment):
    deny_comment = {
        'pr_number': pr_number,
        'user': comment['user']['login'],
        'comment': comment['body'],
        'timestamp': datetime.now().isoformat(),
    }
    with open(DENY_COMMENTS_FILE, 'w', encoding='utf-8') as file:
        json.dump([deny_comment], file, ensure_ascii=False, indent=4)  # 덮어쓰기 방식으로 저장
    print("deny 코멘트가 저장되었습니다.")

# GitHub Actions 워크플로우 트리거 함수
def trigger_github_actions_workflow(pr_number, action='approve'):
    url = f'https://api.github.com/repos/{DEST_REPO}/actions/workflows/approve-and-merge-pr.yml/dispatches'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        'ref': 'main',
        'inputs': {
            'pr_number': str(pr_number),
            'action': action
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 204:
        print(f"PR #{pr_number}에 대해 '{action}' GitHub Actions이 성공적으로 시작되었습니다.")
        return True
    else:
        print(f"Failed to trigger GitHub Actions workflow: {response.text}")
        return False

# PR 내역 저장 함수
def save_pr_history(pr_data, comments):
    history = {
        'PR 번호': pr_data['number'],
        'PR 제목': pr_data['title'],
        'PR 보낸이': pr_data['user']['login'],
        'PR 상태': pr_data['state'],
        'PR merge 여부': pr_data['merged'],
        'PR 종료시간': pr_data['closed_at'],
        'PR 내용': comments,
        '기록 저장한 시간': datetime.now().isoformat(),
    }

    # 필터링된 댓글 리스트 출력
    print(f"필터링된 댓글 리스트: {json.dumps(comments, indent=4, ensure_ascii=False)}")

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
    print("PR 기록이 저장되었습니다.\n")

# 웹훅 시그니처 검증 함수
def verify_signature(payload, signature):
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha1)
    generated_signature = 'sha1=' + mac.hexdigest()
    print(f"GitHub에서 서명한 해시 값: {signature}")
    print(f"생성된 서명: {generated_signature} \n")
    return hmac.compare_digest(generated_signature, signature)

# vm 생성 코드 부분
def run_create_vm_code(pr_number):
    try:
        result = subprocess.run(["python3", "/home/ubuntu/push_to_github/create_vm.py"], capture_output=True, text=True)
        if result.returncode != 0:
            error_message = f"Error running create_vm.py: {result.stderr}"
            print(error_message)
            add_comment_to_pr(pr_number, error_message)  # PR에 실패 원인 코멘트 추가
            return False
        else:
            print(f"create_vm.py output: {result.stdout}")
            if "success" in result.stdout:
                return True
            else:
                error_message = f"VM 생성 스크립트가 실패되었습니다\n실패 사유: {result.stdout}"
                print(error_message)
                add_comment_to_pr(pr_number, error_message)  # PR에 실패 원인 코멘트 추가
                return False
    except Exception as e:
        error_message = f"Exception running create_vm.py: {e}"
        print(error_message)
        add_comment_to_pr(pr_number, error_message)  # PR에 실패 원인 코멘트 추가
        return False

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get('X-Hub-Signature')

    # 웹훅 시그니처 검증
    if not verify_signature(payload, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    event = request.headers.get('X-GitHub-Event')
    body = await request.json()

    # PR 동기화 
    if event == 'pull_request': 
        pr_data = body
        action = pr_data['action']
        merged = pr_data['pull_request']['merged']
        pr_number = pr_data['number']

        # PR이 거절되었고 병합되지 않았을 때 동기화
        if action == 'closed' and not merged:
            print("PR이 거절되었습니다. 포크된 리포지토리를 원본 리포지토리와 동기화합니다.")
            comments = get_pr_comments(pr_number)
            save_pr_history(pr_data['pull_request'], comments)
            sync_fork_with_upstream()

        # PR이 병합되었을 때 동기화
        if action == 'closed' and merged:
            print("PR이 승인되었습니다. 로컬 리포지토리를 원본 리포지토리와 동기화합니다.")
            comments = get_pr_comments(pr_number)
            pr_data['pull_request']['merge_commit_message'] = pr_data['pull_request']['merge_commit_message'] if 'merge_commit_message' in pr_data['pull_request'] else ''
            save_pr_history(pr_data['pull_request'], comments)
            sync_fork_with_upstream()

    # 코멘트 감지
    if event == 'issue_comment':
        comment_data = body # 웹훅 요청의 본문
        comment_body = comment_data['comment']['body'] # 웹훅 본문에서 코멘트 추출
        if '/approve' in comment_body:  # /approve 감지시
            pr_number = comment_data['issue']['number']
            print(f"#{pr_number}에서 /approve가 감지되었습니다")
            if run_create_vm_code(pr_number):
                print("VM이 성공적으로 생성되었습니다")
                ssh_command = "여기에 ssh 명령어 입력"
                add_comment_to_pr(pr_number, ssh_command)
                if trigger_github_actions_workflow(pr_number):
                    print(f"PR #{pr_number}의 'approve' 작업 진행중입니다.")
                else:
                    print(f"Failed to approve and/or merge PR #{pr_number}.")
            else:
                print("VM 생성 실패, PR을 다시 확인해주세요.\n")
        if '/deny' in comment_body:  # /deny 감지시
            pr_number = comment_data['issue']['number']
            print(f"#{pr_number}에서 /deny가 감지되었습니다")
            comments = get_pr_comments(pr_number) # 코멘트 중에 /deny 포함한 코멘트 저장
            for comment in comments:
                 if '/deny' in comment['body']:
                    save_deny_comment(pr_number, comment)
                    break
            if trigger_github_actions_workflow(pr_number, 'deny'): # Githubaction으로 /deny 동기화
                print(f"PR #{pr_number}의 'deny' 작업 진행중입니다.")
            else:
                print(f"Failed to deny PR #{pr_number}.")

    return JSONResponse(content={"message": "Success"})

# PR 생성 및 모니터링
try:
    sync_fork_with_upstream()  # 동기화 먼저 수행
    upload_file_to_github()  # 파일 업로드 수행
    pr = create_pull_request(fork_owner, DEST_REPO, PR_TITLE, PR_BODY, BRANCH_NAME, base_branch) # PR 생성
    pr_number = pr['number'] # PR 번호 지정
    print(f"PR 생성 완료: {pr['html_url']} \n")
except requests.exceptions.HTTPError as err:
    print(f"HTTP 오류 발생: {err}")
    print(f"응답 내용: {err.response.json()}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
