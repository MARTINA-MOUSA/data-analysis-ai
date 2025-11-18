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


class AutoDashboardGenerator:
    """Automatically generates Power BI-like dashboards from data"""
    
    def __init__(self, data_handler: DataHandler, analysis_engine: AnalysisEngine, llm_client: BasetenLLMClient):
        """
        Initialize the dashboard generator
        
        Args:
            data_handler: DataHandler instance
            analysis_engine: AnalysisEngine instance
            llm_client: LLM client for generating visualizations
        """
        self.data_handler = data_handler
        self.analysis_engine = analysis_engine
        self.llm_client = llm_client
        self.df = data_handler.get_dataframe()
    
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
    
    def generate_visualization_code(self, viz_type: str, columns: List[str], description: str) -> str:
        """
        Generate Python code for a specific visualization
        
        Args:
            viz_type: Type of visualization (bar, line, scatter, pie, etc.)
            columns: Columns to use
            description: Description of what to visualize
            
        Returns:
            str: Python code for the visualization
        """
        context = f"""
Generate Python code to create a {viz_type} chart using plotly.

DataFrame variable: df
Columns to use: {', '.join(columns)}
Description: {description}

Requirements:
1. Use plotly express (px) or graph_objects (go)
2. Assign the figure to variable 'fig'
3. Make it interactive and visually appealing
4. Add proper titles and labels
5. Use appropriate colors
6. Only output Python code, no markdown or explanations

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
                    viz_info['description']
                )
                
                # Execute the code
                result, output, error = self.analysis_engine.execute_code(code)
                
                if not error and result is not None:
                    formatted = self.analysis_engine.format_result(result)
                    if formatted['type'] == 'plotly_figure':
                        visualizations.append({
                            'type': 'plotly_figure',
                            'data': formatted['data'],
                            'code': code,
                            'title': viz_info['title'],
                            'description': viz_info['description']
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
        """Generate key metrics from numeric columns"""
        metrics = []
        
        for col in numeric_cols[:5]:  # Limit to 5 metrics
            try:
                col_data = self.df[col]
                metrics.append({
                    'name': col,
                    'sum': float(col_data.sum()) if col_data.dtype in ['int64', 'float64'] else None,
                    'mean': float(col_data.mean()) if col_data.dtype in ['int64', 'float64'] else None,
                    'max': float(col_data.max()) if col_data.dtype in ['int64', 'float64'] else None,
                    'min': float(col_data.min()) if col_data.dtype in ['int64', 'float64'] else None,
                    'count': len(col_data)
                })
            except Exception as e:
                logger.warning(f"Error generating metric for {col}: {e}")
                continue
        
        return metrics
    
    def _plan_visualizations(self, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan which visualizations to create based on data structure"""
        plan = []
        
        numeric_cols = structure['numeric_cols']
        categorical_cols = structure['categorical_cols']
        date_cols = structure['date_cols']
        
        # 1. Distribution of numeric columns
        if numeric_cols:
            for col in numeric_cols[:3]:  # Limit to 3
                plan.append({
                    'type': 'histogram',
                    'columns': [col],
                    'title': f'Distribution of {col}',
                    'description': f'Show the distribution of {col} values'
                })
        
        # 2. Categorical analysis
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0] if categorical_cols else None
            num_col = numeric_cols[0] if numeric_cols else None
            if cat_col and num_col:
                plan.append({
                    'type': 'bar',
                    'columns': [cat_col, num_col],
                    'title': f'{num_col} by {cat_col}',
                    'description': f'Compare {num_col} across different {cat_col} categories'
                })
        
        # 3. Correlation heatmap
        if len(numeric_cols) >= 2:
            plan.append({
                'type': 'heatmap',
                'columns': numeric_cols[:10],  # Limit to 10 columns
                'title': 'Correlation Matrix',
                'description': 'Show correlation between numeric variables'
            })
        
        # 4. Top values
        if categorical_cols:
            cat_col = categorical_cols[0]
            if numeric_cols:
                num_col = numeric_cols[0]
                plan.append({
                    'type': 'bar',
                    'columns': [cat_col, num_col],
                    'title': f'Top {cat_col} by {num_col}',
                    'description': f'Show top categories of {cat_col} by {num_col}'
                })
        
        # 5. Time series (if date column exists)
        if date_cols and numeric_cols:
            date_col = date_cols[0]
            num_col = numeric_cols[0]
            plan.append({
                'type': 'line',
                'columns': [date_col, num_col],
                'title': f'{num_col} Over Time',
                'description': f'Show {num_col} trends over time'
            })
        
        return plan[:6]  # Limit to 6 visualizations
    
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

