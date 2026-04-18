import time
from dataclasses import dataclass
from typing import List

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


@dataclass
class ScraperConfig:
    base_url: str = "https://www.hepsiemlak.com/mentese-satilik"
    max_pages: int = 11
    headless: bool = False
    wait_seconds: int = 4


class HepsiEmlakScraper:
    def __init__(self, config: ScraperConfig | None = None):
        self.config = config or ScraperConfig()

    def _build_driver(self) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        if self.config.headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
        return webdriver.Chrome(options=options)

    def _close_popups(self, driver: webdriver.Chrome) -> None:
        try:
            shadow_host = driver.find_element(By.CSS_SELECTOR, "efilli-layout-dynamic")
            shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)
            shadow_root.find_element(By.CSS_SELECTOR, "div[data-name='Kabul Et']").click()
            time.sleep(1)
        except Exception:
            pass

        try:
            driver.find_element(By.XPATH, "//*[@id='dengage_push-accept-button']").click()
            time.sleep(0.5)
        except Exception:
            pass

    @staticmethod
    def _safe_text(elements: List, i: int) -> str:
        return elements[i].text if i < len(elements) else ""

    def scrape(self) -> pd.DataFrame:
        driver = self._build_driver()
        tum_lokasyon, tum_m2, tum_bina_yasi, tum_fiyat = [], [], [], []

        try:
            for page in range(1, self.config.max_pages + 1):
                url = f"{self.config.base_url}?page={page}"
                driver.get(url)
                time.sleep(self.config.wait_seconds)

                if page == 1:
                    self._close_popups(driver)

                lokasyonlar = driver.find_elements(By.XPATH, "//span[@class='list-view-location']")
                m2_list = driver.find_elements(By.XPATH, "//dd[contains(@class,'squareMeter')]")
                bina_yaslari = driver.find_elements(By.XPATH, "//dd[contains(@class,'buildingAge')]")
                fiyatlar = driver.find_elements(By.XPATH, "//p[contains(@class,'list-view-price')]/strong")

                row_count = max(len(lokasyonlar), len(m2_list), len(bina_yaslari), len(fiyatlar))
                for i in range(row_count):
                    tum_lokasyon.append(self._safe_text(lokasyonlar, i))
                    tum_m2.append(self._safe_text(m2_list, i))
                    tum_bina_yasi.append(self._safe_text(bina_yaslari, i))
                    tum_fiyat.append(self._safe_text(fiyatlar, i))

        finally:
            driver.quit()

        return pd.DataFrame(
            {
                "Lokasyon": tum_lokasyon,
                "m2": tum_m2,
                "Bina Yaşı": tum_bina_yasi,
                "Fiyat": tum_fiyat,
            }
        )
