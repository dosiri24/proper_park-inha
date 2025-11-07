"""
Kakao Roadview 캡처 메인 스크립트 (적응형 샘플링)

개선 사항:
- 로딩 대기 시간 추가 (뿌연 이미지 방지)
- 면적 기반 샘플링 반경 자동 계산
- 적응형 범위 확대 (성공률 낮으면 반경 자동 증가)

VSCode에서 F5 또는 실행 버튼을 누르면 이 파일이 실행됩니다.
"""

import os
from dotenv import load_dotenv
from src import RoadviewClient
from src.park_sampler import ParkSampler
from src.adaptive_capture import AdaptiveCaptureManager

# .env 파일에서 환경변수 로드
load_dotenv()


def main():
    """
    카카오 로드뷰 캡처 실행 (적응형 다방향 샘플링)
    """
    print("=" * 80)
    print("Kakao Roadview Capture - Adaptive Multi-Direction Sampling")
    print("=" * 80)
    print()

    # 클라이언트 및 적응형 캡처 관리자 생성
    try:
        client = RoadviewClient()
        sampler = ParkSampler()
        adaptive_manager = AdaptiveCaptureManager(client, sampler)
    except ValueError as e:
        print(f"❌ 오류: {e}")
        print("\n해결 방법:")
        print("   1. https://developers.kakao.com/ 접속")
        print("   2. 애플리케이션 추가하기 → JavaScript 키 발급")
        print("   3. .env 파일에 KAKAO_API_KEY=발급받은키 입력")
        return

    # 공원 목록 (면적 정보 포함)
    parks = [
        {
            'name': '매소홀어린이공원',
            'lat': 37.441929,
            'lng': 126.654533,
            'type': '어린이공원',
            'area': 3006.9,  # ㎡
            'num_directions': 8,
        },
        {
            'name': '한나루어린이공원',
            'lat': 37.440447,
            'lng': 126.661832,
            'type': '어린이공원',
            'area': 2500,  # ㎡ (추정)
            'num_directions': 8,
        },
    ]

    # 각 공원에 대해 적응형 캡처 실행
    total_success = 0
    total_attempts = 0

    for idx, park in enumerate(parks, 1):
        print()
        print("=" * 80)
        print(f"[{idx}/{len(parks)}] {park['name']} ({park['type']})")
        print("=" * 80)
        print(f"📍 위치: ({park['lat']}, {park['lng']})")
        print(f"📐 면적: {park['area']:.1f}㎡")
        print()

        # 출력 폴더 생성
        park_folder = f"output/roadview_images/{park['name']}"
        os.makedirs(park_folder, exist_ok=True)

        # 적응형 캡처 실행
        success, attempts, final_radius = adaptive_manager.capture_park_adaptive(
            park_name=park['name'],
            center_lat=park['lat'],
            center_lng=park['lng'],
            park_type=park['type'],
            area_sqm=park['area'],
            num_directions=park['num_directions'],
            output_folder=park_folder,
            min_success_rate=0.6,  # 60% 성공률 목표
            max_radius_multiplier=2.5,  # 최대 2.5배
            radius_increment=0.4,  # 0.4배씩 증가
            width=2560,
            height=1440,
            headless=True
        )

        total_success += success
        total_attempts += attempts

        print()
        print(f"📸 {park['name']} 완료: {success}/{attempts}개 ({success/attempts*100:.1f}%)")
        print(f"   최종 반경: {final_radius}m")

    # 최종 통계
    print()
    print("=" * 80)
    print("✅ 전체 캡처 완료!")
    print("=" * 80)
    print(f"총 캡처 성공: {total_success}/{total_attempts}개 ({total_success/total_attempts*100:.1f}%)")
    print(f"이미지 저장 위치: output/[공원명]/")
    print()
    print("개선 사항:")
    print("  ✓ 로딩 대기 시간 추가 (뿌연 이미지 방지)")
    print("  ✓ 면적 기반 샘플링 반경 자동 계산")
    print("  ✓ 적응형 범위 확대 (성공률 낮으면 반경 자동 증가)")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        print("\n해결 방법:")
        print("   1. pip install -r requirements.txt 실행")
        print("   2. playwright install chromium 실행")
        print("   3. .env 파일에 KAKAO_API_KEY 확인")
        import traceback
        traceback.print_exc()
