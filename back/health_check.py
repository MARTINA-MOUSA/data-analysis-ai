"""
Health check utilities for production monitoring
"""
from typing import Dict, Any
from back.logger import logger
from config import Config
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ai.llm_client import BasetenLLMClient
    LLM_AVAILABLE = True
except Exception as e:
    logger.warning(f"LLM client not available: {e}")
    LLM_AVAILABLE = False


def check_health() -> Dict[str, Any]:
    """
    Perform health check on all components
    
    Returns:
        dict: Health status of all components
    """
    health_status = {
        "status": "healthy",
        "components": {}
    }
    
    # Check configuration
    try:
        Config.validate()
        health_status["components"]["config"] = {
            "status": "healthy",
            "message": "Configuration valid"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["components"]["config"] = {
            "status": "unhealthy",
            "message": str(e)
        }
    
    # Check LLM connection
    if LLM_AVAILABLE:
        try:
            client = BasetenLLMClient()
            # Simple test message
            test_messages = [{"role": "user", "content": "test"}]
            response = list(client.chat_completion(
                messages=test_messages,
                stream=False,
                max_tokens=10,
                temperature=0.1
            ))
            health_status["components"]["llm"] = {
                "status": "healthy",
                "message": "LLM API accessible"
            }
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["components"]["llm"] = {
                "status": "unhealthy",
                "message": f"LLM API error: {str(e)}"
            }
    else:
        health_status["components"]["llm"] = {
            "status": "unknown",
            "message": "LLM client not initialized"
        }
    
    # Check disk space (logs directory)
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)
        health_status["components"]["disk"] = {
            "status": "healthy" if free_gb > 1 else "warning",
            "message": f"Free space: {free_gb:.2f} GB"
        }
    except Exception as e:
        health_status["components"]["disk"] = {
            "status": "unknown",
            "message": f"Could not check disk: {str(e)}"
        }
    
    return health_status


def get_system_info() -> Dict[str, Any]:
    """
    Get system information
    
    Returns:
        dict: System information
    """
    import platform
    import psutil
    import sys
    
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "cpu_count": psutil.cpu_count(),
        "memory_total_gb": psutil.virtual_memory().total / (1024**3),
        "memory_available_gb": psutil.virtual_memory().available / (1024**3),
        "environment": Config.ENV,
        "debug": Config.DEBUG
    }

