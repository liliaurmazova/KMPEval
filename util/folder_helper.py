import os
import shutil

def ensure_directory_exists(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def find_relevant_files_in_codebase(codebase_path):
    """Reading all relevant source code files from the codebase, ignoring binary and unnecessary files."""

    # 1. Recursively read all files, ignoring unnecessary ones
    all_source_code = []

    # Lists for ignoring "garbage"
    ignored_dirs = {'build', '.gradle', '.idea', 'gradle'}
    ignored_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.jar', '.zip', '.bin'}

    print(f"🔎 Looking for all relevant files in {codebase_path}...")

    for root, dirs, files in os.walk(codebase_path):
        # Exclude service folders from further traversal
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        
        for file in files:
            # Check file extension
            if any(file.endswith(ext) for ext in ignored_extensions):
                continue # Skip binary/unnecessary files

            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, codebase_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    all_source_code.append(f"// --- FILE: {relative_path.replace(os.sep, '/')} ---\n\n{content}")
            except UnicodeDecodeError:
                # If the file could not be read as text, skip it
                print(f"  ⚠️ Skipped binary or non-text file: {relative_path}")
                continue

    if not all_source_code:
        print(f"❌ Error: No text files found in {codebase_path}")
        return None, None

    print(f"✅ Found {len(all_source_code)} relevant file(s).")
    
    return "\n\n".join(all_source_code)
    