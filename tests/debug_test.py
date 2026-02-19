"""Debug test for the mapper."""

import sys
sys.path.insert(0, '/Users/wojcio/Desktop/Devel/podman-python-mapper')

from src.mapper import Parser, CodeGenerator

dml_code = '''MAPPING test { SOURCE CSV { file: "in.csv" } TARGET XML { file: "out.xml" } RULES { map id -> Item/id } }'''

parser = Parser(dml_code)
mapping = parser.parse()
print(f'Parsed: {mapping.name}')

generator = CodeGenerator(mapping)
python_code = generator.generate()
print(f'Generated {len(python_code)} bytes')