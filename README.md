# Free Korea Transit Tour — Streamlit Dashboard

실제 설문 원시 데이터(`raw_data.xlsx`, n=434)를 기반으로 한  
IPA 분석 포함 인터랙티브 대시보드입니다.

---

## 빠른 시작

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. raw_data.xlsx 를 이 폴더에 위치 확인

# 3. 앱 실행
streamlit run app.py
```

→ 브라우저가 자동으로 `http://localhost:8501` 을 엽니다.

---

## 6개 페이지 구성

| 페이지 | 주요 내용 |
|---|---|
| 📊 KPI Overview | 종합 만족도 9.33/10, 추천 98.6%, 재방문 의향 등 핵심 KPI + Q34 분포 + Q27 투어 요소 만족도 |
| 👥 Demographics | 성별·연령·목적·방문 경험·국적 Top 12·투어별 참여 현황 |
| 🎯 IPA Analysis | 15개 항목 사분면 산점도 + 5개 카테고리 IPA + Gap 분석 바 차트 + 상세 테이블 |
| ✈ Airport Competitiveness | Q9·Q10·Q12·Q14 공항 선택 영향 + Q21 WTP |
| 💡 Business Insights | 소비 분석(Q19·Q20) + Priority vs Satisfaction Gap + Q24 재방문 장벽 + Q23 희망 지역 |
| 💬 Open-Ended Feedback | Q16·Q17 키워드 분석 + 실제 응답 샘플 + Q28 경험 가치 |

---

## 필터 (사이드바)

- **Gender** 다중 선택
- **Age Group** 다중 선택

필터 변경 시 모든 차트가 실시간으로 업데이트됩니다.

---

## IPA 분석 방법론

- **Importance** : (1-1)~(5-1) 컬럼 평균 (5점 척도)
- **Satisfaction** : (1-2)~(5-2) 컬럼 평균 (5점 척도)
- **사분면 기준** : 15개 항목의 전체 평균선 교차점
- **Gap** = Satisfaction − Importance (양수=초과 달성)

| 사분면 | 조건 | 의미 |
|---|---|---|
| ★ Keep Up | imp↑ sat↑ | 현 수준 유지 |
| ▲ Concentrate Here | imp↑ sat↓ | 즉각 개선 필요 |
| ◆ Possible Overkill | imp↓ sat↑ | 자원 재배분 검토 |
| ○ Low Priority | imp↓ sat↓ | 우선순위 낮음 |
