# 수원대 7790 버스정류장 혼잡도 예측 서비스

실시간 버스 데이터, 날씨, 학사일정을 활용해 수원대학교 버스정류장(7790)의 혼잡도를 **혼잡 / 보통 / 여유** 3단계로 예측하는 서비스.

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
| 실시간 버스 도착 | TAGO API (data.go.kr) | 배차 간격, 도착 예정 버스 수 |
| 날씨 (기온/강수) | 기상청 API허브 | 날씨 피처 |
| 미세먼지 | 에어코리아 API | PM10, PM2.5 피처 |
| 공휴일 | 한국천문연구원 API | 공휴일 여부 피처 |
| 학사일정 | 수원대학교 홈페이지 | 학기/시험/수업시간 피처 |
| 과거 승하차 데이터 | stcis.go.kr | 모델 학습용 |

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
│   │   ├── academic_calendar.py  수원대 학사일정
│   │   └── scheduler.py          5분 폴링 스케줄러
│   ├── raw/                      원본 데이터 (gitignore)
│   └── processed/                전처리 데이터 (gitignore)
├── model/
│   ├── features.py               피처 엔지니어링
│   ├── train.py                  LightGBM 학습
│   ├── predict.py                현재 + 30/60분 후 예측
│   └── saved/                    학습된 모델 (gitignore)
├── backend/
│   ├── main.py                   FastAPI 앱
│   ├── schema.py                 Pydantic 스키마
│   └── routers/
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
    └── git_rule.md               우리 프로젝트 Git 규칙
```

---

## 시작하기

### 1. 레포 클론

```bash
git clone https://github.com/[레포주소].git
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

### 3. 백엔드 실행

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
# → http://localhost:8000
```

### 4. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 5. 데이터 수집 스케줄러 실행 (별도 터미널)

```bash
python -m data.collect.scheduler
# 5분마다 데이터 수집 → bus_congestion.db에 저장
```

### 6. 모델 학습 (과거 데이터 확보 후)

```bash
python -m model.train --data data/processed/merged.csv
```

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/current` | 현재 혼잡도 |
| GET | `/predict` | 현재 + 30/60분 후 예측 |
| GET | `/alert/check?label=혼잡` | 알림 발송 여부 |
| POST | `/alert/config` | 알림 임계값 설정 |
| GET | `/health` | 서버 상태 확인 |

---

## Docker로 한번에 실행

```bash
cp .env.example .env   # API 키 입력 후
docker-compose up --build
```

---

## 브랜치 전략

```
main   → 발표용 최종 버전
dev    → 개발 통합 브랜치
feat/* → 각자 작업 브랜치
```

자세한 규칙은 [docs/git_rule.md](docs/git_rule.md) 참고.

---

## 혼잡도 기준

| 단계 | 정류장 대기 인원 | 색상 |
|------|----------------|------|
| 혼잡 | 15명 이상 | 빨강 |
| 보통 | 7 ~ 14명 | 노랑 |
| 여유 | 6명 이하 | 초록 |

> 수원대 7790 정류장 실측 후 임계값 조정 예정
