#!/bin/bash

echo "kakaocloud: 1. Starting environment variable setup"
# 환경 변수 설정: 사용자는 이 부분에 자신의 환경에 맞는 값을 입력해야 합니다.
command=$(cat <<EOF
export ACC_KEY='005bb667e6574c61a5d4577262b61d89'
export SEC_KEY='652351ba4ebc7feec7e2e07582926c4ba7a06b09f2a1dbf4c223d15e15769a30761e63'
export CLUSTER_NAME='k8s-back'
export API_SERVER='https://6cd69b5b-74b5-4115-9ed2-c23b5fb7edd0-public.ke.kr-central-2.kakaocloud.com'
export AUTH_DATA='LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUM2akNDQWRLZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJME1EY3dOekF6TXpnMU1sb1hEVE0wTURjd05UQXpORE0xTWxvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTExDCk1RN01idGVkUzdFRGJ4K1RiWkxGUWp5OExURVVYdkxqR1NSZUx0N0dvbk1wZ3R6TTlITjdYMm9oWm9QQlBjSDIKU0hjbEF0QWtuRkl5T1pxM3NxK2Zna095cWNSamlveGN4OEZLUTdvQlgzN3ZSRFpvVFFvRk40dExQanA0V1huOApLdjdhNEIzUUVCSmxFd3diZzJhTHRkamloRjVaZTMwRWVwSitFS2JPWGhuZ3dJR21sOFdNQkh2ZjdlajZ6eHFTCkQ0V3pTZ0ovV1hKUTJUajZGcTUzcy9yZ2RtVFJFbi84YlFIZU5xaWhKVEhnNUJMU3NQK0FBZy9qVU1MWkNzSFQKQkR0QnBBZGl6NWtwWGIxdkNXNjN3T3B5dWhhcHgvdDFxQUZjVkRUZnBUanQ3NWxnaWVqK1dTU1VnYWpoRlhjRApPbERKUkRLdUxWUlZTOHhvN2tVQ0F3RUFBYU5GTUVNd0RnWURWUjBQQVFIL0JBUURBZ0trTUJJR0ExVWRFd0VCCi93UUlNQVlCQWY4Q0FRQXdIUVlEVlIwT0JCWUVGTjB4bU1MOWYyd2lhejdjUk55ZHJEbGpOTHNWTUEwR0NTcUcKU0liM0RRRUJDd1VBQTRJQkFRQVhiK1ByUmlWQjI2OVg4dlY2VVRSTkJGcVJFWGNBT2RuUkdubmdRV1lOT0J0YgpocWNPNnhYWktsU3ZhU3puc2RIOFhIUXljWFViRmlpRHgwd3lUd1VOclVVVnJVc1dZUVlrTlB3RnZuY0tpUDZ6CmpQcDFBK3I4bDh6YklhKzZqNm83Skt3Vy9pekdUM2hzV1lxZ0VBMnh4ejE4NzdDbkpkUTdNZTQ1SDVsTjdTNm0KaFpleHFkdWhhNEdJZUUzZ1RQTmYyQ3VXU2ZJeitwVjJHdjA2NzhiNWZGVTRaNm1SN0dmMlFNMjhQa3AxdEY1egpWNWhhMVpHZ3d4aVJXN0E4VGVkeHl1L2JQWkVZKzZvNlZOejBBSkpyKzAwNTk3NXJDZU1nZDIvMGNtbFhIS2tQClBCS1ZUNVBKQTR4TnJCU0VXY2htemVRZWFmOE5iR2s2Zlp1Y0VQKzYKLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLQo='
EOF
)

eval "$command"
echo "$command" >> /home/ubuntu/.bashrc
echo "kakaocloud: Environment variable setup completed"

# kubectl 설치
echo "kakaocloud: 2. Installing kubectl"
sudo curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" || { echo "kakaocloud: Failed to download kubectl binary"; exit 1; }
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl || { echo "kakaocloud: Failed to install kubectl binary"; exit 1; }
echo "kakaocloud: Kubectl installed"

# kubeconfig 설정
echo "kakaocloud: 3. Setting up kubeconfig"
mkdir -p ~/.kube
cat <<EOF > ~/.kube/config
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: ${AUTH_DATA}
    server: ${API_SERVER}
  name: ${CLUSTER_NAME}
contexts:
- context:
    cluster: ${CLUSTER_NAME}
    user: ${CLUSTER_NAME}-user
  name: ${CLUSTER_NAME}
current-context: ${CLUSTER_NAME}
kind: Config
preferences: {}
users:
- name: ${CLUSTER_NAME}-user
  user:
    token: ${ACC_KEY}
EOF

chmod 600 ~/.kube/config
chown $(whoami):$(whoami) ~/.kube/config
echo "kakaocloud: kubeconfig setup completed"

# Kubernetes 클러스터 연결 확인
echo "kakaocloud: 4. Checking Kubernetes cluster connection"
kubectl get nodes || { echo "kakaocloud: Failed to communicate with Kubernetes cluster"; exit 1; }
echo "kakaocloud: Successfully communicated with Kubernetes cluster"
