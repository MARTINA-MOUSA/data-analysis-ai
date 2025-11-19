"""
Outlier detection utilities.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px


class OutlierDetector:
    """Detects outliers using IQR method and provides summaries."""

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.df = dataframe

    def detect(self) -> Dict[str, Any]:
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        summary_rows: List[Dict[str, Any]] = []
        combined_mask = pd.Series(False, index=self.df.index)

        for col in numeric_cols:
            series = self.df[col].dropna()
            if series.empty:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            mask = (self.df[col] < lower) | (self.df[col] > upper)
            count = mask.sum()
            if count == 0:
                continue

            combined_mask = combined_mask | mask
            summary_rows.append(
                {
                    "column": col,
                    "iqr": iqr,
                    "lower_bound": lower,
                    "upper_bound": upper,
                    "outlier_count": int(count),
                    "percentage": float(count / len(self.df) * 100),
                }
            )

        summary_df = pd.DataFrame(summary_rows)
        summary_fig = None
        if not summary_df.empty:
            summary_df = summary_df.sort_values(by="outlier_count", ascending=False)
            summary_fig = px.bar(
                summary_df,
                x="column",
                y="outlier_count",
                title="Outlier Counts per Column",
                color="percentage",
                color_continuous_scale="Reds",
            )
            summary_fig.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font=dict(color="#ffffff"))

        outlier_rows = self.df[combined_mask].head(200)
        total_outliers = int(combined_mask.sum())

        text_summary = self._generate_summary_text(summary_df, total_outliers)

        return {
            "summary_df": summary_df,
            "figure": summary_fig,
            "samples": outlier_rows,
            "total_outliers": total_outliers,
            "raw_summary": summary_rows,
            "text_summary": text_summary,
        }

    @staticmethod
    def _generate_summary_text(summary_df: pd.DataFrame, total_outliers: int) -> List[str]:
        if summary_df.empty:
            return ["✅ لم يتم العثور على outliers واضحة في الأعمدة الرقمية."]

        notes = [f"إجمالي القيم الشاذة: {total_outliers}"]
        for _, row in summary_df.head(5).iterrows():
            notes.append(
                f"- العمود {row['column']} يحتوي على {row['outlier_count']} outliers "
                f"(~{row['percentage']:.1f}%) ضمن النطاق [{row['lower_bound']:.2f}, {row['upper_bound']:.2f}]"
            )
        return notes

