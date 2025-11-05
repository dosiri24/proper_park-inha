# Kakao Roadview Capture - Adaptive Multi-Direction Park Sampling

카카오맵 로드뷰를 Python + Playwright로 캡처하는 프로젝트 (적응형 다방향 샘플링)

## 특징

- ✅ 카카오맵 로드뷰 정식 사용
- ✅ 위경도 좌표 하드코딩 가능
- ✅ 한국 지역 커버리지 우수
- ✅ Playwright 브라우저 자동화
- ⭐ **공원 다방향 샘플링** (4방향, 8방향, 12방향, 적응형)
- ⭐ **자동 방향 조정** (카메라가 공원 중심을 향하도록)
- 🔥 **면적 기반 반경 계산** (공원 크기에 맞는 최적 거리)
- 🔥 **적응형 범위 확대** (성공률 낮으면 반경 자동 증가)
- 🔥 **로딩 최적화** (뿌연 이미지 방지)

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

## 적응형 다방향 샘플링

### 기본 사용법

`main.py`의 `parks` 리스트에 공원 정보 추가:

```python
parks = [
    {
        'name': '매소홀어린이공원',
        'lat': 37.441929,           # 공원 중심 위도
        'lng': 126.654533,          # 공원 중심 경도
        'type': '어린이공원',        # 공원 타입
        'area': 3006.9,             # 공원 면적 (㎡)
        'num_directions': 8,        # 8방향 샘플링
    },
    {
        'name': '수봉공원',
        'lat': 37.460187,
        'lng': 126.664212,
        'type': '근린공원',
        'area': 332694,             # 대형 공원
        'num_directions': 12,       # 12방향 샘플링
    },
]
```

### 적응형 캡처 시스템

시스템이 자동으로 다음을 처리합니다:

1. **면적 기반 반경 계산**
   - 공원 면적을 원형으로 가정하여 최적 반경 자동 계산
   - 계산식: `반경 = sqrt(면적/π) × 0.6`
   - 타입별 최소/최대 제한 적용

2. **적응형 범위 확대**
   - 초기 시도: 계산된 기본 반경
   - 성공률 < 60%: 반경을 0.4배씩 증가
   - 최대 2.5배까지 자동 확대
   - 이미 캡처된 방향은 스킵

3. **로딩 최적화**
   - JavaScript 로딩 후 2초 추가 대기
   - 스크린샷 촬영 전 1초 추가 대기
   - 뿌연 이미지 문제 해결

### 타입별 반경 제한

| 공원 타입 | 최소 반경 | 최대 반경 |
|----------|----------|----------|
| 어린이공원 | 15m | 40m |
| 소공원 | 20m | 50m |
| 근린공원 | 30m | 80m |
| 도시공원 | 50m | 150m |

### 샘플링 방향 개수

- **4방향**: 북, 동, 남, 서
- **8방향**: 북, 북동, 동, 남동, 남, 남서, 서, 북서
- **12방향**: 30도 간격 세밀 샘플링
- **16방향**: 22.5도 간격 초정밀 샘플링

### 결과 예시

```
output/
  매소홀어린이공원/
    ├── 북.jpg
    ├── 북동.jpg
    ├── 동.jpg
    ├── 남동.jpg
    ├── 남.jpg
    ├── 남서.jpg
    ├── 서.jpg
    └── 북서.jpg
  수봉공원/
    ├── 북.jpg
    ├── 남.jpg
    ├── 동.jpg
    └── ...
```

## 프로젝트 구조

```
proper_park-inha/
├── .env                                # API 키 (Git에 커밋 금지)
├── requirements.txt                    # Python 의존성
├── main.py                             # 메인 실행 파일 (적응형 샘플링)
├── batch_capture_all_parks.py          # 전체 공원 일괄 캡처
├── 인천광역시_미추홀구_도시공원정보_20250105.csv  # 공원 데이터
├── src/
│   ├── __init__.py
│   ├── roadview_client.py              # 로드뷰 클라이언트
│   ├── park_sampler.py                 # 공원 샘플링 전략
│   ├── adaptive_capture.py             # 적응형 캡처 관리자
│   ├── roadview_template.html          # 기본 HTML 템플릿
│   └── roadview_template_multidir.html # 다방향 샘플링 템플릿
├── claudedocs/
│   └── park_polygon_research_2025.md   # 공원 폴리곤 리서치 결과
└── output/                             # 캡처된 이미지 저장
    ├── 매소홀어린이공원/
    │   ├── 북.jpg
    │   ├── 북동.jpg
    │   └── ...
    └── 수봉공원/
        └── ...
```

## API 사용 방법

### 기본 사용법

```python
from src import RoadviewClient

# 클라이언트 생성
client = RoadviewClient()

# 로드뷰 메타데이터 조회
metadata = client.get_roadview_metadata(lat=37.5665, lng=126.9779)
print(metadata)

# 로드뷰 이미지 캡처 (단일 위치)
success = client.capture_roadview(
    lat=37.5665,
    lng=126.9779,
    output_path="output/example.jpg",
    width=1200,
    height=800
)
```

### 다방향 샘플링 사용법

```python
from src import RoadviewClient
from src.park_sampler import ParkSampler

# 클라이언트와 샘플러 생성
client = RoadviewClient()
sampler = ParkSampler()

# 8방향 샘플링 포인트 생성
points = sampler.generate_circular_points(
    park_name='매소홀어린이공원',
    center_lat=37.441929,
    center_lng=126.654533,
    park_type='어린이공원',
    num_directions=8
)

# 각 방향에서 로드뷰 캡처
for point in points:
    client.capture_roadview_multidir(
        sample_lat=point['sample_lat'],   # 로드뷰 찾을 위치
        sample_lng=point['sample_lng'],
        target_lat=point['target_lat'],   # 카메라가 볼 방향
        target_lng=point['target_lng'],
        output_path=f"output/{point['park_name']}_{point['direction']}.jpg"
    )
```

### 적응형 샘플링 사용법

```python
# 공원 면적에 따라 자동으로 전략 결정
points = sampler.generate_adaptive_points(
    park_name='자동공원',
    center_lat=37.xxx,
    center_lng=126.xxx,
    estimated_area_sqm=5000  # 5000㎡
)
# 면적에 따라 자동으로 4/8방향, 단일/이중 링 결정
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
