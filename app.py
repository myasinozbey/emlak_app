from pathlib import Path

import pandas as pd
import streamlit as st

from analyzer import EmlakAnalyzer
from cleaner import EmlakDataCleaner
from reporter import EmlakReporter
from requests_scraper import HepsiEmlakRequestsScraper, RequestsScraperConfig
from scraper import HepsiEmlakScraper, ScraperConfig


DATA_DIR = Path("data")
RAW_PATH = DATA_DIR / "raw.csv"
CLEAN_PATH = DATA_DIR / "clean.csv"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def run_pipeline(max_pages: int, headless: bool, scraper_type: str):
    if scraper_type == "Requests + BeautifulSoup":
        scraper = HepsiEmlakRequestsScraper(RequestsScraperConfig(max_pages=max_pages))
    else:
        scraper = HepsiEmlakScraper(ScraperConfig(max_pages=max_pages, headless=headless))
    cleaner = EmlakDataCleaner()
    analyzer = EmlakAnalyzer()

    raw_df = scraper.scrape()
    clean_df = cleaner.clean(raw_df)
    vis_df = analyzer.prepare_for_visualization(clean_df)

    return raw_df, clean_df, vis_df, analyzer


def apply_custom_style() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at 10% 10%, #f4f8fb, #eef2f7 35%, #e4eef4 80%);
        }
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #022b3a 0%, #1f7a8c 100%);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 14px;
            box-shadow: 0 8px 22px rgba(2, 43, 58, 0.16);
        }
        [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
            color: #ffffff;
        }
        .block-container {
            padding-top: 2rem;
        }
        .hero {
            background: linear-gradient(120deg, #022b3a 0%, #1f7a8c 60%, #bfdbf7 100%);
            border-radius: 18px;
            padding: 1.4rem 1.2rem;
            color: white;
            margin-bottom: 1rem;
            box-shadow: 0 10px 25px rgba(2, 43, 58, 0.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
          <h2 style="margin: 0;">Mentese Satilik Konut Dashboard</h2>
          <p style="margin-top: 6px; margin-bottom: 0;">
            Veri cekme, temizlik, ilce karsilastirmasi ve fiyat icgoru paneli
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def filter_data(df_vis: pd.DataFrame) -> pd.DataFrame:
    if df_vis.empty:
        return df_vis

    with st.sidebar:
        st.subheader("Analiz Filtreleri")
        ilceler = sorted(df_vis["İlçe"].dropna().unique().tolist())
        selected_ilceler = st.multiselect(
            "Ilceler",
            options=ilceler,
            default=ilceler,
        )

        min_m2, max_m2 = int(df_vis["m2"].min()), int(df_vis["m2"].max())
        m2_range = st.slider("m2 Araligi", min_m2, max_m2, (min_m2, max_m2))

        min_price, max_price = int(df_vis["Fiyat"].min()), int(df_vis["Fiyat"].max())
        price_range = st.slider("Fiyat Araligi (TL)", min_price, max_price, (min_price, max_price))

        min_age, max_age = int(df_vis["Bina Yaşı"].min()), int(df_vis["Bina Yaşı"].max())
        age_range = st.slider("Bina Yasi", min_age, max_age, (min_age, max_age))

    mask = (
        df_vis["İlçe"].isin(selected_ilceler)
        & df_vis["m2"].between(m2_range[0], m2_range[1])
        & df_vis["Fiyat"].between(price_range[0], price_range[1])
        & df_vis["Bina Yaşı"].between(age_range[0], age_range[1])
    )
    return df_vis[mask].copy()


def main():
    st.set_page_config(page_title="Mentese Emlak Studio", layout="wide")
    apply_custom_style()
    render_header()

    ensure_data_dir()

    with st.sidebar:
        st.header("Veri Isleme")
        max_pages = st.slider("Kaç sayfa gezilsin?", min_value=1, max_value=30, value=11)
        scraper_type = st.selectbox(
            "Scraper Tipi",
            options=["Selenium (Dinamik Sayfa)", "Requests + BeautifulSoup"],
            index=1,
        )
        headless = st.checkbox("Headless mod", value=False)
        run_button = st.button("Veriyi Çek ve Analiz Et")
        load_saved_button = st.button("Kayitli veriyi yukle")

    if "clean_df" not in st.session_state and CLEAN_PATH.exists():
        st.session_state["clean_df"] = pd.read_csv(CLEAN_PATH)

    if load_saved_button:
        if CLEAN_PATH.exists():
            st.session_state["clean_df"] = pd.read_csv(CLEAN_PATH)
            st.success("Kayitli temiz veri yuklendi.")
        else:
            st.warning("Kayitli temiz veri bulunamadi.")

    if run_button:
        with st.spinner("Veri çekiliyor ve analiz hazırlanıyor..."):
            try:
                raw_df, clean_df, vis_df, analyzer = run_pipeline(max_pages, headless, scraper_type)
                raw_df.to_csv(RAW_PATH, index=False)
                clean_df.to_csv(CLEAN_PATH, index=False)
                st.session_state["clean_df"] = clean_df
                st.success("İşlem tamamlandı.")
            except ValueError as exc:
                st.error(f"Veri hatasi: {exc}")
                return
            except (TypeError, KeyError) as exc:
                st.error(f"Donusum hatasi: {exc}")
                return
            except Exception as exc:
                st.error(f"Beklenmeyen hata: {exc}")
                return

    if "clean_df" not in st.session_state:
        st.info("Analiz icin soldan veri cekebilir veya kayitli veriyi yukleyebilirsin.")
        return

    analyzer = EmlakAnalyzer()
    base_vis_df = analyzer.prepare_for_visualization(st.session_state["clean_df"])
    filtered_df = filter_data(base_vis_df)

    metrics = analyzer.summary_metrics(filtered_df)
    district_df = analyzer.district_summary(filtered_df)
    charts = analyzer.build_dashboard(filtered_df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ilan Sayisi", f"{metrics['ilan_sayisi']}")
    c2.metric("Ort. Fiyat", f"{metrics['ortalama_fiyat']:,.0f} TL")
    c3.metric("Medyan Fiyat", f"{metrics['medyan_fiyat']:,.0f} TL")
    c4.metric("Ort. m2 Fiyat", f"{metrics['ortalama_m2_fiyat']:,.0f} TL")

    c5, c6, c7 = st.columns(3)
    c5.metric("Ort. m2", f"{metrics['ortalama_m2']:,.1f}")
    c6.metric("m2 Fiyat Q1", f"{metrics['fiyat_m2_25']:,.0f} TL")
    c7.metric("m2 Fiyat Q3", f"{metrics['fiyat_m2_75']:,.0f} TL")

    tab1, tab2, tab3 = st.tabs(["Genel Gorunum", "Ilce Analizi", "Veri"])

    with tab1:
        col_a, col_b = st.columns(2)
        col_a.plotly_chart(charts["scatter"], use_container_width=True)
        col_b.plotly_chart(charts["distribution"], use_container_width=True)

        col_c, col_d = st.columns(2)
        col_c.plotly_chart(charts["segment"], use_container_width=True)
        col_d.plotly_chart(charts["corr"], use_container_width=True)

    with tab2:
        col_e, col_f = st.columns(2)
        col_e.plotly_chart(charts["district_bar"], use_container_width=True)
        col_f.plotly_chart(charts["district_box"], use_container_width=True)
        st.subheader("Ilce Performans Tablosu")
        st.dataframe(
            district_df.style.format(
                {
                    "ortalama_fiyat": "{:,.0f}",
                    "medyan_fiyat": "{:,.0f}",
                    "ortalama_m2": "{:,.1f}",
                    "ortalama_m2_fiyat": "{:,.0f}",
                }
            ),
            use_container_width=True,
        )

    with tab3:
        st.subheader("Filtrelenmis Veri")
        st.dataframe(filtered_df, use_container_width=True)
        reporter = EmlakReporter()
        excel_bytes = reporter.build_excel_bytes(filtered_df, district_df)
        st.download_button(
            "Excel Rapor indir",
            data=excel_bytes,
            file_name="emlak_rapor.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        st.download_button(
            "Filtreli CSV indir",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="filtered_emlak.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
