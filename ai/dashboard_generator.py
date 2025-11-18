"""
Auto Dashboard Generator - Creates Power BI-like dashboards automatically
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back.data_handler import DataHandler
from back.analysis_engine import AnalysisEngine
from ai.llm_client import BasetenLLMClient
from back.logger import logger
from config import Config


# Color themes
COLOR_THEMES = {
    'default': {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ff7f0e',
        'info': '#17a2b8',
        'background': '#0e1117',
        'text': '#ffffff'
    },
    'blue': {
        'primary': '#0066cc',
        'secondary': '#3399ff',
        'success': '#00cc66',
        'danger': '#ff3333',
        'warning': '#ff9900',
        'info': '#00ccff',
        'background': '#0a1929',
        'text': '#e3f2fd'
    },
    'dark': {
        'primary': '#6366f1',
        'secondary': '#8b5cf6',
        'success': '#10b981',
        'danger': '#ef4444',
        'warning': '#f59e0b',
        'info': '#3b82f6',
        'background': '#111827',
        'text': '#f9fafb'
    },
    'corporate': {
        'primary': '#1e3a8a',
        'secondary': '#3b82f6',
        'success': '#059669',
        'danger': '#dc2626',
        'warning': '#d97706',
        'info': '#0284c7',
        'background': '#0f172a',
        'text': '#f1f5f9'
    }
}


class AutoDashboardGenerator:
    """Automatically generates Power BI-like dashboards from data"""
    
    def __init__(self, data_handler: DataHandler, analysis_engine: AnalysisEngine, llm_client: BasetenLLMClient, color_theme: str = 'default'):
        """
        Initialize the dashboard generator
        
        Args:
            data_handler: DataHandler instance
            analysis_engine: AnalysisEngine instance
            llm_client: LLM client for generating visualizations
            color_theme: Color theme name ('default', 'blue', 'dark', 'corporate')
        """
        self.data_handler = data_handler
        self.analysis_engine = analysis_engine
        self.llm_client = llm_client
        self.df = data_handler.get_dataframe()
        self.color_theme = COLOR_THEMES.get(color_theme, COLOR_THEMES['default'])
        self.colors = [
            self.color_theme['primary'],
            self.color_theme['secondary'],
            self.color_theme['success'],
            self.color_theme['danger'],
            self.color_theme['warning'],
            self.color_theme['info']
        ]
    
    def analyze_data_structure(self) -> Dict[str, Any]:
        """
        Analyze the data structure to determine appropriate visualizations
        
        Returns:
            dict: Analysis of data structure
        """
        info = self.data_handler.get_info()
        columns = info.get('columns', [])
        dtypes = info.get('dtypes', {})
        
        numeric_cols = []
        categorical_cols = []
        date_cols = []
        
        for col in columns:
            dtype = str(dtypes.get(col, '')).lower()
            if 'int' in dtype or 'float' in dtype:
                numeric_cols.append(col)
            elif 'date' in dtype or 'time' in dtype:
                date_cols.append(col)
            else:
                categorical_cols.append(col)
        
        return {
            'numeric_cols': numeric_cols,
            'categorical_cols': categorical_cols,
            'date_cols': date_cols,
            'total_cols': len(columns),
            'total_rows': len(self.df)
        }
    
    def generate_visualization_code(self, viz_type: str, columns: List[str], description: str, chart_subtype: str = None) -> str:
        """
        Generate Python code for a specific visualization
        
        Args:
            viz_type: Type of visualization (bar, line, scatter, pie, gauge, area, etc.)
            columns: Columns to use
            description: Description of what to visualize
            chart_subtype: Subtype like 'stacked', 'grouped', 'horizontal', etc.
            
        Returns:
            str: Python code for the visualization
        """
        colors_str = ', '.join([f"'{c}'" for c in self.colors])
        
        # Special instructions for different chart types
        special_instructions = ""
        if viz_type == 'gauge':
            special_instructions = """
- Create a gauge chart using go.Indicator with mode='gauge+number'
- Set value between 0-100
- Use domain={'x': [0, 1], 'y': [0, 1]}
- Add threshold lines and colors
"""
        elif viz_type == 'area':
            special_instructions = """
- Create an area chart using go.Scatter with fill='tonexty' or fill='tozeroy'
- Use stacked area if multiple series
"""
        elif chart_subtype == 'stacked':
            special_instructions = """
- Create a stacked bar/area chart
- Use barmode='stack' for bars
"""
        
        context = f"""
Generate Python code to create a {viz_type} chart using plotly.

DataFrame variable: df
Columns to use: {', '.join(columns)}
Description: {description}
Chart subtype: {chart_subtype or 'standard'}
Color palette: [{colors_str}]

Requirements:
1. Use plotly express (px) or graph_objects (go)
2. Assign the figure to variable 'fig'
3. Make it interactive and visually appealing
4. Add proper titles and labels
5. Use the provided color palette: {colors_str}
6. Set dark theme: plot_bgcolor='{self.color_theme['background']}', paper_bgcolor='{self.color_theme['background']}', font_color='{self.color_theme['text']}'
7. Make charts professional like Power BI dashboard
{special_instructions}
8. Only output Python code, no markdown or explanations

Generate the code:
"""
        
        messages = [
            {"role": "system", "content": "You are a data visualization expert. Generate clean, efficient plotly code."},
            {"role": "user", "content": context}
        ]
        
        code = self.llm_client.get_full_response(
            messages=messages,
            max_tokens=1500,
            temperature=0.3
        )
        
        # Clean up code
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        return code
    
    def generate_dashboard(self) -> Dict[str, Any]:
        """
        Generate a complete dashboard automatically
        
        Returns:
            dict: Dashboard with visualizations and insights
        """
        logger.info("Generating auto dashboard...")
        
        structure = self.analyze_data_structure()
        visualizations = []
        insights = []
        
        # Generate key metrics/KPIs
        if structure['numeric_cols']:
            metrics = self._generate_metrics(structure['numeric_cols'])
            visualizations.append({
                'type': 'metrics',
                'data': metrics,
                'title': 'Key Metrics'
            })
        
        # Generate visualizations based on data structure
        viz_plan = self._plan_visualizations(structure)
        
        for viz_info in viz_plan:
            try:
                code = self.generate_visualization_code(
                    viz_info['type'],
                    viz_info['columns'],
                    viz_info['description'],
                    chart_subtype=viz_info.get('subtype')
                )
                
                # Execute the code
                result, output, error = self.analysis_engine.execute_code(code)
                
                if not error and result is not None:
                    formatted = self.analysis_engine.format_result(result)
                    if formatted['type'] == 'plotly_figure':
                        # Update figure layout for dark theme
                        fig = formatted['data']
                        try:
                            fig.update_layout(
                                plot_bgcolor=self.color_theme['background'],
                                paper_bgcolor=self.color_theme['background'],
                                font_color=self.color_theme['text'],
                                title_font_color=self.color_theme['text'],
                                legend=dict(
                                    bgcolor=self.color_theme['background'],
                                    bordercolor=self.color_theme['text'],
                                    borderwidth=1
                                ) if hasattr(fig, 'update_layout') else None
                            )
                        except:
                            pass  # If update fails, continue with original figure
                        
                        visualizations.append({
                            'type': 'plotly_figure',
                            'data': fig,
                            'code': code,
                            'title': viz_info['title'],
                            'description': viz_info['description'],
                            'chart_type': viz_info.get('type'),
                            'subtype': viz_info.get('subtype')
                        })
                        logger.info(f"Generated visualization: {viz_info['title']}")
            except Exception as e:
                logger.error(f"Error generating visualization {viz_info['title']}: {e}")
                continue
        
        # Generate insights
        insights = self._generate_insights(structure, visualizations)
        
        return {
            'visualizations': visualizations,
            'insights': insights,
            'structure': structure
        }
    
    def _generate_metrics(self, numeric_cols: List[str]) -> List[Dict[str, Any]]:
        """Generate key metrics from numeric columns (like Power BI KPIs)"""
        metrics = []
        
        for col in numeric_cols[:4]:  # Limit to 4 KPIs like Power BI
            try:
                col_data = self.df[col]
                sum_val = float(col_data.sum()) if col_data.dtype in ['int64', 'float64'] else None
                mean_val = float(col_data.mean()) if col_data.dtype in ['int64', 'float64'] else None
                max_val = float(col_data.max()) if col_data.dtype in ['int64', 'float64'] else None
                min_val = float(col_data.min()) if col_data.dtype in ['int64', 'float64'] else None
                
                # Format values for display
                if sum_val:
                    if sum_val >= 1000000:
                        display_value = f"{sum_val/1000000:.1f}M"
                    elif sum_val >= 1000:
                        display_value = f"{sum_val/1000:.1f}K"
                    else:
                        display_value = f"{sum_val:.0f}"
                else:
                    display_value = f"{mean_val:.2f}" if mean_val else "N/A"
                
                metrics.append({
                    'name': col,
                    'label': f"Sum of {col}",
                    'value': sum_val,
                    'display_value': display_value,
                    'mean': mean_val,
                    'max': max_val,
                    'min': min_val,
                    'count': len(col_data)
                })
            except Exception as e:
                logger.warning(f"Error generating metric for {col}: {e}")
                continue
        
        return metrics
    
    def _plan_visualizations(self, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan which visualizations to create - All in one page dashboard"""
        plan = []
        
        numeric_cols = structure['numeric_cols']
        categorical_cols = structure['categorical_cols']
        date_cols = structure['date_cols']
        
        # 1. Gauge Chart - Service Level / Performance Indicator (Top Left)
        if numeric_cols:
            num_col = numeric_cols[0]
            # Calculate percentage for gauge
            plan.append({
                'type': 'gauge',
                'columns': [num_col],
                'title': f'Performance Indicator',
                'description': f'Overall performance based on {num_col}',
                'subtype': None
            })
        
        # 2. Semi-circular Gauge - Handle Rate / Completion Rate (Middle Left)
        if numeric_cols and len(numeric_cols) > 1:
            num_col = numeric_cols[1]
            plan.append({
                'type': 'gauge',
                'columns': [num_col],
                'title': f'Completion Rate',
                'description': f'Completion rate based on {num_col}',
                'subtype': 'semicircular'
            })
        
        # 3. Stacked Bar Chart - Volume by Category/Date (Top Middle)
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            plan.append({
                'type': 'bar',
                'columns': [cat_col, num_col],
                'title': f'Volume by {cat_col}',
                'description': f'Stacked volume breakdown by {cat_col}',
                'subtype': 'stacked'
            })
        
        # 4. Top Skills/Categories with Progress Bars (Middle Middle)
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0] if categorical_cols else None
            num_col = numeric_cols[0]
            plan.append({
                'type': 'horizontal_bar',
                'columns': [cat_col, num_col],
                'title': f'Top Categories by {num_col}',
                'description': f'Top performing categories',
                'subtype': 'top_n'
            })
        
        # 5. Horizontal Stacked Bar - Volume by Modality/Type (Top Right)
        if categorical_cols and numeric_cols:
            type_cols = [c for c in categorical_cols if any(word in c.lower() for word in ['type', 'modality', 'category', 'method', 'mode'])]
            if not type_cols:
                type_cols = categorical_cols[:1]
            
            if type_cols and numeric_cols:
                type_col = type_cols[0]
                num_col = numeric_cols[0]
                plan.append({
                    'type': 'bar',
                    'columns': [type_col, num_col],
                    'title': f'Volume by {type_col}',
                    'description': f'Volume breakdown by {type_col}',
                    'subtype': 'stacked_horizontal'
                })
        
        # 6. Area Chart - Trend over Time (Bottom Right)
        if date_cols and numeric_cols:
            date_col = date_cols[0]
            num_col = numeric_cols[0]
            plan.append({
                'type': 'area',
                'columns': [date_col, num_col],
                'title': f'{num_col} Trend Over Time',
                'description': f'Trend analysis of {num_col}',
                'subtype': 'stacked'
            })
        elif categorical_cols and numeric_cols:
            # Use categorical as x-axis if no date
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            plan.append({
                'type': 'area',
                'columns': [cat_col, num_col],
                'title': f'{num_col} Distribution',
                'description': f'Distribution of {num_col}',
                'subtype': None
            })
        
        # 7. Donut/Pie Chart - Distribution (if we have space)
        if categorical_cols and numeric_cols and len(plan) < 7:
            cat_col = categorical_cols[0] if len(categorical_cols) > 0 else None
            num_col = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
            if cat_col:
                plan.append({
                    'type': 'pie',
                    'columns': [cat_col, num_col],
                    'title': f'Distribution by {cat_col}',
                    'description': f'Percentage distribution',
                    'subtype': 'donut'
                })
        
        return plan[:8]  # Allow up to 8 visualizations for comprehensive dashboard
    
    def _generate_insights(self, structure: Dict[str, Any], visualizations: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from the data"""
        insights = []
        
        # Basic insights
        insights.append(f"Dataset contains {structure['total_rows']} rows and {structure['total_cols']} columns")
        
        if structure['numeric_cols']:
            insights.append(f"Found {len(structure['numeric_cols'])} numeric columns for quantitative analysis")
        
        if structure['categorical_cols']:
            insights.append(f"Found {len(structure['categorical_cols'])} categorical columns for grouping and segmentation")
        
        if structure['date_cols']:
            insights.append(f"Found {len(structure['date_cols'])} date columns for time series analysis")
        
        insights.append(f"Generated {len([v for v in visualizations if v['type'] == 'plotly_figure'])} interactive visualizations")
        
        return insights

