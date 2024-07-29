from fastapi import FastAPI, HTTPException, Query  # FastAPI, HTTP 예외처리, 쿼리 파라미터를 가져옵니다.
import requests  # HTTP 요청을 보내기 위한 requests 라이브러리를 가져옵니다.
import json  # JSON 데이터를 다루기 위한 json 라이브러리를 가져옵니다.
import os  # 운영 체제 인터페이스를 제공하는 os 모듈을 가져옵니다.
import time  # 시간 관련 함수를 제공하는 time 모듈을 가져옵니다.
import smtplib  # 이메일 전송을 위한 smtplib 모듈을 가져옵니다.
from email.mime.multipart import MIMEMultipart  # 이메일 메시지를 다루기 위한 MIMEMultipart을 가져옵니다.
from email.mime.base import MIMEBase  # MIMEBase 클래스를 가져옵니다.
from email import encoders  # 이메일 인코더를 가져옵니다.
from email.mime.text import MIMEText  # 텍스트 이메일 메시지를 다루기 위한 MIMEText를 가져옵니다.

# FastAPI 앱 인스턴스를 생성합니다.
app = FastAPI()

# 키페어를 생성하고 VM을 생성하는 엔드포인트를 정의합니다.
@app.get("/create_vm_with_keypair")
async def create_vm_with_keypair( # 비동기 함수 정의
    access_key_id: str = Query(..., description="API 접근을 위한 액세스 키 ID"),  # API 접근을 위한 액세스 키 ID
    # Query 객체로 설정되어 있어서 매개변수가 전달될 것임
    # FastAPI의 Query라는 객체에 매개변수가 담길꺼임
    # ...은 필수 매개변수
    # description은 사용자가 보기 편한 설명
    access_key_secret: str = Query(..., description="API 접근을 위한 액세스 키 시크릿"),  # API 접근을 위한 액세스 키 시크릿
    keypair_name: str = Query(..., description="생성할 키페어 이름"),  # 생성할 키페어 이름
    vm_name: str = Query(..., description="생성할 VM 이름"),  # 생성할 VM 이름
    image_ref: str = Query(..., description="이미지 ID"),  # 이미지 ID
    flavor_ref: str = Query(..., description="인스턴스 유형 ID"),  # 인스턴스 유형 ID
    network_id: str = Query(..., description="네트워크 ID"),  # 네트워크 ID
    availability_zone: str = Query("kr-central-2-a", description="가용 영역"),  # 가용 영역
    description: str = Query("My VM", description="VM 설명"),  # VM 설명
    security_group_name: str = Query("default", description="보안 그룹 이름"),  # 보안 그룹 이름
    volume_size: int = Query(30, description="루트 볼륨 크기 (GB)"),  # 루트 볼륨 크기 (GB)
    email_to: str = Query(..., description="키 페어와 VM 정보를 보낼 이메일 주소"),  # 키 페어와 VM 정보를 보낼 이메일 주소
):
    # API 토큰 발급
    url_token = "https://iam.kakaocloud.com/identity/v3/auth/tokens"  # 토큰 발급을 위한 URL
    payload_token = { # 토큰 발급 요청시 서버로 전달할 데이터
        "auth": {
            "identity": {
                "methods": ["application_credential"],  # 인증 방법으로 application_credential 사용
                # application_credential 방식은 특히 자동화된 애플리케이션에서 클라우드 리소스에 접근할 때 매우 유용, 주로 access_key_ID와 access_key_secret로 구성
                "application_credential": {
                    "id": access_key_id,  # 접근 키 ID
                    "secret": access_key_secret,  # 접근 키 시크릿
                },
            }
        }
    }
    headers_token = {"Content-Type": "application/json"}  # 딕셔너리 형식, 요청 헤더 설정
    response_token = requests.post(url_token, json=payload_token, headers=headers_token)  # 토큰 요청

    if response_token.status_code != 201:  # 응답 코드가 201이 아닌 경우
        raise HTTPException(
            status_code=response_token.status_code, detail="Failed to obtain token"
        )

    token = response_token.headers.get("X-Subject-Token")  # 응답 헤더에서 X-subject 토큰을 가져옴
    print(f"Token obtained: {token}")

    # 키페어 생성
    url_keypair = "https://0ec59da8-9bdb-465f-993f-eee695fc12aa.api.kr-central-2.kakaoi.io/api/v2/virtual-machine/keypair"  # 키페어 생성 URL
    headers_keypair = {
        "Content-Type": "application/json; charset=UTF-8",  # 요청 헤더 설정
        "X-Auth-Token": token,  # 인증 토큰 설정
    }
    data_keypair = {"name": keypair_name, "type": "ssh"}  # 키페어 생성 데이터
    response_keypair = requests.post(url_keypair, headers=headers_keypair, json=data_keypair)  # 키페어 생성 요청

    if response_keypair.status_code != 200:  # 응답 코드가 200이 아닌 경우
        raise HTTPException(
            status_code=response_keypair.status_code, detail="Failed to create keypair"
        )

    response_json = response_keypair.json()  # JSON 응답을 파싱(보통 문자열로 반응오기 때문에 데이터타입(딕셔너리)로 변환)
    private_key = response_json.get("keypair", {}).get("private_key")  # 프라이빗 키를 가져옴
    print(f"Keypair creation response: {response_json}")

    if private_key:  # 프라이빗 키가 존재하는 경우
        key_save_path = os.path.expanduser(f"/home/ubuntu/keypairs/{keypair_name}.pem")  # vm에 키 저장 경로 설정
        # os.path.expanduser: 사용자 디렉토리를 확장하여 절대 경로를 생성
        os.makedirs(os.path.dirname(key_save_path), exist_ok=True)  # 디렉토리가 없으면 생성
        with open(key_save_path, "w") as file:  # 파일을 열고
            file.write(private_key)  # 프라이빗 키를 파일에 씀
        print(f"Keypair created and saved at {key_save_path}")
    else:  # 프라이빗 키가 없는 경우
        raise HTTPException(status_code=500, detail="Private key not found")

    # VM 생성
    url_vm = "https://0ec59da8-9bdb-465f-993f-eee695fc12aa.api.kr-central-2.kakaoi.io/api/v2/virtual-machine/instances"  # VM 생성 URL
    headers_vm = {
        "Content-Type": "application/json; charset=UTF-8",  # 요청 헤더 설정
        "X-Auth-Token": token,  # 인증 토큰 설정
    }
    data_vm = {
        "count": 1,  # VM 생성 개수
        "name": vm_name,  # VM 이름
        "description": description,  # VM 설명
        "imageRef": image_ref,  # 이미지 ID, %%계속 이미지 ref 업데이트 됌%%
        "availabilityZone": availability_zone,  # 가용 영역
        "disableHyperthreading": False,  # 하이퍼스레딩 비활성화 여부
        "flavorRef": flavor_ref,  # 인스턴스 유형 ID
        "keyName": keypair_name,  # 키페어 이름
        "networks": [{"uuid": network_id}],  # 네트워크 ID
        "securityGroups": [{"name": security_group_name}],  # 보안 그룹 이름
        "userData": "",  # 사용자 데이터 (여기서는 비어 있음)
        "volumes": [
            {"isRoot": True, "deleteOnTermination": True, "volumeSize": volume_size}
        ],  # 루트 볼륨 정보
    }

    response_vm = requests.post(url_vm, headers=headers_vm, json=data_vm)  # VM 생성 요청

    if response_vm.status_code != 202:  # 응답 코드가 202가 아닌 경우
        raise HTTPException(
            status_code=response_vm.status_code, detail="Failed to create VM"
        )

    response_json = response_vm.json()  # JSON 응답을 파싱
    vm_id = response_json.get("server", {}).get("id")  # VM ID를 가져옴
    # server 키가 존재하면 값 반환, 없으면 {} 빈 딕셔너리 반환
    # get("server")한 결과에서 .get("id")로 해당하는 값 반환
    print(f"VM creation response: {response_json}")

    if not vm_id:  # VM ID가 없는 경우
        raise HTTPException(status_code=500, detail="VM ID not found")

    # VM이 활성화될 때까지 대기
    def get_vm_instances(auth_token, limit=20):  # VM 인스턴스를 가져오는 함수 정의
        url = "https://0ec59da8-9bdb-465f-993f-eee695fc12aa.api.kr-central-2.kakaoi.io/api/v2/virtual-machine/instances"  # VM 인스턴스 URL
        headers = {"X-Auth-Token": auth_token, "Content-Type": "application/json"}  # 요청 헤더 설정
        params = {"limit": limit}  # 요청 파라미터 설정
        response = requests.get(url, headers=headers, params=params)  # VM 인스턴스 요청
        if response.status_code == 200:  # 응답 코드가 200인 경우
            print("Successfully fetched VM instances.")
            instances = response.json()  # JSON 응답을 파싱
            if isinstance(instances, list):  # 인스턴스가 리스트인 경우
                return instances
            return instances.get("servers", [])  # 서버 리스트를 반환
        else:  # 응답 코드가 200이 아닌 경우
            print(
                f"Failed to fetch VM instances: {response.status_code}, {response.text}"
            )
            return None

    instance_status = None  # 인스턴스 상태 초기화
    while True:  # 무한 루프
        instances = get_vm_instances(token)  # VM 인스턴스를 가져옴
        if instances:  # 인스턴스가 존재하는 경우
            for instance in instances:  # 각 인스턴스에 대해
                if instance["name"] == vm_name:  # 인스턴스 이름이 VM 이름과 같은 경우
                    instance_status = instance.get("status", None)  # 인스턴스 상태를 가져옴
                    print(f"Current status of VM '{vm_name}': {instance_status}")
                    break

        if instance_status and instance_status.lower() == "active":  # 인스턴스 상태가 활성화된 경우
            print(f"VM '{vm_name}' is now ACTIVE.")
            break
        else:  # 인스턴스 상태가 활성화되지 않은 경우
            print(
                f"VM '{vm_name}' is not yet ACTIVE, current status: {instance_status}"
            )
            time.sleep(2)  # 2초 대기

    # 퍼블릭 IP 생성
    def get_floating_ips(auth_token):  # 플로팅 IP를 가져오는 함수 정의
        url = "https://0ec59da8-9bdb-465f-993f-eee695fc12aa.api.kr-central-2.kakaoi.io/api/v2/virtual-machine/floating-ips"  # 플로팅 IP URL
        headers = {
            "X-Auth-Token": auth_token,  # 인증 토큰 설정
            "Accept": "application/json",  # 요청 헤더 설정
        }
        response = requests.get(url, headers=headers)  # 플로팅 IP 요청
        if response.status_code == 200:  # 응답 코드가 200인 경우
            print("Successfully fetched floating IPs.")
            return response.json()  # JSON 응답을 반환
        else:  # 응답 코드가 200이 아닌 경우
            print(
                f"Failed to get floating IPs: {response.status_code}, {response.text}"
            )
            return None

    def assign_floating_ip(auth_token, floating_ip_id, vm_id):  # 플로팅 IP를 할당하는 함수 정의
        # url에 이미 생성된 플로팅 IP를 vm에 설정하는 방식
        url = f"https://0ec59da8-9bdb-465f-993f-eee695fc12aa.api.kr-central-2.kakaoi.io/api/v2/virtual-machine/instances/{vm_id}/floating-ip"  # 플로팅 IP 할당 URL
        headers = {
            "X-Auth-Token": auth_token,  # 인증 토큰 설정
            "Content-Type": "application/json",  # 요청 헤더 설정
        }
        data = {"floatingIpId": floating_ip_id}  # 플로팅 IP 데이터 설정
        response = requests.post(url, headers=headers, data=json.dumps(data))  # 플로팅 IP 할당 요청
        if response.status_code == 202:  # 응답 코드가 202인 경우
            print("Successfully assigned floating IP.")
        else:  # 응답 코드가 202가 아닌 경우
            print(
                f"Failed to assign floating IP: {response.status_code}, {response.text}"
            )
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to assign floating IP: {response.text}",
            )

    floating_ips = get_floating_ips(token)  # 플로팅 IP를 가져옴
    if floating_ips:  # 플로팅 IP가 존재하는 경우
        floating_ip_id = floating_ips[0]["id"]  # 첫 번째 플로팅 IP ID를 가져옴
        # 새롭게 IP 할당 했을 때 첫 번째 위치에 있어서 그런듯
        # VM을 삭제하는 경우에는 IP삭제까지 같이 진행되어야 IP자원 낭비 x
        assign_floating_ip(token, floating_ip_id, vm_id)  # 플로팅 IP를 VM에 할당

        floating_ip_address = None  # 플로팅 IP 주소 초기화
        while True:  # 무한 루프
            instances = get_vm_instances(token)  # VM 인스턴스를 가져옴
            if instances:  # 인스턴스가 존재하는 경우
                for instance in instances:  # 각 인스턴스에 대해
                    if instance["name"] == vm_name:  # 인스턴스 이름이 VM 이름과 같은 경우
                        for address in instance.get("addresses", []):  # 각 주소에 대해
                            if "floatingIp" in address:  # 플로팅 IP가 존재하는 경우
                                floating_ip_address = address["floatingIp"]  # 플로팅 IP 주소를 가져옴
                                break
                        if floating_ip_address:  # 플로팅 IP 주소가 존재하는 경우
                            break

            if floating_ip_address:  # 플로팅 IP 주소가 존재하는 경우
                print(f"퍼블릭 IP가 부여되었습니다: {floating_ip_address}")
                break
            else:  # 플로팅 IP 주소가 존재하지 않는 경우
                print("퍼블릭 IP가 아직 부여되지 않았습니다. 2초 후 다시 확인합니다.")
                time.sleep(2)  # 2초 대기

        if not floating_ip_address:  # 플로팅 IP 주소를 찾지 못한 경우
            print("Failed to retrieve the floating IP address.")
            raise HTTPException(
                status_code=500, detail="Failed to retrieve the floating IP address."
            )
    else:  # 사용 가능한 플로팅 IP가 없는 경우
        print("No available floating IPs found.")
        raise HTTPException(status_code=404, detail="No available floating IPs found")

    # 이메일 전송
    sender_email = "jjinjukks1227@naver.com"  # 발신자 이메일 주소
    sender_password = "dltjdgus!159"  # 발신자 이메일 비밀번호
    receiver_email = "jjinjukks1227@gmail.com"  # 수신자 이메일 주소

    body = f"""키 페어 및 VM 정보:

    키 페어 이름: {keypair_name}
    VM 이름: {vm_name}
    퍼블릭 IP: {floating_ip_address}
    이미지 ID: {image_ref}
    인스턴스 유형 ID: {flavor_ref}

    SSH 접속 명령어:
    ssh -i ~/Downloads/{keypair_name}.pem ubuntu@{floating_ip_address}
    """  # 이메일 본문 설정

    message = MIMEMultipart()  # 이메일 메시지 객체 생성
    message["From"] = sender_email  # 발신자 설정
    message["To"] = receiver_email  # 수신자 설정
    message["Subject"] = f"{vm_name} VM 정보 및 키 페어"  # 이메일 제목 설정

    message.attach(MIMEText(body, "plain"))  # 이메일 본문 추가

    # 키 페어 파일 첨부
    with open(f"/home/ubuntu//keypairs/{keypair_name}.pem", "rb") as attachment:  # 키 페어 파일 열기
        part = MIMEBase("application", "octet-stream")  # MIMEBase 객체 생성
        part.set_payload(attachment.read())  # 파일 내용을 설정

    encoders.encode_base64(part)  # 파일을 Base64로 인코딩
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {keypair_name}.pem",
    )  # 첨부 파일 헤더 설정

    message.attach(part)  # 메시지에 첨부 파일 추가

    try:
        server = smtplib.SMTP("smtp.naver.com", 587)  # SMTP 서버에 연결
        server.starttls()  # TLS 모드 시작
        server.login(sender_email, sender_password)  # 서버에 로그인
        server.sendmail(sender_email, receiver_email, message.as_string())  # 이메일 전송
        server.quit()  # 서버 연결 종료
    except Exception as e:  # 예외 발생 시
        print(f"Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {
        "message": f"VM created and assigned floating IP: {floating_ip_address}, email sent to {receiver_email}",
        "floating_ip_address": floating_ip_address,
        "keypair_name": keypair_name,
        "ssh_command": f"ssh -i ~/Downloads/{keypair_name}.pem ubuntu@{floating_ip_address}"
    }  # VM 생성 및 이메일 전송 결과 반환
    
