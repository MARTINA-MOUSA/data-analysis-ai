"""
Analysis Engine - Executes Python code and handles results
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Any, Dict, Optional, Tuple
import traceback
import sys
from io import StringIO


class AnalysisEngine:
    """Engine for executing analysis code and generating visualizations"""
    
    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize with a dataframe
        
        Args:
            dataframe: pandas DataFrame to analyze
        """
        self.df = dataframe
        self.execution_context = {
            'pd': pd,
            'go': go,
            'px': px,
            'df': self.df,
            'DataFrame': pd.DataFrame
        }
    
    def execute_code(self, code: str) -> Tuple[Any, Optional[str], Optional[str]]:
        """
        Execute Python code safely
        
        Args:
            code: Python code string to execute
            
        Returns:
            tuple: (result, output_text, error_message)
        """
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        result = None
        error = None
        
        try:
            # Execute code in restricted context
            exec(code, self.execution_context)
            
            # Check if result variable exists
            if 'result' in self.execution_context:
                result = self.execution_context['result']
            elif 'fig' in self.execution_context:
                result = self.execution_context['fig']
            elif 'chart' in self.execution_context:
                result = self.execution_context['chart']
            
            output_text = captured_output.getvalue()
            
        except Exception as e:
            error = str(e)
            output_text = traceback.format_exc()
        
        finally:
            sys.stdout = old_stdout
        
        return result, output_text, error
    
    def is_plotly_figure(self, obj: Any) -> bool:
        """Check if object is a Plotly figure"""
        return isinstance(obj, (go.Figure, go.FigureWidget))
    
    def is_dataframe(self, obj: Any) -> bool:
        """Check if object is a pandas DataFrame"""
        return isinstance(obj, pd.DataFrame)
    
    def is_series(self, obj: Any) -> bool:
        """Check if object is a pandas Series"""
        return isinstance(obj, pd.Series)
    
    def format_result(self, result: Any) -> Dict[str, Any]:
        """
        Format result for display
        
        Args:
            result: Result from code execution
            
        Returns:
            dict: Formatted result with type and data
        """
        if self.is_plotly_figure(result):
            return {
                "type": "plotly_figure",
                "data": result
            }
        elif self.is_dataframe(result):
            return {
                "type": "dataframe",
                "data": result
            }
        elif self.is_series(result):
            return {
                "type": "series",
                "data": result.to_frame()
            }
        elif isinstance(result, (int, float, str, bool)):
            return {
                "type": "scalar",
                "data": result
            }
        elif isinstance(result, (list, dict)):
            return {
                "type": "collection",
                "data": result
            }
        else:
            return {
                "type": "other",
                "data": str(result)
            }

