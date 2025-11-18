"""
Data Handler - Handles CSV file operations and data management
"""
import pandas as pd
from typing import Optional, Dict, Any
import io


class DataHandler:
    """Class for handling CSV data operations"""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.original_df: Optional[pd.DataFrame] = None
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load CSV file from path
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.df = pd.read_csv(file_path)
            self.original_df = self.df.copy()
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def load_from_bytes(self, file_bytes: bytes, filename: str) -> bool:
        """
        Load CSV from bytes (for Streamlit file uploader)
        
        Args:
            file_bytes: File content as bytes
            filename: Name of the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.df = pd.read_csv(io.BytesIO(file_bytes))
            self.original_df = self.df.copy()
            return True
        except Exception as e:
            print(f"Error loading file from bytes: {e}")
            return False
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Get current dataframe"""
        return self.df
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the dataframe
        
        Returns:
            dict: Information about columns, shape, dtypes, etc.
        """
        if self.df is None:
            return {}
        
        return {
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "dtypes": self.df.dtypes.to_dict(),
            "null_counts": self.df.isnull().sum().to_dict(),
            "memory_usage": self.df.memory_usage(deep=True).sum(),
            "sample": self.df.head(5).to_dict('records')
        }
    
    def get_column_names(self) -> list:
        """Get list of column names"""
        if self.df is None:
            return []
        return list(self.df.columns)
    
    def reset_data(self) -> bool:
        """Reset dataframe to original state"""
        if self.original_df is None:
            return False
        self.df = self.original_df.copy()
        return True
    
    def is_loaded(self) -> bool:
        """Check if data is loaded"""
        return self.df is not None

