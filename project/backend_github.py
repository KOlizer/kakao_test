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
from pydantic import BaseModel  # 프론트 내용
from fastapi.middleware.cors import CORSMiddleware  # 프론트 연결 허용

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 요청을 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GitHub Personal Access Token
GITHUB_TOKEN = 'ghp_cJ1u325wWM'  # 실제 토큰 값
WEBHOOK_SECRET = 'syu_1234'

# 저장소 정보
SOURCE_REPO = 'KOlizer/Orign-copy'  # 포크된 리포지토리 이름
DEST_REPO = 'syu-admin/Orign'  # 원본 리포지토리 이름
FILE_PATH = '/home/ubuntu/push_to_github/make_from_front'  # 업로드할 파일 경로 (vm에 맞게 변경)
FILE_NAME_IN_REPO = os.path.basename(FILE_PATH)  # 리포지토리에 저장될 파일 이름 (로컬 파일 경로에서 추출)
REPO_DIR = '/home/ubuntu/Orign-copy'  # 로컬 Git 리포지토리 경로
PR_HISTORY_FILE = '/home/ubuntu/pull_request_history.json'  # PR 내역 저장 파일 경로
DENY_COMMENTS_FILE = '/home/ubuntu/deny_comments.json'  # 원하는 파일 경로로 변경
base_branch = 'main'  # 원본 리포지토리의 기본 브랜치


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

def create_branch(branch_name):
    try:
        repo_user.create_git_ref(ref=f"refs/heads/{branch_name}", sha=repo_user.get_branch("main").commit.sha)
        print(f"브랜치 {branch_name} 생성 완료")
    except Exception as e:
        print(f"브랜치 생성 실패: {e}")

# 파일 업로드 함수 (프론트에서 파일 받아오는 걸로 추가해야됨)
def upload_file_to_github(branch_name): 
    commit_message = f'{branch_name} 추가'
    with open(FILE_PATH, 'r', encoding='utf-8') as file: # FILE_PATH 파일 content에 저장
        content = file.read()

    try:
        existing_file = repo_user.get_contents(FILE_NAME_IN_REPO, ref=branch_name)
        repo_user.update_file(existing_file.path, commit_message, content, existing_file.sha, branch=branch_name)
        print("파일을 성공적으로 업데이트했습니다.")
    except github.GithubException as e:
        if e.status == 404:
            repo_user.create_file(FILE_NAME_IN_REPO, commit_message, content, branch=branch_name)
            print("파일을 성공적으로 업로드했습니다.")
        else:
            raise

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
        response = requests.get(
            "http://localhost:8000/create_vm_with_keypair", # 현재 임의 값으로 다 채워둔 상태
            params={
                "access_key_id": "005bb667e6574c61a5d4577262b61d89",
                "access_key_secret": "652351ba4ebc7feec7e2e07582926c4ba7a06b09f2a1dbf4c223d15e15769a30761e63",
                "keypair_name": "test-lsh-vm",
                "vm_name": "my-lsh-test",
                "image_ref": "920ac13e-04f0-4a4a-81c1-3c36fec7a3a6",
                "flavor_ref": "ff64c2aa-2e80-4cfd-a646-2b475270d31e",
                "network_id": "9efb1795-5ca2-4c70-8e23-eef9c52793e0",
                "availability_zone": "kr-central-2-a",
                "description": "vm test with PR",
                "security_group_name": "default",
                "volume_size": 30,
                "email_to": "jjinjukks1227@gmail.com",
            },
        )

        if response.status_code == 200:
            result = response.json()
            print(f"VM 생성 및 이메일 전송 성공: {result}")
            floating_ip_address = result.get("floating_ip_address")
            keypair_name = result.get("keypair_name")
            return True, floating_ip_address, keypair_name
        else:
            error_message = f"VM 생성 실패: {response.text}"
            print(error_message)
            add_comment_to_pr(pr_number, error_message)
            return False, None, None
        
    except Exception as e:
        error_message = f"Exception running create_vm.py: {e}"
        print(error_message)
        add_comment_to_pr(pr_number, error_message)
        return False, None, None
    
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
        pr_number = pr_data['number']
        merged = pr_data['pull_request'].get('merged', False)

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
            success, floating_ip_address, keypair_name = run_create_vm_code(pr_number)
            if success:
                print("VM이 성공적으로 생성되었습니다")
                ssh_command = f"ssh 접속 명령어: ssh -i ~/Downloads/{keypair_name}.pem ubuntu@{floating_ip_address}"
                add_comment_to_pr(pr_number, ssh_command)
                if trigger_github_actions_workflow(pr_number):
                    print(f"PR #{pr_number}의 'approve' 작업 진행중입니다.")
                else:
                    print(f"Failed to approve and/or merge PR #{pr_number}.")
            else:
                print("VM 생성 실패")
                # run_create_vm_code에서 에러 메시지 코멘트 추가
                pass
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


# PR 생성 및 모니터링 함수
def process_pr(branch_name, pr_title):
    try:
        sync_fork_with_upstream()  # 동기화 먼저 수행
        create_branch(branch_name)  # 브랜치 생성
        upload_file_to_github(branch_name)  # 파일 업로드 수행
        pr_body = f"{branch_name} 브랜치에 새로운 변경 사항이 있습니다."
        pr = create_pull_request(fork_owner, DEST_REPO, pr_title, pr_body, branch_name, base_branch) # PR 생성
        pr_number = pr['number'] # PR 번호 지정
        print(f"PR 생성 완료: {pr['html_url']} \n")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP 오류 발생: {err}")
        print(f"응답 내용: {err.response.json()}")
        
class PRRequest(BaseModel):
    accessKey: str
    secretKey: str
        
        
@app.post("/make_pr")
async def make_pr(request: PRRequest):
    access_key = request.accessKey
    secret_key = request.secretKey
    
    # access_key와 secret_key 확인 (로그 출력 또는 다른 처리)
    print(f"Received 이름: {access_key}")
    print(f"Received 연락처: {secret_key}")
        
    # 파일 수정
    if not os.path.exists(FILE_PATH):
        return JSONResponse(content={"message": "File not found"}, status_code=404)
    
    # 새로운 내용 작성
    new_content = f"""
    -------------------------

    사용자 정보:
    이름: {access_key}
    학번: [여기에 학번 입력]
    비밀번호: [여기에 비밀번호 입력]
    이메일: [여기에 이메일 입력]
    연락처: {secret_key}
    사용 용도: [여기에 사용 용도 입력]

    VM 정보:
    VM 이름: [여기에 VM 이름 입력]
    사용 기간: [여기에 사용 기간 입력]
    스펙: [여기에 스펙 입력]
    개수: [여기에 VM 개수 입력]
    운영체제 (OS): [여기에 운영체제 입력]
    보안 그룹 (SG): [여기에 보안 그룹 입력]
    볼륨: 30GB
    
    """
    
    with open(FILE_PATH, 'a', encoding='utf-8') as file:
        file.write(new_content)
    
    # 고유한 브랜치 이름과 PR 제목 및 커밋 메시지 설정
    branch_name = f'update-{access_key}'
    pr_title = f'{access_key} 추가'
    
    process_pr(branch_name, pr_title)
    return JSONResponse(content={"message": "Pull request processing initiated."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
