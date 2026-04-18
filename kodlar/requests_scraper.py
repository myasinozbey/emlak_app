from dataclasses import dataclass
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup


@dataclass
class RequestsScraperConfig:
    base_url: str = "https://www.hepsiemlak.com/mentese-satilik"
    max_pages: int = 11
    timeout: int = 20


class HepsiEmlakRequestsScraper:
    def __init__(self, config: RequestsScraperConfig | None = None):
        self.config = config or RequestsScraperConfig()
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            }
        )

    @staticmethod
    def _text(el: Any) -> str:
        return el.get_text(strip=True) if el else ""

    def _parse_page(self, html: str) -> list[dict[str, str]]:
        soup = BeautifulSoup(html, "html.parser")

        # Week 3: find / find_all kullanimi
        cards = soup.find_all("li", class_=lambda c: c and "list-view-item" in c)
        rows: list[dict[str, str]] = []

        for card in cards:
            lokasyon = self._text(card.find("span", class_="list-view-location"))
            m2 = self._text(card.find("dd", class_=lambda c: c and "squareMeter" in c))
            bina_yasi = self._text(card.find("dd", class_=lambda c: c and "buildingAge" in c))
            fiyat_block = card.find("p", class_=lambda c: c and "list-view-price" in c)
            fiyat = self._text(fiyat_block.find("strong") if fiyat_block else None)

            if any([lokasyon, m2, bina_yasi, fiyat]):
                rows.append(
                    {
                        "Lokasyon": lokasyon,
                        "m2": m2,
                        "Bina Yaşı": bina_yasi,
                        "Fiyat": fiyat,
                    }
                )

        return rows

    def scrape(self) -> pd.DataFrame:
        all_rows: list[dict[str, str]] = []

        for page in range(1, self.config.max_pages + 1):
            url = f"{self.config.base_url}?page={page}"
            try:
                resp = self.session.get(url, timeout=self.config.timeout)
                resp.raise_for_status()
                all_rows.extend(self._parse_page(resp.text))
            except requests.RequestException:
                continue

        if not all_rows:
            raise ValueError(
                "Requests scraper veri cekemedi. Bu sayfa JS ile yukleniyor olabilir; Selenium modunu kullanin."
            )

        return pd.DataFrame(all_rows)


if __name__ == "__main__":
    scraper = HepsiEmlakRequestsScraper()
    try:
        df = scraper.scrape()
        print(df.head())
    except Exception as exc:
        print(f"Hata: {exc}")
