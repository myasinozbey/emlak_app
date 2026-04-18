import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class EmlakAnalyzer:
    def __init__(self):
        self.color_seq = [
            "#1f7a8c",
            "#bfdbf7",
            "#e1e5f2",
            "#022b3a",
            "#ff7d00",
            "#7c3aed",
        ]

    def prepare_for_visualization(
        self, df_clean: pd.DataFrame, m2_upper_limit: int = 1000, price_quantile: float = 0.99
    ) -> pd.DataFrame:
        if df_clean.empty:
            return df_clean

        df_vis = df_clean.copy()
        df_vis = df_vis[df_vis["m2"] < m2_upper_limit]
        df_vis = df_vis[df_vis["Fiyat"] < df_vis["Fiyat"].quantile(price_quantile)]
        df_vis = df_vis[df_vis["m2"] > 0]
        df_vis["m2_fiyat"] = df_vis["Fiyat"] / df_vis["m2"]
        df_vis["Fiyat (Milyon TL)"] = df_vis["Fiyat"] / 1_000_000
        df_vis["m2_segment"] = pd.cut(
            df_vis["m2"],
            bins=[0, 90, 130, 180, 250, 1000],
            labels=["0-90", "91-130", "131-180", "181-250", "250+"],
            include_lowest=True,
        )
        return df_vis

    def summary_metrics(self, df_vis: pd.DataFrame) -> dict:
        if df_vis.empty:
            return {
                "ilan_sayisi": 0,
                "ortalama_fiyat": 0,
                "ortalama_m2": 0,
                "ortalama_m2_fiyat": 0,
                "medyan_fiyat": 0,
                "fiyat_m2_75": 0,
                "fiyat_m2_25": 0,
            }

        return {
            "ilan_sayisi": int(len(df_vis)),
            "ortalama_fiyat": float(df_vis["Fiyat"].mean()),
            "ortalama_m2": float(df_vis["m2"].mean()),
            "ortalama_m2_fiyat": float(df_vis["m2_fiyat"].mean()),
            "medyan_fiyat": float(df_vis["Fiyat"].median()),
            "fiyat_m2_75": float(df_vis["m2_fiyat"].quantile(0.75)),
            "fiyat_m2_25": float(df_vis["m2_fiyat"].quantile(0.25)),
        }

    def district_summary(self, df_vis: pd.DataFrame) -> pd.DataFrame:
        if df_vis.empty:
            return pd.DataFrame()

        out = (
            df_vis.groupby("İlçe")
            .agg(
                ilan_sayisi=("Fiyat", "count"),
                ortalama_fiyat=("Fiyat", "mean"),
                medyan_fiyat=("Fiyat", "median"),
                ortalama_m2=("m2", "mean"),
                ortalama_m2_fiyat=("m2_fiyat", "mean"),
            )
            .sort_values("ortalama_m2_fiyat", ascending=False)
            .reset_index()
        )
        return out

    def _empty_figure(self, title: str) -> go.Figure:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            template="plotly_white",
            annotations=[
                dict(
                    text="Gosterilecek veri yok",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    font=dict(size=16, color="#4b5563"),
                )
            ],
        )
        return fig

    def build_dashboard(self, df_vis: pd.DataFrame) -> dict[str, go.Figure]:
        if df_vis.empty:
            return {
                "scatter": self._empty_figure("m2 ve Fiyat Iliskisi"),
                "distribution": self._empty_figure("m2 Birim Fiyat Dagilimi"),
                "district_bar": self._empty_figure("Ilce Bazli Ortalama m2 Fiyat"),
                "district_box": self._empty_figure("Ilce Bazli m2 Fiyat Dagilimi"),
                "segment": self._empty_figure("m2 Segmentlerine Gore Fiyat"),
                "corr": self._empty_figure("Korelasyon"),
            }

        district_table = self.district_summary(df_vis).head(10)
        box_districts = district_table["İlçe"].tolist()
        box_df = df_vis[df_vis["İlçe"].isin(box_districts)].copy()

        scatter = px.scatter(
            df_vis,
            x="m2",
            y="Fiyat",
            color="İlçe",
            hover_data=["Mahalle", "Bina Yaşı", "m2_fiyat"],
            title="m2 ve Fiyat Iliskisi",
            opacity=0.72,
            color_discrete_sequence=self.color_seq,
        )
        scatter.update_layout(template="plotly_white", legend_title_text="Ilce")
        scatter.update_traces(marker=dict(size=10, line=dict(width=0.5, color="white")))

        distribution = px.histogram(
            df_vis,
            x="m2_fiyat",
            nbins=35,
            marginal="box",
            title="m2 Birim Fiyat Dagilimi",
            color_discrete_sequence=["#1f7a8c"],
        )
        distribution.update_layout(template="plotly_white", bargap=0.04)

        district_bar = px.bar(
            district_table,
            x="ortalama_m2_fiyat",
            y="İlçe",
            orientation="h",
            title="Ilce Bazli Ortalama m2 Fiyat (Top 10)",
            color="ortalama_m2_fiyat",
            color_continuous_scale="Tealgrn",
        )
        district_bar.update_layout(
            template="plotly_white",
            yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False,
        )

        district_box = px.box(
            box_df,
            x="İlçe",
            y="m2_fiyat",
            title="Ilce Bazli m2 Fiyat Dagilimi (Top 10)",
            color="İlçe",
            color_discrete_sequence=self.color_seq,
        )
        district_box.update_layout(template="plotly_white", showlegend=False)
        district_box.update_xaxes(tickangle=-30)

        segment = px.box(
            df_vis,
            x="m2_segment",
            y="Fiyat",
            title="m2 Segmentlerine Gore Fiyat Dagilimi",
            color="m2_segment",
            color_discrete_sequence=self.color_seq,
        )
        segment.update_layout(template="plotly_white", showlegend=False)
        segment.update_xaxes(title="m2 Segment")

        corr_df = df_vis[["m2", "Fiyat", "Bina Yaşı", "m2_fiyat"]].corr()
        corr = px.imshow(
            corr_df,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            title="Korelasyon Matrisi",
            aspect="auto",
        )
        corr.update_layout(template="plotly_white")

        return {
            "scatter": scatter,
            "distribution": distribution,
            "district_bar": district_bar,
            "district_box": district_box,
            "segment": segment,
            "corr": corr,
        }
