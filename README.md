# 7790번 버스 혼잡도 예측 서비스

실시간 버스 데이터, 날씨, 공휴일 정보를 활용해 **7790번 버스(협성대정문 ↔ 사당역)**의
수원대입구 정류장 혼잡도를 **혼잡 / 보통 / 여유** 3단계로 예측하는 서비스.

> **발표 검증**: 수원대입구 정류장에서 실사진과 예측값을 비교해 발표한다.

---

## 팀원

| 이름 | 역할 |
|------|------|
| 조장 | 전체 설계 + 모델 학습 |
| 정인 | 데이터 수집 파이프라인 |
| 승민 | FastAPI 백엔드 |
| 승주 | Next.js 프론트엔드 |
| 성빈 | 검증 + 발표자료 |

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| 예측 모델 | LightGBM |
| 백엔드 | FastAPI, Python 3.11 |
| 프론트엔드 | Next.js 14, Tailwind CSS, Recharts |
| 지도 | React-Leaflet (OpenStreetMap) |
| DB | SQLite |
| 배포 | Docker Compose |

---

## 데이터 소스

| 데이터 | 출처 | 용도 |
|--------|------|------|
| 7790번 버스 재차인원 (시간대별) | stcis.go.kr | 혼잡도 레이블 생성 (학습용) |
| 실시간 버스 도착 | TAGO API (data.go.kr) | 배차 간격, 도착 예정 버스 수 |
| 날씨 (기온/강수) | 기상청 API허브 | 날씨 피처 |
| 미세먼지 | 에어코리아 API | PM10 피처 |
| 공휴일 | 한국천문연구원 API | 공휴일 여부 피처 |

---

## 혼잡도 기준 (재차인원 기반)

버스 정원 70명 기준으로 설정.

| 단계 | 재차인원 | 색상 |
|------|---------|------|
| 혼잡 | 50명 이상 | 빨강 |
| 보통 | 20 ~ 49명 | 노랑 |
| 여유 | 19명 이하 | 초록 |

> 임계값은 stcis 데이터 분포에 따라 조정 예정

---

## 데이터 파이프라인

```
stcis.go.kr
(7790번 버스 정류장별 재차인원 CSV 다운로드)
        ↓
data/raw/stcis_7790.csv
        ↓
python -m data.process.build_dataset
(재차인원 → 혼잡도 레이블 + 날씨/요일 피처 결합)
        ↓
data/processed/merged.csv
        ↓
python -m model.train --data data/processed/merged.csv
(LightGBM 학습)
        ↓
model/saved/lgbm_model.pkl
```

---

## 모델 피처

| 피처 | 설명 | 출처 |
|------|------|------|
| `hour` | 시간대 | 시간 |
| `day_of_week`, `is_weekend` | 요일 | 시간 |
| `is_holiday` | 공휴일 여부 | 한국천문연구원 API |
| `temp`, `precipitation`, `is_raining` | 날씨 | 기상청 API |
| `pm10` | 미세먼지 | 에어코리아 API |
| `buses_arriving_20min` | 20분 내 도착 버스 수 | TAGO API |
| `avg_interval_min` | 평균 배차 간격 | TAGO API |

**레이블**: stcis.go.kr 재차인원 기반 혼잡도 (혼잡/보통/여유)

---

## 프로젝트 구조

```
bus-congestion/
├── data/
│   ├── collect/
│   │   ├── tago_client.py        TAGO 버스 API
│   │   ├── weather_client.py     기상청 API
│   │   ├── airkorea_client.py    에어코리아 API
│   │   ├── holiday_client.py     공휴일 API
│   │   └── scheduler.py          5분 폴링 스케줄러
│   ├── process/
│   │   └── build_dataset.py      stcis CSV → 학습용 데이터셋 변환
│   ├── raw/                      원본 데이터 (gitignore)
│   └── processed/                전처리 데이터 (gitignore)
├── model/
│   ├── features.py               피처 엔지니어링
│   ├── train.py                  LightGBM 학습
│   ├── predict.py                현재 + 30/60분 후 예측
│   ├── bootstrap_A_rule.py       규칙 기반 임시 모델
│   ├── bootstrap_B_synthetic.py  합성 데이터 임시 모델 (현재 사용 중)
│   └── saved/                    학습된 모델 (gitignore)
├── backend/
│   ├── main.py                   FastAPI 앱
│   ├── schema.py                 Pydantic 스키마
│   └── routers/
│       ├── stops.py              GET /stops/search
│       ├── current.py            GET /current
│       ├── predict.py            GET /predict
│       └── alert.py              GET/POST /alert
├── frontend/
│   ├── pages/index.tsx           메인 화면
│   └── components/
│       ├── CongestionBadge.tsx   혼잡도 뱃지
│       ├── StopCard.tsx          정류장 정보 카드
│       ├── BusStopMap.tsx        지도
│       └── PredictionChart.tsx   예측 차트
└── docs/
    ├── git_guide.md              Git 기본 설명
    ├── git_rule.md               우리 프로젝트 Git 규칙
    └── bootstrap_model_작업내용.md  임시 모델 작업 내용
```

---

## 시작하기

### 1. 레포 클론

```bash
git clone https://github.com/ih021088-ui/bus-congestion.git
cd bus-congestion
git checkout dev
```

### 2. 환경변수 설정

```bash
cp .env.example .env
# .env 파일 열어서 API 키 입력
```

필요한 API 키:
- `DATA_GO_KR_KEY` → [data.go.kr](https://www.data.go.kr) 회원가입 후 발급
- `KMA_API_KEY` → [apihub.kma.go.kr](https://apihub.kma.go.kr) 회원가입 후 발급
- `AIR_KOREA_KEY` → DATA_GO_KR_KEY와 동일

### 3. stcis 데이터 준비

1. [stcis.go.kr](https://stcis.go.kr) 접속
2. 노선·정류장 지표 → 노선별 차내 재차인원
3. 7790번 노선 선택 → 날짜 설정 → 다운로드
4. `data/raw/stcis_7790.csv` 로 저장

### 4. 데이터셋 생성 및 모델 학습

```bash
python -m data.process.build_dataset
python -m model.train --data data/processed/merged.csv
```

임시 모델 사용 시 (stcis 데이터 없을 때):
```bash
python -m model.bootstrap_B_synthetic
```

### 5. 백엔드 실행

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
# → http://localhost:8000/docs
```

### 6. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/current?stop_id=GGB234000743&city_code=31&region=화성` | 현재 혼잡도 |
| GET | `/predict?stop_id=GGB234000743&city_code=31&region=화성` | 30/60분 후 예측 |
| GET | `/health` | 서버 상태 확인 |

---

## 브랜치 전략

```
main   → 발표용 최종 버전
dev    → 개발 통합 브랜치
feat/* → 각자 작업 브랜치
```

자세한 규칙은 [docs/git_rule.md](docs/git_rule.md) 참고.
