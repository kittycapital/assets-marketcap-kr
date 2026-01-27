#!/usr/bin/env python3
"""
시가총액 데이터 수집 스크립트
- 암호화폐: CoinGecko API (무료)
- 주식: FMP API (무료 티어) 또는 하드코딩
- 귀금속: 가격 API + 공급량 계산
"""

import json
import requests
from datetime import datetime, timezone
from pathlib import Path
import time

# ============================================
# 상수 정의
# ============================================

# 귀금속 지상 매장량 (톤)
GOLD_TONNES = 216265  # World Gold Council 2025
SILVER_TONNES = 1751000  # CPM Group Silver Yearbook
TROY_OZ_PER_TONNE = 32150.7

# API 엔드포인트
COINGECKO_API = "https://api.coingecko.com/api/v3"

# 주요 주식 목록 (심볼, 이름, 국가)
TOP_STOCKS = [
    ("AAPL", "Apple", "🇺🇸 미국", "https://logo.clearbit.com/apple.com"),
    ("NVDA", "NVIDIA", "🇺🇸 미국", "https://logo.clearbit.com/nvidia.com"),
    ("MSFT", "Microsoft", "🇺🇸 미국", "https://logo.clearbit.com/microsoft.com"),
    ("GOOG", "Alphabet (Google)", "🇺🇸 미국", "https://logo.clearbit.com/google.com"),
    ("AMZN", "Amazon", "🇺🇸 미국", "https://logo.clearbit.com/amazon.com"),
    ("META", "Meta Platforms", "🇺🇸 미국", "https://logo.clearbit.com/meta.com"),
    ("TSLA", "Tesla", "🇺🇸 미국", "https://logo.clearbit.com/tesla.com"),
    ("BRK-B", "Berkshire Hathaway", "🇺🇸 미국", "https://logo.clearbit.com/berkshirehathaway.com"),
    ("TSM", "TSMC", "🇹🇼 대만", "https://logo.clearbit.com/tsmc.com"),
    ("V", "Visa", "🇺🇸 미국", "https://logo.clearbit.com/visa.com"),
    ("JPM", "JPMorgan Chase", "🇺🇸 미국", "https://logo.clearbit.com/jpmorganchase.com"),
    ("WMT", "Walmart", "🇺🇸 미국", "https://logo.clearbit.com/walmart.com"),
    ("UNH", "UnitedHealth", "🇺🇸 미국", "https://logo.clearbit.com/unitedhealthgroup.com"),
    ("MA", "Mastercard", "🇺🇸 미국", "https://logo.clearbit.com/mastercard.com"),
    ("JNJ", "Johnson & Johnson", "🇺🇸 미국", "https://logo.clearbit.com/jnj.com"),
    ("PG", "Procter & Gamble", "🇺🇸 미국", "https://logo.clearbit.com/pg.com"),
    ("HD", "Home Depot", "🇺🇸 미국", "https://logo.clearbit.com/homedepot.com"),
    ("ORCL", "Oracle", "🇺🇸 미국", "https://logo.clearbit.com/oracle.com"),
    ("COST", "Costco", "🇺🇸 미국", "https://logo.clearbit.com/costco.com"),
    ("BAC", "Bank of America", "🇺🇸 미국", "https://logo.clearbit.com/bankofamerica.com"),
    ("2222.SR", "Saudi Aramco", "🇸🇦 사우디", "https://logo.clearbit.com/aramco.com"),
    ("005930.KS", "삼성전자", "🇰🇷 한국", "https://logo.clearbit.com/samsung.com"),
    ("000660.KS", "SK하이닉스", "🇰🇷 한국", "https://logo.clearbit.com/skhynix.com"),
    ("ASML", "ASML", "🇳🇱 네덜란드", "https://logo.clearbit.com/asml.com"),
    ("LLY", "Eli Lilly", "🇺🇸 미국", "https://logo.clearbit.com/lilly.com"),
    ("AVGO", "Broadcom", "🇺🇸 미국", "https://logo.clearbit.com/broadcom.com"),
    ("NVO", "Novo Nordisk", "🇩🇰 덴마크", "https://logo.clearbit.com/novonordisk.com"),
]


def fetch_crypto_data(limit=50):
    """CoinGecko에서 암호화폐 데이터 가져오기"""
    print(f"📡 암호화폐 데이터 수집 중... (상위 {limit}개)")
    
    try:
        url = f"{COINGECKO_API}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "true",
            "price_change_percentage": "24h,7d"
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        assets = []
        for coin in data:
            assets.append({
                "id": coin["id"],
                "name": coin["name"],
                "symbol": coin["symbol"].upper(),
                "price": coin["current_price"] or 0,
                "marketCap": coin["market_cap"] or 0,
                "change24h": round(coin["price_change_percentage_24h"] or 0, 2),
                "change7d": round(coin.get("price_change_percentage_7d_in_currency") or 0, 2),
                "type": "crypto",
                "country": "-",
                "image": coin["image"],
                "sparkline": coin.get("sparkline_in_7d", {}).get("price", [])
            })
        
        print(f"✅ 암호화폐 {len(assets)}개 수집 완료")
        return assets
        
    except Exception as e:
        print(f"❌ 암호화폐 데이터 수집 실패: {e}")
        return []


def fetch_gold_price():
    """금 가격 가져오기 (CoinGecko의 Tether Gold 또는 대체 소스)"""
    print("📡 금 가격 수집 중...")
    
    try:
        # Tether Gold (XAUT)는 금 1온스와 1:1 페깅
        url = f"{COINGECKO_API}/simple/price"
        params = {
            "ids": "tether-gold",
            "vs_currencies": "usd",
            "include_24hr_change": "true"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "tether-gold" in data:
            price = data["tether-gold"]["usd"]
            change24h = data["tether-gold"].get("usd_24h_change", 0)
            print(f"✅ 금 가격: ${price:.2f}")
            return price, round(change24h, 2)
            
    except Exception as e:
        print(f"⚠️ Tether Gold 가격 수집 실패: {e}")
    
    # 폴백: 대략적인 가격 사용
    print("⚠️ 금 가격 폴백 사용: $2950")
    return 2950, 0.1


def fetch_silver_price():
    """은 가격 가져오기"""
    print("📡 은 가격 수집 중...")
    
    # CoinGecko에는 은 직접 추적이 없으므로 폴백 사용
    # 실제 프로덕션에서는 metals-api.com 등 사용
    print("⚠️ 은 가격 폴백 사용: $33")
    return 33.0, -0.3


def calculate_metal_market_caps():
    """귀금속 시가총액 계산"""
    print("\n🥇 귀금속 시가총액 계산 중...")
    
    gold_price, gold_change = fetch_gold_price()
    silver_price, silver_change = fetch_silver_price()
    
    # 시가총액 계산: 매장량(톤) × 온스/톤 × 가격
    gold_market_cap = GOLD_TONNES * TROY_OZ_PER_TONNE * gold_price
    silver_market_cap = SILVER_TONNES * TROY_OZ_PER_TONNE * silver_price
    
    print(f"✅ 금 시가총액: ${gold_market_cap / 1e12:.2f}T")
    print(f"✅ 은 시가총액: ${silver_market_cap / 1e12:.2f}T")
    
    return [
        {
            "id": "gold",
            "name": "금 (Gold)",
            "symbol": "GOLD",
            "price": gold_price,
            "marketCap": gold_market_cap,
            "change24h": gold_change,
            "change7d": gold_change * 2,  # 추정치
            "type": "metal",
            "country": "-",
            "emoji": "🥇",
            "sparkline": []
        },
        {
            "id": "silver",
            "name": "은 (Silver)",
            "symbol": "SILVER",
            "price": silver_price,
            "marketCap": silver_market_cap,
            "change24h": silver_change,
            "change7d": silver_change * 3,  # 추정치
            "type": "metal",
            "country": "-",
            "emoji": "🥈",
            "sparkline": []
        }
    ]


def fetch_stock_data_fmp(api_key=None):
    """FMP API에서 주식 데이터 가져오기 (API 키 필요)"""
    if not api_key:
        print("⚠️ FMP API 키 없음 - 하드코딩된 데이터 사용")
        return fetch_stock_data_fallback()
    
    print("📡 FMP API에서 주식 데이터 수집 중...")
    
    assets = []
    symbols = [s[0] for s in TOP_STOCKS if not s[0].endswith('.KS') and not s[0].endswith('.SR')]
    
    try:
        # 배치 요청
        symbols_str = ",".join(symbols[:20])  # 무료 티어 제한
        url = f"https://financialmodelingprep.com/api/v3/quote/{symbols_str}?apikey={api_key}"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        stock_info = {s[0]: s for s in TOP_STOCKS}
        
        for stock in data:
            symbol = stock["symbol"]
            if symbol in stock_info:
                _, name, country, image = stock_info[symbol]
                assets.append({
                    "id": symbol.lower(),
                    "name": name,
                    "symbol": symbol,
                    "price": stock["price"],
                    "marketCap": stock["marketCap"],
                    "change24h": round(stock["changesPercentage"], 2),
                    "change7d": round(stock["changesPercentage"] * 1.5, 2),  # 추정
                    "type": "stock",
                    "country": country,
                    "image": image,
                    "sparkline": []
                })
        
        print(f"✅ 주식 {len(assets)}개 수집 완료 (FMP)")
        
    except Exception as e:
        print(f"❌ FMP API 오류: {e}")
        return fetch_stock_data_fallback()
    
    # 한국/사우디 주식 추가 (별도 API 필요하므로 하드코딩)
    assets.extend(get_korean_stocks_fallback())
    
    return assets


def fetch_stock_data_fallback():
    """API 없을 때 사용하는 폴백 데이터"""
    print("📊 주식 폴백 데이터 사용")
    
    # 2026년 1월 기준 대략적인 시가총액 (실제 데이터로 교체 필요)
    fallback_data = {
        "AAPL": (229.86, 3.45e12, 0.87),
        "NVDA": (142.62, 3.49e12, 2.34),
        "MSFT": (420.55, 3.12e12, 1.23),
        "GOOG": (192.46, 2.35e12, -0.45),
        "AMZN": (222.12, 2.32e12, 1.56),
        "META": (645.23, 1.64e12, 2.12),
        "TSLA": (351.34, 1.12e12, -1.23),
        "BRK-B": (502.12, 1.08e12, 0.34),
        "TSM": (189.45, 0.98e12, -0.89),
        "V": (342.67, 0.65e12, 0.45),
        "JPM": (252.34, 0.72e12, 0.67),
        "WMT": (92.45, 0.74e12, 0.12),
        "UNH": (512.78, 0.47e12, -0.34),
        "MA": (528.45, 0.52e12, 0.78),
        "JNJ": (152.34, 0.37e12, 0.23),
        "PG": (172.56, 0.41e12, 0.45),
        "HD": (412.34, 0.38e12, 1.12),
        "ORCL": (178.90, 0.49e12, 2.34),
        "COST": (945.67, 0.42e12, 0.89),
        "BAC": (42.56, 0.33e12, 0.56),
        "2222.SR": (27.85, 1.85e12, 0.22),
        "ASML": (745.23, 0.30e12, 1.45),
        "LLY": (782.34, 0.74e12, 3.21),
        "AVGO": (235.67, 0.98e12, 1.89),
        "NVO": (98.45, 0.42e12, 0.67),
    }
    
    stock_info = {s[0]: s for s in TOP_STOCKS}
    assets = []
    
    for symbol, (price, market_cap, change) in fallback_data.items():
        if symbol in stock_info:
            _, name, country, image = stock_info[symbol]
            assets.append({
                "id": symbol.lower(),
                "name": name,
                "symbol": symbol,
                "price": price,
                "marketCap": market_cap,
                "change24h": change,
                "change7d": change * 1.5,
                "type": "stock",
                "country": country,
                "image": image,
                "sparkline": []
            })
    
    # 한국 주식 추가
    assets.extend(get_korean_stocks_fallback())
    
    return assets


def get_korean_stocks_fallback():
    """한국 주식 폴백 데이터"""
    return [
        {
            "id": "samsung",
            "name": "삼성전자",
            "symbol": "005930",
            "price": 53200,
            "marketCap": 318e9,
            "change24h": -1.2,
            "change7d": -3.5,
            "type": "stock",
            "country": "🇰🇷 한국",
            "image": "https://logo.clearbit.com/samsung.com",
            "sparkline": []
        },
        {
            "id": "skhynix",
            "name": "SK하이닉스",
            "symbol": "000660",
            "price": 178500,
            "marketCap": 130e9,
            "change24h": -0.8,
            "change7d": -2.1,
            "type": "stock",
            "country": "🇰🇷 한국",
            "image": "https://logo.clearbit.com/skhynix.com",
            "sparkline": []
        }
    ]


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🚀 시가총액 데이터 수집 시작")
    print(f"📅 {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 50)
    
    all_assets = []
    
    # 1. 귀금속 데이터
    metals = calculate_metal_market_caps()
    all_assets.extend(metals)
    time.sleep(1)  # Rate limit 방지
    
    # 2. 암호화폐 데이터
    crypto = fetch_crypto_data(limit=50)
    all_assets.extend(crypto)
    time.sleep(1)
    
    # 3. 주식 데이터
    import os
    fmp_key = os.environ.get("FMP_API_KEY")
    stocks = fetch_stock_data_fmp(fmp_key)
    all_assets.extend(stocks)
    
    # 시가총액 순 정렬
    all_assets.sort(key=lambda x: x["marketCap"], reverse=True)
    
    # 결과 저장
    output = {
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
        "totalAssets": len(all_assets),
        "assets": all_assets
    }
    
    output_path = Path(__file__).parent.parent / "data" / "assets.json"
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print(f"✅ 완료! 총 {len(all_assets)}개 자산 저장됨")
    print(f"📁 저장 위치: {output_path}")
    print("=" * 50)
    
    # 상위 10개 출력
    print("\n📊 시가총액 상위 10개:")
    for i, asset in enumerate(all_assets[:10], 1):
        mc = asset["marketCap"]
        if mc >= 1e12:
            mc_str = f"${mc/1e12:.2f}T"
        else:
            mc_str = f"${mc/1e9:.0f}B"
        print(f"  {i:2}. {asset['name'][:20]:<20} {mc_str:>10}")


if __name__ == "__main__":
    main()
