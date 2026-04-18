import re

import pandas as pd


class EmlakDataCleaner:
    @staticmethod
    def _parse_m2(value: str) -> float | None:
        if not isinstance(value, str) or not value.strip():
            return None
        value = re.sub(r"[^\d]", "", value)
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _parse_price(value: str) -> float | None:
        if not isinstance(value, str) or not value.strip():
            return None
        value = re.sub(r"[^\d]", "", value)
        try:
            return float(value)
        except ValueError:
            return None

    @staticmethod
    def _parse_building_age(value: str) -> float | None:
        if not isinstance(value, str) or not value.strip():
            return None
        if "Sıfır" in value:
            return 0
        try:
            match = re.search(r"\d+", value)
            if not match:
                return None
            return float(match.group(0))
        except (ValueError, IndexError):
            return None

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        out = df.copy()
        out["m2"] = out["m2"].apply(self._parse_m2)
        out["Fiyat"] = out["Fiyat"].apply(self._parse_price)
        out["Bina Yaşı"] = out["Bina Yaşı"].apply(self._parse_building_age)

        split_cols = out["Lokasyon"].fillna("").str.split("/", expand=True)
        out["İl"] = split_cols[0].str.strip() if 0 in split_cols else ""
        out["İlçe"] = split_cols[1].str.strip() if 1 in split_cols else ""
        mahalle = split_cols[2].fillna("") if 2 in split_cols else ""
        out["Mahalle"] = (
            mahalle.astype(str).str.replace("Mah.", "", regex=False).str.strip()
            if hasattr(mahalle, "astype")
            else ""
        )

        out = out.drop(columns=["Lokasyon"], errors="ignore")
        out = out.dropna(subset=["m2", "Fiyat", "Bina Yaşı"])

        out["m2"] = out["m2"].astype(int)
        out["Fiyat"] = out["Fiyat"].astype(int)
        out["Bina Yaşı"] = out["Bina Yaşı"].astype(int)

        return out
