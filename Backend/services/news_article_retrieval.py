import requests
import trafilatura
import re, os
import time, random
import io
import json
import pandas as pd
from config import NEWSDATA_API_KEY

NEWSDATA_LATEST_URL = "https://newsdata.io/api/1/latest"


class news_article_retrieval:

    def __init__(self, query: str, limit: int, session_id: str = None,
                 include_sources: list = None, exclude_sources: list = None):
        self.query = query
        self.df = None
        self.session_id = session_id
        self.include_sources = include_sources or []
        self.exclude_sources = exclude_sources or []
        self.valid_links = []
        self.news_ingest = self.news_ingestion(limit)

    # ------------------------------------------------------------------ #
    #  Accessors                                                           #
    # ------------------------------------------------------------------ #
    def get_data(self):
        return self.df

    def get_ingestion(self):
        return self.news_ingest

    def get_links(self):
        return self.valid_links

    # ------------------------------------------------------------------ #
    #  Fetch articles from newsdata.io                                    #
    # ------------------------------------------------------------------ #
    def news_ingestion(self, limit: int = 10):
        """
        Fetch the latest news articles from newsdata.io API.

        Docs: https://newsdata.io/documentation/#latest-news
        """
        if not NEWSDATA_API_KEY:
            return {
                "success": False,
                "data": [],
                "count": 0,
                "error": "NEWSDATA_API_KEY is not set in environment variables.",
                "source": "None"
            }

        try:
            all_results = []
            seen_ids = set()
            next_page = None          # cursor for pagination

            while len(all_results) < limit:
                params = {
                    "apikey": NEWSDATA_API_KEY,
                    "q": self.query,
                    "language": "en",
                    "size": min(10, limit - len(all_results)),  # max 10 per request
                }

                # Source filters — newsdata uses source_id (e.g. "bbc", "cnn")
                # We accept human-friendly names and normalise them to lowercase ids.
                if self.include_sources:
                    params["domainurl"] = ",".join(
                        [s.lower().replace(" ", "") for s in self.include_sources]
                    )
                if self.exclude_sources:
                    params["excludedomain"] = ",".join(
                        [s.lower().replace(" ", "") for s in self.exclude_sources]
                    )

                if next_page:
                    params["page"] = next_page

                print(f"[newsdata.io] Fetching: q={self.query!r} | page={next_page}")
                response = requests.get(NEWSDATA_LATEST_URL, params=params, timeout=15)
                response.raise_for_status()

                payload = response.json()

                if payload.get("status") != "success":
                    raise Exception(f"newsdata.io error: {payload.get('results', payload)}")

                articles = payload.get("results", [])
                if not articles:
                    print("[newsdata.io] No more results.")
                    break

                for item in articles:
                    uid = item.get("article_id") or item.get("link")
                    if uid and uid not in seen_ids:
                        seen_ids.add(uid)
                        all_results.append(item)
                    if len(all_results) >= limit:
                        break

                next_page = payload.get("nextPage")
                if not next_page:
                    break  # no more pages

            if not all_results:
                raise Exception("No results returned from newsdata.io")

            # ---- normalise to a flat DataFrame ---- #
            normalised = []
            for item in all_results[:limit]:
                link = item.get("link", "")
                self.valid_links.append(link)
                normalised.append({
                    "title":       item.get("title", ""),
                    "link":        link,
                    "media":       item.get("source_name", ""),
                    "source_id":   item.get("source_id", ""),
                    "source_url":  item.get("source_url", ""),
                    "desc":        item.get("description", ""),
                    "date":        item.get("pubDate", ""),
                    "image_url":   item.get("image_url", ""),
                    "category":    ", ".join(item.get("category") or []),
                    "country":     ", ".join(item.get("country") or []),
                    "language":    item.get("language", ""),
                    "article_id":  item.get("article_id", ""),
                })

            self.df = pd.DataFrame(normalised)
            self.df.drop_duplicates(subset=["title"], keep="last", inplace=True)
            self.df.reset_index(drop=True, inplace=True)

            print(f"[newsdata.io] Fetched {len(self.df)} articles.")
            print(self.df[["title", "media", "date"]].head())

            return {
                "success": True,
                "data": self.df.to_dict("records"),
                "count": len(self.df),
                "source": "newsdata.io"
            }

        except Exception as e:
            print(f"[newsdata.io] News retrieval failed: {e}")
            return {
                "success": False,
                "data": [],
                "count": 0,
                "error": str(e),
                "source": "None"
            }

    # ------------------------------------------------------------------ #
    #  Scrape full article content and save to disk                       #
    # ------------------------------------------------------------------ #
    def retrieve(self):
        try:
            latest_link = self.df["link"]
        except Exception:
            print(self.df)
            raise Exception("LINK column not found in DataFrame")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }

        descriptions = []
        for url in latest_link:
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code == 200:
                    extracted = trafilatura.extract(
                        resp.text, include_comments=False, include_tables=False
                    )
                    descriptions.append(extracted or "No content could be extracted.")
                else:
                    print(f"[retrieve] Failed: {url} (HTTP {resp.status_code})")
                    descriptions.append("Failed to retrieve the webpage.")
            except requests.exceptions.RequestException as e:
                print(f"[retrieve] Error fetching {url}: {e}")
                descriptions.append("Failed to retrieve the webpage.")

            time.sleep(random.uniform(1, 3))

        self.df["description"] = descriptions

        # ---- persist to disk ---- #
        folder_name = "NEWS_data"
        os.makedirs(folder_name, exist_ok=True)
        created_files = []

        for index, row in self.df.iterrows():
            filename = (
                f"{self.session_id}_description_{index + 1}.txt"
                if self.session_id
                else f"description_{index + 1}.txt"
            )
            file_path = os.path.join(folder_name, filename)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(row["description"])
            created_files.append(filename)

        if self.session_id:
            manifest_data = {
                "session_id": self.session_id,
                "query": self.query,
                "timestamp": time.time(),
                "article_count": len(self.df),
                "files": created_files,
            }
            manifest_path = os.path.join(folder_name, f"session_{self.session_id}.json")
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2)
            print(f"✓ Session manifest created: {manifest_path}")
