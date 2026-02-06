"""
LLM Client for Project Chimera.

Wraps the Google Generative AI SDK to provide a standardized interface
for agents to generate responses.
"""
import os
import json
import logging
from typing import Optional, Any, Dict, Type
import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMClient:
    """ Client for interacting with Google's Gemini models. """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-flash-latest"):
        """
        Initialize the LLM Client.
        
        Args:
            api_key: Gemini API key (defaults to env var GEMINI_API_KEY)
            model_name: Model to use (default: gemini-pro)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. LLM calls will fail.")
        
        self.model_name = model_name
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(model_name)
    
    async def generate_response(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Generate a text response from the LLM.
        
        Args:
            prompt: The user prompt
            system_instruction: Optional system context (prepended to prompt)
            
        Returns:
            Generated text response
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")
            
        full_prompt = prompt
        if system_instruction:
            full_prompt = f"{system_instruction}\n\nUser Input:\n{prompt}"
            
        try:
            # Note: For async, we'd ideally use the async client if available in the SDK
            # robustly, but standard generate_content is synchronous in v1.
            # Wrapping in an executor would be better for high-load, keeping simple for now.
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    async def generate_structured(
        self, 
        prompt: str, 
        response_model: Type[BaseModel],
        system_instruction: Optional[str] = None
    ) -> Any:
        """
        Generates a structured JSON response matching a Pydantic model.
        
        Args:
            prompt: The user prompt
            response_model: Pydantic model class to valid against
            system_instruction: Optional system context
            
        Returns:
            Instance of response_model
        """
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        
        structure_prompt = f"""
        {system_instruction or ''}
        
        You must output valid JSON that matches the following schema:
        {schema_json}
        
        Do not include markdown code blocks (```json). Just return the raw JSON.
        
        User Input:
        {prompt}
        """
        
        text_response = await self.generate_response(structure_prompt)
        
        # Clean up potential markdown formatting
        cleaned_text = text_response.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
            
        try:
            data = json.loads(cleaned_text)
            return response_model.model_validate(data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from LLM: {cleaned_text}")
            raise ValueError(f"LLM did not return valid JSON: {e}")
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise
