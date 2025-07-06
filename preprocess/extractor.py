import json
from typing import Dict, Any, List, Optional, Union, Type
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

class DocumentExtractor:
    def __init__(
        self,
        schema: Type,
        openai_api_key: Optional[str] = None,
        extraction_template: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ):
        """Initialize the document extractor with schema, API key, template, and model."""
        if extraction_template is None:
            raise ValueError("extraction_template must be provided to DocumentExtractor.")
        self.schema = schema
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.1,
            openai_api_key=openai_api_key
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", extraction_template),
            ("human", "{input}")
        ])
        self.chain = prompt | self.llm.with_structured_output(
            schema=self.schema,
            method="function_calling",
            include_raw=False
        )

    async def extract_from_document(self, document: Document) -> Dict[str, Any]:
        """Extract structured data from a document using the schema."""
        source_file = getattr(
            document, 'source',
            getattr(document, 'metadata', {}).get('source') or
            getattr(document, 'metadata', {}).get('file_path', 'unknown')
        )
        try:
            result = await self.chain.ainvoke({"input": document.page_content})
            if not result:
                return {"error": "Extraction returned None", "source_file": source_file}

            data = result.dict()
            metadata = getattr(document, 'metadata', {}) or {}
            from datetime import datetime
            filtered_metadata = {k: metadata.get(k) for k in ["title", "total_pages", "page"] if k in metadata}
            filtered_metadata["date_of_extraction"] = datetime.now().strftime("%Y-%m-%d")
            data['metadata'] = filtered_metadata
            return data

        except Exception as e:
            error_msg = f"Error processing document {source_file}: {str(e)}"
            return {"error": error_msg, "source_file": source_file}
