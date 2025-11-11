# Proper Park Inha

인천광역시 미추홀구 도시공원의 VLM 기반 품질 평가 및 GIS 접근성 분석 연구

---

## 연구 개요

### 연구 목적
인천광역시 미추홀구의 도시공원 품질을 객관적으로 평가하고, 공원 접근성 사각지대를 도출하여 도시계획 개선방안을 제시합니다.

### 연구 배경
- 도시공원은 도시민의 삶의 질에 직접적인 영향을 미치는 중요한 도시기반시설
- 기존 공원 평가는 주관적 설문조사나 단순 통계에 의존
- VLM(Vision Language Model) 기술을 활용한 객관적이고 정량적인 평가 필요
- 실제 공원 이용자 관점에서의 환경 품질 평가 부재

### 연구 대상
- 지역: 인천광역시 미추홀구
- 대상: 도시공원 64개
- 이미지: 공원당 8방향 로드뷰 이미지 (약 500장)

---

## 연구 파이프라인

### 1. 데이터 수집 (완료)
- 미추홀구 도시공원정보 64개 (DATA.GO.KR)
- 공원별 로드뷰 이미지 8방향 × 64개
- 행정동 경계 및 인구 데이터 21개

**구현 기술**
- 카카오맵 API 로드뷰
- Playwright 브라우저 자동화
- 적응형 다방향 샘플링 (4/8/12방향)
- 공원 면적 기반 반경 자동 계산
- 성공률 기반 범위 자동 확대

### 2. VLM 기반 공원 환경 평가 (완료)
- 공원 가시성 (Visibility)
- 접근성 (Accessibility)
- 시각적 쾌적성 (Visual Amenity)
- 녹지 비율 (Green Coverage)

**구현 기술**
- Google Gemini 2.5 Flash
- Vision-Language Model 기반 이미지 분석
- 구조화된 JSON 출력
- 방향별 평가 결과 자동 저장
- 4개 항목 종합 점수 자동 계산 (0-10점 척도)

### 3. GIS 기반 접근성 분석 (예정)
- 서비스 권역 분석 → 사각지대 도출
- 행정동별 1인당 녹지 면적 산출
- 지구단위계획 예정지 중첩 분석

---

## 기술 스택

### 데이터 수집
- Python 3.x
- Playwright (브라우저 자동화)
- Kakao Map API (로드뷰)

### VLM 평가
- Google Gemini 2.5 Flash
- google-genai SDK (v0.6+)
- Pillow (이미지 처리)

### 분석 (예정)
- QGIS (공간 분석)
- Pandas (데이터 분석)

---

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. API 키 설정

`.env` 파일 생성 및 API 키 입력:

```env
# Kakao Maps API
KAKAO_API_KEY=발급받은_JavaScript_키

# Google Gemini API
GEMINI_API_KEY=발급받은_Gemini_API_키
GEMINI_MODEL=gemini-2.5-flash
```

**API 키 발급**
- Kakao: [Kakao Developers](https://developers.kakao.com/)
- Gemini: [Google AI Studio](https://aistudio.google.com/app/apikey)

### 3. 로드뷰 이미지 수집

```bash
# 테스트 (2개 공원)
python main.py

# 전체 공원 (64개)
python batch_capture_all_parks.py
```

### 4. VLM 기반 공원 평가

```bash
python evaluate_parks.py
```

**출력**: `output/[공원명]/evaluation.json`

---

## 프로젝트 구조

```
proper_park-inha/
├── data/                           # 연구 데이터
│   └── 인천광역시_미추홀구_도시공원정보_20250105.csv
│
├── src/                            # 코어 모듈
│   ├── roadview_client.py         # 카카오 로드뷰 클라이언트
│   ├── park_sampler.py            # 공원 다방향 샘플링
│   ├── adaptive_capture.py        # 적응형 캡처 관리자
│   ├── gemini_evaluator.py        # Gemini VLM 평가
│   └── templates/                 # HTML 템플릿
│
├── docs/                           # 연구 문서
│   └── prompts/                   # LLM 프롬프트
│
├── output/                         # 결과물
│   └── [공원명]/
│       ├── [방향].jpg             # 로드뷰 이미지
│       └── evaluation.json        # VLM 평가 결과
│
├── main.py                         # 테스트 캡처 (2개 공원)
├── batch_capture_all_parks.py     # 전체 공원 캡처 (64개)
├── evaluate_parks.py              # VLM 평가 실행
├── .env                            # 환경 변수 (API 키)
├── requirements.txt                # Python 의존성
└── README.md
```

---

## 주요 기능

### 적응형 다방향 샘플링
- 공원 크기별 자동 방향 결정
  - 소형 (< 2,000㎡): 4방향
  - 중형 (2,000-5,000㎡): 6-8방향
  - 대형 (> 5,000㎡): 12방향

### 면적 기반 반경 자동 계산
- 공원 면적을 원형으로 가정하여 최적 샘플링 반경 계산
- 타입별 최소/최대 제한 적용

### 적응형 범위 확대
- 초기 성공률 < 60%: 반경 자동 증가 (0.4배씩, 최대 2.5배)
- 이미 캡처된 방향 스킵

---

## 문제 해결

### API 키 오류
- `.env` 파일에 API 키가 정확히 입력되었는지 확인
- Kakao: JavaScript 키 (REST API 키 아님)
- Gemini: [Google AI Studio](https://aistudio.google.com/app/apikey)에서 발급

### Playwright 오류
```bash
playwright install chromium
```

### Gemini API 할당량 초과
- Google AI Studio에서 사용량 확인
- 유료 요금제 전환 또는 다음 날 재시도

---

## 연구 정보

- 소속: 인하대학교 도시계획론
- 연구 기간: 2025년 2학기
- 연구 지역: 인천광역시 미추홀구

---

## 라이선스

MIT License
