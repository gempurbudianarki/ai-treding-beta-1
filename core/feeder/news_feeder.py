import time
from datetime import datetime, timedelta
from typing import List, Dict

import feedparser
import requests
import urllib3  # Import library buat handle warning SSL
from loguru import logger

# === FIX: Matikan warning SSL biar log bersih ===
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NewsFeeder:
    """
    Feeder berita sederhana berbasis RSS.
    - Pake beberapa sumber (multi-feed)
    - Pake User-Agent supaya nggak gampang di-403
    - Kalau semua gagal, balik list kosong (sentiment jadi neutral).
    """

    def __init__(self) -> None:
        # List feed bisa lo modif sendiri nanti
        self.feeds = [
            # CNBC World Markets
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            # Wall Street Journal Markets
            "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
            # NYTimes Business
            "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
            # FXStreet: market news (Sering error SSL, tapi sekarang udah kita bypass)
            "https://www.fxstreet.com/rss/news",
        ]

        # Header biar request keliatan kayak browser normal
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

    def _fetch_feed(self, url: str) -> List[Dict]:
        """
        Ambil satu feed RSS dan kembalikan list item sederhana:
        {title, published, link}
        """
        try:
            # === FIX SSL DISINI ===
            # verify=False artinya kita bodo amat sama sertifikat SSL yang error
            resp = requests.get(url, headers=self.headers, timeout=10, verify=False)
            resp.raise_for_status()
            parsed = feedparser.parse(resp.text)
        except Exception as e:
            # Jangan panik kalau satu feed gagal, kita masih punya feed lain
            logger.warning(f"NewsFeeder: gagal fetch {url}: {e}")
            return []

        items: List[Dict] = []
        for entry in parsed.entries[:20]:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "").strip()
            published = getattr(entry, "published", "") or getattr(
                entry, "updated", ""
            )

            if not title:
                continue

            item: Dict = {
                "title": title,
                "link": link,
                "published": published,
            }

            # feedparser biasanya nyimpen published_parsed di attribute
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                item["published_parsed"] = entry.published_parsed

            items.append(item)

        return items

    def get_recent_headlines(
        self,
        symbol: str,
        limit: int = 5,
        max_age_minutes: int = 60,
    ) -> List[str]:
        """
        Ambil beberapa headline terbaru (gabungan beberapa RSS).
        Parameter `symbol` belum dipakai, tapi nanti bisa buat filter spesifik
        (misal cuma ambil yang nyebut 'gold', 'XAU', 'dollar', dll).
        """
        all_items: List[Dict] = []
        for url in self.feeds:
            items = self._fetch_feed(url)
            all_items.extend(items)

        if not all_items:
            logger.warning("NewsFeeder: tidak ada item dari semua feed (mungkin jaringan atau blokir situs).")
            return []

        filtered: List[Dict] = []
        now = datetime.utcnow()
        max_delta = timedelta(minutes=max_age_minutes)

        for item in all_items:
            pub_struct = item.get("published_parsed", None)
            if not pub_struct:
                # Kalau nggak ada info waktu, tetep kita masukin
                filtered.append(item)
                continue

            try:
                pub_time = datetime.fromtimestamp(time.mktime(pub_struct))
                if now - pub_time <= max_delta:
                    filtered.append(item)
            except Exception:
                filtered.append(item)

        # Kalau setelah filter kosong, fallback ke semua item
        if not filtered:
            filtered = all_items

        # Sort by terbaru kalau ada waktu
        def sort_key(x: Dict):
            pub_struct = x.get("published_parsed", None)
            if not pub_struct:
                return 0
            return time.mktime(pub_struct)

        filtered_sorted = sorted(filtered, key=sort_key, reverse=True)

        headlines = [it["title"] for it in filtered_sorted]
        headlines = headlines[:limit]

        logger.info(
            "NewsFeeder: dapat {} headline (limit={}, max_age={}m)",
            len(headlines),
            limit,
            max_age_minutes,
        )
        return headlines