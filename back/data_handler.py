"""
Data Handler - Handles CSV file operations and data management
"""
import pandas as pd
from typing import Optional, Dict, Any
import io
from back.exceptions import DataLoadError
from back.logger import logger
from config import Config


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
            
        Raises:
            DataLoadError: If file loading fails
        """
        try:
            logger.info(f"Loading file from path: {file_path}")
            self.df = pd.read_csv(file_path)
            
            # Validate data size
            if len(self.df) > Config.MAX_ROWS_PREVIEW:
                logger.warning(f"Large dataset loaded: {len(self.df)} rows")
            
            self.original_df = self.df.copy()
            logger.info(f"Successfully loaded {len(self.df)} rows, {len(self.df.columns)} columns")
            return True
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            raise DataLoadError(error_msg)
        except pd.errors.EmptyDataError:
            error_msg = f"Empty file: {file_path}"
            logger.error(error_msg)
            raise DataLoadError(error_msg)
        except Exception as e:
            error_msg = f"Error loading file: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise DataLoadError(error_msg)
    
    def load_from_bytes(self, file_bytes: bytes, filename: str) -> bool:
        """
        Load CSV from bytes (for Streamlit file uploader)
        
        Args:
            file_bytes: File content as bytes
            filename: Name of the file
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            DataLoadError: If file loading fails
        """
        try:
            # Validate file size
            file_size_mb = len(file_bytes) / (1024 * 1024)
            if file_size_mb > Config.MAX_FILE_SIZE_MB:
                error_msg = f"File size ({file_size_mb:.2f} MB) exceeds maximum ({Config.MAX_FILE_SIZE_MB} MB)"
                logger.error(error_msg)
                raise DataLoadError(error_msg)
            
            # Validate file extension
            if not any(filename.lower().endswith(ext) for ext in Config.ALLOWED_FILE_EXTENSIONS):
                error_msg = f"File type not allowed. Allowed: {Config.ALLOWED_FILE_EXTENSIONS}"
                logger.error(error_msg)
                raise DataLoadError(error_msg)
            
            logger.info(f"Loading file from bytes: {filename} ({file_size_mb:.2f} MB)")
            self.df = pd.read_csv(io.BytesIO(file_bytes))
            
            # Validate data size
            if len(self.df) > Config.MAX_ROWS_PREVIEW:
                logger.warning(f"Large dataset loaded: {len(self.df)} rows")
            
            self.original_df = self.df.copy()
            logger.info(f"Successfully loaded {len(self.df)} rows, {len(self.df.columns)} columns")
            return True
        except pd.errors.EmptyDataError:
            error_msg = f"Empty file: {filename}"
            logger.error(error_msg)
            raise DataLoadError(error_msg)
        except Exception as e:
            error_msg = f"Error loading file from bytes: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise DataLoadError(error_msg)
    
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

