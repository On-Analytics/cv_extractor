from pathlib import Path

from typing import Type
import os
import json
from preprocess.postprocessing import postprocess_extracted_data
from preprocess.extractor import DocumentExtractor

class Processor:
    """Handles loading and processing of CV documents."""
    def __init__(self, input_dir: Path):
        self.input_dir = Path(input_dir)
        self.supported_extensions = {
            '.pdf': self._load_pdf,
            '.docx': self._load_docx,
            '.doc': self._load_docx,
            '.txt': self._load_text,
        }

    def _load_pdf(self, file_path: Path):
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.schema import Document
        try:
            loader = PyPDFLoader(str(file_path))
            pages = loader.load()
            if not pages:
                return []
            # Concatenate all page contents into one string
            full_text = "\n".join(page.page_content for page in pages)
            # Use metadata from the first page (or file_path)
            metadata = dict(pages[0].metadata) if pages and hasattr(pages[0], 'metadata') else {}
            metadata["source"] = str(file_path)
            # Return a single Document object for the whole file
            return [Document(page_content=full_text, metadata=metadata)]
        except Exception:
            return []
    def _load_docx(self, file_path: Path):
        from langchain_community.document_loaders import Docx2txtLoader
        try:
            loader = Docx2txtLoader(str(file_path))
            return loader.load()
        except Exception:
            return []
    def _load_text(self, file_path: Path):
        from langchain_community.document_loaders import TextLoader
        try:
            loader = TextLoader(str(file_path), encoding='utf-8')
            return loader.load()
        except Exception:
            return []
    def load_documents(self):
        documents = []
        if self.input_dir.is_file():
            ext = self.input_dir.suffix.lower()
            loader_func = self.supported_extensions.get(ext)
            if loader_func:
                docs = loader_func(self.input_dir)
                for doc in docs:
                    documents.append(doc)
        else:
            for ext, loader_func in self.supported_extensions.items():
                for file_path in self.input_dir.glob(f"*{ext}"):
                    docs = loader_func(file_path)
                    for doc in docs:
                        documents.append(doc)
        return documents

import asyncio

def run_sync_or_async(coro):
    """Helper to run either sync or async functions"""
    if asyncio.iscoroutine(coro):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in a running event loop, create a new one in a thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(coro)
                    )
                    return future.result()
            else:
                # Run in the current event loop
                return loop.run_until_complete(coro)
        except RuntimeError:
            # If there's no event loop, create one
            return asyncio.run(coro)
    return coro

async def run_extraction_pipeline(
    schema: Type,
    input_dir: Path,
    output_file: str,
    openai_api_key: str,
    extraction_template: str = None,
    model: str = "gpt-4o-mini"
):
    """
    Run the extraction pipeline with optional extraction prompt template and model name.
    Handles both single file and directory input, and manages sync/async extraction.
    """
    input_path = Path(input_dir)
    extractor = DocumentExtractor(
        schema=schema,
        openai_api_key=openai_api_key,
        extraction_template=extraction_template,
        model=model
    )

    processor = Processor(input_path)
    documents = processor.load_documents()

    if not documents:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([] if input_path.is_dir() else {}, f, indent=2, ensure_ascii=False)
        return {}

    try:
        if input_path.is_file():
            result = extractor.extract_from_document(documents[0])
            if asyncio.iscoroutine(result):
                result = await result
            # Write only a single output file (dict for single file)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            return result
        else:
            results = []
            for doc in documents:
                result = extractor.extract_from_document(doc)
                if asyncio.iscoroutine(result):
                    result = await result
                results.append(result)
            # Write only a single output file (list for batch)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            return results
    except Exception as e:
        # Ensure we have a valid return value even in case of error
        error_result = {"error": str(e)}

        return error_result
