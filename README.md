# Mentese Emlak Analiz Projesi

## Proje Yapisi

- `app.py`: Modern Streamlit arayuzu
- `main.py`: CLI calistirma ornegi (`__name__ == "__main__"`)
- `scraper.py`: Selenium scraper (dinamik sayfa)
- `requests_scraper.py`: Requests + BeautifulSoup scraper
- `cleaner.py`: Regex ile veri temizleme
- `analyzer.py`: Metrikler ve Plotly analizleri
- `reporter.py`: CSV/Excel rapor uretimi
- `data/`: Uretilen veri dosyalari

## 2. Hafta Konulari

- Coklu `.py` dosya ve moduler yapi
- `import` yapisi
- `__name__ == "__main__"` kullanimi (`main.py`, `requests_scraper.py`, `reporter.py`)
- `try / except / finally` (ozellikle `main.py` ve `app.py`)
- Hata turleri: `ValueError`, `TypeError`, `FileNotFoundError`, `PermissionError`
- Dosya ve kullanici giris hatasi yonetimi

## 3. Hafta Konulari

- `requests` kutuphanesi (`requests_scraper.py`)
- HTML yapisi ve parse islemi
- `BeautifulSoup` kullanimi
- `find` / `find_all` metotlari

## 4. Hafta Konulari

- String + temel `regex` ile veri temizleme (`cleaner.py`)
- CSV kaydetme (`reporter.py`)
- Pandas ile dosya olusturma
- Excel otomasyonu ve rapor uretimi (`reporter.py`)

## Local Run

```bash
cd /Users/batuhandemirci/Documents/Playground/emlak_app
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## CLI Run

```bash
cd /Users/batuhandemirci/Documents/Playground/emlak_app
source .venv/bin/activate
python main.py
```

## Streamlit Community Cloud Deploy

1. Klasoru GitHub'a push et.
2. [https://share.streamlit.io](https://share.streamlit.io) adresine git.
3. `New app` sec.
4. Repo sec.
5. Main file path: `app.py`
6. `Deploy` butonuna bas.
