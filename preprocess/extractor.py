"""
DocumentExtractor: Utility for extracting structured data from documents using a flexible schema and LLM.
"""
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

class DocumentExtractor:
    def __init__(
        self,
        schema: Type[BaseModel],
        openai_api_key: Optional[str] = None,
        extraction_template: Optional[str] = None,
        model: str = "gpt-4o-mini"
    ):
        """
        Initialize the DocumentExtractor.

        Args:
            schema (Type[BaseModel]): Pydantic schema/model to use for extraction.
            openai_api_key (Optional[str]): OpenAI API key for authentication.
            extraction_template (Optional[str]): System prompt template for extraction.
            model (str): OpenAI model name. Default is "gpt-4o-mini".
        """
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
        """
        Extract structured data from a document using the provided schema.

        Args:
            document (Document): The document to extract data from.

        Returns:
            Dict[str, Any]: Extracted structured data or an error message.
        """
        try:
            result = await self.chain.ainvoke({"input": document.page_content})
            if not result:
                return {"error": "Extraction returned None"}
            data = result.dict()
            return data
        except Exception as e:
            error_msg = f"Error processing document: {str(e)}"
            return {"error": error_msg}
