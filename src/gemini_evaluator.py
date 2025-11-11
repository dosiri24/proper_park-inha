"""
Gemini API를 사용한 공원 이미지 평가 모듈 (2025년 최신 버전)

google-genai SDK를 사용하여 공원 로드뷰 이미지를 분석하고
접근성, 가시성, 쾌적성, 녹지 비율 등을 평가합니다.
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Optional
from google import genai
from google.genai import types, errors
from PIL import Image
from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일 명시적으로 로드 (기존 환경변수 덮어쓰기)
_env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=_env_path, override=True)

logger = logging.getLogger(__name__)


class GeminiEvaluator:
    """Gemini API를 사용한 공원 이미지 평가 클라이언트 (2025 최신 버전)"""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        초기화

        Args:
            api_key: Google Gemini API 키 (없으면 환경변수에서 로드)
            model_name: 사용할 모델명 (기본: gemini-2.5-flash)
        """
        # API 키 설정
        if not api_key:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError(
                    "GEMINI_API_KEY가 설정되지 않았습니다.\n"
                    ".env 파일에 GEMINI_API_KEY를 설정하거나\n"
                    "GeminiEvaluator(api_key='your_key')로 전달하세요."
                )
            # 공백 제거
            api_key = api_key.strip()
            logger.info(f"API 키 로드 완료 (길이: {len(api_key)}자)")

        # 모델명 설정 (2025년 최신 모델 사용)
        if not model_name:
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

        self.api_key = api_key
        self.model_name = model_name

        # 재시도 설정 (503 에러 대응)
        self.max_retries = int(os.getenv('GEMINI_MAX_RETRIES', '5'))
        self.initial_retry_wait = float(os.getenv('GEMINI_RETRY_WAIT', '2.0'))

        # Gemini Client 초기화 (새로운 SDK)
        self.client = genai.Client(api_key=self.api_key)

        logger.info(f"GeminiEvaluator 초기화 완료 (Model: {self.model_name})")
        logger.info(f"재시도 설정: 최대 {self.max_retries}회, 초기 대기 {self.initial_retry_wait}초")

        # 프롬프트 로드
        self.prompt_path = Path(__file__).parent.parent / 'docs' / 'prompts' / 'park_evaluation_prompt.md'
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"평가 프롬프트를 찾을 수 없습니다: {self.prompt_path}")

        with open(self.prompt_path, 'r', encoding='utf-8') as f:
            self.evaluation_prompt = f.read()

        logger.info(f"평가 프롬프트 로드 완료: {self.prompt_path}")

    def evaluate_image(
        self,
        image_path: str,
        park_name: str,
        direction: str
    ) -> Dict:
        """
        공원 이미지를 평가합니다

        Args:
            image_path: 이미지 파일 경로
            park_name: 공원 이름
            direction: 방향 (북, 남, 동, 서 등)

        Returns:
            평가 결과 딕셔너리
            {
                'visibility': {'score': int, 'reason': str},
                'accessibility': {'score': int, 'reason': str},
                'visual_amenity': {'score': int, 'reason': str},
                'green_coverage': {'score': int, 'reason': str},
                'overall_score': float,
                'summary': str
            }
        """
        logger.info(f"이미지 평가 시작: {park_name} - {direction} ({image_path})")

        try:
            # 이미지 로드 및 바이트 변환
            with Image.open(image_path) as img:
                # 이미지를 바이트로 변환
                import io
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_bytes = img_byte_arr.getvalue()

            # 평가 프롬프트에 공원 정보 추가
            full_prompt = (
                f"공원명: {park_name}\n"
                f"방향: {direction}\n\n"
                f"{self.evaluation_prompt}"
            )

            # 이미지를 Part 객체로 생성
            image_part = types.Part.from_bytes(
                data=img_bytes,
                mime_type='image/jpeg'
            )

            # Gemini API 호출 (재시도 로직 포함)
            logger.info(f"Gemini API 호출 중... (모델: {self.model_name})")

            response = None
            last_error = None
            response_text = None

            for attempt in range(self.max_retries):
                try:
                    # JSON Schema 정의
                    response_schema = {
                        "type": "object",
                        "properties": {
                            "facility_maintenance": {
                                "type": "object",
                                "properties": {
                                    "level": {"type": "string", "enum": ["low", "medium", "high", "not_visible"]},
                                    "reason": {"type": "string"}
                                },
                                "required": ["level", "reason"]
                            },
                            "rest_facilities": {
                                "type": "object",
                                "properties": {
                                    "level": {"type": "string", "enum": ["low", "medium", "high", "not_visible"]},
                                    "reason": {"type": "string"}
                                },
                                "required": ["level", "reason"]
                            },
                            "greenery_diversity": {
                                "type": "object",
                                "properties": {
                                    "level": {"type": "string", "enum": ["low", "medium", "high", "not_visible"]},
                                    "reason": {"type": "string"}
                                },
                                "required": ["level", "reason"]
                            },
                            "openness": {
                                "type": "object",
                                "properties": {
                                    "level": {"type": "string", "enum": ["low", "medium", "high", "not_visible"]},
                                    "reason": {"type": "string"}
                                },
                                "required": ["level", "reason"]
                            },
                            "aesthetics": {
                                "type": "object",
                                "properties": {
                                    "level": {"type": "string", "enum": ["low", "medium", "high", "not_visible"]},
                                    "reason": {"type": "string"}
                                },
                                "required": ["level", "reason"]
                            },
                            "summary": {"type": "string"}
                        },
                        "required": ["facility_maintenance", "rest_facilities", "greenery_diversity", "openness", "aesthetics", "summary"]
                    }

                    # 멀티모달 요청 생성
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=[full_prompt, image_part],
                        config=types.GenerateContentConfig(
                            temperature=0.2,  # 일관된 평가를 위해 낮은 temperature
                            top_p=0.95,
                            top_k=40,
                            max_output_tokens=2048,
                            response_mime_type="application/json",  # JSON 출력 강제
                            response_schema=response_schema,  # JSON Schema 강제
                        )
                    )

                    # 응답 검증
                    if response is None or not hasattr(response, 'text') or response.text is None:
                        # Safety 차단 확인
                        if hasattr(response, 'prompt_feedback'):
                            logger.warning(f"프롬프트 피드백: {response.prompt_feedback}")
                        if hasattr(response, 'candidates'):
                            logger.warning(f"후보 응답: {response.candidates}")
                        raise ValueError("API 응답이 비어있습니다 (Safety 필터 또는 기타 차단 가능)")

                    # 응답 텍스트 추출
                    response_text = response.text.strip()

                    # 빈 응답 체크
                    if not response_text:
                        raise ValueError("응답 텍스트가 비어있습니다")

                    # 디버그: 응답 앞부분 로깅
                    logger.debug(f"응답 앞 200자: {response_text[:200]}")

                    # JSON 파싱 시도 (코드 블록 제거)
                    if '```json' in response_text:
                        response_text = response_text.split('```json')[1].split('```')[0].strip()
                    elif '```' in response_text:
                        response_text = response_text.split('```')[1].split('```')[0].strip()

                    # JSON 파싱 검증
                    result = json.loads(response_text)

                    # 성공하면 루프 종료
                    logger.info(f"API 호출 및 파싱 성공 (시도 {attempt + 1}/{self.max_retries})")
                    return result

                except (errors.ServerError, errors.APIError, json.JSONDecodeError, ValueError) as e:
                    last_error = e
                    error_message = str(e)

                    # JSON 파싱 에러 시 실제 응답 로깅
                    if isinstance(e, json.JSONDecodeError) and response_text:
                        logger.error(f"JSON 파싱 실패. 응답 내용:\n{response_text[:500]}")

                    # 재시도 가능한 에러 판단
                    is_retryable = (
                        "503" in error_message or
                        "500" in error_message or
                        "overloaded" in error_message.lower() or
                        "internal" in error_message.lower() or
                        isinstance(e, json.JSONDecodeError) or
                        isinstance(e, ValueError)
                    )

                    if is_retryable and attempt < self.max_retries - 1:
                        # 지수 백오프: 2초, 4초, 8초, 16초, 32초...
                        wait_time = self.initial_retry_wait * (2 ** attempt)

                        error_type = "서버 과부하" if "503" in error_message or "500" in error_message else "응답 파싱"
                        logger.warning(
                            f"⚠️  {error_type} 에러 발생. {wait_time:.1f}초 대기 후 재시도... "
                            f"(시도 {attempt + 1}/{self.max_retries})"
                        )
                        time.sleep(wait_time)
                    else:
                        # 재시도 불가능하거나 마지막 시도인 경우 에러 발생
                        logger.error(f"최종 재시도 실패: {error_message}")
                        # JSON 파싱 실패 시 응답 저장
                        if isinstance(e, json.JSONDecodeError) and response_text:
                            error_file = Path(__file__).parent.parent / 'output' / 'error_responses' / f'{park_name}_{direction}_error.txt'
                            error_file.parent.mkdir(parents=True, exist_ok=True)
                            with open(error_file, 'w', encoding='utf-8') as f:
                                f.write(response_text)
                            logger.error(f"에러 응답 저장: {error_file}")
                        raise

            # 모든 재시도 실패 시 (이 코드에 도달하면 안 됨)
            if last_error:
                raise last_error
            else:
                raise Exception("API 호출 실패: 알 수 없는 오류")

        except Exception as e:
            logger.error(f"이미지 평가 실패: {e}", exc_info=True)
            raise

    def evaluate_park_images(
        self,
        park_folder: str,
        park_name: str
    ) -> Dict[str, Dict]:
        """
        공원의 모든 방향 이미지를 평가합니다

        Args:
            park_folder: 공원 이미지 폴더 경로
            park_name: 공원 이름

        Returns:
            방향별 평가 결과
            {
                '북': {...},
                '남': {...},
                '동': {...},
                '서': {...}
            }
        """
        logger.info(f"공원 전체 평가 시작: {park_name} ({park_folder})")

        park_path = Path(park_folder)
        if not park_path.exists():
            raise FileNotFoundError(f"공원 폴더를 찾을 수 없습니다: {park_folder}")

        results = {}

        # 모든 .jpg 파일 찾기
        image_files = sorted(park_path.glob('*.jpg'))

        logger.info(f"찾은 이미지: {len(image_files)}개")

        for image_file in image_files:
            # 방향명 추출 (파일명에서 확장자 제거)
            direction = image_file.stem

            try:
                # 이미지 평가
                result = self.evaluate_image(
                    image_path=str(image_file),
                    park_name=park_name,
                    direction=direction
                )

                results[direction] = result

            except Exception as e:
                logger.error(f"이미지 평가 실패: {direction} - {e}")
                results[direction] = {
                    'error': str(e),
                    'overall_score': 0.0
                }

        logger.info(f"공원 전체 평가 완료: {park_name} ({len(results)}/{len(image_files)}개 성공)")

        return results

    def save_evaluation_results(
        self,
        results: Dict[str, Dict],
        output_path: str
    ):
        """
        평가 결과를 JSON 파일로 저장합니다

        Args:
            results: 평가 결과 딕셔너리
            output_path: 저장할 파일 경로
        """
        logger.info(f"평가 결과 저장 중: {output_path}")

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"평가 결과 저장 완료: {output_path}")


# 사용 예시
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )

    # 평가자 생성
    evaluator = GeminiEvaluator()

    # 테스트: 한나루어린이공원 평가
    results = evaluator.evaluate_park_images(
        park_folder='output/한나루어린이공원',
        park_name='한나루어린이공원'
    )

    # 결과 저장
    evaluator.save_evaluation_results(
        results=results,
        output_path='output/한나루어린이공원/evaluation.json'
    )

    # 결과 출력
    print("\n" + "=" * 80)
    print("평가 결과:")
    print("=" * 80)
    for direction, result in results.items():
        if 'error' in result:
            print(f"\n{direction}: 평가 실패 - {result['error']}")
        else:
            print(f"\n{direction}: {result['overall_score']}점")
            print(f"  요약: {result['summary']}")
