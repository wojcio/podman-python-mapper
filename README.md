# DML Mapper - Data Mapping Language

A language and parser for describing data mappings between different formats (XML, EDI, DB, CSV).

## Quick Start

```bash
# Compile a mapping file to Python code
python3 src/simple_mapper.py input.map output.py

# Run the generated mapper
python3 output.py input.csv output.xml
```

## Mapping Language Syntax

The DML (Data Mapping Language) uses a simple block-based syntax:

```
MAPPING name {
    SOURCE TYPE { configuration }
    TARGET TYPE { configuration }
    RULES {
        map source_field -> target_field [TRANSFORM function] [IF condition]
    }
}
```

### Supported Types

- **CSV** - Comma-separated values files
- **XML** - Extensible Markup Language files  
- **DB** - Database (SQLite supported)
- **EDI** - Electronic Data Interchange files

### Configuration Options

#### SOURCE / TARGET for CSV
- `file`: Path to the file
- `has_header`: true/false (default: true)

#### SOURCE / TARGET for XML
- `file`: Path to the file
- `root_element`: Root element name for iteration

#### SOURCE / TARGET for DB
- `type`: Database type (e.g., "sqlite")
- `connection_string`: Connection string
- `query`: SQL query (for source) or `table`: Table name (for target)

#### SOURCE / TARGET for EDI
- `file`: Path to the file
- `version`: EDI version (e.g., "X12")

### Mapping Rules

Each rule maps a source field to a target field:

```
map CustomerID -> RecordCustomerID
```

Optional modifiers:
- `TRANSFORM function()` - Apply a transformation (upper, lower, trim, int, float)
- `AS type` - Cast to a specific type
- `IF condition` - Conditional mapping

## Examples

### CSV to XML

```dml
MAPPING csv_to_xml {
    SOURCE CSV { file: "input.csv", has_header: true }
    TARGET XML { file: "output.xml" }
    RULES {
        map id -> RecordID
        map name -> RecordName
        map price -> RecordPrice TRANSFORM float()
    }
}
```

### XML to CSV

```dml
MAPPING xml_to_csv {
    SOURCE XML { file: "input.xml", root_element: "Items" }
    TARGET CSV { file: "output.csv" }
    RULES {
        map RecordID -> id
        map RecordName -> name
    }
}
```

### CSV to Database (SQLite)

```dml
MAPPING csv_to_db {
    SOURCE CSV { file: "customers.csv" }
    TARGET DB { type: sqlite, connection_string: "data.db", table: "customers" }
    RULES {
        map id -> customer_id
        map name -> customer_name TRANSFORM upper()
    }
}
```

### Database to CSV

```dml
MAPPING db_to_csv {
    SOURCE DB { type: sqlite, connection_string: "data.db", query: "SELECT * FROM customers" }
    TARGET CSV { file: "output.csv" }
    RULES {
        map customer_id -> id
        map customer_name -> name
    }
}
```

### CSV to EDI

```dml
MAPPING csv_to_edi {
    SOURCE CSV { file: "orders.csv" }
    TARGET EDI { file: "output.edi", version: "X12" }
    RULES {
        map segment -> segment
        map data -> data
    }
}
```

## Advanced Features

### Transform Functions

- `upper()` - Convert to uppercase
- `lower()` - Convert to lowercase  
- `trim()` - Remove whitespace
- `int()` - Convert to integer
- `float()` - Convert to float

### Python API

```python
from src.simple_mapper import compile_mapping, SimpleMapper

# Option 1: Compile from file
compile_mapping("input.map", "output.py")

# Option 2: Parse and generate programmatically
mapper = SimpleMapper()
mapping = mapper.parse_mapping(dml_code)
code = mapper.generate_code(mapping)
```

## Usage

### From Python Code

```python
from src.simple_mapper import compile_mapping, SimpleMapper

# Option 1: Compile from file
compile_mapping("input.map", "output.py")

# Option 2: Parse and generate programmatically
mapper = SimpleMapper()
mapping = mapper.parse_mapping(dml_code)
code = mapper.generate_code(mapping)
```

### From Command Line

```bash
python src/simple_mapper.py input.map output.py
```

## Generated Python Code

The mapper generates a fully executable Python script with:
- Source data reading functions
- Target data writing functions  
- Transform utility functions
- Main execute_mapping function

The generated code can be run directly:

```bash
python generated_mapper.py input.csv output.xml
```

## Project Structure

```
podman-python-mapper/
├── src/
│   └── simple_mapper.py    # Main mapper implementation
├── tests/
│   ├── test_simple_mapper.py  # Unit tests
│   └── test_csv_xml.map       # Sample mapping file
├── README.md               # This documentation
└── mapping_language.md     # Full language specification
```

## Testing

```bash
python3 tests/test_simple_mapper.py