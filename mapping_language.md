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
- `substring(value, start, length)` - Extract substring
- `trim(value)` - Remove whitespace
- `replace(value, old, new)` - Replace text

#### Numeric Functions
- `format_number(value, format)` - Format number
- `round(value, decimals)` - Round decimal

#### Date Functions
- `format_date(value, format)` - Format date
- `convert_timezone(value, from_tz, to_tz)` - Convert timezone

#### Conditional Functions
- `ifelse(condition, true_value, false_value)` - If-then-else

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
```
loop source_collection {
    map item -> target_item
    
    sub_rules {
        # Nested rules for each item
        map id -> Item/id
        map name -> Item/name
    }
}
```

### Conditional Blocks
```
IF condition {
    map field1 -> target1
    map field2 -> target2
} ELSE {
    map field3 -> target3
}
```

### Aggregations
```
AGGREGATE {
    source_field AS target_field
    FUNCTION sum | avg | count | min | max
}
```

## Comments
```
# Single line comment
/* Multi-line 
   comment */
```

## File Extension
`.map` - Mapping definition files