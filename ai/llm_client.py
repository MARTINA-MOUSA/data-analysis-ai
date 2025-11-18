"""
LLM Client - Handles communication with Baseten API
"""
from openai import OpenAI
from typing import Iterator, Optional
import sys
import os
import time
from back.exceptions import LLMError
from back.logger import logger

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class BasetenLLMClient:
    """Client for interacting with Baseten OpenAI-compatible API"""
    
    def __init__(self):
        """Initialize the client with configuration"""
        Config.validate()
        self.client = OpenAI(
            api_key=Config.BASETEN_API_KEY,
            base_url=Config.BASETEN_BASE_URL,
            timeout=Config.BASETEN_TIMEOUT,
            max_retries=Config.BASETEN_MAX_RETRIES
        )
        self.model = Config.BASETEN_MODEL
        logger.info(f"Initialized LLM client with model: {self.model}")
    
    def chat_completion(
        self,
        messages: list,
        stream: bool = True,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        top_p: float = 1.0
    ) -> Iterator[str]:
        """
        Create chat completion with streaming
        
        Args:
            messages: List of message dictionaries
            stream: Whether to stream the response
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            
        Yields:
            str: Chunks of the response
        """
        try:
            logger.debug(f"Making LLM request with {len(messages)} messages")
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
                stream_options={
                    "include_usage": True,
                    "continuous_usage_stats": True
                },
                top_p=top_p,
                max_tokens=max_tokens,
                temperature=temperature,
                presence_penalty=0,
                frequency_penalty=0
            )
            
            if stream:
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content
            else:
                if response.choices and response.choices[0].message.content:
                    yield response.choices[0].message.content
            
            elapsed_time = time.time() - start_time
            logger.info(f"LLM request completed in {elapsed_time:.2f}s")
                    
        except Exception as e:
            error_msg = f"LLM API error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise LLMError(error_msg)
    
    def get_full_response(
        self,
        messages: list,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Get full response without streaming
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            str: Full response text
        """
        response_text = ""
        for chunk in self.chat_completion(
            messages=messages,
            stream=True,
            max_tokens=max_tokens,
            temperature=temperature
        ):
            response_text += chunk
        return response_text

