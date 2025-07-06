import streamlit as st
import os
import sys
import json
from pathlib import Path
import tempfile
import pandas as pd

# Add parent directory to path to import from extract.py
sys.path.append(str(Path(__file__).parent.parent))

# Import functions from the functions.py file
from functions import (
    load_available_schemas,
    process_uploaded_file,
    display_extraction_results,
    convert_to_dataframe,
    validate_api_key
)

# Set page configuration
st.set_page_config(
    page_title="Document Information Extractor",
    page_icon="📄",
    layout="wide"
)

def test_api_connection():
    """Test if the OpenAI API is accessible with the current key."""
    import asyncio
    import inspect
    
    try:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            return False, "No API key provided"
        
        # Try both old and new OpenAI client approaches
        try:
            # Try the newer OpenAI client (v1.0+)
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            # Try a simple API call
            try:
                response = client.models.list()
                return True, "API connection successful (OpenAI v1.0+)"
            except Exception as e:
                error_msg = str(e)
                if "403" in error_msg or "Forbidden" in error_msg:
                    return False, "Access denied (403): Check API key permissions"
                elif "401" in error_msg or "Unauthorized" in error_msg:
                    return False, "Unauthorized (401): Invalid API key"
                elif "quota" in error_msg.lower():
                    return False, "Quota exceeded: Check your OpenAI billing"
                elif "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
                    return False, f"Async error: {error_msg} - Try restarting the app"
                else:
                    return False, f"API error: {error_msg}"
                    
        except ImportError:
            # Fallback to older OpenAI client
            try:
                import openai
                openai.api_key = api_key
                
                # Handle both sync and async versions
                try:
                    if hasattr(openai.Model, 'list'):
                        if inspect.iscoroutinefunction(openai.Model.list):
                            # Async version
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                response = loop.run_until_complete(openai.Model.list())
                                return True, "API connection successful (async)"
                            finally:
                                loop.close()
                        else:
                            # Sync version
                            response = openai.Model.list()
                            return True, "API connection successful (sync)"
                    else:
                        return False, "OpenAI client method not found"
                except Exception as e:
                    error_msg = str(e)
                    if "403" in error_msg or "Forbidden" in error_msg:
                        return False, "Access denied (403): Check API key permissions"
                    elif "401" in error_msg or "Unauthorized" in error_msg:
                        return False, "Unauthorized (401): Invalid API key"
                    elif "quota" in error_msg.lower():
                        return False, "Quota exceeded: Check your OpenAI billing"
                    elif "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
                        return False, f"Async error: {error_msg} - Try restarting the app"
                    else:
                        return False, f"API error: {error_msg}"
                        
            except ImportError:
                return False, "OpenAI library not installed"
            
    except Exception as e:
        error_msg = str(e)
        if "event loop" in error_msg.lower() or "asyncio" in error_msg.lower():
            return False, f"Async execution error: {error_msg} - Try restarting the app"
        else:
            return False, f"Connection test failed: {error_msg}"

def main():
    # App title and description
    st.title("📄 Document Information Extractor")
    st.markdown(
        """
        Upload documents (Resumes, invoices, etc.).
        """
    )
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Load available schemas
        available_schemas = load_available_schemas()
        SCHEMA_DISPLAY_NAMES = {
            "invoice_schema": "Invoice",
            "cv_schema": "Resume",
            "bank_statement_schema": "Bank Statement",
            "utility_bill_schema": "Utility Bill",
            # Add more as needed
        }
        # Build display names list
        display_schema_names = [SCHEMA_DISPLAY_NAMES.get(s, s) for s in available_schemas]
        selected_display_schema = st.selectbox(
            "Select extraction schema",
            display_schema_names,
            index=0
        )
        # Map back to internal schema name for processing
        display_to_internal = {v: k for k, v in SCHEMA_DISPLAY_NAMES.items()}
        selected_schema = display_to_internal.get(selected_display_schema, selected_display_schema)
        
        # Model selection
        model_options = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
        selected_model = st.selectbox(
            "Select Model",
            model_options,
            index=0,
            help="Choose the OpenAI model for extraction"
        )

        # API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.environ.get("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key if not set in environment"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        # API Connection Test
        st.subheader("API Status")
        if st.button("Test API Connection"):
            with st.spinner("Testing API connection..."):
                success, message = test_api_connection()
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # Show current API key status
        if validate_api_key():
            st.success("✅ API key format looks valid")
        else:
            st.warning("⚠️ API key missing or invalid format")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Upload Documents")
        
        # Add file upload tips
        with st.expander("📋 File Upload Tips"):
            st.markdown("""
            - **Supported formats**: PDF, DOCX, DOC, TXT
            - **Maximum file size**: 10MB per file
            - **Ensure good quality**: Clear, readable documents work best
            """)
        
        uploaded_files = st.file_uploader(
            "Upload one or more documents",
            type=["pdf", "docx", "doc", "txt"],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            # Display file information
            st.subheader("Uploaded Files")
            for i, file in enumerate(uploaded_files):
                file_size = len(file.getvalue()) / (1024 * 1024)  # Size in MB
                st.write(f"**{i+1}.** {file.name} ({file_size:.1f}MB)")
            
            if st.button("Extract Information", type="primary"):
                if not os.environ.get("OPENAI_API_KEY"):
                    st.error("Please provide an OpenAI API key in the sidebar.")
                elif not validate_api_key():
                    st.error("Please provide a valid OpenAI API key in the sidebar.")
                else:
                    # Test API connection before processing
                    with st.spinner("Testing API connection..."):
                        api_success, api_message = test_api_connection()
                    
                    if not api_success:
                        st.error(f"API connection failed: {api_message}")
                        st.info("Please check your API key and try again.")
                    else:
                        with st.spinner("Processing documents..."):
                            progress_bar = st.progress(0)
                            results = []
                            for i, uploaded_file in enumerate(uploaded_files):
                                try:
                                    result = process_uploaded_file(
                                        uploaded_file,
                                        selected_schema,
                                        selected_model
                                    )
                                    if result:
                                        results.append(result)
                                except Exception as e:
                                    st.error(f"Error processing {uploaded_file.name}: {e}")
                                progress_bar.progress((i + 1) / len(uploaded_files))
                            st.success(f"Successfully processed {len(results)} out of {len(uploaded_files)} document(s)")
                            progress_bar.empty()
                            if results:
                                # Store results in session state for access across reruns
                                st.session_state.extraction_results = results

                                if len(results) < len(uploaded_files):
                                    st.warning(f"{len(uploaded_files) - len(results)} document(s) failed to process. Check the error messages above.")
                            else:
                                st.error("Failed to process any documents. Check the error messages above for details.")

                            
                                # Additional troubleshooting info
                                st.info("🔧 Troubleshooting suggestions:")
                                st.info("1. Check if your `extract_from_file` function is working correctly")
                                st.info("2. Verify that the required dependencies are installed")
                                st.info("3. Check if there are any import errors in your extraction module")
                                st.info("4. Try processing a single, smaller file first")
    
    with col2:
        st.header("Extracted Information")
        
        # Display results if available in session state
        if 'extraction_results' in st.session_state and st.session_state.extraction_results:
            results = st.session_state.extraction_results
            output_format = 'JSON'

            # Show only the first document's JSON output
            st.subheader("First Document Extracted (JSON)")
            st.json(results[0])
            
            # Export options
            st.subheader("Export Results")
            col_json, col_csv, col_excel = st.columns(3)

            with col_json:
                json_data = json.dumps(results, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="extracted_data.json",
                    mime="application/json"
                )
            with col_csv:
                import pandas as pd
                df = pd.DataFrame(results)
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="extracted_data.csv",
                    mime="text/csv"
                )
            with col_excel:
                import io
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='ExtractedData')
                st.download_button(
                    label="Download Excel",
                    data=output.getvalue(),
                    file_name="extracted_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

if __name__ == "__main__":
    main()