from typing import Any, Dict, List
from collections import defaultdict
from preprocess.schemas.cv_schema import DocumentSchema, Experience

def postprocess_extracted_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Postprocess the extracted data: clean and enrich.
    - Filters out None values (but keeps empty lists/dicts)
    """
    filtered_data = {k: v for k, v in data.items() if v is not None}
    return filtered_data


def merge_documents(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge a list of extracted CV result dicts into a single dict.
    - Lists (like professional_experience, education, skills, etc.) are concatenated and deduplicated.
    - Scalar fields (name, email, summary, etc.) use the first non-null value found.
    - Collects all unique sources and pages as top-level lists: 'sources', 'pages'.
    - If only one result is given, returns it unchanged.
    """
    if not results:
        return {}
    if len(results) == 1:
        return results[0]

    merged: Dict[str, Any] = {}
    list_fields = [
        'professional_experience', 'education', 'skills', 'languages', 'certifications', 'profiles'
    ]
    seen = defaultdict(set)

    # Merge list fields
    for field in list_fields:
        merged[field] = []
        for r in results:
            items = r.get(field, [])
            if items:
                for item in items:
                    # Use tuple for hashable deduplication
                    t = tuple(sorted(item.items())) if isinstance(item, dict) else item
                    if t not in seen[field]:
                        seen[field].add(t)
                        merged[field].append(item)

    # Merge scalar fields: take the first non-null, non-empty value
    scalar_fields = [
        'name', 'summary', 'email', 'phone', 'location', 'years_experience', 'current_position', 'current_company'
    ]
    for field in scalar_fields:
        for r in results:
            val = r.get(field)
            if val not in (None, '', [], {}):
                merged[field] = val
                break

    # Remove source and file_name fields if present
    merged.pop('source', None)
    merged.pop('file_name', None)
    # Remove 'page' if present in merged output (top-level)
    merged.pop('page', None)
    # Also remove 'page' from any nested structures if necessary (defensive, but usually not needed)
    # Do NOT include 'sources' or 'pages' in merged output
    return merged


def save_postprocessed_results(merged_result, output_file, raw_output_file=None):
    """
    Save the merged postprocessed result to a file and print a completion message.
    Optionally, also print the location of the raw output file.
    """
    import json
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_result, f, indent=2, ensure_ascii=False)


def run_postprocessing(raw_output_file, postprocessed_file):
    """
    Complete postprocessing pipeline: load, process, merge, save, and print.
    """
    import json
    results = []
    import os
    # Handle empty file gracefully
    if os.path.getsize(raw_output_file) == 0:
        results = []
    else:
        with open(raw_output_file, "r", encoding="utf-8") as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = []
    processed_results = [postprocess_extracted_data(r) for r in results]
    merged_result = merge_documents(processed_results)
    save_postprocessed_results(merged_result, postprocessed_file, raw_output_file=raw_output_file)
