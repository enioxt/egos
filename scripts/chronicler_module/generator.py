#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""KOIOS Chronicler Module - Documentation Generator

This module is responsible for AI-powered documentation generation, including:
- AI model interaction (OpenRouter)
- Prompt engineering and context preparation
- Response parsing and formatting

Part of the KOIOS subsystem within EGOS.

Author: EGOS Team
Date Created: 2025-04-22
Last Modified: 2025-05-18

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import os
import logging
import json
import time
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime

# Constants
DEFAULT_MODEL = "anthropic/claude-3-opus"
DEFAULT_MAX_TOKENS = 4000
DEFAULT_TEMPERATURE = 0.7
API_RETRY_ATTEMPTS = 3
API_RETRY_DELAY = 2  # seconds


class DocumentationGenerator:
    """
    Generates documentation from codebase analysis results using AI models.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the DocumentationGenerator.
        
        Args:
            config: Configuration dictionary containing API keys and settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Extract configuration
        self.api_key = self._get_api_key()
        self.model = config.get('model', DEFAULT_MODEL)
        self.max_tokens = config.get('max_tokens', DEFAULT_MAX_TOKENS)
        self.temperature = config.get('temperature', DEFAULT_TEMPERATURE)
        
        self.logger.info(f"Initialized generator with model: {self.model}")
    
    def generate(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate documentation based on analysis results.
        
        Args:
            analysis_results: Dictionary containing codebase analysis results
            
        Returns:
            Dictionary containing generated documentation
        """
        self.logger.info("Starting documentation generation...")
        
        # Prepare documentation structure
        documentation = {
            "project_name": analysis_results["project_name"],
            "project_path": analysis_results["project_path"],
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": "",
            "structure_overview": "",
            "language_analysis": "",
            "recommendations": "",
            "raw_analysis": analysis_results
        }
        
        # Prepare prompt for the AI model
        prompt = self._prepare_prompt(analysis_results)
        
        # Generate documentation using AI
        try:
            ai_response = self._call_ai_model(prompt)
            
            # Parse AI response
            parsed_response = self._parse_ai_response(ai_response)
            
            # Update documentation with parsed response
            documentation.update(parsed_response)
            
            self.logger.info("Documentation generation completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error generating documentation: {e}")
            documentation["error"] = str(e)
            documentation["summary"] = "Error occurred during documentation generation."
        
        return documentation
    
    def _prepare_prompt(self, analysis_results: Dict[str, Any]) -> str:
        """
        Prepare a prompt for the AI model based on analysis results.
        
        Args:
            analysis_results: Dictionary containing codebase analysis results
            
        Returns:
            Formatted prompt string
        """
        self.logger.debug("Preparing AI prompt...")
        
        # Extract key information for the prompt
        project_name = analysis_results["project_name"]
        file_count = analysis_results["file_count"]
        total_size = analysis_results["total_size"]
        languages = analysis_results["languages"]
        
        # Get top files by size (up to 10)
        top_files = sorted(
            analysis_results["files"],
            key=lambda x: x["size"],
            reverse=True
        )[:10]
        
        # Format the prompt
        prompt = f"""
        You are an expert software documentation specialist. Analyze the following codebase information and generate comprehensive documentation.
        
        PROJECT INFORMATION:
        - Name: {project_name}
        - Files: {file_count}
        - Total Size: {total_size / 1024:.2f} KB
        
        LANGUAGE DISTRIBUTION:
        {self._format_languages(languages)}
        
        TOP FILES BY SIZE:
        {self._format_top_files(top_files)}
        
        DIRECTORY STRUCTURE:
        {self._format_directories(analysis_results["directories"])}
        
        Based on this information, please provide:
        
        1. PROJECT SUMMARY: A concise overview of what this project appears to be, its likely purpose, and main components.
        
        2. STRUCTURE OVERVIEW: Analysis of the project's organization, architecture patterns, and key components.
        
        3. LANGUAGE ANALYSIS: Insights about the technology stack, programming paradigms, and development patterns.
        
        4. RECOMMENDATIONS: Suggestions for documentation improvements, code organization, or potential issues to address.
        
        Format your response as JSON with the following structure:
        {{
            "summary": "Project summary here...",
            "structure_overview": "Structure analysis here...",
            "language_analysis": "Language insights here...",
            "recommendations": "Recommendations here..."
        }}
        """
        
        return prompt.strip()
    
    def _format_languages(self, languages: Dict[str, Dict[str, Any]]) -> str:
        """Format language information for the prompt."""
        result = []
        for lang, stats in languages.items():
            result.append(f"- {lang}: {stats['count']} files ({stats['size'] / 1024:.2f} KB)")
        return "\n".join(result)
    
    def _format_top_files(self, files: List[Dict[str, Any]]) -> str:
        """Format top files information for the prompt."""
        result = []
        for file in files:
            result.append(f"- {file['path']} ({file['size'] / 1024:.2f} KB, {file['language']})")
        return "\n".join(result)
    
    def _format_directories(self, directories: List[Dict[str, Any]]) -> str:
        """Format directory structure for the prompt."""
        # Simple implementation - just list directories
        result = []
        for directory in directories:
            result.append(f"- {directory['path']}")
        return "\n".join(result)
    
    def _call_ai_model(self, prompt: str) -> str:
        """
        Call the AI model API with the prepared prompt.
        
        Args:
            prompt: Formatted prompt string
            
        Returns:
            Model response as string
            
        Raises:
            Exception: If API call fails after retries
        """
        self.logger.info(f"Calling AI model: {self.model}")
        
        # OpenRouter API endpoint
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are an expert software documentation specialist."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://egos.ai",  # Replace with actual domain
            "X-Title": "KOIOS Chronicler"
        }
        
        # Attempt API call with retries
        for attempt in range(1, API_RETRY_ATTEMPTS + 1):
            try:
                self.logger.debug(f"API attempt {attempt}/{API_RETRY_ATTEMPTS}")
                
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=60  # 60 second timeout
                )
                
                response.raise_for_status()  # Raise exception for HTTP errors
                
                # Parse response
                response_data = response.json()
                
                # Extract content from response
                content = response_data["choices"][0]["message"]["content"]
                
                self.logger.info(f"AI response received ({len(content)} chars)")
                return content
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"API request failed (attempt {attempt}): {e}")
                
                if attempt < API_RETRY_ATTEMPTS:
                    self.logger.info(f"Retrying in {API_RETRY_DELAY} seconds...")
                    time.sleep(API_RETRY_DELAY)
                else:
                    self.logger.error("All API attempts failed")
                    raise Exception(f"Failed to generate documentation after {API_RETRY_ATTEMPTS} attempts: {e}")
    
    def _parse_ai_response(self, response: str) -> Dict[str, str]:
        """
        Parse the AI model response into structured documentation.
        
        Args:
            response: Raw response from the AI model
            
        Returns:
            Dictionary containing parsed documentation sections
        """
        self.logger.debug("Parsing AI response...")
        
        # Default structure in case parsing fails
        result = {
            "summary": "",
            "structure_overview": "",
            "language_analysis": "",
            "recommendations": ""
        }
        
        try:
            # Extract JSON from response (handle potential text before/after JSON)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                parsed = json.loads(json_str)
                
                # Update result with parsed values
                for key in result.keys():
                    if key in parsed:
                        result[key] = parsed[key]
                
                self.logger.info("AI response parsed successfully")
            else:
                # Fallback if JSON not found
                self.logger.warning("JSON structure not found in AI response")
                result["summary"] = "Error parsing AI response: JSON structure not found."
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing AI response as JSON: {e}")
            result["summary"] = f"Error parsing AI response: {e}"
        
        return result
    
    def _get_api_key(self) -> str:
        """
        Get API key from config or environment variable.
        
        Returns:
            API key as string
            
        Raises:
            ValueError: If API key is not found
        """
        # Try to get from config
        api_key = self.config.get('api_key')
        
        # If not in config, try environment variable
        if not api_key:
            api_key = os.environ.get('OPENROUTER_API_KEY')
        
        # Validate API key
        if not api_key:
            self.logger.error("API key not found in config or environment variables")
            raise ValueError(
                "OpenRouter API key not found. Please provide it in the config file "
                "or set the OPENROUTER_API_KEY environment variable."
            )
        
        return api_key


# For testing
if __name__ == "__main__":
    import sys
    import json
    
    # Setup basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Sample analysis results for testing
    sample_results = {
        "project_name": "sample_project",
        "project_path": "/path/to/sample_project",
        "files": [
            {"path": "main.py", "size": 1024, "language": "Python"},
            {"path": "utils.py", "size": 512, "language": "Python"},
            {"path": "index.html", "size": 2048, "language": "HTML"}
        ],
        "directories": [
            {"path": "src", "name": "src"},
            {"path": "docs", "name": "docs"}
        ],
        "languages": {
            "Python": {"count": 2, "size": 1536},
            "HTML": {"count": 1, "size": 2048}
        },
        "file_count": 3,
        "total_size": 3584,
        "gitignore_rules": []
    }
    
    # Mock config with API key
    config = {
        "model": "anthropic/claude-3-opus",
        "max_tokens": 1000,
        "temperature": 0.7,
        "api_key": "YOUR_API_KEY_HERE"  # Replace with actual key for testing
    }
    
    print("This is a test module. In a real scenario, you would need a valid API key.")