import os
from pathlib import Path

def save_file(file_path: str, content: str) -> None:
    """
    Save content to a file at the specified path.
    
    Args:
        file_path: Path to the file where content will be saved.
        content: Content to be written to the file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        raise IOError(f"Error saving file {file_path}: {e}")

def load_file(file_path: str) -> str:
    """
    Load content from a file at the specified path.
    
    Args:
        file_path: Path to the file to be loaded.
        
    Returns:
        Content of the file as a string.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise IOError(f"Error loading file {file_path}: {e}")

def delete_file(file_path: str) -> None:
    """
    Delete a file at the specified path.
    
    Args:
        file_path: Path to the file to be deleted.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise IOError(f"Error deleting file {file_path}: {e}")

def get_file_extension(file_path: str) -> str:
    """
    Get the file extension of a given file path.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        The file extension as a string.
    """
    return Path(file_path).suffix

def is_supported_file_type(file_path: str, supported_extensions: list) -> bool:
    """
    Check if the file type is supported based on its extension.
    
    Args:
        file_path: Path to the file.
        supported_extensions: List of supported file extensions.
        
    Returns:
        True if the file type is supported, False otherwise.
    """
    file_extension = get_file_extension(file_path)
    return file_extension in supported_extensions


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        File size in bytes.
    """
    return os.path.getsize(file_path)


def ensure_directory_exists(directory: Path) -> None:
    """
    Ensure a directory exists, create it if it doesn't.
    
    Args:
        directory: Path to the directory.
    """
    directory.mkdir(parents=True, exist_ok=True)


def generate_unique_filename(original_filename: str, target_language: str) -> str:
    """
    Generate a unique filename for translated documents.
    
    Args:
        original_filename: Original filename
        target_language: Target language code
        
    Returns:
        Unique filename with language suffix
    """
    path = Path(original_filename)
    stem = path.stem
    suffix = path.suffix
    return f"{stem}_{target_language}{suffix}"