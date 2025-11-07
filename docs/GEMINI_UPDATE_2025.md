# Gemini API 업데이트 (2025년 11월)

## 변경 사항 요약

### 1. 라이브러리 마이그레이션
**이전**: `google-generativeai` (레거시, 2025년 11월 지원 종료)  
**현재**: `google-genai` (통합 SDK, 2025년 최신)

### 2. 모델 업그레이드
**이전**: `gemini-2.0-flash-exp` (실험 버전)  
**현재**: `gemini-2.5-flash` (안정 버전, 15배 저렴)

### 3. API 패턴 변경

#### 이전 (google-generativeai)
```python
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content([prompt, image])
```

#### 현재 (google-genai)
```python
from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=[prompt, image_part],
    config=types.GenerateContentConfig(
        response_mime_type="application/json"  # 구조화된 출력
    )
)
```

## 주요 개선사항

### 1. 구조화된 JSON 출력
```python
config=types.GenerateContentConfig(
    response_mime_type="application/json"
)
```
→ Gemini가 자동으로 올바른 JSON 형식으로 응답

### 2. 이미지 처리 개선
```python
# 바이트로 이미지 전달
image_part = types.Part.from_bytes(
    data=img_bytes,
    mime_type='image/jpeg'
)
```

### 3. 더 나은 설정 제어
```python
config=types.GenerateContentConfig(
    temperature=0.2,      # 일관성 향상
    top_p=0.95,
    top_k=40,
    max_output_tokens=2048
)
```

## 성능 비교

### Gemini 2.5 Flash vs 2.0 Flash

| 항목 | 2.0 Flash | 2.5 Flash |
|------|-----------|-----------|
| 속도 | 빠름 | 더 빠름 (274 tokens/s) |
| 가격 | 기준 | 15배 저렴 |
| Context | 1M tokens | 1M tokens |
| 정확도 | 좋음 | 개선됨 |
| 비전 능력 | 우수 | 더 우수 (Enhanced) |

### 비용 절감
- **입력**: $0.075 per 1M tokens (2.5 Flash)
- **출력**: $0.30 per 1M tokens (2.5 Flash)
- **Pro 대비**: 약 15배 저렴

## 마이그레이션 가이드

### 1. 패키지 업데이트
```bash
# 기존 패키지 제거
pip uninstall google-generativeai

# 새 패키지 설치
pip install google-genai>=0.6.0
```

### 2. 코드 수정
```python
# AS-IS
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name)
response = model.generate_content([prompt, image])

# TO-BE
from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)
image_part = types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg')
response = client.models.generate_content(
    model=model_name,
    contents=[prompt, image_part],
    config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)
```

### 3. 환경변수 업데이트
```env
# .env
GEMINI_MODEL=gemini-2.5-flash  # 2.0-flash-exp → 2.5-flash
```

## 새로운 기능

### 1. Native Multimodal
- 텍스트, 이미지, 오디오, 비디오 통합 처리
- 단일 API로 모든 모달리티 지원

### 2. Enhanced Vision
- 객체 감지 (Object Detection)
- 세그멘테이션 (Segmentation)
- 이미지 편집 (Image Editing) - 2.5 Flash Image

### 3. Thinking Models
- 응답 전 추론 과정 수행
- 더 정확한 결과

## 참고 자료

- [Google GenAI SDK GitHub](https://github.com/googleapis/python-genai)
- [Gemini API 공식 문서](https://ai.google.dev/gemini-api/docs)
- [모델 비교](https://ai.google.dev/gemini-api/docs/models)
- [Vision 가이드](https://ai.google.dev/gemini-api/docs/vision)

## 지원 종료 일정

- **google-generativeai**: 2025년 11월 30일 지원 종료
- **마이그레이션 권장**: 즉시

---

**업데이트 날짜**: 2025-11-05  
**작성자**: AI Assistant
