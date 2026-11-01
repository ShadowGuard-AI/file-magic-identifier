import argparse
import logging
import magic
import os
import pathlib
import sys


# Set up logging
# magic is imported unguarded at the top of this file. Without
# python-magic this tool does not start at all, not even to print help,
# because there is no fallback identifier behind it.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command line interface.
    """
    parser = argparse.ArgumentParser(description="Identifies file type based on magic numbers.")
    parser.add_argument("file_path", help="Path to the file to identify.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    return parser

def identify_file_type(file_path):
    """
    Identifies the file type using magic numbers.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: A description of the file type, or None if an error occurs.
    """
    try:
        # Check if the file exists
        if not pathlib.Path(file_path).exists():
            logging.error(f"File not found: {file_path}")
            return None

        # Use python-magic to identify the file type
        mime = magic.Magic(mime=True)
        # The file is identified twice, once through a Magic instance for the
        # MIME type and once through the module function for the long
        # description. libmagic reads the file both times; the two answers come
        # from the same database, so they cannot disagree in kind.
        mime_type = mime.from_file(file_path)

        file_info = magic.from_file(file_path)

        return f"MIME Type: {mime_type}, File Info: {file_info}"

    except magic.MagicException as e:
        logging.error(f"Error identifying file type: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None

def main():
    """
    Main function to parse arguments and identify the file type.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    # Configure logging verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose logging enabled.")

    file_path = args.file_path

    # Input Validation: Check if file_path is a valid path
    # Constructing a Path cannot fail for an odd string, so this try block
    # validates nothing in practice. The real existence check lives inside
    # identify_file_type, and the empty string check below is the only part
    # of this validation that can actually fire.
    try:
        pathlib.Path(file_path)
    except OSError:
        logging.error("Invalid file path.")
        sys.exit(1)

    # Ensure the file path is not empty after potential normalization
    if not file_path:
        logging.error("File path cannot be empty.")
        sys.exit(1)

    # Call the function to identify the file type
    file_type = identify_file_type(file_path)

    # None is the only failure signal, and it merges file not found with
    # libmagic failing. Both exit 1 with the reason in the log.
    if file_type:
        print(f"File type: {file_type}")
    else:
        sys.exit(1) # Exit with an error code if file type identification failed

# Example Usage (can be added in a docstring or separate example file)
# To run: python main.py <file_path> [-v]
# Example: python main.py /path/to/my/file.txt
# Example with verbose logging: python main.py /path/to/my/file.txt -v

if __name__ == "__main__":
    main()