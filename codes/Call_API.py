import requests

# 발급받은 인증 토큰
auth_token = 'Auth Token: gAAAAABmfiQVUhejOfpjR18bb7wb63YybupkWD-nyHquhAWHybtwtSDdFJ-7uCwFhM2IKOR42GifXlePaqBnaB018k5ywGYaX7VAI6OmiFRfGStNPxxVa9j4ygEzMta6noxbnic0oTNuR_cXR91T_HAy78YutGAxa0qoxYcTo2i9tAGT_T9ILs8j6v3nOL0PWPvDTlrzctrs'

# 번역할 텍스트 설정
text_to_translate = "안녕하세요, 어떻게 도와드릴까요?"

# 번역 API 요청 URL 설정
translate_url = "https://api.kakaocloud.com/translate"

# 요청 헤더 설정
translate_headers = {
    "Authorization": f"Bearer {auth_token}",
    "Content-Type": "application/json"
}

# 요청 바디 설정
translate_data = {
    "source_lang": "kr",
    "target_lang": "en",
    "query": text_to_translate
}

# 번역 API 호출
translate_response = requests.post(translate_url, headers=translate_headers, json=translate_data)

# 응답 데이터 출력
if translate_response.status_code == 200:
    translated_text = translate_response.json().get('translated_text')
    print(f"Translated Text: {translated_text}")
else:
    print(f"Error: {translate_response.status_code}, {translate_response.text}")
