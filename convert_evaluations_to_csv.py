#!/usr/bin/env python
"""
공원 평가 결과를 CSV로 변환하는 스크립트

입력: output/roadview_evaluate/*.json
출력: output/park_evaluations.csv

변환 규칙:
- low → 1, medium → 2, high → 3
- 5가지 항목 중 하나라도 not_visible이면 모든 항목을 not_visible로 처리
"""

import os
import json
import csv
import logging
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def convert_level_to_score(level):
    """
    평가 레벨을 점수로 변환

    Args:
        level (str): 평가 레벨 (low, medium, high, not_visible)

    Returns:
        str: 변환된 점수 (1, 2, 3) 또는 not_visible
    """
    level_map = {
        'low': '1',
        'medium': '2',
        'high': '3',
        'not_visible': 'not_visible'
    }
    return level_map.get(level, 'not_visible')


def check_all_visible(direction_data):
    """
    모든 항목이 visible 상태인지 확인

    Args:
        direction_data (dict): 방향별 평가 데이터

    Returns:
        bool: 모든 항목이 visible이면 True, 하나라도 not_visible이면 False
    """
    indicators = ['facility_maintenance', 'rest_facilities', 'greenery_diversity', 'openness', 'aesthetics']

    for indicator in indicators:
        if indicator in direction_data:
            level = direction_data[indicator].get('level', 'not_visible')
            if level == 'not_visible':
                return False

    return True


def process_json_file(json_path):
    """
    JSON 파일을 읽어서 CSV 행 데이터로 변환

    Args:
        json_path (Path): JSON 파일 경로

    Returns:
        list: CSV 행 데이터 리스트
    """
    park_name = json_path.stem  # 파일명에서 확장자 제거하여 공원명 추출

    logger.info(f"처리 중: {park_name}")

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows = []

    for direction, direction_data in data.items():
        # summary는 방향이 아니므로 건너뛰기
        if direction == 'summary' or not isinstance(direction_data, dict):
            continue

        # 모든 항목이 visible 상태인지 확인
        all_visible = check_all_visible(direction_data)

        # CSV 행 생성
        row = {
            '공원명': park_name,
            '사진방향': direction,
        }

        # 5가지 지표 처리
        indicators = ['facility_maintenance', 'rest_facilities', 'greenery_diversity', 'openness', 'aesthetics']

        if all_visible:
            # 모든 항목이 visible이면 실제 값 사용
            for indicator in indicators:
                if indicator in direction_data:
                    level = direction_data[indicator].get('level', 'not_visible')
                    row[indicator] = convert_level_to_score(level)
                else:
                    row[indicator] = 'not_visible'
        else:
            # 하나라도 not_visible이면 모든 항목을 not_visible로 처리
            for indicator in indicators:
                row[indicator] = 'not_visible'

        rows.append(row)

    return rows


def main():
    """
    메인 함수: JSON 파일들을 읽어서 CSV로 변환
    """
    # 입력/출력 경로 설정
    input_dir = Path('output/roadview_evaluate')
    output_path = Path('output/park_evaluations.csv')

    logger.info(f"입력 디렉토리: {input_dir}")
    logger.info(f"출력 파일: {output_path}")

    # 출력 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 모든 JSON 파일 찾기
    json_files = sorted(input_dir.glob('*.json'))

    # roadview_evaluate.json은 제외 (메타 파일로 추정)
    json_files = [f for f in json_files if f.name != 'roadview_evaluate.json']

    logger.info(f"총 {len(json_files)}개의 JSON 파일 발견")

    # 모든 데이터 수집
    all_rows = []

    for json_path in json_files:
        rows = process_json_file(json_path)
        all_rows.extend(rows)

    logger.info(f"총 {len(all_rows)}개의 데이터 행 생성")

    # CSV 파일 작성
    fieldnames = ['공원명', '사진방향', 'facility_maintenance', 'rest_facilities',
                  'greenery_diversity', 'openness', 'aesthetics']

    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    logger.info(f"CSV 파일 생성 완료: {output_path}")

    # 통계 출력
    visible_count = sum(1 for row in all_rows if row['facility_maintenance'] != 'not_visible')
    not_visible_count = len(all_rows) - visible_count

    logger.info(f"평가 가능 데이터: {visible_count}개")
    logger.info(f"평가 불가 데이터 (not_visible): {not_visible_count}개")


if __name__ == '__main__':
    main()
