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
- `IF condition` - Conditional mapping for a single rule
- `DEFAULT value` - Default value if source field is missing or null

### Control Flow Blocks

You can group multiple rules under control flow constructs:

#### Conditional Blocks (IF/ELSE)
```dml
IF amount > 1000 {
    map status -> Record/Status DEFAULT "Premium"
    map "High Value" -> Record/Priority
} ELSE {
    map status -> Record/Status DEFAULT "Standard"
    map "Normal" -> Record/Priority
}
```

#### Error Handling (TRY/CATCH)
```dml
TRY {
    map price -> Record/Price AS decimal
} CATCH AS err {
    map "0.0" -> Record/Price
    # err variable available in catch block for custom logic
}
```

#### Multi-condition Dispatch (SWITCH/CASE)
```dml
SWITCH category {
    CASE "electronics": {
        map id -> Item/E_ID
    }
    CASE "books": {
        map id -> Item/B_ID
    }
    DEFAULT: {
        map id -> Item/GEN_ID
    }
}
```

### Control Flow Blocks
...
```

### Variables and Macros

#### User-defined Variables
Define reusable values or constants:
```dml
VAR threshold = 100
CONST API_URL = "https://api.example.com"
```

#### Macros
Define reusable snippets of mapping rules:
```dml
MACRO standard_id(src, tgt) {
    map src -> tgt TRANSFORM trim()
}

RULES {
    standard_id(item_id, RecordID)
}
```

#### File Inclusion
Split mapping into multiple files:
```dml
INCLUDE "common_rules.map"
```

### Loops and Iteration

Process collections and nested data with advanced loop control:

```dml
LOOP items AS line_item INDEX idx {
    IF idx > 100 {
        BREAK
    }
    
    IF line_item/status == "cancelled" {
        CONTINUE
    }
    
    map line_item/id -> Order/ItemID
    
    # Nested loops
    LOOP line_item/details AS detail {
        map detail/info -> Order/ItemDetail
    }
}
```

### Data Quality and Validation

Maintain high data quality with built-in cleansing and validation:

#### Data Cleansing
Automatically normalize data before mapping:
```dml
CLEANSE {
    TRIM true,
    CASE "UPPER"  # or "LOWER"
}
```

#### Data Validation
Filter out invalid records:
```dml
VALIDATE email FORMAT "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$" MESSAGE "Invalid email format"
VALIDATE amount amount > 0 MESSAGE "Amount must be positive"
```

#### Duplicate Detection
Ensure output contains only unique records:
```dml
DISTINCT
```

### Data Aggregation

You can group records and calculate summary values:

```dml
MAPPING agg_test {
    SOURCE CSV { file: "sales.csv" }
    TARGET CSV { file: "summary.csv" }
    AGGREGATE {
        GROUP BY region, category
        RULES {
            map amount -> total_sales TRANSFORM sum(amount)
            map amount -> average_sale TRANSFORM avg(amount)
            map id -> transaction_count TRANSFORM count(id)
        }
    }
}
```

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

#### String Functions
- `upper()` - Convert to uppercase
- `lower()` - Convert to lowercase  
- `trim()` - Remove whitespace
- `concat(str1, str2, ...)` - Concatenate strings
- `left(length)`, `right(length)` - Extract from edges
- `len()` - Get string length
- `substring(start, length)` - Extract part of string
- `split(delimiter)` - Split string into list
- `join(delimiter)` - Join list into string

#### Numeric Functions
- `int()` - Convert to integer
- `float()` - Convert to float
- `abs()` - Absolute value
- `mod(divisor)` - Modulo operation
- `pow(exponent)` - Power operation
- `sqrt()` - Square root
- `format_number(format)` - Format number (e.g., "#,##0.00")

#### Date Functions
- `now()` - Current timestamp
- `today()` - Current date
- `format_date(format)` - Format date (e.g., "YYYY-MM-DD")
- `date_diff(date2)` - Difference in days
- `add_days(n)`, `add_months(n)` - Date arithmetic

#### Window Functions
- `row_number()` - Sequential number for each record
- `rank()` - Rank of each record (currently same as row_number)

#### Conditional Functions
- `ifelse(true_val, false_val)` - Inline conditional based on source value
- `coalesce(val1, val2, ...)` - First non-null value

#### File Operations
- `read_file(path)` - Read external file content
- `write_file(path)` - Write current value to file
- `append_file(path)` - Append current value to file

#### External References
- `lookup(key, table_path, key_col, val_col)` - Lookup value in external CSV/JSON
- `api_get(url, params_json)` - Fetch data from an external API
- `env(var_name, default)` - Access environment variables

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