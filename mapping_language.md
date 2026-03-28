# Data Mapping Language Specification

## Overview
A domain-specific language (DSL) for defining mappings between different data formats: XML, EDI, DB (databases), CSV.

## Basic Concepts

### Data Sources and Targets
- `SOURCE` - The input data format (XML, EDI, DB, CSV, JSON)
- `COMPONENT` - Optional intermediate data storage and enrichtment block (DB)
- `TARGET` - The output data format (XML, EDI, DB, CSV, JSON)

### Data Types
- `string` - Text data
- `integer` - Whole numbers
- `decimal` - Decimal numbers
- `boolean` - True/false values
- `datetime` - Date/time values

## Syntax

### Basic Structure
```
MAPPING name {
    SOURCE type [AS alias] {
        # Source configuration
    }
    
    [COMPONENT type {
        # Component configuration and enrichment query
    }]
    
    TARGET type {
        # Target configuration
    }
    
    RULES {
        # Mapping rules
    }
}
```

### Source/Target Configuration

#### XML
```
XML {
    file: "input.xml"
    root_element: "RootElement"
    namespace: "http://example.com/ns"
}
```

#### CSV
```
CSV {
    file: "input.csv"
    delimiter: ","
    has_header: true
}
```

#### DB (Database)
```
DB {
    type: "postgres" | "mysql" | "sqlite"
    connection_string: "host=localhost dbname=test"
    query: "SELECT * FROM table_name"
}
```

#### EDI
```
EDI {
    file: "input.edi"
    version: "X12" | "EDIFACT"
    segment_delimiter: "~"
}
```

#### JSON
```
JSON {
    file: "output.json"
}
```

### Intermediate Component

#### DB (In-Memory SQLite)
```
COMPONENT DB {
    schema: "id INTEGER, name TEXT, ref_id INTEGER"
    query: "SELECT main.id, main.name, ref.status FROM main LEFT JOIN ref ON main.ref_id = ref.id"
}
```

### Mapping Rules

#### Field-to-Field Mapping
```
map source_field -> target_field [AS type] [IF condition]
```

#### Value Transformations
```
map source_field -> target_field 
    TRANSFORM function_name(params)
```

#### Conditional Mapping
```
map source_field -> target_field 
    IF condition
```

#### Default Values
```
map null -> target_field 
    DEFAULT value
```

### Functions

#### String Functions
- `upper(value)` - Convert to uppercase
- `lower(value)` - Convert to lowercase
- `trim(value)` - Remove whitespace
- `concat(value, str1, ...)` - Concatenate strings
- `left(value, length)` - Extract from the left
- `right(value, length)` - Extract from the right
- `len(value)` - Get length of the string
- `substring(value, start, length)` - Extract substring
- `split(value, delimiter)` - Split string into list
- `join(list, delimiter)` - Join list into string
- `replace(value, old, new)` - Replace text

#### Numeric Functions
- `int(value)` - Convert to integer
- `float(value)` - Convert to float
- `abs(value)` - Absolute value
- `mod(value, divisor)` - Modulo operation
- `pow(value, exponent)` - Power operation
- `sqrt(value)` - Square root
- `format_number(value, format)` - Format number (e.g., "#,##0.00")
- `round(value, decimals)` - Round decimal

#### Date Functions
- `now()` - Current timestamp (ISO format)
- `today()` - Current date (ISO format)
- `format_date(value, format)` - Format date (e.g., "YYYY-MM-DD")
- `date_diff(value, date2)` - Difference in days
- `add_days(value, n)` - Add n days to date
- `add_months(value, n)` - Add n months to date
- `convert_timezone(value, from_tz, to_tz)` - Convert timezone

#### Window Functions
- `row_number()` - Sequential number of current record
- `rank()` - Rank of current record (currently same as row_number)

#### Conditional Functions
- `ifelse(condition_value, true_value, false_value)` - Inline conditional
- `coalesce(value, val1, val2, ...)` - First non-null value

#### Aggregation Functions (use in AGGREGATE block)
- `sum(field)` - Sum of field values in group
- `count(field)` - Number of records in group
- `avg(field)` - Average of field values in group
- `min(field)` - Minimum value in group
- `max(field)` - Maximum value in group

## Examples

### XML to CSV
```
MAPPING xml_to_csv {
    SOURCE XML {
        file: "orders.xml"
        root_element: "Orders"
    }
    
    TARGET CSV {
        file: "output.csv"
        delimiter: ","
    }
    
    RULES {
        map Order/OrderID -> order_id AS integer
        map Order/CustomerID -> customer_id AS string
        map Order/TotalAmount -> total_amount AS decimal
        map Order/OrderDate -> order_date 
            TRANSFORM format_date("YYYY-MM-DD")
    }
}
```

### CSV to XML
```
MAPPING csv_to_xml {
    SOURCE CSV {
        file: "data.csv"
        has_header: true
    }
    
    TARGET XML {
        file: "output.xml"
        root_element: "Records"
    }
    
    RULES {
        map CustomerID -> Record/CustomerID
        map Name -> Record/Name 
            TRANSFORM trim()
        map Amount -> Record/Amount 
            TRANSFORM format_number("#,##0.00")
    }
}
```

### Database to EDI
```
MAPPING db_to_edi {
    SOURCE DB {
        type: "postgres"
        connection_string: "host=localhost dbname=orders"
        query: "SELECT * FROM orders WHERE status = 'pending'"
    }
    
    TARGET EDI {
        file: "orders.edi"
        version: "X12"
    }
    
    RULES {
        map order_id -> N100/ID
        map customer_name -> N200/Name
        map order_total -> SL100/Total 
            TRANSFORM format_number("999999.99")
    }
}
```

### EDI to Database
```
MAPPING edi_to_db {
    SOURCE EDI {
        file: "input.edi"
        version: "X12"
    }
    
    TARGET DB {
        type: "mysql"
        connection_string: "host=localhost dbname=import"
        table: "orders"
        mode: "insert" | "update" | "upsert"
    }
    
    RULES {
        map 1000/OrderID -> order_id AS integer
        map 2000/CustomerName -> customer_name AS string
        map 3000/TotalAmount -> total_amount AS decimal
    }
}
```

### Data Enrichment with COMPONENT
```
MAPPING enrich_mapping {
    SOURCE CSV AS main {
        file: "main_data.csv"
        has_header: true
    }
    
    SOURCE XML AS ref {
        file: "reference.xml"
        root_element: "Items"
    }
    
    COMPONENT DB { 
        schema: "id INTEGER, name TEXT, ref_id INTEGER"
        query: "SELECT main.id, main.name, ref.status FROM main LEFT JOIN ref ON main.ref_id = ref.id"
    }
    
    TARGET JSON {
        file: "enriched_output.json"
    }
    
    RULES {
        map id -> target_id
        map name -> target_name
        map status -> target_status DEFAULT "unknown"
    }
}
```

### Complex Transformations
```
MAPPING complex_mapping {
    SOURCE CSV {
        file: "input.csv"
    }
    
    TARGET XML {
        file: "output.xml"
        root_element: "Data"
    }
    
    RULES {
        # Direct mapping
        map id -> Record/id
        
        # With transformation
        map name -> Record/name 
            TRANSFORM upper()
        
        # Conditional mapping
        map amount -> Record/status
            IF amount > 1000
                DEFAULT "premium"
            ELSE
                DEFAULT "standard"
        
        # Concatenation
        map first_name, last_name -> Record/full_name 
            TRANSFORM concat(" ")
        
        # Date formatting
        map created_date -> Record/created_formatted 
            TRANSFORM format_date("DD/MM/YYYY")
    }
}
```

## Advanced Features

### Looping for Collections
Iterate over collections with optional aliases and index access.
```dml
LOOP collection [AS item_alias] [INDEX index_alias] {
    # Loop body
    IF condition {
        BREAK
    }
    IF condition {
        CONTINUE
    }
    
    map item_alias/field -> target
    
    # Nested loops
    LOOP item_alias/sub_collection {
        ...
    }
}
```

### Conditional Blocks
```dml
IF condition {
    map field1 -> target1
    map field2 -> target2
} [ELSE {
    map field3 -> target3
}]
```

### Error Handling
```dml
TRY {
    # Rules that might fail (e.g., type casting)
    map amount -> Amount AS integer
} CATCH [AS error_var] {
    # Recovery rules
    map "0" -> Amount
}
```

### Multi-condition Dispatch
```dml
SWITCH source_field {
    CASE "value1": {
        map field1 -> target1
    }
    CASE "value2": {
        map field2 -> target2
    }
    DEFAULT: {
        map field3 -> target3
    }
}
```

### Data Aggregation
```dml
AGGREGATE {
    GROUP BY field1, field2, ...
    RULES {
        map source_field -> target_field TRANSFORM aggregation_function(source_field)
    }
}
```

### Data Cleansing
Automatically normalize input data fields.
```dml
CLEANSE {
    TRIM true | false,
    CASE "UPPER" | "LOWER"
}
```

### Data Validation
Filter records based on format or conditions.
```dml
VALIDATE field FORMAT "regex" [MESSAGE "error message"]
VALIDATE field condition [MESSAGE "error message"]
```

### Duplicate Detection
Ensure only unique records are processed.
```dml
DISTINCT
```

## Comments
```
# Single line comment
/* Multi-line 
   comment */
```

## File Extension
`.map` - Mapping definition files