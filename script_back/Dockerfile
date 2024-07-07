# Dockerfile

# 단계 1: 빌드 단계
FROM python:3.9-slim AS builder

# PyInstaller 설치
RUN pip install pyinstaller

# 애플리케이션 코드 복사
COPY backend /app/backend

# 작업 디렉토리 설정
WORKDIR /app/backend

# PyInstaller를 사용하여 바이너리 생성
RUN pyinstaller --onefile main.py --name backend_binary

# 단계 2: 최종 이미지
FROM python:3.9-slim

# 빌드 단계에서 생성된 바이너리를 복사
COPY --from=builder /app/backend/dist/backend_binary /usr/local/bin/backend_binary

# 실행 명령어 설정
CMD ["backend_binary"]
