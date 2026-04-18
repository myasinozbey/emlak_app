from io import BytesIO
from pathlib import Path

import pandas as pd


class EmlakReporter:
    def save_csv(self, df: pd.DataFrame, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)

    def build_excel_bytes(self, clean_df: pd.DataFrame, district_df: pd.DataFrame) -> bytes:
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            clean_df.to_excel(writer, sheet_name="Temiz Veri", index=False)
            district_df.to_excel(writer, sheet_name="Ilce Ozet", index=False)

            wb = writer.book
            for ws in wb.worksheets:
                for col in ws.columns:
                    max_len = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                    ws.column_dimensions[col[0].column_letter].width = min(max(max_len + 2, 10), 32)

        output.seek(0)
        return output.read()


if __name__ == "__main__":
    sample = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    reporter = EmlakReporter()
    data = reporter.build_excel_bytes(sample, sample)
    print(f"Uretilen byte: {len(data)}")
