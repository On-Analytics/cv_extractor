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
        try:
            result = await self.chain.ainvoke({"input": document.page_content})
            if not result:
                return {"error": "Extraction returned None"}

            data = result.dict()
            return data

        except Exception as e:
            error_msg = f"Error processing document: {str(e)}"
            return {"error": error_msg}
