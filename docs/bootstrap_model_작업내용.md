# 부트스트랩 모델 작업 내용 (2026-05-06)

담당: 정인

---

## 작업 배경

실제 정류장 데이터가 없어서 모델 학습이 불가능한 상황.
`/current`, `/predict` API 호출 시 예측값이 전부 `null`로 반환되는 문제를 해결하기 위해
진짜 데이터가 쌓일 때까지 버틸 임시 모델을 제작.

---

## 생성 파일

### `model/bootstrap_A_rule.py` - 옵션 A: 규칙 기반 모델
- `buses_arriving_20min` + 출퇴근 시간대 기준으로 여유/보통/혼잡 분류
- LightGBM 없이 규칙만으로 동작
- 장점: 단순하고 빠름
- 단점: 날씨/요일 등 복합 피처 미반영

### `model/bootstrap_B_synthetic.py` - 옵션 B: 합성 데이터 LightGBM (채택)
- 2만 건의 합성 데이터 생성 후 LightGBM 학습
- 출퇴근 시간대, 주말, 공휴일, 강수 등 패턴 반영
- 검증 정확도: 100% (합성 데이터 기준)
- 피처 중요도 1위: `buses_arriving_20min` → 2위: `hour`
- 실 데이터 확보 후 `model.train`으로 교체 예정

---

## 실행 방법

```bash
# 옵션 B로 모델 생성 (채택)
cd /home/jovyan/work/bus-congestion
python -m model.bootstrap_B_synthetic
# → model/saved/lgbm_model.pkl 생성됨
```

---

## 주의사항

- `model/saved/lgbm_model.pkl`은 `.gitignore`에 등록되어 있어 GitHub에 올라가지 않음
- 팀원 각자 아래 명령어로 모델 생성 필요:
  ```bash
  python -m model.bootstrap_B_synthetic
  ```

---

## 환경변수 (.env)

프로젝트 루트에 `.env` 파일 생성 필요 (GitHub에 올라가지 않음):

```
DATA_GO_KR_KEY=발급받은키
KMA_API_KEY=발급받은키
AIR_KOREA_KEY=DATA_GO_KR_KEY와 동일
PORT=8000
FRONTEND_URL=http://localhost:3000
```

---

## 다음 단계

1. 스케줄러 실행으로 실제 데이터 수집 시작 (최소 3~4일)
   ```bash
   python -m data.collect.scheduler
   ```
2. 데이터 충분히 쌓인 후 실 데이터로 재학습
   ```bash
   python -m model.train --data data/processed/merged.csv
   ```
