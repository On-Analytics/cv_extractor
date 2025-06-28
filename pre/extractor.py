import json
from typing import Dict, Any, List, Optional, Union, Type
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

class DocumentExtractor:
    def __init__(self, schema, openai_api_key: Optional[str] = None, extraction_template: Optional[str] = None, model: str = "gpt-4o-mini"):
        """Initialize the document extractor with a dynamic schema, optional OpenAI API key, required extraction prompt template, and model name."""
        if extraction_template is None:
            raise ValueError("extraction_template must be provided to DocumentExtractor.")
        self.schema = schema
        self.llm = ChatOpenAI( # Initialize the LLM
            model=model,
            temperature=0.1,
            openai_api_key=openai_api_key
        )

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([ # Create the prompt template
            ("system", extraction_template), # System prompt
            ("human", "{input}") # Human prompt
        ])
        
        # Create the chain with structured output
        self.chain = prompt | self.llm.with_structured_output( # Create the chain with structured output
            schema=self.schema, # Schema for structured output
            method="function_calling", # Method for structured output
            include_raw=False 
        )

    async def extract_from_document(self, document: Document) -> Dict[str, Any]:
        """Extract structured data from a single document using Pydantic models."""
        # Try to get the filename from document metadata
        source_file = None
        if hasattr(document, 'metadata') and isinstance(document.metadata, dict):
            source_file = document.metadata.get('source') or document.metadata.get('file_path')
        if not source_file:
            source_file = getattr(document, 'source', None)
        if not source_file:
            source_file = 'unknown'
        print(f"[Extract] Starting extraction from document: {source_file}")
        
        try:
            # Log the first 100 chars of the document for debugging
            # logger.debug(f"Document content preview: {document.page_content[:200]}...")
            
            # The chain now returns a Pydantic model directly
            # logger.info("Invoking extraction chain...")
            result = await self.chain.ainvoke({"input": document.page_content})

            if result is not None:
                print("[Extract] Extraction completed, processing results...")
                # Convert Pydantic model to dict
                data = result.dict()
                # logger.debug(f"Raw extracted data: {json.dumps(data, indent=2, default=str)[:500]}...")

                # Add source, file_name, and page metadata if present
                if hasattr(document, 'metadata') and isinstance(document.metadata, dict):
                    if 'source' in document.metadata:
                        data['source'] = document.metadata['source']
                    elif 'file_path' in document.metadata:
                        data['source'] = document.metadata['file_path']
                    # Add file_name (file name only)
                    if 'source' in document.metadata:
                        data['file_name'] = os.path.basename(document.metadata['source'])
                    elif 'file_path' in document.metadata:
                        data['file_name'] = os.path.basename(document.metadata['file_path'])
                    if 'page' in document.metadata:
                        data['page'] = document.metadata['page']
                elif hasattr(document, 'source'):
                    data['source'] = getattr(document, 'source', None)
                    data['file_name'] = os.path.basename(getattr(document, 'source', ''))

                print(f"[Extract] Extraction successful. Fields extracted: {list(data.keys())}")
                return data
                
            print("[Extract] Extraction returned None")
            return {}
            
        except Exception as e:
            error_msg = f"Error processing document {source_file}: {str(e)}"
            print(f"[Extract][Error] {error_msg}")
            return {"error": error_msg, "source_file": source_file}

