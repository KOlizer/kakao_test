from github import Github

# 깃허브 액세스 토큰과 리포지토리 정보
token = 'My_Token'  # 여기에 개인 액세스 토큰을 입력하세요.
repo_name = 'KOlizer/Orign-copy'
file_path = 'C:\\vm_info\\lsh-vm.txt'  # 업로드할 파일 경로
file_name_in_repo = 'lsh-vm.txt'  # 리포지토리에 저장될 파일 이름
commit_message = 'Add lsh-vm.txt using PyGithub' # 커밋 메시지

# 깃허브에 인증
g = Github(token)
repo = g.get_repo(repo_name)

# 파일 읽기
with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()

# 파일 업로드
try:
    repo.create_file(file_name_in_repo, commit_message, content, branch="main")
    print("File uploaded successfully")
except Exception as e:
    print(f"Error: {e}")
