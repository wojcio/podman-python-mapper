# DML Mapper - Data Mapping Language

A language and parser for describing data mappings between different formats (XML, EDI, DB, CSV).

## Quick Start

```bash
# Compile a mapping file to Python code
python3 src/mapper.py input.map output.py

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
- **JSON** - JSON format
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

Each rule maps a source field (or a component query result) to a target field:

```
map CustomerID -> RecordCustomerID
```

Optional modifiers:
- `TRANSFORM function()` - Apply a transformation (upper, lower, trim, int, float)
- `AS type` - Cast to a specific type
- `IF condition` - Conditional mapping

## Examples

### Intermediate Data Enrichment with COMPONENT and Multiple Sources

You can join data between multiple sources by defining aliases and using a `COMPONENT DB` block to execute an in-memory SQL query:

```dml
MAPPING enrich_mapping {
    # 1. Provide multiple sources with aliases
    SOURCE CSV AS main { file: "main_data.csv", has_header: true }
    SOURCE XML AS ref { file: "reference.xml", root_element: "Items" }

    # 2. Use a COMPONENT to hold data and apply an enrichment query
    COMPONENT DB { 
        schema: "id INTEGER, name TEXT, ref_id INTEGER",
        query: "SELECT main.id, main.name, ref.status FROM main LEFT JOIN ref ON main.ref_id = ref.id"
    }

    TARGET JSON { file: "output.json" }

    # 3. Rules map from the COMPONENT's query output to the TARGET
    RULES {
        map id -> target_id
        map name -> target_name
        map status -> target_status DEFAULT "unknown"
    }
}
```

> **Note**: For multiple sources, the generated mapper accepts arguments in pairs: `python mapper_out.py main main.csv ref reference.xml output.json`.

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
from src.mapper import compile_mapping, parse_dml_file, generate_python_code

# Option 1: Compile from file
compile_mapping("input.map", "output.py")

# Option 2: Parse and generate programmatically
mapping = parse_dml_file("input.map")
code = generate_python_code(mapping)
```

## Usage

### From Python Code

```python
from src.mapper import compile_mapping, parse_dml_file, generate_python_code

# Option 1: Compile from file
compile_mapping("input.map", "output.py")

# Option 2: Parse and generate programmatically
mapping = parse_dml_file("input.map")
code = generate_python_code(mapping)
```

### From Command Line

```bash
python src/mapper.py input.map output.py
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
│   └── mapper.py           # Main mapper implementation
├── tests/
│   ├── test_mapper.py         # Unit tests
│   └── test_csv_xml.map       # Sample mapping file
├── README.md               # This documentation
└── mapping_language.md     # Full language specification
```

## Testing

```bash
python3 tests/test_mapper.py


Have fun! Licence MIT 