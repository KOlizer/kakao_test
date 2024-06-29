# main.py
from fastapi import FastAPI, HTTPException
from kubernetes import client, config
from kubernetes.client.rest import ApiException

app = FastAPI()

# Kubernetes 클라이언트 설정 (토큰 사용)
KUBERNETES_HOST = "https://51d9835d-8e18-4b80-920c-3098961b5ff3-public.ke.kr-central-2.kakaocloud.com:443"  # Kubernetes API 서버 URL
KUBERNETES_TOKEN = "gAAAAABmf1gbpPnpSpAauorq0SsE5ETwRL7kacIMKdM06RMfmWG5e7l9sDLUKp1z9OUz6gS5r2Myd3a173quheG6GoZE6HJix-aVa1P7OUKiu7_gPnI0Sr1Bp6HmU6DO4iTVTrqe8sbphMCA3FEUstj6Djquau5OCN2DxHVlx1q2qP8wLqZP22GkGoE4sVc3xQYmaQov_bij"  # 제공받은 토큰

configuration = client.Configuration()
configuration.host = KUBERNETES_HOST
configuration.verify_ssl = False  # SSL 인증서를 검증하지 않으려면 False로 설정
configuration.api_key = {"authorization": f"Bearer {KUBERNETES_TOKEN}"}

client.Configuration.set_default(configuration)

@app.get("/clusters/{cluster_name}")
async def get_clusters(cluster_name: str):
    try:
        v1 = client.CoreV1Api()
        nodes = v1.list_node()
        return {
            "cluster_name": cluster_name,
            "nodes": [node.metadata.name for node in nodes.items]
        }
    except ApiException as e:
        raise HTTPException(status_code=e.status, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
