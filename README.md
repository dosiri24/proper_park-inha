# Proper Park Inha - 도시공원 품질 평가 연구

**인천광역시 미추홀구 도시공원의 VLM 기반 품질 평가 및 GIS 접근성 분석**

## 📋 연구 개요

### 연구 목적
인천광역시 미추홀구의 도시공원 품질을 객관적으로 평가하고, 공원 접근성 사각지대를 도출하여 도시계획 개선방안을 제시합니다.

### 연구 배경
- 도시공원은 도시민의 삶의 질에 직접적인 영향을 미치는 중요한 도시기반시설
- 기존 공원 평가는 주관적 설문조사나 단순 통계에 의존
- **VLM(Vision Language Model)** 기술을 활용한 객관적이고 정량적인 평가 필요
- 실제 공원 이용자 관점에서의 환경 품질 평가 부재

### 연구 대상
- **지역**: 인천광역시 미추홀구
- **대상**: 도시공원 64개
- **이미지**: 공원당 8방향 로드뷰 이미지 (약 500장)

---

## 🔬 연구 파이프라인

### 1️⃣ 데이터 수집 (완료 ✅)
```
📊 DATA.GO.KR 공공데이터
├─ 미추홀구 도시공원정보 (64개)
├─ 공원별 로드뷰 이미지 (8방향 × 64개)
└─ 행정동 경계 및 인구 데이터 (21개)
```

**구현 기술**:
- 카카오맵 API 로드뷰
- Playwright 브라우저 자동화
- 적응형 다방향 샘플링 (4/8/12방향)
- 공원 면적 기반 반경 자동 계산
- 성공률 기반 범위 자동 확대

---

### 2️⃣ VLM 기반 공원 환경 평가 (완료 ✅)
```
🤖 Gemini 0-10점 척도 평가
├─ 공원 가시성 (Visibility)
├─ 접근성 (Accessibility)
├─ 시각적 쾌적성 (Visual Amenity)
└─ 녹지 비율 (Green Coverage)
```

**구현 기술**:
- Google Gemini 2.5 Flash (2025 최신 모델)
- 새로운 google-genai SDK 사용
- Vision-Language Model 기반 이미지 분석
- 구조화된 JSON 출력 (response_mime_type)
- 방향별 평가 결과 자동 저장
- 4개 항목 종합 점수 자동 계산

---

### 3️⃣ GIS 기반 접근성 분석 (예정 ⏳)
```
🗺️ QGIS 공간 분석
├─ 서비스 권역 분석 → 사각지대 도출
├─ 행정동별 1인당 녹지 면적 산출
└─ 지구단위계획 예정지 중첩 분석
```

---

## 📂 프로젝트 구조

```
proper_park-inha/
├── data/                           # 연구 데이터
│   └── 인천광역시_미추홀구_도시공원정보_20250105.csv
│
├── src/                            # 코어 모듈
│   ├── __init__.py
│   ├── roadview_client.py         # 카카오 로드뷰 클라이언트
│   ├── park_sampler.py            # 공원 다방향 샘플링
│   ├── adaptive_capture.py        # 적응형 캡처 관리자
│   ├── gemini_evaluator.py        # Gemini VLM 평가 클라이언트
│   └── templates/                 # HTML 템플릿
│       ├── roadview_template.html
│       └── roadview_template_multidir.html
│
├── docs/                           # 연구 문서
│   └── prompts/                   # LLM 프롬프트
│       └── park_evaluation_prompt.md
│
├── output/                         # 결과물
│   └── [공원명]/                  # 공원별 결과
│       ├── 북.jpg                 # 로드뷰 이미지
│       ├── 북동.jpg
│       ├── ...
│       └── evaluation.json        # VLM 평가 결과
│
├── .claude/                        # 프로젝트 설정
│   └── CLAUDE.md
│
├── main.py                         # 테스트용 캡처 (2개 공원)
├── batch_capture_all_parks.py     # 전체 공원 일괄 캡처
├── evaluate_parks.py              # VLM 기반 공원 평가
├── .env                            # 환경 변수 (API 키)
├── .env.example                    # 환경 변수 예시
├── requirements.txt                # Python 의존성
└── README.md                       # 프로젝트 문서
```

---

## 🚀 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. API 키 설정

#### 카카오 API 키
1. [Kakao Developers](https://developers.kakao.com/) 접속
2. **애플리케이션 추가** → **JavaScript 키** 발급
3. `.env` 파일에 API 키 입력

#### Gemini API 키
1. [Google AI Studio](https://aistudio.google.com/app/apikey) 접속
2. **Create API Key** 클릭하여 키 발급
3. `.env` 파일에 API 키 입력

#### .env 파일 설정
```env
# Kakao Maps API
KAKAO_API_KEY=발급받은_JavaScript_키

# Google Gemini API (2025 최신)
GEMINI_API_KEY=발급받은_Gemini_API_키
GEMINI_MODEL=gemini-2.5-flash  # 빠르고 저렴 (권장)
```

### 3. 로드뷰 이미지 수집

#### 테스트 캡처 (2개 공원)
```bash
python main.py
```

#### 전체 공원 일괄 캡처 (64개 공원)
```bash
python batch_capture_all_parks.py
```

**출력 결과**:
- `output/[공원명]/[방향].jpg`
- 예: `output/한나루어린이공원/북.jpg`

### 4. VLM 기반 공원 평가

로드뷰 이미지를 Gemini API로 평가합니다.

```bash
python evaluate_parks.py
```

**평가 항목** (각 0-10점):
- 공원 가시성 (Visibility)
- 접근성 (Accessibility)
- 시각적 쾌적성 (Visual Amenity)
- 녹지 비율 (Green Coverage)

**출력 결과**:
- `output/[공원명]/evaluation.json`
- 방향별 평가 점수 및 종합 평가

---

## 🎯 주요 기능

### ⭐ 적응형 다방향 샘플링
- **공원 크기별 자동 방향 결정**
  - 소형 공원 (< 2,000㎡): 4방향
  - 중형 공원 (2,000-5,000㎡): 6-8방향
  - 대형 공원 (> 5,000㎡): 12방향

### 🔥 면적 기반 반경 자동 계산
- 공원 면적을 원형으로 가정하여 최적 샘플링 반경 계산
- 타입별 최소/최대 제한 적용
- 공원 경계 근처에서 로드뷰 캡처

### 🚀 적응형 범위 확대
- 초기 성공률 < 60%: 반경 자동 증가 (0.4배씩)
- 최대 2.5배까지 확대
- 이미 캡처된 방향은 스킵

### 💡 로딩 최적화
- JavaScript 완전 로딩 후 2초 대기
- 스크린샷 촬영 전 1초 추가 대기
- 뿌연 이미지 문제 해결

---

## 📊 연구 진행 현황

| 단계 | 내용 | 상태 |
|------|------|------|
| 2.1 | 데이터 수집 (로드뷰 이미지) | ✅ 완료 |
| 2.2 | 선행연구 검토 | ✅ 완료 |
| 2.3 | VLM 기반 공원 평가 시스템 구축 | ✅ 완료 |
| 2.4 | 전체 공원 평가 실행 | 🔄 진행중 |
| 2.5 | GIS 접근성 분석 | ⏳ 예정 |

---

## 🛠️ 기술 스택

### 데이터 수집
- **Python 3.x**: 프로젝트 언어
- **Playwright**: 브라우저 자동화
- **Kakao Map API**: 로드뷰 이미지
- **Adaptive Sampling**: 면적 기반 최적화

### VLM 평가
- **Google Gemini 2.5 Flash**: 최신 Vision-Language Model (2025)
- **google-genai SDK**: 통합 Gemini Python SDK (v0.6+)
- **Pillow**: 이미지 처리
- **JSON**: 구조화된 평가 결과 저장

### 분석 (예정)
- **QGIS**: GIS 기반 접근성 분석
- **Pandas**: 데이터 분석 및 통계

---

## 📝 개발 규칙

본 프로젝트는 엄격한 개발 원칙을 따릅니다. 자세한 내용은 [.claude/CLAUDE.md](.claude/CLAUDE.md) 참조.

**핵심 원칙**:
- ✅ 지시받은 기능만 정확히 구현
- ✅ 철저한 문서화 및 주석
- ✅ 실제 동작하는 완전한 코드만 작성
- ✅ 최신 기술은 리서치 먼저
- ❌ 모킹 데이터, TODO 주석 금지
- ❌ 요청하지 않은 기능 추가 금지

---

## 🔧 문제 해결

### "KAKAO_API_KEY가 설정되지 않았습니다"
→ `.env` 파일에 카카오 API 키를 정확히 입력했는지 확인

### "GEMINI_API_KEY가 설정되지 않았습니다"
→ `.env` 파일에 Gemini API 키를 정확히 입력했는지 확인
→ [Google AI Studio](https://aistudio.google.com/app/apikey)에서 키 발급

### "HTML 템플릿을 찾을 수 없습니다"
→ `src/templates/` 폴더에 HTML 파일이 있는지 확인

### "평가 프롬프트를 찾을 수 없습니다"
→ `docs/prompts/park_evaluation_prompt.md` 파일이 있는지 확인

### Playwright 오류
→ `playwright install chromium` 실행

### Gemini API 할당량 초과
→ Google AI Studio에서 API 사용량 확인
→ 유료 요금제 전환 또는 다음 날 재시도

### 로드뷰가 표시되지 않음
→ 카카오 개발자 사이트에서 Web 플랫폼 도메인이 제대로 등록되었는지 확인

---

## 📄 라이선스

MIT License

---

## 👤 연구자

- **소속**: 인하대학교 도시계획론
- **연구 기간**: 2025년 2학기
- **연구 지역**: 인천광역시 미추홀구

---

## 📧 문의

프로젝트 관련 문의사항은 이슈를 등록해주세요.
