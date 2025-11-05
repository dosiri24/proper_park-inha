"""
Kakao Roadview 캡처 메인 스크립트

VSCode에서 F5 또는 실행 버튼을 누르면 이 파일이 실행됩니다.
"""

import os
from dotenv import load_dotenv
from src import RoadviewClient

# .env 파일에서 환경변수 로드
load_dotenv()


def main():
    """
    카카오 로드뷰 캡처 실행
    """
    print("=" * 60)
    print("Kakao Roadview Capture")
    print("=" * 60)
    print()

    # 클라이언트 생성 (.env에서 API 키 자동 로드)
    try:
        client = RoadviewClient()
    except ValueError as e:
        print(f"❌ 오류: {e}")
        print("\n해결 방법:")
        print("   1. https://developers.kakao.com/ 접속")
        print("   2. 애플리케이션 추가하기 → JavaScript 키 발급")
        print("   3. .env 파일에 KAKAO_API_KEY=발급받은키 입력")
        return

    # 테스트 위치 목록 (Google Maps에서 검증된 정확한 좌표)
    locations = [
        {'name': '매소홀어린이공원', 'lat': 37.441929, 'lng':126.654533},
        {'name': '한나루어린이공원', 'lat': 37.440447, 'lng':126.661832}
    ]

    # 각 위치에 대해 로드뷰 캡처
    for loc in locations:
        print(f"\n📍 {loc['name']}")
        print("-" * 60)

        # 메타데이터 조회
        metadata = client.get_roadview_metadata(loc['lat'], loc['lng'])
        print(f"   상태: {metadata['status']}")

        if metadata['status'] == 'OK':
            print(f"   Pano ID: {metadata['pano_id']}")

        # 이미지 캡처
        output_path = f"output/{loc['name']}.jpg"
        success = client.capture_roadview(
            loc['lat'],
            loc['lng'],
            output_path=output_path,
            width=2560,
            height=1440,
            headless=True
        )

        if success:
            print(f"   ✅ 저장: {output_path}")
        else:
            print(f"   ⚠️  캡처 실패 또는 로드뷰 없음")

    print("\n" + "=" * 60)
    print("✅ 완료! output/ 폴더에 이미지가 저장되었습니다.")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        print("\n해결 방법:")
        print("   1. pip install -r requirements.txt 실행")
        print("   2. playwright install chromium 실행")
        print("   3. .env 파일에 KAKAO_API_KEY 확인")
        import traceback
        traceback.print_exc()
