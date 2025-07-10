"""
extract.py: Main entry point for extracting structured data from files or directories using a flexible schema system and LLM.
"""
import os
import json
from pathlib import Path
from typing import Union, Dict, Any, Optional, Type
import importlib

SCHEMA_DIR = Path(__file__).parent / 'preprocess' / 'schemas'

def load_schema(schema_name: str) -> Type:
    """
    Dynamically import a schema module and return its schema class via get_schema().

    Args:
        schema_name (str): Name of the schema module (e.g., 'cv_schema').

    Returns:
        Type: The Pydantic schema class.
    """
    module_path = f"preprocess.schemas.{schema_name}"
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'get_schema'):
            return module.get_schema()
        else:
            raise ImportError(f"Schema module '{module_path}' does not have a get_schema() function.")
    except Exception as e:
        raise ImportError(f"Could not import schema '{schema_name}': {e}")

from preprocess.run_pipeline import run_extraction_pipeline


# Default configuration
DEFAULT_CONFIG = {
    "model": "gpt-4o-mini",
    "outputs_subdir": "outputs"
}

def setup_directories(outputs_dir: Union[str, Path]) -> Path:
    """
    Ensure output directories exist.

    Args:
        outputs_dir (Union[str, Path]): Path to the outputs directory.

    Returns:
        Path: The created/existing outputs directory as a Path object.
    """
    outputs_dir = Path(outputs_dir)
    os.makedirs(outputs_dir, exist_ok=True)
    return outputs_dir

async def extract_from_file_async(
    input_path: Union[str, Path],
    schema_name: str = 'cv_schema',
    output_dir: Optional[Path] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Async version of extract_from_file.
    Extract information from a file or directory of files.

    Args:
        input_path (Union[str, Path]): Path to input file or directory.
        schema_name (str): Name of the schema module to use.
        output_dir (Optional[Path]): Directory to write output to.
        **kwargs: Additional config options.

    Returns:
        Dict[str, Any]: Extraction results or error message.
    """
    from preprocess.run_pipeline import run_extraction_pipeline, run_sync_or_async
    config = DEFAULT_CONFIG.copy()
    config.update(kwargs)
    input_path = Path(input_path)
    if output_dir is None:
        base_dir = input_path if input_path.is_dir() else input_path.parent
        output_dir = setup_directories(base_dir / "outputs")
    else:
        output_dir = setup_directories(output_dir)
    output_file = (
        output_dir / f"{input_path.stem}.json"
        if input_path.is_file()
        else output_dir / "extracted_data.json"
    )
    if output_file.exists():
        output_file.unlink()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key is required (set in .env or environment variable)")
    try:
        schema_class = load_schema(schema_name)
        module_path = f"preprocess.schemas.{schema_name}"
        module = importlib.import_module(module_path)
        if hasattr(module, 'get_prompt'):
            extraction_prompt = module.get_prompt()
        else:
            raise ImportError(f"Schema module '{module_path}' does not have a get_prompt() function.")
        result = await run_extraction_pipeline(
            schema=schema_class,
            input_dir=str(input_path),
            output_file=str(output_file),
            openai_api_key=openai_api_key,
            extraction_template=extraction_prompt,
            model=config["model"]
        )
        return result
    except Exception as e:
        error_msg = str(e)
        return {"error": f"Failed to process {input_path.name}: {error_msg}"}

def extract_from_file(
    input_path: Union[str, Path],
    schema_name: str = 'cv_schema',
    output_dir: Optional[Path] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Sync wrapper for extract_from_file_async.
    Extract information from a file or directory of files.

    Args:
        input_path (Union[str, Path]): Path to input file or directory.
        schema_name (str): Name of the schema module to use.
        output_dir (Optional[Path]): Directory to write output to.
        **kwargs: Additional config options.

    Returns:
        Dict[str, Any]: Extraction results or error message.
    """
    from preprocess.run_pipeline import run_sync_or_async
    coro = extract_from_file_async(input_path, schema_name, output_dir, **kwargs)
    return run_sync_or_async(coro)

def main():
    """
    Command-line interface for the extraction script.
    """
    import argparse
    parser = argparse.ArgumentParser(description='Extract information from CVs')
    parser.add_argument('--input', '-i', required=True, help='Input file or directory containing CVs')
    parser.add_argument('--schema', default="cv_schema", help="Schema to use (e.g., cv_schema or invoice_schema)")
    args = parser.parse_args()
    if not Path(args.input).exists():
        return 1
    try:
        extract_from_file(input_path=args.input, schema_name=args.schema)
        return 0
    except Exception:
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
