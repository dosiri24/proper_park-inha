"""
미추홀구 전체 공원 로드뷰 일괄 캡처

CSV 파일에서 공원 정보를 읽어서 모든 공원의 로드뷰를 다방향 샘플링으로 캡처합니다.
"""

import csv
import os
from dotenv import load_dotenv
from src import RoadviewClient
from src.park_sampler import ParkSampler
from src.adaptive_capture import AdaptiveCaptureManager

# .env 파일에서 환경변수 로드
load_dotenv()


def parse_park_type(park_classification: str) -> str:
    """
    공원구분을 시스템 타입으로 변환

    Args:
        park_classification: CSV의 공원구분 (예: "어린이공원", "근린공원")

    Returns:
        시스템 타입 ("어린이공원", "근린공원", "도시공원", "기타")
    """
    if "어린이" in park_classification:
        return "어린이공원"
    elif "근린" in park_classification:
        return "근린공원"
    elif "도시" in park_classification:
        return "도시공원"
    elif "소공원" in park_classification:
        return "소공원"
    else:
        return "기타"


def get_num_directions(park_type: str, area: float) -> int:
    """
    공원 타입과 면적에 따라 적절한 방향 개수 결정

    Args:
        park_type: 공원 타입
        area: 공원 면적 (㎡)

    Returns:
        방향 개수 (4, 6, 8, 12)
    """
    if park_type == "근린공원" or park_type == "도시공원":
        # 큰 공원: 12방향
        return 12
    elif area > 5000:
        # 큰 어린이공원: 8방향
        return 8
    elif area > 2000:
        # 중간 어린이공원: 6방향
        return 6
    else:
        # 작은 공원: 4방향
        return 4


def load_parks_from_csv(csv_path: str):
    """
    CSV 파일에서 공원 정보 로드

    Args:
        csv_path: CSV 파일 경로

    Returns:
        공원 정보 리스트
    """
    parks = []

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                # 필수 데이터 추출
                name = row['공원명'].strip()
                lat = float(row['위도'])
                lng = float(row['경도'])

                # 면적 (빈 값 처리)
                area_str = row['공원면적'].strip()
                area = float(area_str) if area_str else 1500.0

                # 공원 타입
                park_classification = row['공원구분'].strip()
                park_type = parse_park_type(park_classification)

                # 방향 개수 자동 결정
                num_directions = get_num_directions(park_type, area)

                parks.append({
                    'name': name,
                    'lat': lat,
                    'lng': lng,
                    'type': park_type,
                    'area': area,
                    'num_directions': num_directions,
                    'classification': park_classification,
                })

            except (ValueError, KeyError) as e:
                print(f"⚠️  데이터 파싱 오류: {row.get('공원명', 'Unknown')} - {e}")
                continue

    return parks


def main():
    """
    미추홀구 전체 공원 로드뷰 일괄 캡처
    """
    print("=" * 80)
    print("미추홀구 전체 공원 로드뷰 일괄 캡처")
    print("=" * 80)
    print()

    # CSV 파일 경로
    csv_path = "data/인천광역시_미추홀구_도시공원정보_20250105.csv"

    if not os.path.exists(csv_path):
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        return

    # 공원 정보 로드
    print(f"📂 CSV 파일 로드 중: {csv_path}")
    parks = load_parks_from_csv(csv_path)
    print(f"✅ {len(parks)}개 공원 정보 로드 완료")
    print()

    # 통계
    park_types = {}
    for park in parks:
        park_type = park['type']
        park_types[park_type] = park_types.get(park_type, 0) + 1

    print("📊 공원 타입별 통계:")
    for park_type, count in sorted(park_types.items()):
        print(f"   {park_type}: {count}개")
    print()

    # 캡처 시작 안내
    print(f"총 {len(parks)}개 공원의 로드뷰를 캡처합니다.")
    print(f"예상 이미지 수: 약 {sum(p['num_directions'] for p in parks)}개")
    print()
    print("캡처를 시작합니다...")
    print()

    # 클라이언트 및 적응형 캡처 관리자 생성
    try:
        client = RoadviewClient()
        sampler = ParkSampler()
        adaptive_manager = AdaptiveCaptureManager(client, sampler)
    except ValueError as e:
        print(f"❌ 오류: {e}")
        return

    # 전체 통계
    total_parks = len(parks)
    total_success = 0
    total_fail = 0
    total_images = 0

    # 각 공원 처리
    for idx, park in enumerate(parks, 1):
        print()
        print("=" * 80)
        print(f"[{idx}/{total_parks}] {park['name']} ({park['classification']}, {park['area']:.1f}㎡)")
        print("=" * 80)
        print(f"📍 위치: ({park['lat']}, {park['lng']})")

        # 출력 폴더 생성
        park_folder = f"output/roadview_images/{park['name']}"
        os.makedirs(park_folder, exist_ok=True)

        # 적응형 캡처 실행
        park_success, total_attempts, final_radius = adaptive_manager.capture_park_adaptive(
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

        # 공원별 결과
        print()
        print(f"📸 {park['name']} 완료: {park_success}/{total_attempts}개 캡처 성공 (최종 반경: {final_radius}m)")

        total_images += park_success
        if park_success > 0:
            total_success += 1
        else:
            total_fail += 1

    # 최종 통계
    print()
    print("=" * 80)
    print("✅ 전체 캡처 완료!")
    print("=" * 80)
    print(f"총 공원 수: {total_parks}개")
    print(f"로드뷰 캡처 성공: {total_success}개 공원")
    print(f"로드뷰 없음: {total_fail}개 공원")
    print(f"총 이미지 수: {total_images}개")
    print(f"이미지 저장 위치: output/[공원명]/")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
