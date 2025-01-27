import os

def lines_of_code(file_path, extensions=None, exclude_dirs=None):
    if extensions is None:
        extensions = ['py', 'js', 'html', 'css', 'scss', 'md', 'txt']
    
    if exclude_dirs is None:
        exclude_dirs = {
            'node_modules',
            '/templates',  # Adding leading slash to match only root-level templates
            'db_backups',
            'media',
            'migrations',
        }
    
    total_lines = 0
    
    for root, dirs, files in os.walk(file_path):
        # Get the relative path from the project root
        rel_path = os.path.relpath(root, file_path)
        
        # Remove excluded directories from dirs list to prevent walking into them
        dirs[:] = [d for d in dirs if not any(
            # Check if the full relative path + directory matches any exclude pattern
            (ex.startswith('/') and (rel_path == '.' and d == ex[1:])) or  # Root-level check
            (not ex.startswith('/') and ex in os.path.join(rel_path, d))  # Path-based check
            for ex in exclude_dirs
        )]
        
        for file in files:
            if any(file.endswith(f'.{ext}') for ext in extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = sum(1 for line in f if line.strip())
                        total_lines += lines
                except (IOError, UnicodeDecodeError):
                    continue
    
    return total_lines

if __name__ == "__main__":
    # Get the project root directory (3 levels up from this file)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    count = lines_of_code(project_root)
    print(f"Total lines of code in MMP (excluding node_modules, templates, db_backups, media, and migrations): {count:,} lines")
