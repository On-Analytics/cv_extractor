# Document Information Extractor App

This Streamlit application provides a user-friendly web interface for the Document Information Extractor. It allows you to upload various document types (CVs, invoices, etc.) and extract structured information using different schemas.

## Features

- Upload multiple documents (PDF, DOCX, TXT)
- Select from available extraction schemas
- Choose OpenAI model for extraction
- Display results in JSON or table format
- Export results as JSON or CSV
- Configure OpenAI API key through the interface

## Running the App

1. Make sure you have installed all dependencies:
   ```
   pip install -r ../requirements.txt
   ```

2. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

3. The app will open in your default web browser at http://localhost:8501

## Usage Instructions

1. Select the appropriate schema for your document type in the sidebar
2. Choose the OpenAI model you want to use
3. Enter your OpenAI API key if not already set in environment variables
4. Upload one or more documents
5. Click "Extract Information" to process the documents
6. View the extracted information in your preferred format (JSON or Table)
7. Download the results as JSON or CSV if needed
