import xml.etree.ElementTree as ET
import sys

def validate_diagram_xml():
    """
    Validates the 'diagram.xml' file to ensure it is well-formed XML.
    If parsing fails, it prints a detailed error message, including the
    line number and the content of the problematic line.
    """
    filepath = 'diagram.xml'
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        ET.fromstring(xml_content)
        
        print(f"Validation successful: '{filepath}' is well-formed XML.")
        
    except ET.ParseError as e:
        print(f"--- XML Validation Failed ---", file=sys.stderr)
        print(f"An error was found in '{filepath}'.", file=sys.stderr)
        print(f"Error message: {e.msg}", file=sys.stderr)
        print(f"Line number:   {e.lineno}", file=sys.stderr)
        print(f"Column number: {e.position}", file=sys.stderr)
        
        # To provide more context, read and display the problematic line
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if 0 < e.lineno <= len(lines):
                    problematic_line = lines[e.lineno - 1].strip()
                    print(f"Problematic line content: > {problematic_line}", file=sys.stderr)
        except Exception as read_error:
            print(f"(Could not read the specific line from the file: {read_error})", file=sys.stderr)
            
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.", file=sys.stderr)
        
    except Exception as e:
        print(f"An unexpected error occurred during validation: {e}", file=sys.stderr)

if __name__ == "__main__":
    validate_diagram_xml()
