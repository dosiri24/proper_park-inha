#!/usr/bin/env python
"""
공원 이미지 평가 실행 스크립트

output/ 폴더의 모든 공원 이미지를 Gemini API로 평가합니다.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
from src.gemini_evaluator import GeminiEvaluator


def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("Gemini API를 사용한 공원 이미지 평가")
    print("=" * 80)
    print()

    # 환경변수 로드
    load_dotenv()

    # 로깅 설정
    setup_logging()

    # 평가자 생성
    try:
        evaluator = GeminiEvaluator()
    except ValueError as e:
        print(f"\n❌ 오류: {e}")
        print("\n.env 파일에 GEMINI_API_KEY를 설정해주세요.")
        print("자세한 내용은 .env.example 파일을 참고하세요.")
        sys.exit(1)

    # output 폴더에서 공원 목록 찾기
    # 먼저 output/ 직접 확인, 없으면 output/roadview_images/ 확인
    output_dir = Path('output')
    if not output_dir.exists():
        print(f"\n❌ 오류: {output_dir} 폴더를 찾을 수 없습니다.")
        print("먼저 main.py 또는 batch_capture_all_parks.py를 실행하여 이미지를 캡처하세요.")
        sys.exit(1)

    # 공원 폴더 목록 (output/ 또는 output/roadview_images/)
    park_folders = [f for f in output_dir.iterdir() if f.is_dir() and f.name != 'roadview_images']

    # output/ 직접 하위에 공원 폴더가 없으면 roadview_images/ 확인
    if not park_folders:
        roadview_dir = output_dir / 'roadview_images'
        if roadview_dir.exists():
            print(f"📂 roadview_images 폴더에서 공원 검색 중...")
            park_folders = [f for f in roadview_dir.iterdir() if f.is_dir()]

    if not park_folders:
        print(f"\n❌ 오류: {output_dir} 폴더에 공원 이미지가 없습니다.")
        print("먼저 main.py 또는 batch_capture_all_parks.py를 실행하여 이미지를 캡처하세요.")
        sys.exit(1)

    print(f"📂 찾은 공원: {len(park_folders)}개\n")

    # 각 공원 평가
    total_parks = len(park_folders)
    success_count = 0
    failed_parks = []

    for idx, park_folder in enumerate(park_folders, 1):
        park_name = park_folder.name

        print(f"\n[{idx}/{total_parks}] {park_name}")
        print("-" * 80)

        try:
            # 공원 이미지 평가
            results = evaluator.evaluate_park_images(
                park_folder=str(park_folder),
                park_name=park_name
            )

            # 결과 저장
            output_path = park_folder / 'evaluation.json'
            evaluator.save_evaluation_results(
                results=results,
                output_path=str(output_path)
            )

            # 간단한 결과 출력
            total_score = sum(
                r.get('overall_score', 0.0)
                for r in results.values()
                if 'error' not in r
            )
            valid_count = sum(1 for r in results.values() if 'error' not in r)

            if valid_count > 0:
                avg_score = total_score / valid_count
                print(f"✅ 평가 완료: 평균 점수 {avg_score:.1f}점 ({valid_count}/{len(results)}개 성공)")
                success_count += 1
            else:
                print(f"⚠️  모든 이미지 평가 실패")
                failed_parks.append(park_name)

        except Exception as e:
            print(f"❌ 평가 실패: {e}")
            failed_parks.append(park_name)

    # 최종 결과 출력
    print("\n" + "=" * 80)
    print("✅ 전체 평가 완료!")
    print("=" * 80)
    print(f"성공: {success_count}/{total_parks}개 공원")

    if failed_parks:
        print(f"\n⚠️  실패한 공원 ({len(failed_parks)}개):")
        for park_name in failed_parks:
            print(f"  - {park_name}")

    print(f"\n📊 평가 결과는 각 공원 폴더의 evaluation.json 파일에 저장되었습니다.")
    print("=" * 80)


if __name__ == '__main__':
    main()
