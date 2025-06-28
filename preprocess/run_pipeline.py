from pathlib import Path
from preprocess.schemas.cv_schema import DocumentSchema
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
        try:
            loader = PyPDFLoader(str(file_path))
            return loader.load()
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
        for ext, loader_func in self.supported_extensions.items():
            for file_path in self.input_dir.glob(f"*{ext}"):
                print(f"[Main] Processing file: {file_path.name}")
                docs = loader_func(file_path)
                for doc in docs:
                    documents.append(doc)
        return documents

def run_extraction_pipeline(schema: Type, input_dir: Path, output_file: str, openai_api_key: str, extraction_template: str = None, model: str = "gpt-4o-mini"):
    """
    Run the extraction pipeline with optional extraction prompt template and model name.
    """
    
    """Run the extraction pipeline with optional extraction prompt template."""
    print("[Pipeline] Starting extraction pipeline...")
    processor = Processor(input_dir) # creates an instance of the Processor class
    extractor = DocumentExtractor(schema=schema, openai_api_key=openai_api_key, extraction_template=extraction_template, model=model) #creates an instance of the DocumentExtractor class
    documents = processor.load_documents() # Load documents
    if not documents:
        print("[Pipeline][Warn] No documents found to process.")
        # Always write an empty list to output_file for valid JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        print(f"[Pipeline] Wrote empty results to {output_file}")
        return
    
    # Extract from all documents (merged or not, depending on your extractor)
    results = []
    for doc in documents:
        result = extractor.extract_from_document(doc)
        if hasattr(result, '__await__'):
            import asyncio
            result = asyncio.get_event_loop().run_until_complete(result)
        # Only extract; do not postprocess here
        results.append(result)
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"[Pipeline] Results saved to {output_file}")
