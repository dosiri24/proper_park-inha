#!/usr/bin/env python
"""
공원 평가 점수 분포 시각화 스크립트

입력: output/park_best_directions.csv
출력: output/score_distribution.png

기능:
- 총점 기준 2점 간격 구간별 분포 막대그래프 생성
- N/A (평가 불가) 공원 제외
- 한글 폰트 지원
"""

import csv
import logging
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def setup_korean_font():
    """
    한글 폰트 설정

    OS별로 적절한 한글 폰트를 설정하여 matplotlib 그래프에서
    한글이 깨지지 않도록 함

    Returns:
        str: 설정된 폰트 이름
    """
    system = platform.system()

    # OS별 기본 한글 폰트
    font_candidates = {
        'Darwin': ['AppleGothic', 'Apple SD Gothic Neo'],  # macOS
        'Windows': ['Malgun Gothic', 'NanumGothic'],       # Windows
        'Linux': ['NanumGothic', 'UnDotum']                # Linux
    }

    available_fonts = [f.name for f in fm.fontManager.ttflist]

    # 현재 OS에 맞는 폰트 찾기
    for font in font_candidates.get(system, []):
        if font in available_fonts:
            plt.rcParams['font.family'] = font
            logger.info(f"한글 폰트 설정: {font}")
            return font

    # 기본 폰트 사용
    logger.warning("한글 폰트를 찾을 수 없습니다. 기본 폰트 사용")
    return None


def load_score_data(csv_path):
    """
    CSV 파일에서 점수 데이터 로드

    Args:
        csv_path (Path): CSV 파일 경로

    Returns:
        list: 총점 리스트 (N/A 제외)

    Note:
        - 사진방향이 'N/A'인 행은 제외
        - 총점 컬럼을 정수로 변환하여 반환
    """
    scores = []
    total_parks = 0
    excluded_parks = 0

    # CP949 인코딩으로 읽기 (Excel 호환)
    try:
        with open(csv_path, 'r', encoding='cp949') as f:
            reader = csv.DictReader(f)

            for row in reader:
                total_parks += 1

                # N/A 체크 (사진방향 컬럼)
                direction = row.get('사진방향', '').strip()
                if direction == 'N/A':
                    excluded_parks += 1
                    logger.debug(f"{row.get('공원명', 'Unknown')}: N/A 제외")
                    continue

                # 총점 추출
                score_str = row.get('총점', '0').strip()
                try:
                    score = int(score_str)
                    scores.append(score)
                except ValueError:
                    logger.warning(f"잘못된 점수 형식: {score_str} in {row.get('공원명', 'Unknown')}")
                    continue

    except UnicodeDecodeError:
        # CP949 실패 시 UTF-8-BOM 시도
        logger.warning("CP949 인코딩 실패, UTF-8-BOM으로 재시도...")
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                total_parks += 1

                direction = row.get('사진방향', '').strip()
                if direction == 'N/A':
                    excluded_parks += 1
                    continue

                score_str = row.get('총점', '0').strip()
                try:
                    score = int(score_str)
                    scores.append(score)
                except ValueError:
                    continue

    logger.info(f"총 공원 수: {total_parks}개")
    logger.info(f"N/A 제외: {excluded_parks}개")
    logger.info(f"분석 대상: {len(scores)}개")

    return scores


def create_score_bins(scores, bin_size=2):
    """
    점수를 구간별로 그룹화

    Args:
        scores (list): 점수 리스트
        bin_size (int): 구간 크기 (기본값: 2점)

    Returns:
        tuple: (구간 레이블 리스트, 각 구간별 개수 리스트)

    Note:
        구간 예시 (bin_size=2):
        - 6-7점, 8-9점, 10-11점, ...
    """
    if not scores:
        logger.error("점수 데이터가 비어있습니다")
        return [], []

    min_score = min(scores)
    max_score = max(scores)

    logger.info(f"점수 범위: {min_score}점 ~ {max_score}점")

    # 구간 시작점 계산 (bin_size로 내림)
    bin_start = (min_score // bin_size) * bin_size
    bin_end = ((max_score // bin_size) + 1) * bin_size

    # 구간 생성
    bins = {}
    bin_labels = []

    for start in range(bin_start, bin_end, bin_size):
        end = start + bin_size - 1
        label = f"{start}-{end}점"
        bins[label] = 0
        bin_labels.append(label)

    # 각 점수를 해당 구간에 카운트
    for score in scores:
        bin_idx = (score - bin_start) // bin_size
        if 0 <= bin_idx < len(bin_labels):
            label = bin_labels[bin_idx]
            bins[label] += 1

    # 결과 생성
    counts = [bins[label] for label in bin_labels]

    logger.info(f"총 {len(bin_labels)}개 구간 생성")

    return bin_labels, counts


def plot_distribution(bin_labels, counts, output_path):
    """
    점수 분포 히스토그램 생성 및 저장 (한국 논문 스타일)

    Args:
        bin_labels (list): 구간 레이블 리스트
        counts (list): 각 구간별 개수 리스트
        output_path (Path): 출력 이미지 파일 경로

    Note:
        - 그래프 크기: 10x6 인치
        - 막대 색상: 회색조 (논문 스타일)
        - 막대 간격: 없음 (히스토그램)
        - 간결한 스타일
    """
    if not bin_labels or not counts:
        logger.error("그래프 생성에 필요한 데이터가 없습니다")
        return

    # 그래프 생성 (논문 스타일: 간결한 크기, 2:1 비율)
    fig, ax = plt.subplots(figsize=(12, 6))

    # 히스토그램 스타일: 막대 간격 없이 붙여서 표시
    x_pos = range(len(bin_labels))
    bars = ax.bar(x_pos, counts, width=1.0, color='#080085', edgecolor='black', linewidth=1.2)

    # 막대 위에 개수 표시 (간결하게)
    for i, (bar, count) in enumerate(zip(bars, counts)):
        if count > 0:
            height = bar.get_height()
            ax.text(i, height, f'{int(count)}',
                   ha='center', va='bottom', fontsize=10)

    # 그래프 스타일 설정 (논문 스타일: 심플)
    ax.set_xlabel('점수 구간', fontsize=12)
    ax.set_ylabel('공원 수', fontsize=12)
    ax.set_title('도시공원 평가 점수 분포', fontsize=16, pad=15)

    # x축 레이블 설정
    ax.set_xticks(x_pos)
    ax.set_xticklabels(bin_labels, rotation=0)

    # y축 정수로 표시
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # 그리드 제거 (깔끔한 논문 스타일)
    ax.grid(False)

    # 테두리 스타일 (논문 스타일: 상단/우측 테두리 제거)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)

    # 레이아웃 조정
    plt.tight_layout()

    # 저장 (고해상도)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    logger.info(f"그래프 저장 완료: {output_path}")

    # 화면 표시
    plt.show()
    logger.info("그래프 표시 완료")


def main():
    """
    메인 함수

    실행 흐름:
    1. 한글 폰트 설정
    2. CSV 데이터 로드
    3. 점수 구간 생성
    4. 막대그래프 생성 및 저장
    """
    # 경로 설정
    csv_path = Path('output/park_best_directions.csv')
    output_path = Path('output/score_distribution.png')

    # 파일 존재 확인
    if not csv_path.exists():
        logger.error(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
        return

    # 출력 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 한글 폰트 설정
    setup_korean_font()

    # 데이터 로드
    logger.info(f"CSV 파일 로드: {csv_path}")
    scores = load_score_data(csv_path)

    if not scores:
        logger.error("유효한 점수 데이터가 없습니다")
        return

    # 구간 생성
    bin_labels, counts = create_score_bins(scores, bin_size=2)

    # 분포 정보 출력
    logger.info("\n점수 분포:")
    for label, count in zip(bin_labels, counts):
        if count > 0:
            percentage = (count / len(scores)) * 100
            logger.info(f"  {label}: {count}개 ({percentage:.1f}%)")

    # 그래프 생성
    plot_distribution(bin_labels, counts, output_path)


if __name__ == '__main__':
    main()
