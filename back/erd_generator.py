"""
ERD Generator - Infers relationships and builds visual summaries.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class ERDGenerator:
    """Generates simplified ERD-style relationship visuals."""

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.df = dataframe

    def generate(self) -> Dict[str, Any]:
        """Generate available ERD visualizations and summaries."""
        result: Dict[str, Any] = {}
        summary_notes: List[str] = []

        numeric_graph = self._numeric_relationship_graph()
        if numeric_graph:
            result["numeric_network"] = numeric_graph["figure"]
            summary_notes.extend(numeric_graph["summary"])

        categorical_heatmap = self._categorical_heatmap()
        if categorical_heatmap:
            result["categorical_heatmap"] = categorical_heatmap["figure"]
            summary_notes.extend(categorical_heatmap["summary"])

        hierarchy_chart = self._hierarchy_chart()
        if hierarchy_chart:
            result["hierarchy_chart"] = hierarchy_chart["figure"]
            summary_notes.extend(hierarchy_chart["summary"])

        result["summary"] = summary_notes
        return result

    # ------------------------------------------------------------------ #
    # Numeric Relationships
    # ------------------------------------------------------------------ #
    def _numeric_relationship_graph(self) -> Optional[Dict[str, Any]]:
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            return None

        corr_matrix = self.df[numeric_cols].corr().fillna(0)
        threshold = 0.45
        edges: List[Tuple[str, str, float]] = []
        for i, col_a in enumerate(numeric_cols):
            for col_b in numeric_cols[i + 1 :]:
                corr_val = corr_matrix.loc[col_a, col_b]
                if abs(corr_val) >= threshold:
                    edges.append((col_a, col_b, corr_val))

        if not edges:
            return None

        nodes = list({col for edge in edges for col in edge[:2]})
        num_nodes = len(nodes)
        angles = np.linspace(0, 2 * np.pi, num_nodes, endpoint=False)
        node_positions = {node: (np.cos(angle), np.sin(angle)) for node, angle in zip(nodes, angles)}

        fig = go.Figure()

        # Plot edges
        for edge in edges:
            x0, y0 = node_positions[edge[0]]
            x1, y1 = node_positions[edge[1]]
            fig.add_trace(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line=dict(width=abs(edge[2]) * 3, color="#00aaff" if edge[2] > 0 else "#ff6b6b"),
                    hoverinfo="none",
                )
            )

        # Plot nodes
        fig.add_trace(
            go.Scatter(
                x=[node_positions[node][0] for node in nodes],
                y=[node_positions[node][1] for node in nodes],
                mode="markers+text",
                marker=dict(size=18, color="#ffffff", line=dict(width=2, color="#6c63ff")),
                text=nodes,
                textposition="middle center",
                hoverinfo="text",
            )
        )

        fig.update_layout(
            title="Numeric Relationship Network",
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            font=dict(color="#ffffff"),
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            showlegend=False,
        )

        summary = [
            f"قوة ارتباط {edge[0]} و {edge[1]} = {edge[2]:.2f}"
            for edge in sorted(edges, key=lambda x: abs(x[2]), reverse=True)[:6]
        ]

        return {"figure": fig, "summary": summary}

    # ------------------------------------------------------------------ #
    # Categorical Relationships
    # ------------------------------------------------------------------ #
    def _categorical_heatmap(self) -> Optional[Dict[str, Any]]:
        categorical_cols = self.df.select_dtypes(include=["object", "category"]).columns.tolist()
        categorical_cols = [col for col in categorical_cols if self.df[col].nunique() <= 25]
        if len(categorical_cols) < 2:
            return None

        top_cols = categorical_cols[: min(8, len(categorical_cols))]
        matrix = np.zeros((len(top_cols), len(top_cols)))

        for i, col_a in enumerate(top_cols):
            for j, col_b in enumerate(top_cols):
                if i == j:
                    matrix[i, j] = 1.0
                elif i < j:
                    cramers = self._cramers_v(col_a, col_b)
                    matrix[i, j] = cramers
                    matrix[j, i] = cramers

        fig = px.imshow(
            matrix,
            x=top_cols,
            y=top_cols,
            color_continuous_scale="Purples",
            title="Categorical Relationship Heatmap (Cramér's V)",
        )
        fig.update_layout(paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font=dict(color="#ffffff"))

        summary = []
        # Collect top relationships excluding diagonal
        for i in range(len(top_cols)):
            for j in range(i + 1, len(top_cols)):
                score = matrix[i, j]
                if score >= 0.15:
                    summary.append(f"العلاقة بين {top_cols[i]} و {top_cols[j]} = {score:.2f}")

        return {"figure": fig, "summary": summary[:6]}

    def _cramers_v(self, col_a: str, col_b: str) -> float:
        contingency = pd.crosstab(self.df[col_a], self.df[col_b])
        if contingency.empty:
            return 0.0

        chi2 = self._chi_square(contingency.values)
        n = contingency.values.sum()
        r, k = contingency.shape
        if n == 0 or min(k - 1, r - 1) == 0:
            return 0.0
        return np.sqrt((chi2 / n) / min(k - 1, r - 1))

    @staticmethod
    def _chi_square(table: np.ndarray) -> float:
        row_sums = table.sum(axis=1, keepdims=True)
        col_sums = table.sum(axis=0, keepdims=True)
        total = table.sum()
        expected = row_sums @ col_sums / total
        with np.errstate(divide="ignore", invalid="ignore"):
            chi2 = np.nan_to_num(((table - expected) ** 2) / expected)
        return chi2.sum()

    # ------------------------------------------------------------------ #
    # Hierarchical view (Sunburst)
    # ------------------------------------------------------------------ #
    def _hierarchy_chart(self) -> Optional[Dict[str, Any]]:
        categorical_cols = self.df.select_dtypes(include=["object", "category"]).columns.tolist()
        if len(categorical_cols) < 2:
            return None

        col_a, col_b = categorical_cols[0], categorical_cols[1]
        limited_df = (
            self.df[[col_a, col_b]]
            .dropna()
            .copy()
        )
        limited_df[col_a] = limited_df[col_a].astype(str)
        limited_df[col_b] = limited_df[col_b].astype(str)

        fig = px.sunburst(
            limited_df,
            path=[col_a, col_b],
            title=f"Hierarchy: {col_a} → {col_b}",
            maxdepth=2,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig.update_layout(paper_bgcolor="#0e1117", font=dict(color="#ffffff"))

        summary = [f"التوزيع الهرمي بين {col_a} و {col_b} يعطي نظرة على تداخل الفئات."]

        return {"figure": fig, "summary": summary}

