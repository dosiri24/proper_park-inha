"""
적응형 로드뷰 캡처 모듈

성공률이 낮으면 반경을 자동으로 늘려가며 재시도
"""

import os
from typing import Dict, List, Tuple
from .roadview_client import RoadviewClient
from .park_sampler import ParkSampler


class AdaptiveCaptureManager:
    """적응형 캡처 관리자"""

    def __init__(self, client: RoadviewClient, sampler: ParkSampler):
        """
        초기화

        Args:
            client: RoadviewClient 인스턴스
            sampler: ParkSampler 인스턴스
        """
        self.client = client
        self.sampler = sampler

    def capture_park_adaptive(
        self,
        park_name: str,
        center_lat: float,
        center_lng: float,
        park_type: str,
        area_sqm: float,
        num_directions: int,
        output_folder: str,
        min_success_rate: float = 0.5,
        max_radius_multiplier: float = 2.0,
        radius_increment: float = 0.3,
        width: int = 2560,
        height: int = 1440,
        headless: bool = True
    ) -> Tuple[int, int, int]:
        """
        적응형 공원 캡처

        성공률이 낮으면 반경을 늘려가며 재시도

        Args:
            park_name: 공원 이름
            center_lat: 공원 중심 위도
            center_lng: 공원 중심 경도
            park_type: 공원 타입
            area_sqm: 공원 면적 (제곱미터)
            num_directions: 방향 개수
            output_folder: 출력 폴더
            min_success_rate: 최소 성공률 (기본 50%)
            max_radius_multiplier: 최대 반경 배수 (기본 2.0배)
            radius_increment: 반경 증가 배수 (기본 0.3배씩)
            width: 이미지 너비
            height: 이미지 높이
            headless: 헤드리스 모드

        Returns:
            (성공 개수, 전체 시도 개수, 최종 반경)
        """
        # 기본 반경 계산
        base_radius = self.sampler.calculate_radius_from_area(area_sqm, park_type)

        print(f"📐 기본 반경: {base_radius}m (면적: {area_sqm:.1f}㎡)")

        current_multiplier = 1.0
        attempt = 1

        while current_multiplier <= max_radius_multiplier:
            current_radius = int(base_radius * current_multiplier)

            print(f"\n🔄 시도 {attempt}: 반경 {current_radius}m (×{current_multiplier:.1f})")
            print("-" * 80)

            # 샘플링 포인트 생성
            sample_points = self.sampler.generate_circular_points(
                park_name=park_name,
                center_lat=center_lat,
                center_lng=center_lng,
                radius_meters=current_radius,
                num_directions=num_directions,
                park_type=park_type,
                area_sqm=area_sqm
            )

            # 검색 반경 계산 (샘플링 반경의 1.5배, 최소 20m, 최대 50m)
            # 작은 공원은 검색 반경을 작게 하여 중복 로드뷰 방지
            search_radius = int(current_radius * 1.5)
            search_radius = max(20, min(search_radius, 50))

            print(f"🔍 검색 반경: {search_radius}m (샘플링 반경의 1.5배)")

            # 캡처 시도
            success_count = 0
            failed_directions = []

            for i, point in enumerate(sample_points, 1):
                print(f"[{i}/{len(sample_points)}] {point['direction']}", end=" ")

                output_path = os.path.join(output_folder, f"{point['direction']}.jpg")

                # 이미 성공한 파일이 있으면 스킵
                if os.path.exists(output_path):
                    print(f"✅ (기존)")
                    success_count += 1
                    continue

                # 로드뷰 캡처
                success = self.client.capture_roadview_multidir(
                    sample_lat=point['sample_lat'],
                    sample_lng=point['sample_lng'],
                    target_lat=point['target_lat'],
                    target_lng=point['target_lng'],
                    output_path=output_path,
                    width=width,
                    height=height,
                    headless=headless,
                    search_radius=search_radius
                )

                if success:
                    print(f"✅")
                    success_count += 1
                else:
                    print(f"⚠️")
                    failed_directions.append(point['direction'])

            # 성공률 계산
            success_rate = success_count / len(sample_points)

            print()
            print(f"📊 결과: {success_count}/{len(sample_points)}개 성공 ({success_rate*100:.1f}%)")

            # 성공률이 충분하면 종료
            if success_rate >= min_success_rate:
                print(f"✅ 성공률 {success_rate*100:.1f}% 달성! (목표: {min_success_rate*100:.0f}%)")
                return success_count, len(sample_points), current_radius

            # 실패한 방향들 출력
            if failed_directions:
                print(f"⚠️  실패한 방향: {', '.join(failed_directions)}")

            # 최대 반경에 도달했으면 종료
            if current_multiplier >= max_radius_multiplier:
                print(f"⚠️  최대 반경 도달 ({current_radius}m)")
                return success_count, len(sample_points), current_radius

            # 반경 증가
            current_multiplier += radius_increment
            attempt += 1
            print(f"↗️  반경을 {int(base_radius * current_multiplier)}m로 증가하여 재시도...")

        return success_count, len(sample_points), current_radius


# 사용 예시
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()

    client = RoadviewClient()
    sampler = ParkSampler()
    manager = AdaptiveCaptureManager(client, sampler)

    # 수봉공원 테스트 (대형 공원)
    success, total, final_radius = manager.capture_park_adaptive(
        park_name='수봉공원',
        center_lat=37.460187,
        center_lng=126.664212,
        park_type='근린공원',
        area_sqm=332694,
        num_directions=12,
        output_folder='test_adaptive/수봉공원',
        min_success_rate=0.7,  # 70% 성공률 목표
        max_radius_multiplier=2.5,  # 최대 2.5배
        radius_increment=0.3,  # 0.3배씩 증가
    )

    print()
    print("=" * 80)
    print(f"최종 결과: {success}/{total}개 성공, 최종 반경: {final_radius}m")
    print("=" * 80)
