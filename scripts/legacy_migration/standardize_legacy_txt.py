# scripts/legacy_migration/standardize_legacy_txt.py
import os
import argparse
import logging
from datetime import datetime

# Try to import langdetect, but don't fail if it's not available
try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
    logging.info("Using langdetect library for language detection")
except ImportError:
    LANGDETECT_AVAILABLE = False
    logging.warning("langdetect library not available, falling back to heuristic detection")

# from egos.utils.logging import KoiosLogger # Assuming logger setup exists

# TODO: Set up proper logging (using KoiosLogger or standard logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
METADATA_TEMPLATE = """---
legacy_artifact: true
original_filename: "{original_filename}"
source_context: "{source_context}" # Placeholder - needs better inference or input
estimated_date: "{estimated_date}" # Placeholder - needs better inference or input
language: "{language}" # Placeholder - needs detection implementation
status: "processed" # Initial status after this script runs
tags: ["legacy", "standardized_script"] # Basic tags
---

"""

# --- Helper Functions ---

def detect_language(content: str) -> str:
    """
    Detects the language of the given text content.
    Uses langdetect if available, otherwise falls back to heuristic approach.
    Returns the ISO 639-1 language code (e.g., 'en', 'pt') or 'unknown'.
    """
    # If content is empty, return unknown
    if not content.strip():
        return 'unknown'
        
    # Try using langdetect if available
    if LANGDETECT_AVAILABLE:
        try:
            # Reduce content size for efficiency if very large
            content_snippet = content[:5000]  # Use first 5000 chars for detection
            lang = detect(content_snippet)
            
            # Basic check for mixed content (heuristic - refine as needed)
            if lang == 'en' and ('sistema' in content.lower() or 'projeto' in content.lower() or 'atenção' in content.lower()):
                if 'import ' in content or 'def ' in content or 'class ' in content:
                    return 'mixed-en-pt'  # More specific mixed type
            elif lang == 'pt' and ('import ' in content or 'def ' in content or 'class ' in content):
                return 'mixed-pt-en'
                
            return lang
        except (LangDetectException, Exception) as e:
            logging.warning(f"Language detection with langdetect failed: {e}, falling back to heuristic")
            # Fall through to heuristic method
    
    # Heuristic-based detection (fallback method)
    # Check for Portuguese indicators
    pt_indicators = ['sistema', 'projeto', 'atenção', 'definição', 'código', 'função', 
                    'arquivo', 'diretório', 'configuração', 'execução', 'maravilhoso']
    pt_count = sum(1 for word in pt_indicators if word in content.lower())
    
    # Check for English indicators
    en_indicators = ['system', 'project', 'attention', 'definition', 'code', 'function',
                    'file', 'directory', 'configuration', 'execution', 'wonderful']
    en_count = sum(1 for word in en_indicators if word in content.lower())
    
    # Check for code indicators
    code_indicators = ['import ', 'def ', 'class ', 'function', 'return', 'if ', 'for ', 'while ']
    has_code = any(indicator in content for indicator in code_indicators)
    
    # Determine language based on counts
    if pt_count > en_count:
        return 'mixed-pt-en' if has_code else 'pt'
    elif en_count > pt_count:
        return 'mixed-en-pt' if has_code else 'en'
    elif has_code:  # Equal counts but has code
        return 'mixed'
    else:
        return 'unknown'  # Can't determine

def get_file_metadata(file_path: str) -> tuple[str, str]:
    """
    Attempts to extract basic metadata like estimated date from file system.
    """
    try:
        mod_timestamp = os.path.getmtime(file_path)
        estimated_date = datetime.fromtimestamp(mod_timestamp).strftime('%Y-%m-%d')
    except OSError:
        estimated_date = "unknown"

    # Infer context from path (very basic)
    source_context = "Unknown"
    if "Chat history" in file_path:
        source_context = "Chat History"
    elif "research" in file_path:
        source_context = "Research Note"

    return estimated_date, source_context


def process_txt_file(txt_file_path: str, output_dir: str, overwrite: bool = False):
    """
    Processes a single .txt file: creates a corresponding .md file with metadata header in the output directory.
    """
    try:
        logging.info(f"Processing file: {txt_file_path}")
        original_filename = os.path.basename(txt_file_path)
        base_name = os.path.splitext(original_filename)[0]
        md_filename = base_name + ".md"
        md_file_path = os.path.join(output_dir, md_filename)

        if os.path.exists(md_file_path) and not overwrite:
            logging.warning(f"Skipping: Output file already exists: {md_file_path}")
            return False # Indicate skipped

        # Read original content
        with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f_in:
            original_content = f_in.read()

        # Detect language (placeholder)
        language = detect_language(original_content)

        # Get other metadata
        estimated_date, source_context = get_file_metadata(txt_file_path)

        # Format metadata header
        metadata_header = METADATA_TEMPLATE.format(
            original_filename=original_filename,
            source_context=source_context,
            estimated_date=estimated_date,
            language=language,
        )

        # Write new .md file
        os.makedirs(output_dir, exist_ok=True) # Ensure output dir exists
        with open(md_file_path, 'w', encoding='utf-8') as f_out:
            f_out.write(metadata_header)
            f_out.write(original_content)

        logging.info(f"Successfully created: {md_file_path}")
        # TODO: Optionally delete or move the original .txt file after successful processing
        return True # Indicate success

    except Exception as e:
        logging.error(f"Failed to process file {txt_file_path}: {e}")
        return False # Indicate failure

def find_and_process_files(input_dir: str, output_dir: str, recursive: bool = False, overwrite: bool = False):
    """
    Finds .txt files in the input directory and processes them.
    """
    logging.info(f"Starting scan in directory: {input_dir}")
    total_files = 0
    processed_count = 0
    failed_count = 0
    skipped_count = 0

    if recursive:
        for root, _, files in os.walk(input_dir):
            for filename in files:
                if filename.lower().endswith(".txt"):
                    total_files += 1
                    file_path = os.path.join(root, filename)
                    # Determine relative path for output structure preservation
                    relative_path = os.path.relpath(root, input_dir)
                    current_output_dir = os.path.join(output_dir, relative_path)
                    if not os.path.exists(current_output_dir):
                       os.makedirs(current_output_dir, exist_ok=True)
                    
                    result = process_txt_file(file_path, current_output_dir, overwrite)
                    if result is True:
                        processed_count += 1
                    elif result is False and os.path.exists(os.path.join(current_output_dir, os.path.splitext(filename)[0] + '.md')):
                        skipped_count +=1 # Assumes False means skipped due to existing file if it exists
                    elif result is False:
                        failed_count += 1
                        
    else:
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(".txt"):
                 total_files += 1
                 file_path = os.path.join(input_dir, filename)
                 if os.path.isfile(file_path):
                     result = process_txt_file(file_path, output_dir, overwrite)
                     if result is True:
                         processed_count += 1
                     elif result is False and os.path.exists(os.path.join(output_dir, os.path.splitext(filename)[0] + '.md')):
                         skipped_count +=1 # Assumes False means skipped due to existing file if it exists
                     elif result is False:
                        failed_count += 1

    logging.info(f"Scan complete. Found {total_files} .txt files.")
    logging.info(f"Successfully processed: {processed_count}")
    logging.info(f"Skipped (already exist): {skipped_count}")
    logging.info(f"Failed: {failed_count}")


# --- Main Execution ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standardize legacy .txt files to .md with metadata.")
    parser.add_argument("input_dir", help="Directory containing legacy .txt files.")
    parser.add_argument("output_dir", help="Directory where processed .md files will be saved.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Scan input directory recursively.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing .md files in the output directory.")
    # TODO: Add argument for specifying source_context if auto-detection is insufficient
    # TODO: Add argument for explicitly setting language if needed

    args = parser.parse_args()

    # Basic validation
    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory not found: {args.input_dir}")
        exit(1)

    find_and_process_files(args.input_dir, args.output_dir, args.recursive, args.overwrite)

    print("Script finished.")
