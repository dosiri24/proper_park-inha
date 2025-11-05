# Proper Park Inha - 프로젝트 개발 규칙

본 문서는 Proper Park Inha 프로젝트의 개발 원칙과 코딩 규칙을 정의합니다.

## 프로젝트 개요
프로젝트명: Proper Park Inha
목적: [프로젝트 목적 추가 예정]
개발 환경: [개발 환경 추가 예정]

---

## 핵심 개발 원칙

### 1. 엄격한 스코프 제한 (Strict Scope Discipline)
**원칙**: 지시받은 기능만 정확히 구현
- ✅ 요청된 기능의 정확한 구현
- ❌ 요청하지 않은 기능 추가 금지
- ❌ 확장성을 염두에 둔 사전 구현 금지
- ❌ "나중을 위한" 코드 작성 금지

**이유**:
- 프로젝트 복잡도 증가 방지
- 유지보수성 향상
- 명확한 요구사항 추적

**예시**:
```
요청: "로그인 기능 구현"
✅ 올바른 접근: 로그인 폼 + 인증 로직만 구현
❌ 잘못된 접근: 로그인 + 회원가입 + 비밀번호 찾기 + OAuth 통합
```

---

### 2. 철저한 문서화 (Comprehensive Documentation)
**원칙**: 모든 코드에 명확한 주석 작성
- 모든 함수에 목적, 매개변수, 반환값 설명
- 모든 클래스에 역할과 책임 설명
- 복잡한 로직에는 단계별 설명 추가
- 차기 수정자가 즉시 이해할 수 있는 수준

**주석 형식**:
```python
def calculate_park_score(location_data, facility_data):
    """
    공원 점수를 계산하는 함수

    Args:
        location_data (dict): 위치 정보 (latitude, longitude, address)
        facility_data (dict): 시설 정보 (type, count, condition)

    Returns:
        float: 0-100 사이의 공원 점수

    Note:
        점수 계산 로직:
        1. 위치 접근성 (40%)
        2. 시설 다양성 (30%)
        3. 시설 상태 (30%)
    """
    # 구현...
```

---

### 3. 무제한 리소스 활용 (Unlimited Resource Usage)
**원칙**: 토큰 제약 없이 최대한 완벽한 작업 수행
- MCP 도구 최대한 활용 (Context7, Sequential, Serena 등)
- 코드 분석 시 전체 파일 완전히 읽기
- 부분적 이해가 아닌 완전한 이해 추구
- 병렬 도구 호출로 효율성 극대화

**적용 사례**:
- ✅ 전체 파일 읽기: `Read(entire_file)`
- ✅ 여러 파일 동시 분석: `Read(file1), Read(file2), Read(file3)` 병렬 호출
- ✅ MCP 도구 활용: Serena로 심볼 탐색 → Context7로 패턴 확인 → Sequential로 분석
- ❌ 부분적 읽기: `Read(file, offset=100, limit=50)`

---

### 4. 실제 동작 코드만 작성 (Production-Ready Code Only)
**원칙**: 모든 코드는 즉시 프로덕션에 배포 가능해야 함
- ❌ 모킹 데이터 금지
- ❌ TODO 주석 금지
- ❌ `console.log()`, `print()` 디버깅 출력 금지
- ❌ 임시 테스트 코드 금지
- ✅ 실제 동작하는 완전한 구현만

**잘못된 예시**:
```python
# ❌ 절대 금지
def get_user_data():
    # TODO: 실제 데이터베이스 연결
    return {"mock": "data"}  # 임시 모킹

def process_data(data):
    print(f"Processing: {data}")  # 디버그 출력
```

**올바른 예시**:
```python
# ✅ 올바른 구현
def get_user_data(user_id):
    """실제 데이터베이스에서 사용자 데이터 조회"""
    return database.query(User).filter_by(id=user_id).first()
```

---

### 5. 최신 기술 리서치 우선 (Research-First for Trending Tech)
**원칙**: AI, 프레임워크 등 빠르게 변하는 기술은 리서치 먼저
- MCP Context7로 최신 공식 문서 확인
- MCP Tavily로 최신 베스트 프랙티스 검색
- 검증된 최신 방법론 적용

**적용 프로세스**:
1. 기술 스택 확인 필요 시 → Context7로 공식 문서 조회
2. 최신 트렌드 필요 시 → Tavily로 웹 리서치
3. 검증된 방법 확인 후 → 구현 시작

**예시**:
```
작업: "Next.js 14 서버 컴포넌트 구현"
1. Context7: Next.js 14 공식 문서 확인
2. Tavily: 2024년 Server Components 베스트 프랙티스 검색
3. 검증된 패턴으로 구현
```

---

### 6. 로깅 기반 개발 (Logging-Driven Development)
**원칙**: 철저한 로깅 시스템 구축 및 활용
- 모든 주요 함수에 로깅 추가
- 로그 레벨 적절히 사용 (DEBUG, INFO, WARNING, ERROR)
- 코드 수정 시 로그를 참고하여 영향 범위 파악

**로깅 구조**:
```python
import logging

logger = logging.getLogger(__name__)

def calculate_score(data):
    """점수 계산 함수"""
    logger.info(f"점수 계산 시작: data_size={len(data)}")

    try:
        result = complex_calculation(data)
        logger.info(f"점수 계산 완료: result={result}")
        return result
    except Exception as e:
        logger.error(f"점수 계산 실패: {str(e)}", exc_info=True)
        raise
```

---

### 7. 테스트 우선 개발 (Test-First Development)
**원칙**: 기능 구현 전 테스트 작성 및 검증
- 새 기능 추가 시: 테스트 작성 → 검증 → 기능 구현
- 검증된 방법으로만 실제 코드에 적용
- 실험적 코드는 별도 테스트 환경에서만

**프로세스**:
1. 기능 요구사항 분석
2. 테스트 케이스 작성
3. 테스트로 동작 검증
4. 검증된 방법으로 실제 코드 구현

**예시**:
```python
# 1단계: 테스트 먼저 작성
def test_park_score_calculation():
    """공원 점수 계산 테스트"""
    test_data = {
        "location": {"lat": 37.5, "lng": 127.0},
        "facilities": ["playground", "bench"]
    }
    score = calculate_park_score(test_data)
    assert 0 <= score <= 100

# 2단계: 테스트 검증
# 3단계: 실제 함수 구현
```

---

### 8. 명확한 네이밍 (Clear and Concise Naming)
**원칙**: 간결하면서 핵심을 담은 이름 사용
- 함수명: 동사 + 명사 (예: `calculate_score`, `get_user_data`)
- 클래스명: 명사 (예: `ParkAnalyzer`, `UserManager`)
- 파일명: 역할 반영 (예: `park_calculator.py`, `user_service.py`)
- 약어 최소화, 불가피한 경우만 사용

**네이밍 가이드**:
```python
# ✅ 좋은 예시
class ParkScoreCalculator:
    def calculate_accessibility_score(self, location):
        pass

# ❌ 나쁜 예시
class PSC:
    def calc_acc_scr(self, loc):
        pass
```

---

### 9. 전문가 수준 코드, 초보자 수준 설명
**원칙**: 코드는 최고 수준, 설명은 누구나 이해 가능하게
- 코드: SOLID 원칙, 디자인 패턴, 최적화 적용
- 설명: 비전공자도 이해할 수 있는 명확한 한글 설명
- 기술 용어 사용 시 괄호 안에 쉬운 설명 추가

**설명 예시**:
```
❌ "싱글톤 패턴으로 DB 커넥션 풀을 관리합니다"
✅ "데이터베이스 연결을 하나만 만들어서 여러 곳에서 같이 쓰도록 했습니다 (메모리 절약)"

❌ "O(n²) 복잡도로 인한 성능 저하"
✅ "데이터가 많아질수록 처리 시간이 급격히 늘어나는 문제가 있습니다"
```

---

### 10. 계획서 중심 개발 (Plan-Driven Development)
**원칙**: 모든 개발은 계획서 작성 후 진행
- 계획서에 코드 하드카피 첨부 금지
- '무엇을', '어떻게', '왜'에 집중
- 변경사항은 반드시 계획서에 동기화

**계획서 구조**:
```markdown
# [기능명] 구현 계획

## 1. 무엇을 (What)
- 구현할 기능의 명확한 정의
- 핵심 요구사항

## 2. 어떻게 (How)
- 구현 접근 방법
- 사용할 기술 스택
- 주요 단계

## 3. 왜 (Why)
- 이 접근 방법을 선택한 이유
- 고려한 대안과 선택 근거

## 4. 변경 이력
- [날짜] 변경 내용 및 사유
```

---

### 11. 계획서 실시간 동기화 (Live Plan Synchronization)
**원칙**: 개발 중 변경사항을 계획서에 즉시 반영
- 사용자 피드백으로 기능 추가/변경 시 → 계획서 업데이트
- 구현 중 발견된 이슈로 접근법 변경 시 → 계획서 업데이트
- 계획서와 실제 구현의 100% 동기화 유지

**업데이트 프로세스**:
1. 변경사항 발생
2. 계획서에 변경 내용 기록
3. 변경 사유 명시
4. 영향 범위 표시

---

### 12. 최소한의 에러 핸들링 (Minimal Error Handling)
**원칙**: 요청하지 않은 에러 처리 코드 작성 금지
- 예외 상황 발생 시 → 에러 반환만
- try-except 남용 금지
- 에러 처리 로직은 명시적 요청 시에만 구현

**기본 원칙**:
```python
# ✅ 기본 방식 (에러 처리 요청 없을 때)
def divide(a, b):
    """나눗셈 수행"""
    return a / b  # ZeroDivisionError는 호출자가 처리

# ✅ 에러 처리 요청 시에만
def divide_safe(a, b):
    """안전한 나눗셈 (에러 처리 포함)"""
    if b == 0:
        raise ValueError("0으로 나눌 수 없습니다")
    return a / b
```

---

## 도구 활용 가이드

### MCP 도구 우선순위
1. **Serena**: 심볼 탐색, 프로젝트 메모리, 세션 관리
2. **Context7**: 공식 문서, 프레임워크 패턴
3. **Sequential**: 복잡한 분석, 다단계 추론
4. **Tavily**: 최신 정보 리서치
5. **Magic**: UI 컴포넌트 생성
6. **Playwright**: 브라우저 테스트

### 작업별 도구 선택
| 작업 유형 | 주 도구 | 보조 도구 |
|----------|---------|----------|
| 코드 분석 | Serena | Sequential |
| 최신 기술 조사 | Tavily, Context7 | - |
| 복잡한 로직 설계 | Sequential | Serena |
| UI 구현 | Magic | Context7 |
| 테스트 | Playwright | - |

---

## 작업 체크리스트

### 기능 구현 전
- [ ] 요구사항 명확히 이해
- [ ] 계획서 작성 (What/How/Why)
- [ ] 최신 기술인 경우 리서치 수행
- [ ] 테스트 케이스 작성

### 구현 중
- [ ] 주석 철저히 작성
- [ ] 로깅 적절히 추가
- [ ] 실제 동작 코드만 작성 (모킹/TODO 금지)
- [ ] 요청된 기능만 구현

### 구현 후
- [ ] 테스트 통과 확인
- [ ] 계획서 동기화
- [ ] 코드 리뷰 (전문가 수준 확인)
- [ ] 설명 준비 (초보자 수준)

---

## 금지 사항 요약

### 절대 금지
❌ 요청하지 않은 기능 추가
❌ 확장성을 위한 사전 구현
❌ 모킹 데이터 사용
❌ TODO 주석
❌ `print()`, `console.log()` 디버깅 출력
❌ 임시 테스트 코드
❌ 요청하지 않은 에러 핸들링
❌ 계획서에 코드 하드카피

### 반드시 수행
✅ 지시받은 기능만 정확히 구현
✅ 모든 함수/클래스에 주석
✅ MCP 도구 최대한 활용
✅ 실제 동작하는 완전한 코드
✅ 최신 기술은 리서치 먼저
✅ 철저한 로깅
✅ 테스트 우선 개발
✅ 명확한 네이밍
✅ 계획서 작성 및 동기화

---

## 문서 버전 관리
- 버전: 1.0.0
- 최초 작성: 2025-11-04
- 최종 수정: 2025-11-04
- 작성자: AI Assistant with User Requirements

## 변경 이력
| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-11-04 | 1.0.0 | 초기 개발 규칙 정의 |
