"""
Kakao Roadview Client

카카오맵 로드뷰를 Playwright로 캡처하는 클라이언트 (HTTP 서버 버전)
"""

import os
import http.server
import socketserver
import threading
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


class RoadviewClient:
    """카카오 로드뷰 클라이언트"""

    def __init__(self, api_key: str = None):
        """
        초기화

        Args:
            api_key: 카카오 JavaScript API 키
        """
        if not api_key:
            api_key = os.getenv('KAKAO_API_KEY')
            if not api_key:
                raise ValueError(
                    "KAKAO_API_KEY가 설정되지 않았습니다.\n"
                    ".env 파일에 KAKAO_API_KEY를 설정하거나\n"
                    "RoadviewClient(api_key='your_key')로 전달하세요."
                )

        self.api_key = api_key
        self.template_path = Path(__file__).parent / 'roadview_template.html'
        self.template_multidir_path = Path(__file__).parent / 'roadview_template_multidir.html'

        if not self.template_path.exists():
            raise FileNotFoundError(f"HTML 템플릿을 찾을 수 없습니다: {self.template_path}")

        print(f"[INFO] RoadviewClient 초기화 완료 (API Key: {api_key[:10]}...)")

        # HTTP 서버 설정
        self.port = 8080
        self.server = None
        self.server_thread = None

    def _create_html(self, lat: float, lng: float) -> str:
        """
        위경도를 포함한 HTML 생성

        Args:
            lat: 위도
            lng: 경도

        Returns:
            HTML 내용
        """
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        html = template.replace('{{KAKAO_API_KEY}}', self.api_key)
        html = html.replace('{{LATITUDE}}', str(lat))
        html = html.replace('{{LONGITUDE}}', str(lng))

        return html

    def _start_server(self, html_content: str):
        """
        간단한 HTTP 서버 시작

        Args:
            html_content: 서빙할 HTML 내용
        """
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            html = html_content

            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(self.html.encode('utf-8'))

            def log_message(self, format, *args):
                pass  # 로그 출력 억제

        handler = CustomHandler
        socketserver.TCPServer.allow_reuse_address = True
        self.server = socketserver.TCPServer(("", self.port), handler)

        def serve():
            self.server.serve_forever()

        self.server_thread = threading.Thread(target=serve, daemon=True)
        self.server_thread.start()
        time.sleep(0.5)  # 서버 시작 대기

    def _stop_server(self):
        """HTTP 서버 종료"""
        if self.server:
            self.server.shutdown()
            self.server = None

    def capture_roadview(
        self,
        lat: float,
        lng: float,
        output_path: str,
        width: int = 1200,
        height: int = 800,
        headless: bool = True,
        timeout: int = 15000
    ) -> bool:
        """
        로드뷰 캡처

        Args:
            lat: 위도
            lng: 경도
            output_path: 저장 경로
            width: 이미지 너비
            height: 이미지 높이
            headless: 헤드리스 모드 여부
            timeout: 타임아웃 (밀리초)

        Returns:
            성공 여부
        """
        print(f"[INFO] 로드뷰 캡처 시작: lat={lat}, lng={lng}")

        # HTML 생성
        html_content = self._create_html(lat, lng)

        # HTTP 서버 시작
        self._start_server(html_content)

        try:
            with sync_playwright() as p:
                # 브라우저 실행
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context(viewport={'width': width, 'height': height})
                page = context.new_page()

                # HTTP 서버로 접속
                url = f'http://localhost:{self.port}/'
                print(f"[INFO] URL: {url}")
                page.goto(url)
                print(f"[INFO] HTML 로드 완료")

                # 로드뷰가 로드될 때까지 대기
                try:
                    # roadview-loaded 또는 roadview-error 클래스가 추가될 때까지 대기
                    page.wait_for_selector('body.roadview-loaded, body.roadview-error', timeout=timeout)

                    # 에러 체크
                    if page.locator('body.roadview-error').count() > 0:
                        print(f"[WARN] 해당 위치에 로드뷰가 없습니다")
                        # 에러 화면도 스크린샷
                        page.screenshot(path=output_path, full_page=False)
                        print(f"[INFO] 에러 화면 저장: {output_path}")
                        return False

                    # 추가 대기 (로드뷰 렌더링 완료)
                    page.wait_for_timeout(2000)

                    # 스크린샷
                    page.screenshot(path=output_path, full_page=False)
                    print(f"[INFO] 로드뷰 캡처 완료: {output_path}")

                    return True

                except PlaywrightTimeoutError:
                    print(f"[ERROR] 타임아웃: 로드뷰 로드 실패")
                    return False

                finally:
                    browser.close()

        finally:
            # HTTP 서버 종료
            self._stop_server()

    def get_roadview_metadata(self, lat: float, lng: float, radius: int = 50) -> dict:
        """
        로드뷰 메타데이터 조회

        Args:
            lat: 위도
            lng: 경도
            radius: 검색 반경 (미터)

        Returns:
            메타데이터 딕셔너리
        """
        print(f"[INFO] 로드뷰 메타데이터 조회: lat={lat}, lng={lng}, radius={radius}m")

        html_content = self._create_html(lat, lng)
        self._start_server(html_content)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(f'http://localhost:{self.port}/')

                try:
                    # 로드 대기
                    page.wait_for_selector('body.roadview-loaded, body.roadview-error', timeout=15000)

                    # 상태 텍스트 읽기
                    status_text = page.locator('#status').text_content()

                    if 'roadview-error' in page.locator('body').get_attribute('class'):
                        return {
                            'status': 'NOT_FOUND',
                            'message': '로드뷰를 찾을 수 없습니다'
                        }

                    # Pano ID 추출
                    if 'Pano ID:' in status_text:
                        pano_id = status_text.split('Pano ID:')[1].strip().rstrip(')')
                        return {
                            'status': 'OK',
                            'pano_id': pano_id,
                            'location': {'lat': lat, 'lng': lng}
                        }

                    return {
                        'status': 'ERROR',
                        'message': '메타데이터 파싱 실패'
                    }

                except PlaywrightTimeoutError:
                    return {
                        'status': 'TIMEOUT',
                        'message': '타임아웃'
                    }

                finally:
                    browser.close()

        finally:
            self._stop_server()

    def capture_roadview_multidir(
        self,
        sample_lat: float,
        sample_lng: float,
        target_lat: float,
        target_lng: float,
        output_path: str,
        width: int = 1200,
        height: int = 800,
        headless: bool = True,
        timeout: int = 15000,
        search_radius: int = 50
    ) -> bool:
        """
        다방향 샘플링용 로드뷰 캡처

        샘플 좌표 주변에서 로드뷰를 찾아, 타겟 좌표를 향하도록 캡처

        Args:
            sample_lat: 샘플 위도 (로드뷰 찾을 위치)
            sample_lng: 샘플 경도 (로드뷰 찾을 위치)
            target_lat: 타겟 위도 (카메라가 볼 방향)
            target_lng: 타겟 경도 (카메라가 볼 방향)
            output_path: 저장 경로
            width: 이미지 너비
            height: 이미지 높이
            headless: 헤드리스 모드 여부
            timeout: 타임아웃 (밀리초)

        Returns:
            성공 여부
        """
        if not self.template_multidir_path.exists():
            raise FileNotFoundError(f"다방향 템플릿을 찾을 수 없습니다: {self.template_multidir_path}")

        print(f"[INFO] 다방향 로드뷰 캡처: sample=({sample_lat}, {sample_lng}), target=({target_lat}, {target_lng})")

        # HTML 생성 (4개 좌표 사용)
        with open(self.template_multidir_path, 'r', encoding='utf-8') as f:
            template = f.read()

        html = template.replace('{{KAKAO_API_KEY}}', self.api_key)
        html = html.replace('{{SAMPLE_LAT}}', str(sample_lat))
        html = html.replace('{{SAMPLE_LNG}}', str(sample_lng))
        html = html.replace('{{TARGET_LAT}}', str(target_lat))
        html = html.replace('{{TARGET_LNG}}', str(target_lng))
        html = html.replace('{{SEARCH_RADIUS}}', str(search_radius))

        # HTTP 서버 시작
        self._start_server(html)

        try:
            with sync_playwright() as p:
                # 브라우저 실행
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context(viewport={'width': width, 'height': height})
                page = context.new_page()

                # HTTP 서버로 접속
                url = f'http://localhost:{self.port}/'
                page.goto(url)

                # 로드뷰가 로드될 때까지 대기
                try:
                    page.wait_for_selector('body.roadview-loaded, body.roadview-error', timeout=timeout)

                    # 에러 체크
                    if 'roadview-error' in page.locator('body').get_attribute('class'):
                        print(f"[WARN] 로드뷰 없음: sample=({sample_lat}, {sample_lng})")
                        browser.close()
                        return False

                    # 이미지 완전 로딩을 위한 추가 대기 (1초)
                    page.wait_for_timeout(1000)

                    # 스크린샷 촬영
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    page.screenshot(path=output_path, full_page=False)

                    print(f"[INFO] 캡처 완료: {output_path}")
                    browser.close()
                    return True

                except PlaywrightTimeoutError:
                    print(f"[ERROR] 타임아웃: {output_path}")
                    browser.close()
                    return False

        except Exception as e:
            print(f"[ERROR] 캡처 실패: {e}")
            return False

        finally:
            self._stop_server()
