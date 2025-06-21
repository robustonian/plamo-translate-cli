#!/usr/bin/env python3
"""
Simple HTTP API server for plamo-translate that can be accessed from other machines.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from plamo_translate.servers.utils import (
    PLAMO_TRANSLATE_CLI_MODEL_NAME,
    SUPPORTED_LANGUAGES,
    TranslateRequest,
    Message,
    construct_llm_input,
)

logger = logging.getLogger(__name__)


class SimpleTranslateRequest(BaseModel):
    """Simplified request model for HTTP API"""
    text: str
    from_lang: str = "English|Japanese"
    to_lang: str = ""


class TranslateResponse(BaseModel):
    """Response model for translation"""
    translated_text: str
    from_lang: str
    to_lang: str


class PLaMoHTTPServer:
    """Simple HTTP server for plamo-translate"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app = FastAPI(title="PLaMo Translate HTTP API", version="1.0.0")
        
        # Enable CORS for all origins
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize model
        self.model = None
        self.tokenizer = None
        self.sampler = None
        self.logits_processors = None
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {"message": "PLaMo Translate HTTP API", "version": "1.0.0"}
        
        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "model_loaded": self.model is not None}
        
        @self.app.post("/translate", response_model=TranslateResponse)
        async def translate(request: SimpleTranslateRequest):
            if self.model is None:
                raise HTTPException(status_code=503, detail="Model not loaded")
            
            try:
                # Convert to internal format
                messages = [Message(role="user", content=request.text)]
                translate_req = TranslateRequest(
                    messages=messages,
                    source_language=request.from_lang,
                    target_language=request.to_lang
                )
                
                # Construct LLM input
                llm_messages = construct_llm_input(translate_req)
                prompt = self.tokenizer.apply_chat_template(llm_messages, add_generation_prompt=False)
                
                # Generate translation
                translated_text = await self._generate_translation(prompt)
                
                return TranslateResponse(
                    translated_text=translated_text.strip(),
                    from_lang=request.from_lang,
                    to_lang=request.to_lang
                )
                
            except Exception as e:
                logger.error(f"Translation error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
        
        @self.app.get("/languages")
        async def get_supported_languages():
            """Get list of supported languages"""
            return {"supported_languages": SUPPORTED_LANGUAGES}
    
    async def _generate_translation(self, prompt: str) -> str:
        """Generate translation using the loaded model"""
        from mlx_lm.generate import stream_generate
        from plamo_translate.servers.utils import PLAMO_MAX_TOKENS
        
        translation = ""
        for segment in stream_generate(
            model=self.model,
            tokenizer=self.tokenizer,
            prompt=prompt,
            sampler=self.sampler,
            logits_processors=self.logits_processors,
            max_tokens=int(PLAMO_MAX_TOKENS),
        ):
            translation += segment.text
        
        return translation
    
    def load_model(self):
        """Load the MLX model"""
        import importlib.resources
        import mlx.core as mx
        import mlx.nn as nn
        from mlx_lm.utils import load
        from mlx_lm.sample_utils import make_logits_processors, make_sampler
        from plamo_translate.servers.utils import (
            PLAMO_TRANSLATE_CLI_TEMP,
            PLAMO_TRANSLATE_CLI_TOP_P,
            PLAMO_TRANSLATE_CLI_TOP_K,
            PLAMO_TRANSLATE_CLI_REPETITION_PENALTY,
            PLAMO_TRANSLATE_CLI_REPETITION_CONTEXT_SIZE,
        )
        
        try:
            # Load chat template
            ref = importlib.resources.files("plamo_translate.assets").joinpath("chat_template.jinja2")
            chat_template = ref.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise RuntimeError("chat_template.jinja2 not found in assets directory")
        
        model_name = os.getenv("PLAMO_TRANSLATE_CLI_MODEL_NAME", PLAMO_TRANSLATE_CLI_MODEL_NAME)
        
        logger.info(f"Loading model: {model_name}")
        
        model, tokenizer = load(
            model_name,
            model_config={"trust_remote_code": True},
            tokenizer_config={
                "trust_remote_code": True,
                "chat_template": chat_template,
            },
        )
        tokenizer.add_eos_token("<|plamo:op|>")
        
        sampler = make_sampler(
            temp=float(PLAMO_TRANSLATE_CLI_TEMP),
            top_p=float(PLAMO_TRANSLATE_CLI_TOP_P),
            top_k=int(PLAMO_TRANSLATE_CLI_TOP_K),
        )
        
        logits_processors = make_logits_processors(
            repetition_penalty=(
                float(PLAMO_TRANSLATE_CLI_REPETITION_PENALTY)
                if PLAMO_TRANSLATE_CLI_REPETITION_PENALTY is not None
                else None
            ),
            repetition_context_size=(
                int(PLAMO_TRANSLATE_CLI_REPETITION_CONTEXT_SIZE)
                if PLAMO_TRANSLATE_CLI_REPETITION_CONTEXT_SIZE is not None
                else None
            ),
        )
        
        self.model = model
        self.tokenizer = tokenizer
        self.sampler = sampler
        self.logits_processors = logits_processors
        
        logger.info("Model loaded successfully")
    
    def run(self):
        """Run the HTTP server"""
        logger.info("Loading model...")
        self.load_model()
        logger.info(f"Starting HTTP server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)


def main():
    """Main entry point for HTTP server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PLaMo Translate HTTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    
    server = PLaMoHTTPServer(host=args.host, port=args.port)
    server.run()


if __name__ == "__main__":
    main()