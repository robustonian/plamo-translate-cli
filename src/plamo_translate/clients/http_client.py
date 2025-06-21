#!/usr/bin/env python3
"""
HTTP client for plamo-translate that communicates with the HTTP server
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, List
import aiohttp

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP client for plamo-translate HTTP server"""
    
    def __init__(self, host: str = "localhost", port: int = 8080, stream: bool = True):
        self.host = host
        self.port = port
        self.stream = stream
        self.base_url = f"http://{host}:{port}"
    
    async def translate(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Translate messages using HTTP API"""
        
        # Extract text from messages - assume last message contains the text to translate
        text = ""
        from_lang = "English|Japanese"
        to_lang = ""
        
        # Parse messages to extract text and language info
        for message in messages:
            content = message.get("content", "")
            if content.startswith("input"):
                if "lang:" in content:
                    # Extract language and text
                    lines = content.split("\n", 1)
                    if len(lines) > 1:
                        lang_line = lines[0]
                        text = lines[1]
                        if "lang:" in lang_line:
                            from_lang = lang_line.split("lang:")[1].strip()
                else:
                    # No language specified, extract text
                    lines = content.split("\n", 1)
                    if len(lines) > 1:
                        text = lines[1]
            elif content.startswith("output"):
                if "lang:" in content:
                    to_lang = content.split("lang:")[1].strip()
        
        # If no text was found in structured format, use the last message content
        if not text and messages:
            text = messages[-1].get("content", "")
        
        payload = {
            "text": text,
            "from_lang": from_lang,
            "to_lang": to_lang
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/translate",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        translated_text = result.get("translated_text", "")
                        yield translated_text
                    else:
                        error_text = await response.text()
                        logger.error(f"HTTP error {response.status}: {error_text}")
                        raise Exception(f"HTTP translation failed: {response.status}")
        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {e}")
            raise Exception(f"Failed to connect to HTTP server at {self.base_url}: {e}")
    
    async def check_health(self) -> bool:
        """Check if the HTTP server is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        return health_data.get("model_loaded", False)
                    return False
        except Exception:
            return False