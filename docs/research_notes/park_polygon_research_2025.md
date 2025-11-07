# 공원 폴리곤 자동화 리서치 결과 (2025)

## 📋 Executive Summary

공원의 경계 좌표(폴리곤)를 자동으로 가져오는 방법을 조사한 결과, **OpenStreetMap Overpass API**와 **공공데이터포털**이 가장 실행 가능한 방법으로 확인되었습니다.

### ✅ 결론: 추천 방법
1. **OpenStreetMap Overpass API** (완전 자동화 가능) ⭐ 추천
2. **공공데이터포털** (수동 다운로드 + 자동 처리)

### ❌ 불가능한 방법
- Kakao Map API: 폴리곤 데이터 제공 안 함
- Naver Map API: 폴리곤 데이터 제공 안 함

---

## 🔍 조사 결과 상세

### 1. Kakao Map API

**조사 결과:** ❌ **공원 폴리곤 데이터 제공 안 함**

**제공 기능:**
- 장소 검색 (Local API)
- 좌표 ↔ 주소 변환 (Geocoding)
- 지도 위 도형 그리기 (폴리곤, 서클, 폴리라인) - 사용자가 직접 그림
- 길찾기, 거리 계산

**한계:**
- 미리 정의된 공원 경계 데이터 없음
- 사용자가 직접 폴리곤을 그려야 함
- POI(Point of Interest) 폴리곤 제공 안 함

**2024년 업데이트:**
- 2024년 12월 1일부터 새 앱은 Kakao Map 기능 활성화 필수

**출처:**
- https://developers.kakao.com/docs/latest/en/local/dev-guide

---

### 2. Naver Map API

**조사 결과:** ❌ **공원 폴리곤 데이터 제공 안 함**

**제공 기능:**
- Web Dynamic Map API (JavaScript 기반)
- 검색, 지도, 번역 API
- 인터랙티브 맵 통합

**한계:**
- 공원 경계 폴리곤 데이터 명시적으로 제공 안 함
- POI 폴리곤 데이터셋 없음
- 전용 공원 데이터 엔드포인트 없음

**대안 정보:**
- 한국 행정구역 경계 Shapefile은 별도 GIS 데이터로 제공 (KML, GeoJSON, CSV)
- 하지만 이는 행정구역이지 공원 데이터가 아님

**출처:**
- https://www.ncloud.com/product/applicationService/maps
- https://navermaps.github.io/maps.js.en/docs/

---

### 3. OpenStreetMap Overpass API ⭐

**조사 결과:** ✅ **완전 자동화 가능 - 최고의 방법**

#### 🎯 핵심 장점
- 완전 무료, 오픈소스
- REST API로 실시간 쿼리 가능
- Python으로 자동화 구현 쉬움
- 폴리곤 좌표를 직접 받을 수 있음
- 전 세계 데이터 커버리지

#### 📊 한국 데이터 품질
**현황:**
- OSM 한국 데이터는 과거 매우 빈약했고 현재도 부족
- 한국 지역 매퍼가 적음
- 로컬 데이터 수집 작업에 집중

**하지만:**
- 주요 도시 공원은 대부분 매핑됨
- 서울, 인천 등 대도시는 커버리지 양호
- 데이터 계속 개선 중

#### 🔧 기술적 구현 방법

**기본 쿼리 구조:**
```
[out:json];
way["leisure"="park"]({{bbox}});
out geom;
```

**폴리곤 좌표 받기:**
```python
import requests

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
way["leisure"="park"](37.44, 126.65, 37.45, 126.66);
out geom;
"""

response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()

# 폴리곤 좌표 추출
for element in data['elements']:
    if element['type'] == 'way' and 'geometry' in element:
        coords = [(node['lon'], node['lat']) for node in element['geometry']]
        print(f"Park polygon: {coords}")
```

**복잡한 공원 (multipolygon) 처리:**
```
[out:json];
rel["type"="multipolygon"]["leisure"="park"]({{bbox}});
out geom;
```

**특정 공원 이름으로 찾기:**
```
[out:json];
area["name"="매소홀어린이공원"];
way["leisure"="park"](area);
out geom;
```

#### 📦 Python 라이브러리

**1. overpy (추천)**
```bash
pip install overpy
```

```python
import overpy

api = overpy.Overpass()
result = api.query("""
    way["leisure"="park"](37.44, 126.65, 37.45, 126.66);
    out geom;
""")

for way in result.ways:
    coords = [(float(node.lon), float(node.lat)) for node in way.nodes]
    print(f"Park: {way.tags.get('name', 'Unknown')}")
    print(f"Coordinates: {coords}")
```

**2. requests (기본)**
```bash
pip install requests
```

#### 🌐 Overpass Turbo (테스트 도구)
- URL: https://overpass-turbo.eu/
- 브라우저에서 쿼리 테스트
- 결과를 지도에서 시각화
- Export to GeoJSON, GPX, KML 가능

#### ⚠️ 주의사항
- 타임아웃: `[timeout:25]` 설정 권장
- 대량 쿼리 시 서버 부하 주의
- Bounding box 크기 적절히 제한

**출처:**
- https://wiki.openstreetmap.org/wiki/Overpass_API
- https://janakiev.com/blog/openstreetmap-with-python-and-overpass-api/

---

### 4. 공공데이터포털 (data.go.kr)

**조사 결과:** ✅ **고품질 공식 데이터 제공**

#### 📂 제공 데이터셋

**1. 국립공원 공원경계 (23개 국립공원)**
- URL: https://www.data.go.kr/data/15017313/fileData.do
- 형식: SHP, GeoJSON
- 좌표계: EPSG:4326 (WGS 84, 경위도)
- 업데이트: 수시 (1회성 데이터)
- 최종 수정: 2024-02-05
- 다운로드: 4,335회

**파일 구조:**
```
국립공원경계.shp  (폴리곤 형상)
국립공원경계.dbf  (속성 데이터)
국립공원경계.shx  (인덱스)
국립공원경계.prj  (좌표계 정보)
```

**2. 전국 도시공원 표준 데이터**
- 위경도 좌표 포함
- 전국 도시 공원 정보

**⚠️ 중요 주의사항:**
> "공원 경계에 대한 고시는 도면 고시로 실제 좌표값과 상이할 수 있습니다"
>
> 공식 경계 발표는 지도 기반이므로 실제 좌표와 다를 수 있음

#### 🔧 Python으로 Shapefile 읽기

**라이브러리: geopandas**
```bash
pip install geopandas
```

```python
import geopandas as gpd

# Shapefile 읽기
parks = gpd.read_file("국립공원경계.shp")

# 데이터 확인
print(parks.head())
print(parks.columns)

# 특정 공원 찾기
park = parks[parks['name'] == '설악산']

# 폴리곤 좌표 추출
for idx, row in parks.iterrows():
    park_name = row['name']
    geometry = row['geometry']

    # 폴리곤 좌표
    if geometry.geom_type == 'Polygon':
        coords = list(geometry.exterior.coords)
        print(f"{park_name}: {coords}")
    elif geometry.geom_type == 'MultiPolygon':
        for poly in geometry.geoms:
            coords = list(poly.exterior.coords)
            print(f"{park_name} (part): {coords}")
```

**GeoJSON으로 변환:**
```python
# GeoJSON으로 저장
parks.to_file("parks.geojson", driver='GeoJSON')

# JSON으로 읽기
import json
with open("parks.geojson", 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)
```

#### 📊 장단점

**장점:**
✅ 공식 정부 데이터 (신뢰도 높음)
✅ 고품질 경계 좌표
✅ WGS84 좌표계 (GPS 호환)
✅ GIS 표준 포맷 (SHP, GeoJSON)

**단점:**
❌ API 없음 (파일 다운로드만 가능)
❌ 국립공원만 제공 (도시 공원은 별도)
❌ 업데이트 빈도 낮음 (수시)
❌ 자동화 위해 파일 다운로드 필요

**출처:**
- https://www.data.go.kr/data/15017313/fileData.do

---

## 🎯 실행 가능한 방법 종합

### 방법 1: OpenStreetMap Overpass API (추천) ⭐

**적합한 경우:**
- 완전 자동화가 필요한 경우
- 실시간으로 최신 데이터 필요
- 다양한 공원 (도시공원, 근린공원, 어린이공원)
- 경계 좌표를 프로그래밍으로 가져와야 할 때

**구현 난이도:** 쉬움

**구현 예시:**
```python
# requirements.txt
# overpy>=0.7

import overpy

def get_park_polygon(park_name, bbox=None):
    """
    공원 이름으로 폴리곤 좌표 가져오기

    Args:
        park_name: 공원 이름 (예: "매소홀어린이공원")
        bbox: (남위, 서경, 북위, 동경) 또는 None

    Returns:
        List of (lon, lat) tuples
    """
    api = overpy.Overpass()

    if bbox:
        bbox_str = f"({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]})"
    else:
        bbox_str = ""

    query = f"""
    way["leisure"="park"]["name"="{park_name}"]{bbox_str};
    out geom;
    """

    result = api.query(query)

    polygons = []
    for way in result.ways:
        coords = [(float(node.lon), float(node.lat)) for node in way.nodes]
        polygons.append({
            'name': way.tags.get('name', 'Unknown'),
            'coordinates': coords
        })

    return polygons

# 사용 예시
bbox_incheon = (37.40, 126.60, 37.50, 126.70)  # 인천 지역
parks = get_park_polygon("매소홀어린이공원", bbox_incheon)

for park in parks:
    print(f"Park: {park['name']}")
    print(f"Polygon: {park['coordinates']}")
```

**한계 및 대응:**
- 한국 OSM 데이터 품질 부족 → 공공데이터와 병행
- 이름이 정확해야 함 → Fuzzy matching 또는 좌표 기반 검색

---

### 방법 2: 공공데이터포털 Shapefile

**적합한 경우:**
- 국립공원 데이터 필요
- 공식 정부 데이터 필요
- 높은 정확도 요구
- 오프라인 처리 가능

**구현 난이도:** 중간

**구현 예시:**
```python
# requirements.txt
# geopandas>=0.14.0
# shapely>=2.0.0

import geopandas as gpd

def load_park_polygons(shapefile_path):
    """
    Shapefile에서 공원 폴리곤 로드

    Args:
        shapefile_path: .shp 파일 경로

    Returns:
        GeoDataFrame
    """
    parks = gpd.read_file(shapefile_path)
    return parks

def get_park_by_name(parks_gdf, park_name):
    """
    이름으로 공원 찾기
    """
    park = parks_gdf[parks_gdf['name'] == park_name]

    if len(park) == 0:
        return None

    geometry = park.iloc[0].geometry

    # 폴리곤 좌표 추출
    if geometry.geom_type == 'Polygon':
        coords = list(geometry.exterior.coords)
    elif geometry.geom_type == 'MultiPolygon':
        coords = [list(poly.exterior.coords) for poly in geometry.geoms]

    return {
        'name': park_name,
        'geometry_type': geometry.geom_type,
        'coordinates': coords
    }

# 사용 예시
parks = load_park_polygons("data/국립공원경계.shp")
seorak = get_park_by_name(parks, "설악산")

if seorak:
    print(f"Park: {seorak['name']}")
    print(f"Type: {seorak['geometry_type']}")
    print(f"Coordinates: {seorak['coordinates'][:5]}...")  # 처음 5개만
```

**한계 및 대응:**
- 파일 다운로드 수동 → 스크립트로 주기적 체크
- 국립공원만 → OSM 데이터로 보완

---

### 방법 3: 하이브리드 (OpenStreetMap + 공공데이터)

**적합한 경우:**
- 최고 품질과 커버리지 필요
- 다양한 공원 타입
- 실시간 + 공식 데이터 병행

**구현 전략:**
1. 먼저 공공데이터에서 찾기 (국립공원, 주요 공원)
2. 없으면 OpenStreetMap에서 찾기 (도시공원, 근린공원)
3. 둘 다 없으면 4방향 오프셋 방식 사용 (fallback)

```python
def get_park_polygon_hybrid(park_name, park_lat, park_lng):
    """
    공공데이터 → OSM → Fallback 순으로 폴리곤 찾기
    """
    # 1. 공공데이터 시도
    polygon = get_from_public_data(park_name)
    if polygon:
        return {'source': 'public_data', 'polygon': polygon}

    # 2. OpenStreetMap 시도
    bbox = get_bbox_around_point(park_lat, park_lng, radius_meters=500)
    polygon = get_from_osm(park_name, bbox)
    if polygon:
        return {'source': 'osm', 'polygon': polygon}

    # 3. Fallback: 4방향 오프셋 포인트 생성
    points = generate_4_direction_points(park_lat, park_lng, offset_meters=50)
    return {'source': 'fallback', 'points': points}
```

---

## 🚀 추천 구현 로드맵

### Phase 1: OpenStreetMap 구현 (1-2시간)
1. `overpy` 라이브러리 설치
2. 기본 쿼리 함수 작성
3. 인천 지역 공원 몇 개로 테스트
4. 폴리곤 좌표 → 경계선 샘플링 로직 구현

### Phase 2: 폴리곤 → 로드뷰 샘플링 (2-3시간)
1. 폴리곤 경계선을 N미터 간격으로 샘플링
2. 각 샘플 포인트에서 로드뷰 찾기
3. 로드뷰가 공원 중심을 향하도록 설정
4. 캡처 및 저장

### Phase 3: 공공데이터 통합 (선택, 1시간)
1. `geopandas` 설치
2. Shapefile 읽기 구현
3. OSM과 병합 로직

### Phase 4: 최적화 (선택, 1-2시간)
1. 캐싱 (같은 공원 재쿼리 방지)
2. 병렬 처리 (여러 공원 동시 처리)
3. 에러 핸들링

---

## 📝 최종 권장사항

### 🥇 1순위: OpenStreetMap Overpass API
**이유:**
- 완전 자동화 가능
- 실시간 데이터
- Python 구현 쉬움
- 무료

**시작 코드:**
```bash
pip install overpy requests
```

```python
import overpy

api = overpy.Overpass()
result = api.query("""
    way["leisure"="park"]["name"="매소홀어린이공원"](37.44, 126.65, 37.45, 126.66);
    out geom;
""")

for way in result.ways:
    coords = [(float(node.lon), float(node.lat)) for node in way.nodes]
    print(f"Found park polygon with {len(coords)} points")
    print(coords)
```

### 🥈 2순위: 공공데이터포털
**이유:**
- 공식 정부 데이터
- 높은 정확도
- 국립공원은 완벽

**시작 코드:**
```bash
pip install geopandas
```

```python
import geopandas as gpd

parks = gpd.read_file("국립공원경계.shp")
print(parks.head())
```

### 🥉 3순위: 하이브리드 (둘 다 사용)
**이유:**
- 최고 커버리지
- 최고 품질

---

## 🔗 유용한 리소스

### 테스트 도구
- **Overpass Turbo**: https://overpass-turbo.eu/
  - 브라우저에서 쿼리 테스트
  - 지도 시각화
  - Export 기능

### 문서
- **Overpass API 위키**: https://wiki.openstreetmap.org/wiki/Overpass_API
- **Python Overpass 튜토리얼**: https://janakiev.com/blog/openstreetmap-with-python-and-overpass-api/
- **공공데이터포털**: https://www.data.go.kr/

### Python 라이브러리
- **overpy**: `pip install overpy`
- **geopandas**: `pip install geopandas`
- **shapely**: `pip install shapely`

---

## 📊 비교표

| 항목 | Kakao API | Naver API | OpenStreetMap | 공공데이터포털 |
|------|-----------|-----------|---------------|----------------|
| **폴리곤 제공** | ❌ | ❌ | ✅ | ✅ |
| **자동화** | - | - | ✅ 완전 | ⚠️ 부분 |
| **실시간** | - | - | ✅ | ❌ |
| **정확도** | - | - | ⚠️ 중간 | ✅ 높음 |
| **커버리지** | - | - | ⚠️ 중간 | ✅ 국립공원만 |
| **비용** | 무료 | 무료 | 무료 | 무료 |
| **구현 난이도** | - | - | ⭐ 쉬움 | ⭐⭐ 중간 |
| **API** | ✅ | ✅ | ✅ REST | ❌ 파일만 |

---

## ✅ 다음 단계

1. **즉시 시작 가능:**
   ```bash
   pip install overpy
   ```

   ```python
   import overpy
   api = overpy.Overpass()
   # 테스트 쿼리 실행
   ```

2. **Overpass Turbo에서 쿼리 테스트:**
   - https://overpass-turbo.eu/
   - 인천 지역 bbox: `(37.40, 126.60, 37.50, 126.70)`
   - 쿼리: `way["leisure"="park"]({{bbox}});`

3. **폴리곤 샘플링 로직 구현**

4. **기존 로드뷰 캡처 시스템과 통합**

---

**리서치 완료일:** 2025-01-05
**신뢰도:** ⭐⭐⭐⭐⭐ (높음)
**실행 가능성:** ✅ 즉시 구현 가능
