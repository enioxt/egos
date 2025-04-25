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


# TODO: Set up proper logging (using KoiosLogger or standard logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
METADATA_TEMPLATE = """---
legacy_artifact: true
original_filename: "{original_filename}"
source_context: "{source_context}"
estimated_date: "{estimated_date}"
language: "{language}"
status: "processed"
tags: {tags}
---

"""

# Common content types for context detection
CONTENT_TYPES = {
    'chat': ['conversation with', 'chat with', 'asked', 'responded', 'user:', 'assistant:', 'ai:', 'human:'],
    'code': ['def ', 'class ', 'function', 'import ', 'from ', 'return ', 'if __name__'],
    'documentation': ['readme', 'documentation', 'guide', 'manual', 'tutorial', 'how to'],
    'research': ['research', 'analysis', 'study', 'investigation', 'findings', 'results', 'conclusion'],
    'design': ['design', 'architecture', 'structure', 'pattern', 'diagram', 'workflow', 'interface'],
    'meeting': ['meeting', 'discussion', 'call', 'conference', 'agenda', 'minutes', 'participants'],
    'roadmap': ['roadmap', 'plan', 'timeline', 'milestone', 'objective', 'goal', 'strategy'],
    'technical': ['technical', 'specification', 'protocol', 'algorithm', 'implementation', 'configuration'],
}

# Common topics for tag generation
COMMON_TOPICS = {
    'ethichain': ['ethichain', 'ethik chain', 'blockchain', 'ethereum', 'solidity', 'smart contract'],
    'rpg': ['rpg', 'game', 'character', 'quest', 'level', 'player', 'npc', 'dungeon'],
    'personas': ['persona', 'avatar', 'profile', 'character', 'identity', 'role', 'archetype'],
    'quantum': ['quantum', 'q-bit', 'superposition', 'entanglement', 'quantum search', 'quantum computing'],
    'mycelium': ['mycelium', 'network', 'node', 'connection', 'message', 'communication', 'protocol'],
    'dashboard': ['dashboard', 'visualization', 'chart', 'graph', 'metric', 'kpi', 'report', 'analytics'],
    'koios': ['koios', 'documentation', 'standard', 'guideline', 'process', 'template', 'format'],
    'cronos': ['cronos', 'time', 'history', 'timeline', 'version', 'backup', 'archive', 'preservation'],
    'ethik': ['ethik', 'ethics', 'moral', 'principle', 'value', 'guideline', 'standard', 'compliance'],
    'harmony': ['harmony', 'integration', 'compatibility', 'interoperability', 'cross-platform'],
    'nexus': ['nexus', 'connection', 'relationship', 'dependency', 'link', 'reference', 'association'],
    'atlas': ['atlas', 'map', 'navigation', 'guide', 'directory', 'index', 'catalog'],
    'coruja': ['coruja', 'monitoring', 'observation', 'alert', 'notification', 'detection'],
}

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

def infer_content_type(content: str) -> str:
    """
    Infers the content type based on text patterns.
    Returns the most likely content type based on keyword matches.
    """
    content_lower = content.lower()
    type_scores = {}
    
    for content_type, keywords in CONTENT_TYPES.items():
        score = sum(1 for keyword in keywords if keyword.lower() in content_lower)
        type_scores[content_type] = score
    
    # Get the content type with the highest score
    if type_scores:
        max_score = max(type_scores.values())
        if max_score > 0:  # Only if we have matches
            best_types = [t for t, s in type_scores.items() if s == max_score]
            return best_types[0].capitalize()  # Return the first highest scoring type
    
    return "Unknown"  # Default if no clear type is detected

def generate_tags(content: str, file_path: str) -> list:
    """
    Generates tags based on file content and path.
    Returns a list of relevant tags.
    """
    content_lower = content.lower()
    tags = ["legacy", "standardized_script"]  # Start with default tags
    
    # Add content type tag
    content_type = infer_content_type(content)
    if content_type != "Unknown":
        tags.append(content_type.lower())
    
    # Add topic-specific tags based on content
    for topic, keywords in COMMON_TOPICS.items():
        if any(keyword.lower() in content_lower for keyword in keywords):
            tags.append(topic)
    
    # Add path-based tags
    path_parts = file_path.lower().split(os.sep)
    for part in path_parts:
        if part and part not in ["c:", "egos", "strategic-thinking", "research", "chat", "history"]:
            # Clean up the part to make it a valid tag
            clean_part = part.replace(" ", "_").replace("-", "_")
            if clean_part not in tags and len(clean_part) > 3:  # Avoid short/meaningless tags
                tags.append(clean_part)
    
    return tags

def get_file_metadata(file_path: str, content: str) -> tuple[str, str, list]:
    """
    Extracts metadata from file system and content analysis.
    Returns estimated_date, source_context, and tags.
    """
    try:
        mod_timestamp = os.path.getmtime(file_path)
        estimated_date = datetime.fromtimestamp(mod_timestamp).strftime('%Y-%m-%d')
    except OSError:
        estimated_date = "unknown"

    # Infer context from path and content
    path_context = "Unknown"
    if "Chat history" in file_path:
        path_context = "Chat History"
    elif "research" in file_path:
        path_context = "Research Note"
    
    # Get content-based context
    content_context = infer_content_type(content)
    
    # Combine path and content context
    if path_context != "Unknown":
        if content_context != "Unknown":
            source_context = f"{path_context}: {content_context}"
        else:
            source_context = path_context
    else:
        source_context = content_context
    
    # Generate tags
    tags = generate_tags(content, file_path)
    
    return estimated_date, source_context, tags


def process_txt_file(txt_file_path: str, output_dir: str, organize_by_language: bool = False, overwrite: bool = False):
    """
    Processes a single .txt file: creates a corresponding .md file with metadata header in the output directory.
    If organize_by_language is True, files will be placed in subdirectories based on detected language.
    """
    try:
        logging.info(f"Processing file: {txt_file_path}")
        original_filename = os.path.basename(txt_file_path)
        base_name = os.path.splitext(original_filename)[0]
        md_filename = base_name + ".md"
        
        # Read original content
        with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f_in:
            original_content = f_in.read()

        # Detect language
        language = detect_language(original_content)

        # Get metadata with content-based analysis
        estimated_date, source_context, tags = get_file_metadata(txt_file_path, original_content)

        # Determine output directory (potentially language-specific)
        current_output_dir = output_dir
        if organize_by_language and language != 'unknown':
            # Create language-specific subdirectory
            current_output_dir = os.path.join(output_dir, language)
        
        # Ensure output directory exists
        os.makedirs(current_output_dir, exist_ok=True)
        
        # Full path for the new .md file
        md_file_path = os.path.join(current_output_dir, md_filename)

        # Check if file already exists
        if os.path.exists(md_file_path) and not overwrite:
            logging.warning(f"Skipping: Output file already exists: {md_file_path}")
            return False  # Indicate skipped

        # Format metadata header with proper tag formatting
        metadata_header = METADATA_TEMPLATE.format(
            original_filename=original_filename,
            source_context=source_context,
            estimated_date=estimated_date,
            language=language,
            tags=str(tags).replace("'", "\"")  # Format tags as JSON-compatible list
        )

        # Write new .md file
        with open(md_file_path, 'w', encoding='utf-8') as f_out:
            f_out.write(metadata_header)
            f_out.write(original_content)

        logging.info(f"Successfully created: {md_file_path}")
        # TODO: Optionally delete or move the original .txt file after successful processing
        return True  # Indicate success

    except Exception as e:
        logging.error(f"Failed to process file {txt_file_path}: {e}")
        return False  # Indicate failure

def find_and_process_files(input_dir: str, output_dir: str, recursive: bool = False, organize_by_language: bool = False, overwrite: bool = False):
    """
    Finds .txt files in the input directory and processes them.
    If organize_by_language is True, processed files will be organized into subdirectories by detected language.
    """
    logging.info(f"Starting scan in directory: {input_dir}")
    total_files = 0
    processed_count = 0
    failed_count = 0
    skipped_count = 0
    language_counts = {}

    if recursive:
        for root, _, files in os.walk(input_dir):
            for filename in files:
                if filename.lower().endswith(".txt"):
                    total_files += 1
                    file_path = os.path.join(root, filename)
                    
                    # Determine relative path for output structure preservation
                    relative_path = os.path.relpath(root, input_dir)
                    current_output_dir = os.path.join(output_dir, relative_path)
                    
                    # Process the file
                    result = process_txt_file(file_path, current_output_dir, organize_by_language, overwrite)
                    
                    # Track results
                    if result is True:
                        processed_count += 1
                        # Note: We can't easily track language counts here since processing happens in process_txt_file
                    elif result is False:
                        # Check if it was skipped due to existing file
                        md_filename = os.path.splitext(filename)[0] + '.md'
                        if organize_by_language:
                            # Check in potential language subdirectories
                            skipped = False
                            for lang_dir in ['en', 'pt', 'mixed-pt-en', 'mixed-en-pt', 'mixed', 'unknown']:
                                lang_path = os.path.join(current_output_dir, lang_dir, md_filename)
                                if os.path.exists(lang_path):
                                    skipped_count += 1
                                    skipped = True
                                    break
                            if not skipped:
                                failed_count += 1
                        else:
                            # Standard path check
                            if os.path.exists(os.path.join(current_output_dir, md_filename)):
                                skipped_count += 1
                            else:
                                failed_count += 1
    else:
        for filename in os.listdir(input_dir):
            if filename.lower().endswith(".txt"):
                total_files += 1
                file_path = os.path.join(input_dir, filename)
                if os.path.isfile(file_path):
                    # Process the file
                    result = process_txt_file(file_path, output_dir, organize_by_language, overwrite)
                    
                    # Track results
                    if result is True:
                        processed_count += 1
                    elif result is False:
                        # Check if it was skipped due to existing file
                        md_filename = os.path.splitext(filename)[0] + '.md'
                        if organize_by_language:
                            # Check in potential language subdirectories
                            skipped = False
                            for lang_dir in ['en', 'pt', 'mixed-pt-en', 'mixed-en-pt', 'mixed', 'unknown']:
                                lang_path = os.path.join(output_dir, lang_dir, md_filename)
                                if os.path.exists(lang_path):
                                    skipped_count += 1
                                    skipped = True
                                    break
                            if not skipped:
                                failed_count += 1
                        else:
                            # Standard path check
                            if os.path.exists(os.path.join(output_dir, md_filename)):
                                skipped_count += 1
                            else:
                                failed_count += 1

    # Count files by language if organized by language
    if organize_by_language and os.path.exists(output_dir):
        for lang_dir in os.listdir(output_dir):
            lang_path = os.path.join(output_dir, lang_dir)
            if os.path.isdir(lang_path):
                lang_count = len([f for f in os.listdir(lang_path) if f.endswith('.md')])
                language_counts[lang_dir] = lang_count
                logging.info(f"Language '{lang_dir}': {lang_count} files")

    # Log summary
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
    parser.add_argument("--organize-by-language", action="store_true", help="Organize output files into subdirectories by detected language.")
    parser.add_argument("--source-context", help="Override the auto-detected source context with this value.")
    parser.add_argument("--default-language", help="Set a default language if detection fails.")
    parser.add_argument("--inventory", help="Path to write a markdown inventory of processed files.")

    args = parser.parse_args()

    # Basic validation
    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory not found: {args.input_dir}")
        exit(1)

    # Process files
    find_and_process_files(
        args.input_dir, 
        args.output_dir, 
        args.recursive, 
        args.organize_by_language, 
        args.overwrite
    )
    
    # Generate inventory file if requested
    if args.inventory:
        try:
            with open(args.inventory, 'w', encoding='utf-8') as f:
                f.write("# Legacy Files Inventory\n\n")
                f.write("| File | Language | Source Context | Tags |\n")
                f.write("| ---- | -------- | ------------- | ---- |\n")
                
                # Walk through the output directory
                for root, _, files in os.walk(args.output_dir):
                    for filename in sorted(files):
                        if filename.endswith('.md'):
                            file_path = os.path.join(root, filename)
                            rel_path = os.path.relpath(file_path, args.output_dir)
                            
                            # Extract metadata from the file
                            try:
                                with open(file_path, 'r', encoding='utf-8') as md_file:
                                    content = md_file.read(1000)  # Read first 1000 chars to get metadata
                                    
                                    # Extract basic metadata
                                    language = "unknown"
                                    source_context = "unknown"
                                    tags = []
                                    
                                    if "language:" in content:
                                        lang_line = [l for l in content.split('\n') if l.strip().startswith('language:')][0]
                                        language = lang_line.split(':', 1)[1].strip().strip('"')
                                    
                                    if "source_context:" in content:
                                        context_line = [l for l in content.split('\n') if l.strip().startswith('source_context:')][0]
                                        source_context = context_line.split(':', 1)[1].strip().strip('"')
                                    
                                    if "tags:" in content:
                                        tags_line = [l for l in content.split('\n') if l.strip().startswith('tags:')][0]
                                        tags_str = tags_line.split(':', 1)[1].strip()
                                        # Convert tags string to list for display
                                        tags = eval(tags_str)  # Safe since we're generating this ourselves
                                    
                                    # Write to inventory
                                    f.write(f"| [{rel_path}]({rel_path.replace(' ', '%20')}) | {language} | {source_context} | {', '.join(tags)} |\n")
                            except Exception as e:
                                logging.error(f"Error processing {file_path} for inventory: {e}")
                                f.write(f"| {rel_path} | Error | Error | Error |\n")
                
                logging.info(f"Inventory file created at {args.inventory}")
        except Exception as e:
            logging.error(f"Failed to create inventory file: {e}")

    print("Script finished.")
