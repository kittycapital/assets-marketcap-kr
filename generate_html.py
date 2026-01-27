#!/usr/bin/env python3
"""
JSON 데이터를 읽어서 HTML 파일에 임베드하는 스크립트
"""

import json
from pathlib import Path
from datetime import datetime

def generate_html():
    # 데이터 로드
    data_path = Path(__file__).parent.parent / "data" / "assets.json"
    
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    last_updated = data["lastUpdated"][:10]  # YYYY-MM-DD만
    assets_json = json.dumps(data["assets"], ensure_ascii=False)
    
    html_content = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>시가총액 순위 | 전세계 자산</title>
    <meta name="description" content="전세계 자산 시가총액 순위 - 주식, 암호화폐, 귀금속 포함">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Noto Sans KR', sans-serif; background: #0a0a0a; }}
        .asset-row:hover {{ background-color: #1a1a1a; }}
        .positive {{ color: #22c55e; }}
        .negative {{ color: #ef4444; }}
        .filter-btn.active {{ background-color: #3b82f6; color: white; }}
        .precious-metal {{ background-color: rgba(234, 179, 8, 0.1); }}
        .cryptocurrency {{ background-color: rgba(168, 85, 247, 0.1); }}
        .sparkline {{ height: 40px; }}
        .logo-fallback {{ 
            width: 32px; height: 32px; 
            border-radius: 50%; 
            background: linear-gradient(135deg, #374151, #1f2937);
            display: flex; align-items: center; justify-content: center;
            font-size: 14px; font-weight: bold; color: #9ca3af;
        }}
    </style>
</head>
<body class="text-gray-100">
    <div class="max-w-7xl mx-auto px-4 py-8">
        <!-- Header -->
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-white mb-2">🌍 전세계 자산 시가총액 순위</h1>
            <p class="text-gray-400">상장기업 / 귀금속 / 암호화폐 포함</p>
            <p class="text-xs text-gray-500 mt-2">📅 마지막 업데이트: {last_updated}</p>
        </div>

        <!-- Stats -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-gray-900 rounded-lg p-4 border border-gray-800">
                <div class="text-2xl font-bold text-white" id="total-count">-</div>
                <div class="text-sm text-gray-400">총 자산</div>
            </div>
            <div class="bg-gray-900 rounded-lg p-4 border border-gray-800">
                <div class="text-2xl font-bold text-yellow-400" id="metal-count">-</div>
                <div class="text-sm text-gray-400">귀금속</div>
            </div>
            <div class="bg-gray-900 rounded-lg p-4 border border-gray-800">
                <div class="text-2xl font-bold text-blue-400" id="stock-count">-</div>
                <div class="text-sm text-gray-400">주식</div>
            </div>
            <div class="bg-gray-900 rounded-lg p-4 border border-gray-800">
                <div class="text-2xl font-bold text-purple-400" id="crypto-count">-</div>
                <div class="text-sm text-gray-400">암호화폐</div>
            </div>
        </div>

        <!-- Filters -->
        <div class="flex gap-2 mb-6 flex-wrap">
            <button class="filter-btn active px-4 py-2 rounded-full text-sm font-medium bg-gray-800 hover:bg-gray-700 transition" data-filter="all">전체</button>
            <button class="filter-btn px-4 py-2 rounded-full text-sm font-medium bg-gray-800 hover:bg-gray-700 transition" data-filter="stock">🏢 주식</button>
            <button class="filter-btn px-4 py-2 rounded-full text-sm font-medium bg-gray-800 hover:bg-gray-700 transition" data-filter="metal">🥇 귀금속</button>
            <button class="filter-btn px-4 py-2 rounded-full text-sm font-medium bg-gray-800 hover:bg-gray-700 transition" data-filter="crypto">🪙 암호화폐</button>
        </div>

        <!-- Search -->
        <div class="mb-6">
            <input type="text" id="search-input" placeholder="자산 검색..." 
                   class="w-full md:w-80 px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-blue-500">
        </div>

        <!-- Table -->
        <div class="bg-gray-900 rounded-xl shadow-lg overflow-hidden border border-gray-800">
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-gray-800">
                            <th class="text-left py-4 px-4 text-sm font-semibold text-gray-400 w-16">순위</th>
                            <th class="text-left py-4 px-4 text-sm font-semibold text-gray-400">이름</th>
                            <th class="text-right py-4 px-4 text-sm font-semibold text-gray-400 cursor-pointer hover:text-white" onclick="sortBy('marketCap')">
                                시가총액 ↓
                            </th>
                            <th class="text-right py-4 px-4 text-sm font-semibold text-gray-400">가격</th>
                            <th class="text-right py-4 px-4 text-sm font-semibold text-gray-400 cursor-pointer hover:text-white" onclick="sortBy('change24h')">
                                24시간
                            </th>
                            <th class="text-center py-4 px-4 text-sm font-semibold text-gray-400 w-32">7일 차트</th>
                            <th class="text-center py-4 px-4 text-sm font-semibold text-gray-400 w-28">국가/유형</th>
                        </tr>
                    </thead>
                    <tbody id="assets-body">
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Pagination -->
        <div class="flex justify-center gap-2 mt-6" id="pagination">
        </div>

        <!-- Footer -->
        <div class="mt-8 p-6 bg-gray-900 rounded-xl border border-gray-800">
            <h2 class="text-lg font-semibold mb-4 text-white">📊 시가총액 계산 방식</h2>
            <div class="grid md:grid-cols-3 gap-4 text-sm">
                <div class="p-4 bg-yellow-900/20 rounded-lg border border-yellow-800/30">
                    <h3 class="font-semibold text-yellow-400 mb-2">🥇 금 (Gold)</h3>
                    <p class="text-yellow-200/70">216,265톤 × 32,150.7oz × 가격</p>
                    <p class="text-yellow-200/50 text-xs mt-1">World Gold Council 2025</p>
                </div>
                <div class="p-4 bg-gray-700/20 rounded-lg border border-gray-600/30">
                    <h3 class="font-semibold text-gray-300 mb-2">🥈 은 (Silver)</h3>
                    <p class="text-gray-400">1,751,000톤 × 32,150.7oz × 가격</p>
                    <p class="text-gray-500 text-xs mt-1">CPM Group Silver Yearbook</p>
                </div>
                <div class="p-4 bg-blue-900/20 rounded-lg border border-blue-800/30">
                    <h3 class="font-semibold text-blue-400 mb-2">📈 주식 & 암호화폐</h3>
                    <p class="text-blue-200/70">발행주식/유통량 × 현재가격</p>
                </div>
            </div>
        </div>

        <div class="mt-6 text-center text-sm text-gray-600">
            <p>데이터는 매일 자동 업데이트됩니다</p>
        </div>
    </div>

    <script>
        // ============================================
        // 📦 임베드된 데이터
        // ============================================
        const ASSETS_DATA = {assets_json};
        
        let currentFilter = 'all';
        let currentSort = 'marketCap';
        let sortDirection = 'desc';
        let currentPage = 1;
        const perPage = 50;
        let searchQuery = '';

        // Format functions
        function formatMarketCap(value) {{
            if (value >= 1e12) return `${{(value / 1e12).toFixed(2)}}T`;
            if (value >= 1e9) return `${{(value / 1e9).toFixed(1)}}B`;
            if (value >= 1e6) return `${{(value / 1e6).toFixed(1)}}M`;
            return `${{value.toFixed(2)}}`;
        }}

        function formatPrice(value, symbol) {{
            if (symbol === '005930' || symbol === '000660') return `₩${{value.toLocaleString()}}`;
            if (value >= 1000) return `${{value.toLocaleString('en-US', {{maximumFractionDigits: 2}})}}`;
            if (value >= 1) return `${{value.toFixed(2)}}`;
            if (value >= 0.01) return `${{value.toFixed(4)}}`;
            return `${{value.toFixed(6)}}`;
        }}

        // Create sparkline
        function createSparkline(data, change7d) {{
            const width = 100;
            const height = 35;
            const isPositive = change7d >= 0;
            const color = isPositive ? '#22c55e' : '#ef4444';
            
            if (data && data.length > 10) {{
                // Use actual sparkline data
                const step = Math.floor(data.length / 20);
                const sampled = data.filter((_, i) => i % step === 0).slice(-20);
                const min = Math.min(...sampled);
                const max = Math.max(...sampled);
                const range = max - min || 1;
                
                const points = sampled.map((val, i) => {{
                    const x = (i / (sampled.length - 1)) * width;
                    const y = height - 5 - ((val - min) / range) * (height - 10);
                    return `${{x}},${{y}}`;
                }}).join(' ');
                
                return `<svg width="${{width}}" height="${{height}}" class="sparkline">
                    <polyline fill="none" stroke="${{color}}" stroke-width="2" points="${{points}}" />
                </svg>`;
            }}
            
            // Generate fake sparkline based on change
            const points = [];
            for (let i = 0; i < 7; i++) {{
                const progress = i / 6;
                const y = isPositive 
                    ? 28 - progress * 18 + (Math.random() - 0.5) * 8
                    : 10 + progress * 18 + (Math.random() - 0.5) * 8;
                points.push(`${{i * 15 + 5}},${{Math.max(5, Math.min(30, y))}}`);
            }}
            
            return `<svg width="${{width}}" height="${{height}}" class="sparkline">
                <polyline fill="none" stroke="${{color}}" stroke-width="2" points="${{points.join(' ')}}" />
            </svg>`;
        }}

        // Get filtered and sorted data
        function getFilteredData() {{
            let filtered = ASSETS_DATA;
            
            if (currentFilter !== 'all') {{
                filtered = filtered.filter(a => a.type === currentFilter);
            }}
            
            if (searchQuery) {{
                const query = searchQuery.toLowerCase();
                filtered = filtered.filter(a => 
                    a.name.toLowerCase().includes(query) || 
                    a.symbol.toLowerCase().includes(query)
                );
            }}
            
            filtered.sort((a, b) => {{
                const aVal = a[currentSort] || 0;
                const bVal = b[currentSort] || 0;
                return sortDirection === 'desc' ? bVal - aVal : aVal - bVal;
            }});
            
            return filtered;
        }}

        // Render table
        function renderTable() {{
            const tbody = document.getElementById('assets-body');
            tbody.innerHTML = '';
            
            const filtered = getFilteredData();
            const totalPages = Math.ceil(filtered.length / perPage);
            const start = (currentPage - 1) * perPage;
            const paged = filtered.slice(start, start + perPage);
            
            paged.forEach((asset, index) => {{
                const globalRank = start + index + 1;
                const rowClass = asset.type === 'metal' ? 'precious-metal' : 
                               asset.type === 'crypto' ? 'cryptocurrency' : '';
                
                const typeLabel = asset.type === 'metal' ? '🏆 귀금속' :
                                 asset.type === 'crypto' ? '🪙 암호화폐' : asset.country;
                
                const row = document.createElement('tr');
                row.className = `asset-row border-b border-gray-800 ${{rowClass}}`;
                
                const imgHtml = asset.image 
                    ? `<img src="${{asset.image}}" alt="${{asset.name}}" class="w-8 h-8 rounded-full bg-gray-800" onerror="this.outerHTML='<div class=\\'logo-fallback\\'>${{asset.symbol.charAt(0)}}</div>'">`
                    : `<div class="logo-fallback">${{asset.emoji || asset.symbol.charAt(0)}}</div>`;
                
                row.innerHTML = `
                    <td class="py-4 px-4 text-gray-400 font-medium">${{globalRank}}</td>
                    <td class="py-4 px-4">
                        <div class="flex items-center gap-3">
                            ${{imgHtml}}
                            <div>
                                <div class="font-semibold text-white">${{asset.name}}</div>
                                <div class="text-xs text-gray-500">${{asset.symbol}}</div>
                            </div>
                        </div>
                    </td>
                    <td class="py-4 px-4 text-right font-medium text-white">${{formatMarketCap(asset.marketCap)}}</td>
                    <td class="py-4 px-4 text-right text-gray-300">${{formatPrice(asset.price, asset.symbol)}}</td>
                    <td class="py-4 px-4 text-right font-medium ${{asset.change24h >= 0 ? 'positive' : 'negative'}}">
                        ${{asset.change24h >= 0 ? '+' : ''}}${{asset.change24h.toFixed(2)}}%
                    </td>
                    <td class="py-4 px-4">
                        <div class="flex justify-center">
                            ${{createSparkline(asset.sparkline, asset.change7d)}}
                        </div>
                    </td>
                    <td class="py-4 px-4 text-center text-sm text-gray-400">${{typeLabel}}</td>
                `;
                
                tbody.appendChild(row);
            }});
            
            renderPagination(totalPages);
            updateStats();
        }}

        // Render pagination
        function renderPagination(totalPages) {{
            const container = document.getElementById('pagination');
            container.innerHTML = '';
            
            if (totalPages <= 1) return;
            
            for (let i = 1; i <= totalPages; i++) {{
                const btn = document.createElement('button');
                btn.className = `px-3 py-1 rounded ${{i === currentPage ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}}`;
                btn.textContent = i;
                btn.onclick = () => {{ currentPage = i; renderTable(); }};
                container.appendChild(btn);
            }}
        }}

        // Update stats
        function updateStats() {{
            document.getElementById('total-count').textContent = ASSETS_DATA.length;
            document.getElementById('metal-count').textContent = ASSETS_DATA.filter(a => a.type === 'metal').length;
            document.getElementById('stock-count').textContent = ASSETS_DATA.filter(a => a.type === 'stock').length;
            document.getElementById('crypto-count').textContent = ASSETS_DATA.filter(a => a.type === 'crypto').length;
        }}

        // Sort function
        function sortBy(field) {{
            if (currentSort === field) {{
                sortDirection = sortDirection === 'desc' ? 'asc' : 'desc';
            }} else {{
                currentSort = field;
                sortDirection = 'desc';
            }}
            currentPage = 1;
            renderTable();
        }}

        // Initialize
        renderTable();
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                currentPage = 1;
                renderTable();
            }});
        }});
        
        // Search
        document.getElementById('search-input').addEventListener('input', (e) => {{
            searchQuery = e.target.value;
            currentPage = 1;
            renderTable();
        }});
    </script>
</body>
</html>'''
    
    # HTML 파일 저장
    output_path = Path(__file__).parent.parent / "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ HTML 생성 완료: {output_path}")


if __name__ == "__main__":
    generate_html()
