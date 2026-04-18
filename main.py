from pathlib import Path

import pandas as pd

from cleaner import EmlakDataCleaner
from reporter import EmlakReporter
from requests_scraper import HepsiEmlakRequestsScraper, RequestsScraperConfig
from scraper import HepsiEmlakScraper, ScraperConfig


def ask_int(prompt: str, default: int) -> int:
    raw = input(prompt).strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError("Sayi girilmelidir.") from exc


def run_cli() -> None:
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    reporter = EmlakReporter()

    try:
        print("Scraper secin: 1) Selenium  2) Requests+BS4")
        choice = input("Secim (1/2): ").strip() or "1"
        pages = ask_int("Kac sayfa gezilsin? (varsayilan 5): ", 5)

        if choice == "2":
            scraper = HepsiEmlakRequestsScraper(RequestsScraperConfig(max_pages=pages))
        else:
            scraper = HepsiEmlakScraper(ScraperConfig(max_pages=pages, headless=False))

        raw_df = scraper.scrape()
        clean_df = EmlakDataCleaner().clean(raw_df)

        csv_path = data_dir / "cli_clean.csv"
        reporter.save_csv(clean_df, csv_path)

        district_df = (
            clean_df.assign(m2_fiyat=clean_df["Fiyat"] / clean_df["m2"])
            .groupby("İlçe", as_index=False)
            .agg(ortalama_m2_fiyat=("m2_fiyat", "mean"), ilan_sayisi=("m2_fiyat", "count"))
        )
        excel_bytes = reporter.build_excel_bytes(clean_df, district_df)
        excel_path = data_dir / "cli_report.xlsx"
        excel_path.write_bytes(excel_bytes)

        print(f"CSV kaydedildi: {csv_path}")
        print(f"Excel kaydedildi: {excel_path}")

    except FileNotFoundError as exc:
        print(f"Dosya bulunamadi: {exc}")
    except PermissionError as exc:
        print(f"Dosya yazma izni yok: {exc}")
    except ValueError as exc:
        print(f"Girdi/veri hatasi: {exc}")
    except TypeError as exc:
        print(f"Tip hatasi: {exc}")
    finally:
        print("Program sonlandi.")


if __name__ == "__main__":
    run_cli()
