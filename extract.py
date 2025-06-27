"""
Main entry point for running the full extraction and postprocessing pipeline.
Run this file from the project root:
    python extract.py
"""
import os
from pathlib import Path
from preprocessing.schemas.cv_schema import DocumentSchema
from preprocessing.run_pipeline import run_extraction_pipeline
from preprocessing.postprocessing import run_postprocessing

# Project root, input, and output directories
project_root = Path(__file__).parent.resolve()
input_dir = project_root / "documents_folder"
outputs_dir = project_root / "outputs"
os.makedirs(outputs_dir, exist_ok=True)
output_file = outputs_dir / "extraction_results.json"
postprocessed_file = outputs_dir / "pos_extraction_results.json"

# OpenAI API key and extraction template
openai_api_key = os.getenv("OPENAI_API_KEY") or "YOUR_API_KEY"
extraction_template = (
    """Extract all relevant entities and information mentioned as a JSON object that follows the schema class structure.\n\n
- For each professional experience, extract start_date and end_date if present (e.g., 'Aug 2005', 'Aug 2007', 'Present').\n
- If a property is not present or cannot be determined, leave it as null or do not include it in the output.\n
- Do NOT use generic placeholders like 'N/A', 'Not specified', 'City', 'Company Name', etc.\n\n
Passage:\n{input}"""
)
model = "gpt-4o-mini"

def main():
    print("[Extract] Running extraction pipeline...")
    run_extraction_pipeline(
        schema=DocumentSchema,
        input_dir=input_dir,
        output_file=str(output_file),
        openai_api_key=openai_api_key,
        extraction_template=extraction_template,
        model=model
    )
    print("[Extract] Running postprocessing...")
    run_postprocessing(str(output_file), str(postprocessed_file))
    print(f"[Extract] All done! Results in {postprocessed_file}")

if __name__ == "__main__":
    main()
