from src.mapper import parse_dml_file, generate_python_code

dml = """
MAPPING csv_to_xml {
    SOURCE CSV { file: "input.csv", has_header: true }
    TARGET XML { file: "output.xml" }
    RULES {
        map id -> RecordID
        map name -> RecordName TRANSFORM upper()
        map price -> RecordPrice TRANSFORM float() AS float
    }
}
"""
import tempfile
with tempfile.NamedTemporaryFile("w", delete=False) as f:
    f.write(dml)
    f.close()
    
mapping = parse_dml_file(f.name)
print(generate_python_code(mapping))
