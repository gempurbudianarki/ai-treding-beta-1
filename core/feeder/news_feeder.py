import time
from datetime import datetime, timedelta
from typing import List, Dict
import feedparser
import requests
import urllib3
from loguru import logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class NewsFeeder:
    """
    Feeder berita v2: Sumber lebih stabil & Anti-Blokir.
    """
    def __init__(self) -> None:
        self.feeds = [
            # Investing.com (Biasanya stabil)
            "https://www.investing.com/rss/news.rss",
            # DailyFX (Bagus untuk forex/gold)
            "https://www.dailyfx.com/feeds/market-news",
            # CNBC Market (Cadangan)
            "https://www.cnbc.com/id/10000664/device/rss/rss.html",
            # Reuters Business
            "http://feeds.reuters.com/reuters/businessNews"
        ]
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def _fetch_feed(self, url: str) -> List[Dict]:
        try:
            # Timeout dipercepat biar gak nunggu lama
            resp = requests.get(url, headers=self.headers, timeout=5, verify=False)
            if resp.status_code != 200: return []
            
            parsed = feedparser.parse(resp.content)
            if not parsed.entries: return []
            
            items = []
            for entry in parsed.entries[:5]: # Ambil 5 teratas aja per feed
                title = getattr(entry, "title", "").strip()
                if title:
                    items.append({
                        "title": title,
                        "link": getattr(entry, "link", ""),
                        "published_parsed": getattr(entry, "published_parsed", None)
                    })
            return items
        except Exception as e:
            # Silent error biar log gak penuh spam
            return []

    def get_recent_headlines(self, symbol: str, limit: int = 5, max_age_minutes: int = 60) -> List[str]:
        all_items = []
        for url in self.feeds:
            items = self._fetch_feed(url)
            all_items.extend(items)

        if not all_items:
            # Fallback text kalau semua offline, biar AI gak bingung
            return ["Market is quiet.", "No significant news detected."]

        # Filter Berita Lama
        filtered = []
        now = datetime.utcnow()
        limit_time = now - timedelta(minutes=max_age_minutes)

        for item in all_items:
            pub = item.get("published_parsed")
            if pub:
                try:
                    pub_dt = datetime.fromtimestamp(time.mktime(pub))
                    if pub_dt > limit_time:
                        filtered.append(item)
                except: pass
            else:
                # Kalau gak ada tanggal, anggap baru
                filtered.append(item)

        # Sort dari yang paling baru (kalau ada tanggalnya)
        # Ambil title-nya aja
        headlines = [x['title'] for x in filtered[:limit]]
        
        logger.info(f"NewsFeeder: Fetched {len(headlines)} headlines.")
        return headlines