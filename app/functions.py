"""
functions.py: Streamlit utility functions for schema selection, file upload, validation, and result display in the extraction app.
"""
import os
import sys
import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import streamlit as st

# Add parent directory to path to import from extract.py
sys.path.append(str(Path(__file__).parent.parent))

from extract import extract_from_file, load_schema
from preprocess.schemas import cv_schema, invoice_schema  # Import available schemas

def load_available_schemas() -> List[str]:
    """
    Load available schema modules from the schemas directory.
    Returns a list of schema names (without the .py extension).
    """
    schemas_dir = Path(__file__).parent.parent / 'preprocess' / 'schemas'
    schemas = []
    
    for file_path in schemas_dir.glob('*.py'):
        if file_path.stem not in ['__init__', '__pycache__']:
            schemas.append(file_path.stem)
    
    return schemas

def validate_api_key(api_key: str) -> bool:
    """
    Validate that the OpenAI API key is present and properly formatted.
    Args:
        api_key (str): The API key to validate.
    Returns:
        bool: True if API key appears valid, False otherwise
    """
    if not api_key:
        return False
    # Basic validation - OpenAI API keys typically start with 'sk-'
    if not api_key.startswith('sk-'):
        st.warning("API key should start with 'sk-'. Please verify your OpenAI API key.")
        return False
    # Check minimum length (OpenAI keys are typically longer)
    if len(api_key) < 20:
        st.warning("API key appears to be too short. Please verify your OpenAI API key.")
        return False
    return True

def process_uploaded_file(
    uploaded_file,
    schema_name: str,
    model: str
) -> Optional[Dict[str, Any]]:
    """
    Process an uploaded file using the specified schema and model.
    Handles both synchronous and asynchronous extraction functions.
    
    Args:
        uploaded_file: The uploaded file from Streamlit
        schema_name: Name of the schema to use for extraction
        model: Name of the OpenAI model to use
        
    Returns:
        Dictionary containing the extracted information or None if processing failed
    """
    import asyncio
    import inspect
    import time
    
    try:
        # Validate API key before processing
        if not validate_api_key():
            st.error("Invalid or missing OpenAI API key. Please check your API key in the sidebar.")
            return None
        
        # Validate file size (optional - adjust limit as needed)
        file_size = len(uploaded_file.getvalue())
        max_size = 10 * 1024 * 1024  # 10MB limit
        if file_size > max_size:
            st.error(f"File {uploaded_file.name} is too large ({file_size / (1024*1024):.1f}MB). Maximum size is {max_size / (1024*1024)}MB.")
            return None
        
        # Create a temporary file to save the uploaded content
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            

        except Exception as temp_error:
            st.error(f"Failed to create temporary file: {temp_error}")
            return None
        
        # Verify the temporary file was created successfully
        if not os.path.exists(tmp_path):
            st.error(f"Failed to create temporary file for {uploaded_file.name}")
            return None
        
        # Add a small delay to ensure file is fully written
        time.sleep(0.1)
        
        try:
            # Determine if we're using async or sync function
            is_async = inspect.iscoroutinefunction(extract_from_file)
            
            # Create a wrapper function for async execution
            async def run_async_extraction():
                return await extract_from_file(
                    input_path=tmp_path,
                    schema_name=schema_name,
                    model=model
                )
            
            # Execute the appropriate function
            if is_async:
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run,
                            run_async_extraction()
                        )
                        result = future.result(timeout=120)
                else:
                    result = loop.run_until_complete(run_async_extraction())
            else:
                result = extract_from_file(
                    input_path=tmp_path,
                    schema_name=schema_name,
                    model=model
                )
            
            # We no longer add the original filename to the result
            # The file_name is now included in the metadata if needed
            return result
                
        except Exception as extract_error:
            # Handle specific extraction errors
            error_msg = str(extract_error)
            st.error(f"❌ Extraction failed: {error_msg}")
            
            import traceback
            st.error(f"📋 Full error traceback:")
            st.code(traceback.format_exc())
            
            if "403" in error_msg or "Forbidden" in error_msg:
                st.error(f"Authentication error: Please verify your OpenAI API key has the necessary permissions.")
            elif "401" in error_msg or "Unauthorized" in error_msg:
                st.error(f"Authentication failed: Please check your OpenAI API key.")
            elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                st.error(f"API quota exceeded: Please check your OpenAI account billing and usage limits.")
            elif "rate" in error_msg.lower() and "limit" in error_msg.lower():
                st.error(f"Rate limit exceeded: Please wait a moment and try again.")
            elif "timeout" in error_msg.lower():
                st.error(f"Request timeout: The file might be too large or complex. Try with a smaller file.")
            elif "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
                st.error(f"Async execution error: {error_msg}")
                st.info("This might be related to synchronous/asynchronous function handling. Try refreshing the page.")
            else:
                st.error(f"Error during extraction: {error_msg}")
            return None
        
        finally:
            # Clean up the temporary file
            try:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            except Exception as cleanup_error:
                st.error(f"⚠️ Failed to clean up temporary file: {cleanup_error}")
    
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Unexpected error: {error_msg}")
        
        # Log the full error for debugging
        import traceback
        st.error(f"📋 Full error traceback:")
        st.code(traceback.format_exc())
        
        if "403" in error_msg:
            st.error(f"Access denied (403) for {uploaded_file.name}: This usually indicates an API authentication issue. Please verify your OpenAI API key.")
        elif "401" in error_msg:
            st.error(f"Unauthorized (401) for {uploaded_file.name}: Please check your OpenAI API key.")
        elif "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
            st.error(f"Async execution error for {uploaded_file.name}: {error_msg}")

        else:
            st.error(f"Error processing {uploaded_file.name}: {error_msg}")
        return None

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested dictionary for easier conversion to DataFrame.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            # For lists of dictionaries, we'll join them with a delimiter
            # This is a simplification - in a real app you might handle this differently
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    flat_item = flatten_dict(item, f"{new_key}{sep}{i}", sep=sep)
                    items.extend(flat_item.items())
        else:
            items.append((new_key, v))
    return dict(items)

def convert_to_dataframe(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert extraction results to a pandas DataFrame.
    For complex nested structures, this is a simplified approach.
    """
    # For simple structures, we can directly convert to DataFrame
    try:
        return pd.DataFrame(results)
    except:
        # For more complex nested structures, try flattening first
        flattened_results = [flatten_dict(result) for result in results]
        return pd.DataFrame(flattened_results)

def display_extraction_results(results: List[Dict[str, Any]], output_format: str) -> None:
    """
    Display extraction results in the specified format.
    
    Args:
        results: List of dictionaries containing extraction results
        output_format: Format to display results in ('JSON' or 'Table')
    """
    if not results:
        st.info("No results to display")
        return
    
    # Display each result
    for i, result in enumerate(results):
        # Get file_name from metadata if available
        file_name = "Unknown"
        if result.get('metadata') and isinstance(result['metadata'], dict):
            file_name = result['metadata'].get('file_name', 'Unknown')
        st.subheader(f"Document {i+1}: {file_name}")
        
        if output_format == "JSON":
            # Display as formatted JSON
            st.json(result)
        else:
            # Display as table
            try:
                # For simple flat structures
                if not any(isinstance(v, (dict, list)) for v in result.values()):
                    st.table(pd.DataFrame([result]))
                else:
                    # For nested structures, we'll display each section separately
                    for key, value in result.items():
                        if isinstance(value, dict):
                            st.write(f"**{key}:**")
                            st.table(pd.DataFrame([value]))
                        elif isinstance(value, list) and value and isinstance(value[0], dict):
                            st.write(f"**{key}:**")
                            st.table(pd.DataFrame(value))
                        else:
                            st.write(f"**{key}:** {value}")
            except Exception as e:
                st.error(f"Could not display as table: {str(e)}")
                st.json(result)