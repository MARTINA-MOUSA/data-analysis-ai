"""
Custom exceptions for the application
"""


class DataAnalysisError(Exception):
    """Base exception for data analysis errors"""
    pass


class DataLoadError(DataAnalysisError):
    """Raised when data loading fails"""
    pass


class AnalysisExecutionError(DataAnalysisError):
    """Raised when code execution fails"""
    pass


class LLMError(DataAnalysisError):
    """Raised when LLM API calls fail"""
    pass


class ConfigurationError(DataAnalysisError):
    """Raised when configuration is invalid"""
    pass

