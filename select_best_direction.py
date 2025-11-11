#!/usr/bin/env python
"""
각 공원별로 5가지 지표 점수 합이 가장 높은 방향 하나만 선택하는 스크립트

입력: output/park_evaluations.csv
출력: output/park_best_directions.csv

선택 기준:
- 5가지 지표(facility_maintenance, rest_facilities, greenery_diversity, openness, aesthetics)의 합이 가장 높은 방향
- not_visible인 행은 제외
- 모든 방향이 not_visible인 공원은 5개 항목을 모두 9로 설정하여 포함
"""

import csv
import logging
import unicodedata
from pathlib import Path
from collections import defaultdict

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def normalize_text(text):
    """
    텍스트 정규화 (NFC 형식으로 통일, 공백 제거)

    Args:
        text (str): 정규화할 텍스트

    Returns:
        str: 정규화된 텍스트
    """
    return unicodedata.normalize('NFC', text.strip())


def load_park_info(park_info_path):
    """
    공원 정보 CSV 파일 로드

    Args:
        park_info_path (Path): 공원 정보 CSV 파일 경로

    Returns:
        dict: 공원명을 키로 하는 공원 정보 딕셔너리
    """
    park_info = {}

    with open(park_info_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            park_name = normalize_text(row['공원명'])  # 정규화
            # 첫 번째 등장하는 공원 정보만 저장 (중복 제거)
            if park_name not in park_info:
                park_info[park_name] = {
                    '공원구분': row['공원구분'].strip(),
                    '위도': row['위도'].strip(),
                    '경도': row['경도'].strip(),
                    '공원면적': row['공원면적'].strip(),
                    '지정고시일': row['지정고시일'].strip()
                }

    logger.info(f"공원 정보 로드 완료: {len(park_info)}개 공원")
    logger.debug(f"로드된 공원 목록 (처음 5개): {list(park_info.keys())[:5]}")
    return park_info


def calculate_total_score(row):
    """
    5가지 지표의 총 점수 계산

    Args:
        row (dict): CSV 행 데이터

    Returns:
        int or None: 총 점수 (not_visible인 경우 None 반환)
    """
    indicators = ['facility_maintenance', 'rest_facilities', 'greenery_diversity', 'openness', 'aesthetics']

    total = 0
    for indicator in indicators:
        value = row[indicator]

        # not_visible인 경우 None 반환
        if value == 'not_visible':
            return None

        # 숫자로 변환하여 합산
        try:
            total += int(value)
        except ValueError:
            logger.warning(f"잘못된 값 발견: {indicator}={value} in {row['공원명']}-{row['사진방향']}")
            return None

    return total


def select_best_directions(input_path, output_path, park_info_path):
    """
    각 공원별로 가장 점수가 높은 방향 하나만 선택

    Args:
        input_path (Path): 입력 CSV 파일 경로
        output_path (Path): 출력 CSV 파일 경로
        park_info_path (Path): 공원 정보 CSV 파일 경로
    """
    logger.info(f"입력 파일: {input_path}")
    logger.info(f"출력 파일: {output_path}")
    logger.info(f"공원 정보 파일: {park_info_path}")

    # 공원 정보 로드
    park_info = load_park_info(park_info_path)

    # 공원별 데이터 저장
    park_data = defaultdict(list)
    all_parks = set()  # 모든 공원 목록 추적

    # CSV 파일 읽기
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            park_name = normalize_text(row['공원명'])  # 정규화
            all_parks.add(park_name)  # 공원 목록에 추가

            # 총 점수 계산
            total_score = calculate_total_score(row)

            # not_visible인 경우 건너뛰기
            if total_score is None:
                continue

            # 공원별 데이터에 추가
            park_data[park_name].append({
                'row': row,
                'total_score': total_score
            })

    logger.info(f"총 {len(all_parks)}개의 공원 발견")

    # 각 공원별로 가장 높은 점수의 방향 선택
    best_rows = []
    not_visible_parks = []

    for park_name in all_parks:
        directions = park_data.get(park_name, [])

        # 공원 정보 가져오기
        info = park_info.get(park_name, {})
        if not info:
            logger.warning(f"{park_name}: 공원 정보를 찾을 수 없습니다")

        if not directions:
            # 모든 방향이 not_visible인 경우 - 모든 항목을 9로 설정
            not_visible_parks.append(park_name)
            logger.warning(f"{park_name}: 모든 방향이 not_visible - 모든 항목을 9로 설정")

            # 9점으로 채워진 행 생성 (공원 정보 포함)
            default_row = {
                '공원명': park_name,
                '공원구분': info.get('공원구분', ''),
                '위도': info.get('위도', ''),
                '경도': info.get('경도', ''),
                '공원면적': info.get('공원면적', ''),
                '지정고시일': info.get('지정고시일', ''),
                '사진방향': normalize_text('N/A'),
                'facility_maintenance': '9',
                'rest_facilities': '9',
                'greenery_diversity': '9',
                'openness': '9',
                'aesthetics': '9',
                '총점': '45'
            }
            best_rows.append(default_row)
            continue

        # 총 점수가 가장 높은 방향 선택
        best_direction = max(directions, key=lambda x: x['total_score'])

        # 방향 값 정규화
        direction_normalized = normalize_text(best_direction['row']['사진방향'])

        logger.info(f"{park_name}: {direction_normalized} 선택 (총점: {best_direction['total_score']})")

        # 총점 정보 및 공원 정보 추가 (모든 텍스트 정규화)
        row_with_score = {
            '공원명': park_name,
            '공원구분': info.get('공원구분', ''),
            '위도': info.get('위도', ''),
            '경도': info.get('경도', ''),
            '공원면적': info.get('공원면적', ''),
            '지정고시일': info.get('지정고시일', ''),
            '사진방향': direction_normalized,
            'facility_maintenance': normalize_text(best_direction['row']['facility_maintenance']),
            'rest_facilities': normalize_text(best_direction['row']['rest_facilities']),
            'greenery_diversity': normalize_text(best_direction['row']['greenery_diversity']),
            'openness': normalize_text(best_direction['row']['openness']),
            'aesthetics': normalize_text(best_direction['row']['aesthetics']),
            '총점': str(best_direction['total_score'])
        }

        best_rows.append(row_with_score)

    logger.info(f"선택된 공원: {len(best_rows)}개")
    logger.info(f"평가 가능 공원: {len(best_rows) - len(not_visible_parks)}개")
    logger.info(f"not_visible 처리 공원 (9점 기본값): {len(not_visible_parks)}개")

    # CSV 파일 작성 (헤더 순서: 공원 정보 → 평가 정보)
    fieldnames = [
        '공원명', '공원구분', '위도', '경도', '공원면적', '지정고시일',
        '사진방향', 'facility_maintenance', 'rest_facilities',
        'greenery_diversity', 'openness', 'aesthetics', '총점'
    ]

    # 공원명으로 정렬
    best_rows.sort(key=lambda x: x['공원명'])

    # Excel 호환성을 위해 CP949 인코딩 사용 (한글 자음/모음 분리 방지)
    try:
        with open(output_path, 'w', encoding='cp949', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(best_rows)
        logger.info(f"CSV 파일 생성 완료 (CP949 인코딩): {output_path}")
    except UnicodeEncodeError:
        # CP949로 인코딩할 수 없는 문자가 있는 경우 UTF-8-BOM 사용
        logger.warning("CP949 인코딩 실패, UTF-8-BOM으로 재시도...")
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(best_rows)
        logger.info(f"CSV 파일 생성 완료 (UTF-8-BOM 인코딩): {output_path}")

    # not_visible 처리된 공원 목록 출력
    if not_visible_parks:
        logger.info("\nNot_visible 처리 공원 목록 (기본값 9점 적용):")
        for park in sorted(not_visible_parks):
            logger.info(f"  - {park}")


def main():
    """
    메인 함수
    """
    # 입력/출력 경로 설정
    input_path = Path('output/park_evaluations.csv')
    output_path = Path('output/park_best_directions.csv')
    park_info_path = Path('data/인천광역시_미추홀구_도시공원정보_20250105.csv')

    # 파일 존재 확인
    if not input_path.exists():
        logger.error(f"입력 파일을 찾을 수 없습니다: {input_path}")
        return

    if not park_info_path.exists():
        logger.error(f"공원 정보 파일을 찾을 수 없습니다: {park_info_path}")
        return

    # 출력 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 최고 점수 방향 선택
    select_best_directions(input_path, output_path, park_info_path)


if __name__ == '__main__':
    main()
