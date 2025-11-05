"""
공원 샘플링 전략 모듈

폴리곤 데이터 없이 공원을 다양한 각도에서 캡처하기 위한 샘플링 포인트 생성
"""

import math
from typing import List, Dict, Literal


class ParkSampler:
    """공원 샘플링 포인트 생성기"""

    # 공원 타입별 기본 반경 (미터) - 면적 정보 없을 때만 사용
    DEFAULT_RADIUS = {
        '어린이공원': 30,
        '소공원': 40,
        '근린공원': 60,
        '도시공원': 100,
        '기타': 50,
    }

    # 공원 타입별 반경 제한 (최소, 최대)
    RADIUS_LIMITS = {
        '어린이공원': (15, 40),
        '소공원': (20, 50),
        '근린공원': (30, 80),
        '도시공원': (50, 150),
        '기타': (20, 60),
    }

    def __init__(self):
        """초기화"""
        pass

    @staticmethod
    def calculate_radius_from_area(area_sqm: float, park_type: str = '기타') -> int:
        """
        공원 면적에서 적절한 샘플링 반경 계산

        공원을 원형으로 가정하여 반경을 추정한 후,
        샘플링 포인트가 공원 내부에서 약간 벗어난 정도의 거리로 조정

        Args:
            area_sqm: 공원 면적 (제곱미터)
            park_type: 공원 타입

        Returns:
            샘플링 반경 (미터)
        """
        # 원형 가정: 면적 = π * r²
        # r = sqrt(면적 / π)
        estimated_radius = math.sqrt(area_sqm / math.pi)

        # 샘플링 반경: 추정 반경의 60% (공원 경계 근처)
        # 너무 멀면 주변 건물만 보이고, 너무 가까우면 공원 내부만 보임
        sampling_radius = int(estimated_radius * 0.6)

        # 타입별 최소/최대 반경 제한
        min_radius, max_radius = ParkSampler.RADIUS_LIMITS.get(park_type, (20, 60))
        sampling_radius = max(min_radius, min(sampling_radius, max_radius))

        return sampling_radius

    def generate_circular_points(
        self,
        park_name: str,
        center_lat: float,
        center_lng: float,
        radius_meters: int = None,
        num_directions: int = 4,
        park_type: str = '기타',
        area_sqm: float = None
    ) -> List[Dict]:
        """
        공원 중심에서 원형 패턴으로 샘플링 포인트 생성

        Args:
            park_name: 공원 이름
            center_lat: 공원 중심 위도
            center_lng: 공원 중심 경도
            radius_meters: 샘플링 반경 (미터), None이면 area_sqm 또는 park_type에 따라 자동
            num_directions: 방향 개수 (4, 8, 12, 16)
            park_type: 공원 타입 ('어린이공원', '근린공원', '도시공원', '기타')
            area_sqm: 공원 면적 (제곱미터), 제공 시 면적 기반 반경 자동 계산

        Returns:
            샘플 포인트 리스트
            [
                {
                    'park_name': '매소홀어린이공원',
                    'direction': '북',
                    'angle': 0,
                    'sample_lat': 37.442,
                    'sample_lng': 126.654,
                    'target_lat': 37.441,  # 공원 중심
                    'target_lng': 126.654,
                },
                ...
            ]
        """
        # 반경 결정 우선순위: radius_meters > area_sqm > park_type 기본값
        if radius_meters is None:
            if area_sqm is not None:
                radius_meters = self.calculate_radius_from_area(area_sqm, park_type)
            else:
                radius_meters = self.DEFAULT_RADIUS.get(park_type, 50)

        # 위도/경도 1도당 미터 환산
        lat_per_meter = 1 / 111320  # 위도 1도 = 약 111.32km
        lng_per_meter = 1 / (111320 * math.cos(math.radians(center_lat)))

        # 방향 이름 매핑
        direction_names = self._get_direction_names(num_directions)

        # 샘플 포인트 생성
        points = []
        for i in range(num_directions):
            angle = (360 / num_directions) * i  # 0도 = 북쪽
            angle_rad = math.radians(angle)

            # 극좌표 → 직교좌표 변환
            lat_offset = radius_meters * math.cos(angle_rad)
            lng_offset = radius_meters * math.sin(angle_rad)

            # 최종 좌표
            sample_lat = center_lat + (lat_offset * lat_per_meter)
            sample_lng = center_lng + (lng_offset * lng_per_meter)

            points.append({
                'park_name': park_name,
                'direction': direction_names[i],
                'angle': angle,
                'sample_lat': sample_lat,
                'sample_lng': sample_lng,
                'target_lat': center_lat,
                'target_lng': center_lng,
            })

        return points

    def generate_multi_ring_points(
        self,
        park_name: str,
        center_lat: float,
        center_lng: float,
        inner_radius: int = 30,
        outer_radius: int = 60,
        num_directions: int = 8
    ) -> List[Dict]:
        """
        공원 중심에서 2개 링으로 샘플링 (더 완전한 커버리지)

        Args:
            park_name: 공원 이름
            center_lat: 공원 중심 위도
            center_lng: 공원 중심 경도
            inner_radius: 내부 링 반경 (미터)
            outer_radius: 외부 링 반경 (미터)
            num_directions: 각 링당 방향 개수

        Returns:
            2개 링의 샘플 포인트 리스트
        """
        inner_points = self.generate_circular_points(
            park_name, center_lat, center_lng,
            radius_meters=inner_radius,
            num_directions=num_directions,
            park_type='기타'
        )

        outer_points = self.generate_circular_points(
            park_name, center_lat, center_lng,
            radius_meters=outer_radius,
            num_directions=num_directions,
            park_type='기타'
        )

        # 링 구분 추가
        for point in inner_points:
            point['ring'] = 'inner'
            point['direction'] = f"내부_{point['direction']}"

        for point in outer_points:
            point['ring'] = 'outer'
            point['direction'] = f"외부_{point['direction']}"

        return inner_points + outer_points

    def generate_adaptive_points(
        self,
        park_name: str,
        center_lat: float,
        center_lng: float,
        estimated_area_sqm: int = None,
        park_type: str = '기타'
    ) -> List[Dict]:
        """
        공원 면적에 따라 자동으로 샘플링 전략 결정

        Args:
            park_name: 공원 이름
            center_lat: 공원 중심 위도
            center_lng: 공원 중심 경도
            estimated_area_sqm: 예상 면적 (제곱미터), None이면 park_type으로 추정
            park_type: 공원 타입

        Returns:
            적응형 샘플 포인트 리스트
        """
        # 면적 추정
        if estimated_area_sqm is None:
            # 공원 타입별 평균 면적 (제곱미터)
            area_estimates = {
                '어린이공원': 1500,   # ~1500㎡ (반경 약 22m)
                '소공원': 3000,       # ~3000㎡
                '근린공원': 10000,    # ~1ha
                '도시공원': 100000,   # ~10ha
                '기타': 5000,
            }
            estimated_area_sqm = area_estimates.get(park_type, 5000)

        # 전략 결정
        if estimated_area_sqm < 2000:
            # 소형 공원: 4방향, 단일 링
            return self.generate_circular_points(
                park_name, center_lat, center_lng,
                num_directions=4,
                park_type=park_type,
                area_sqm=estimated_area_sqm
            )
        elif estimated_area_sqm < 10000:
            # 중형 공원: 8방향, 단일 링
            return self.generate_circular_points(
                park_name, center_lat, center_lng,
                num_directions=8,
                park_type=park_type,
                area_sqm=estimated_area_sqm
            )
        else:
            # 대형 공원: 8방향, 2개 링 (면적 기반 반경 자동 계산)
            calculated_radius = self.calculate_radius_from_area(estimated_area_sqm, park_type)
            return self.generate_multi_ring_points(
                park_name, center_lat, center_lng,
                inner_radius=int(calculated_radius * 0.8),
                outer_radius=int(calculated_radius * 1.3),
                num_directions=8
            )

    def _get_direction_names(self, num_directions: int) -> List[str]:
        """
        방향 개수에 따라 방향 이름 생성

        Args:
            num_directions: 4, 8, 12, 16

        Returns:
            방향 이름 리스트
        """
        if num_directions == 4:
            return ['북', '동', '남', '서']
        elif num_directions == 8:
            return ['북', '북동', '동', '남동', '남', '남서', '서', '북서']
        elif num_directions == 12:
            return [
                '북', '북북동', '북동', '동북동',
                '동', '동남동', '남동', '남남동',
                '남', '남남서', '남서', '서남서',
            ]
        elif num_directions == 16:
            return [
                '북', '북북동', '북동', '동북동',
                '동', '동남동', '남동', '남남동',
                '남', '남남서', '남서', '서남서',
                '서', '서북서', '북서', '북북서',
            ]
        else:
            # 기타: 각도로 표시
            return [f"{int((360/num_directions)*i)}도" for i in range(num_directions)]


# 사용 예시
if __name__ == '__main__':
    sampler = ParkSampler()

    # 예시 1: 어린이공원 4방향
    points = sampler.generate_circular_points(
        park_name='매소홀어린이공원',
        center_lat=37.441929,
        center_lng=126.654533,
        park_type='어린이공원',
        num_directions=4
    )

    print("=== 4방향 샘플링 ===")
    for p in points:
        print(f"{p['direction']:4s}: ({p['sample_lat']:.6f}, {p['sample_lng']:.6f})")

    # 예시 2: 8방향
    points = sampler.generate_circular_points(
        park_name='매소홀어린이공원',
        center_lat=37.441929,
        center_lng=126.654533,
        park_type='어린이공원',
        num_directions=8
    )

    print("\n=== 8방향 샘플링 ===")
    for p in points:
        print(f"{p['direction']:4s}: ({p['sample_lat']:.6f}, {p['sample_lng']:.6f})")

    # 예시 3: 적응형 (면적 기반)
    points = sampler.generate_adaptive_points(
        park_name='매소홀어린이공원',
        center_lat=37.441929,
        center_lng=126.654533,
        estimated_area_sqm=1500,  # 1500㎡ 어린이공원
    )

    print(f"\n=== 적응형 샘플링 ({len(points)}개 포인트) ===")
    for p in points:
        print(f"{p['direction']:6s}: ({p['sample_lat']:.6f}, {p['sample_lng']:.6f})")
