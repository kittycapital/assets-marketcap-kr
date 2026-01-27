# 🌍 전세계 자산 시가총액 순위

전세계 주요 자산(주식, 암호화폐, 귀금속)의 시가총액을 한눈에 보여주는 대시보드입니다.

![Preview](preview.png)

## 📊 포함된 자산

- **귀금속**: 금(Gold), 은(Silver)
- **주식**: 미국, 한국, 대만, 사우디 등 글로벌 대형주
- **암호화폐**: Bitcoin, Ethereum 등 상위 50개 코인

## 🛠️ 기술 스택

- **Frontend**: HTML, Tailwind CSS, Vanilla JS
- **Data Fetching**: Python + requests
- **자동 업데이트**: GitHub Actions (매일 UTC 00:00)
- **호스팅**: GitHub Pages (무료)

## 📡 데이터 소스 (무료 API)

| 자산 유형 | API | 제한 |
|----------|-----|------|
| 암호화폐 | CoinGecko | 30 calls/min, 10k/month |
| 주식 | FMP (선택) | 250 calls/day |
| 귀금속 | 가격 API + 수동 계산 | - |

### 귀금속 시가총액 계산 공식

```
금: 216,265톤 × 32,150.7oz/톤 × 현재가격
은: 1,751,000톤 × 32,150.7oz/톤 × 현재가격
```

## 🚀 설치 및 실행

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/assets-marketcap.git
cd assets-marketcap
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 데이터 수집

```bash
python scripts/fetch_data.py
```

### 4. HTML 생성

```bash
python scripts/generate_html.py
```

### 5. 로컬에서 확인

```bash
python -m http.server 8000
# http://localhost:8000 접속
```

## ⚙️ GitHub Actions 설정

### 필요한 Secrets (선택사항)

- `FMP_API_KEY`: FinancialModelingPrep API 키 (주식 실시간 데이터용)

### 워크플로우

`.github/workflows/update-data.yml` 파일이 매일 자동으로:
1. 암호화폐 데이터 수집 (CoinGecko)
2. 주식 데이터 수집 (FMP 또는 폴백)
3. 귀금속 시가총액 계산
4. HTML 파일 생성
5. GitHub Pages로 배포

## 📁 프로젝트 구조

```
assets-marketcap/
├── index.html              # 메인 페이지 (자동 생성)
├── data/
│   └── assets.json         # 자산 데이터 (자동 생성)
├── scripts/
│   ├── fetch_data.py       # 데이터 수집 스크립트
│   └── generate_html.py    # HTML 생성 스크립트
├── .github/
│   └── workflows/
│       └── update-data.yml # GitHub Actions 워크플로우
├── requirements.txt
└── README.md
```

## 🔧 커스터마이징

### 주식 목록 변경

`scripts/fetch_data.py`의 `TOP_STOCKS` 리스트를 수정하세요:

```python
TOP_STOCKS = [
    ("AAPL", "Apple", "🇺🇸 미국", "https://logo.clearbit.com/apple.com"),
    # 추가할 주식...
]
```

### 암호화폐 개수 변경

`fetch_crypto_data(limit=50)` 의 limit 값을 변경하세요.

## 📄 라이선스

MIT License

## 🙏 크레딧

- 암호화폐 데이터: [CoinGecko](https://www.coingecko.com/)
- 금 매장량: [World Gold Council](https://www.gold.org/)
- 은 매장량: [CPM Group](https://www.cpmgroup.com/)
- 기업 로고: [Clearbit](https://clearbit.com/)
