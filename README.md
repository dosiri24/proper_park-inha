# Kakao Roadview Capture

카카오맵 로드뷰를 Python + Playwright로 캡처하는 프로젝트

## 특징

- ✅ 카카오맵 로드뷰 정식 사용
- ✅ 위경도 좌표 하드코딩 가능
- ✅ 한국 지역 커버리지 우수
- ✅ Playwright 브라우저 자동화

## 설치

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. Playwright 브라우저 설치

```bash
playwright install chromium
```

### 3. 카카오 API 키 발급

1. [Kakao Developers](https://developers.kakao.com/) 접속
2. **애플리케이션 추가하기**
3. **플랫폼 설정** → **Web 플랫폼 추가** → 사이트 도메인 등록 (로컬 테스트: `http://localhost`)
4. **앱 키** → **JavaScript 키** 복사

### 4. .env 파일 설정

`.env` 파일을 열고 발급받은 JavaScript 키 입력:

```
KAKAO_API_KEY=발급받은_JavaScript_키
```

## 사용법

### VSCode에서 실행 (권장)

1. `main.py` 열기
2. **F5** 또는 **실행 버튼** 클릭
3. `output/` 폴더에 이미지 저장됨

### 터미널에서 실행

```bash
python main.py
```

## 좌표 수정

`main.py` 파일의 `locations` 리스트에서 위경도 좌표 수정:

```python
locations = [
    {'name': '서울시청', 'lat': 37.5665851, 'lng': 126.9782038},
    {'name': '경복궁', 'lat': 37.579617, 'lng': 126.977041},
    {'name': '인하대학교', 'lat': 37.447155, 'lng': 126.654062},
    # 원하는 위치 추가
    {'name': '새로운 장소', 'lat': 위도, 'lng': 경도},
]
```

## 프로젝트 구조

```
proper_park-inha/
├── .env                       # API 키 (Git에 커밋 금지)
├── requirements.txt           # Python 의존성
├── main.py                    # 메인 실행 파일
├── src/
│   ├── __init__.py
│   ├── roadview_client.py     # 로드뷰 클라이언트
│   └── roadview_template.html # HTML 템플릿
└── output/                    # 캡처된 이미지 저장
    ├── 서울시청.jpg
    ├── 경복궁.jpg
    └── 인하대학교.jpg
```

## API 사용 방법

```python
from src import RoadviewClient

# 클라이언트 생성
client = RoadviewClient()

# 로드뷰 메타데이터 조회
metadata = client.get_roadview_metadata(lat=37.5665, lng=126.9779)
print(metadata)

# 로드뷰 이미지 캡처
success = client.capture_roadview(
    lat=37.5665,
    lng=126.9779,
    output_path="output/example.jpg",
    width=1200,
    height=800
)
```

## 주의사항

### 로드뷰가 없는 경우

일부 위치에는 로드뷰가 없을 수 있습니다. 이 경우:
- 에러 메시지가 표시된 화면이 캡처됩니다
- 가까운 도로 위치로 좌표를 조정해보세요

### API 키 보안

- `.env` 파일을 **절대 Git에 커밋하지 마세요**
- `.gitignore`에 `.env`가 포함되어 있는지 확인하세요

## 문제 해결

### "KAKAO_API_KEY가 설정되지 않았습니다"

→ `.env` 파일에 API 키를 정확히 입력했는지 확인

### "HTML 템플릿을 찾을 수 없습니다"

→ `src/roadview_template.html` 파일이 있는지 확인

### Playwright 오류

→ `playwright install chromium` 실행

### 로드뷰가 표시되지 않음

→ 카카오 개발자 사이트에서 Web 플랫폼 도메인이 제대로 등록되었는지 확인

## 라이선스

MIT License
