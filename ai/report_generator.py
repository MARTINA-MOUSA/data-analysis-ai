"""
Report Generator - Creates comprehensive data analysis reports
"""
import pandas as pd
from typing import Dict, Any, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from back.data_handler import DataHandler
from ai.llm_client import BasetenLLMClient
from back.logger import logger


class ReportGenerator:
    """Generates comprehensive data analysis reports with predictions and insights"""
    
    def __init__(self, data_handler: DataHandler, llm_client: BasetenLLMClient):
        """
        Initialize the report generator
        
        Args:
            data_handler: DataHandler instance
            llm_client: LLM client for generating insights
        """
        self.data_handler = data_handler
        self.llm_client = llm_client
        self.df = data_handler.get_dataframe()
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report with data explanation, predictions, and insights
        
        Returns:
            dict: Complete report with all sections
        """
        logger.info("Generating comprehensive report...")
        
        info = self.data_handler.get_info()
        
        report = {
            'data_overview': self._generate_data_overview(info),
            'data_explanation': self._generate_data_explanation(info),
            'statistical_summary': self._generate_statistical_summary(),
            'predictions': self._generate_predictions(info),
            'insights': self._generate_insights(info),
            'recommendations': self._generate_recommendations(info),
            'data_quality': self._assess_data_quality(info)
        }
        
        return report
    
    def _generate_data_overview(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data overview section"""
        return {
            'total_rows': info.get('shape', (0, 0))[0],
            'total_columns': info.get('shape', (0, 0))[1],
            'columns': info.get('columns', []),
            'memory_usage_mb': round(info.get('memory_usage', 0) / (1024 * 1024), 2),
            'null_values': sum(info.get('null_counts', {}).values()),
            'duplicate_rows': self.df.duplicated().sum()
        }
    
    def _generate_data_explanation(self, info: Dict[str, Any]) -> str:
        """Generate explanation of what the data contains"""
        columns = info.get('columns', [])
        dtypes = info.get('dtypes', {})
        sample_data = self.df.head(3).to_dict('records')
        
        context = f"""
Explain what this dataset contains in detail. Be specific and helpful.

Dataset Information:
- Total rows: {len(self.df)}
- Total columns: {len(columns)}
- Columns: {', '.join(columns)}

Column Types:
{chr(10).join([f"- {col}: {dtype}" for col, dtype in dtypes.items()])}

Sample Data (first 3 rows):
{sample_data}

Provide a comprehensive explanation in Arabic that covers:
1. What this dataset represents
2. What each column means
3. What kind of analysis can be done
4. What business questions it can answer
5. What insights can be extracted

Write in a clear, professional manner suitable for business users.
"""
        
        messages = [
            {"role": "system", "content": "You are a data analysis expert. Explain datasets clearly and comprehensively in Arabic."},
            {"role": "user", "content": context}
        ]
        
        explanation = self.llm_client.get_full_response(
            messages=messages,
            max_tokens=1500,
            temperature=0.7
        )
        
        return explanation
    
    def _generate_statistical_summary(self) -> Dict[str, Any]:
        """Generate statistical summary"""
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        summary = {}
        for col in numeric_cols[:10]:  # Limit to 10 columns
            try:
                summary[col] = {
                    'mean': float(self.df[col].mean()),
                    'median': float(self.df[col].median()),
                    'std': float(self.df[col].std()),
                    'min': float(self.df[col].min()),
                    'max': float(self.df[col].max()),
                    'q25': float(self.df[col].quantile(0.25)),
                    'q75': float(self.df[col].quantile(0.75))
                }
            except Exception as e:
                logger.warning(f"Error calculating stats for {col}: {e}")
                continue
        
        return summary
    
    def _generate_predictions(self, info: Dict[str, Any]) -> str:
        """Generate predictions and forecasts"""
        columns = info.get('columns', [])
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        
        # Calculate trends
        trends = {}
        for col in numeric_cols[:5]:
            try:
                if len(self.df) > 1:
                    trend = (self.df[col].iloc[-1] - self.df[col].iloc[0]) / len(self.df)
                    trends[col] = trend
            except:
                continue
        
        context = f"""
Based on this dataset, provide predictions and forecasts in Arabic.

Dataset Summary:
- Columns: {', '.join(columns)}
- Numeric columns: {', '.join(numeric_cols[:10])}
- Categorical columns: {', '.join(categorical_cols[:10])}
- Total rows: {len(self.df)}

Trends detected:
{chr(10).join([f"- {col}: {trend:.2f} per row" for col, trend in trends.items()])}

Provide:
1. Short-term predictions (next period)
2. Long-term forecasts (if applicable)
3. Potential risks and opportunities
4. What patterns suggest about future trends
5. Recommendations based on predictions

Write in a clear, actionable manner for business decision-makers.
"""
        
        messages = [
            {"role": "system", "content": "You are a data scientist and business analyst. Provide accurate predictions and forecasts in Arabic."},
            {"role": "user", "content": context}
        ]
        
        predictions = self.llm_client.get_full_response(
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )
        
        return predictions
    
    def _generate_insights(self, info: Dict[str, Any]) -> str:
        """Generate key insights"""
        columns = info.get('columns', [])
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # Calculate key metrics
        key_metrics = {}
        for col in numeric_cols[:5]:
            try:
                key_metrics[col] = {
                    'total': float(self.df[col].sum()),
                    'average': float(self.df[col].mean()),
                    'top_value': float(self.df[col].max())
                }
            except:
                continue
        
        context = f"""
Analyze this dataset and provide key business insights in Arabic.

Dataset:
- Columns: {', '.join(columns)}
- Rows: {len(self.df)}

Key Metrics:
{chr(10).join([f"- {col}: Total={metrics['total']:.2f}, Average={metrics['average']:.2f}" for col, metrics in key_metrics.items()])}

Provide:
1. Most important findings
2. Surprising patterns or anomalies
3. Business implications
4. Actionable insights
5. What decision-makers should focus on

Write clearly and focus on business value.
"""
        
        messages = [
            {"role": "system", "content": "You are a business intelligence analyst. Provide actionable insights in Arabic."},
            {"role": "user", "content": context}
        ]
        
        insights = self.llm_client.get_full_response(
            messages=messages,
            max_tokens=2000,
            temperature=0.7
        )
        
        return insights
    
    def _generate_recommendations(self, info: Dict[str, Any]) -> str:
        """Generate actionable recommendations"""
        context = f"""
Based on the dataset analysis, provide actionable recommendations in Arabic.

Dataset has {len(self.df)} rows and {len(info.get('columns', []))} columns.

Provide:
1. Immediate actions to take
2. Strategic recommendations
3. Areas to investigate further
4. Optimization opportunities
5. Risk mitigation strategies

Write in a clear, prioritized manner.
"""
        
        messages = [
            {"role": "system", "content": "You are a business consultant. Provide strategic recommendations in Arabic."},
            {"role": "user", "content": context}
        ]
        
        recommendations = self.llm_client.get_full_response(
            messages=messages,
            max_tokens=1500,
            temperature=0.7
        )
        
        return recommendations
    
    def _assess_data_quality(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data quality"""
        null_counts = info.get('null_counts', {})
        total_nulls = sum(null_counts.values())
        total_cells = len(self.df) * len(self.df.columns)
        completeness = ((total_cells - total_nulls) / total_cells * 100) if total_cells > 0 else 0
        
        duplicates = self.df.duplicated().sum()
        duplicate_percentage = (duplicates / len(self.df) * 100) if len(self.df) > 0 else 0
        
        return {
            'completeness_percentage': round(completeness, 2),
            'null_values': total_nulls,
            'duplicate_rows': int(duplicates),
            'duplicate_percentage': round(duplicate_percentage, 2),
            'quality_score': round((completeness / 100) * (1 - duplicate_percentage / 100) * 100, 2),
            'columns_with_nulls': [col for col, count in null_counts.items() if count > 0]
        }

