# Data Mapping Language - Feature Analysis & Enhancement Recommendations (v2)

## Executive Summary

This document provides a comprehensive analysis of the current Data Mapping Language (DSL) implementation and identifies features that should be added to make it production-ready for enterprise data integration scenarios.

## Current State Analysis

### Implemented Features (Working)

#### Core DSL Structure
- **Mapping Definition**: `MAPPING name { ... }` block structure ✓
- **Source Configuration**: CSV, XML, DB (SQLite), EDI, JSON support ✓
- **Target Configuration**: CSV, XML, DB (SQLite), EDI, JSON support ✓
- **Rules Block**: `RULES { ... }` for mapping definitions ✓

#### Basic Mapping Rules
- **Basic Field Mapping**: `map source -> target` ✓
- **Transformations**: `TRANSFORM function()` (upper, lower, trim) ✓
- **Type Casting**: `AS type` (integer, string, decimal, float, boolean) ✓
- **Conditional Mapping**: `IF condition` with optional `DEFAULT value` ✓

#### Advanced Features (Partially Implemented)
- **Multiple Sources**: With aliases (SOURCE AS alias) ✓
- **Component/Enrichment**: In-memory DB with SQL JOIN support ✓
- **Loop Constructs**: `loop` keyword for collection iteration ✓

### Critical Bugs Found

#### 1. Code Generator Bug (mapper.py:692)
**Issue**: `component_config = self.mapping.get('component', {}).get('config', {})` fails when `self.mapping` is None
**Impact**: Code generation fails for any mapping without a component block
**Fix Required**: Add null check before accessing nested dict methods

#### 2. Parser Return Type Inconsistency
**Issue**: `parser.py` returns dataclass objects, `mapper.py` Parser returns dict
**Impact**: Inconsistent API, potential confusion for users
**Fix Required**: Standardize return types across both parsers

### Missing Control Flow Constructs

#### 1. IF/ELSE Blocks for Rule Groups
**Current**: Only supports `IF` with single rule and `DEFAULT`
**Missing**: Full IF/ELSE blocks for multiple rules
```dml
# Should support:
IF condition {
    map field1 -> target1
    map field2 -> target2
} ELSE {
    map field3 -> target3
}
```

#### 2. Switch/Case Statements
**Current**: Not implemented in mapper.py (exists in parser.py dataclasses)
**Missing**: Multi-condition dispatch for cleaner code
```dml
SWITCH category {
    CASE "E": { map "Electronics" -> CategoryName }
    CASE "B": { map "Books" -> CategoryName }
    DEFAULT: { map "Other" -> CategoryName }
}
```

#### 3. Error Handling (TRY/CATCH)
**Current**: Not implemented in mapper.py (exists in parser.py dataclasses)
**Missing**: Graceful error recovery for type conversions
```dml
TRY {
    map raw_price -> Price AS decimal
} CATCH AS err {
    map "0.0" -> Price
    LOG "Conversion error: {err}"
}
```

### Missing Data Transformation Features

#### String Functions
| Function | Description | Priority |
|----------|-------------|----------|
| `concat(str1, str2, ...)` | Join multiple strings | HIGH |
| `left(str, n)` | Extract first n characters | MEDIUM |
| `right(str, n)` | Extract last n characters | MEDIUM |
| `len(str)` | Get string length | HIGH |
| `split(str, delimiter)` | Split into list | MEDIUM |
| `join(list, delimiter)` | Join list to string | MEDIUM |
| `replace(str, old, new)` | Replace text | HIGH |
| `substring(str, start, length)` | Extract substring | MEDIUM |

#### Numeric Functions
| Function | Description | Priority |
|----------|-------------|----------|
| `abs(value)` | Absolute value | MEDIUM |
| `mod(value, divisor)` | Modulo operation | LOW |
| `pow(base, exp)` | Power operation | LOW |
| `sqrt(value)` | Square root | LOW |
| `round(value, decimals)` | Round decimal | HIGH |

#### Date/Time Functions
| Function | Description | Priority |
|----------|-------------|----------|
| `now()` | Current timestamp (ISO) | HIGH |
| `today()` | Current date (ISO) | HIGH |
| `date_diff(date1, date2)` | Difference in days | MEDIUM |
| `add_days(date, n)` | Add n days to date | HIGH |
| `add_months(date, n)` | Add n months to date | MEDIUM |

#### Conditional Functions
| Function | Description | Priority |
|----------|-------------|----------|
| `ifelse(cond, true_val, false_val)` | Inline conditional | HIGH |
| `coalesce(val1, val2, ...)` | First non-null value | HIGH |

### Missing Aggregation Features

#### 1. Group By Support
**Current**: `AGGREGATE` block exists in parser but not implemented in mapper.py code generator
**Missing**: Full GROUP BY with aggregation functions

#### 2. Aggregation Functions
| Function | Description |
|----------|-------------|
| `sum(field)` | Sum of field values in group |
| `count(field)` | Number of records in group |
| `avg(field)` | Average of field values in group |
| `min(field)` | Minimum value in group |
| `max(field)` | Maximum value in group |

#### 3. Window Functions
| Function | Description |
|----------|-------------|
| `row_number()` | Sequential number of current record |
| `rank()` | Rank of current record (ties get same rank) |
| `dense_rank()` | Rank without gaps |
| `percent_rank()` | Relative rank as percentage |

### Missing Data Quality Features

#### 1. Validation Rules
**Current**: `VALIDATE` keyword exists in parser but not implemented in mapper.py
**Missing**: Data validation before mapping with custom messages

#### 2. Data Cleansing
**Current**: `CLEANSE` block exists in parser but not implemented in mapper.py code generator
**Missing**: Automatic whitespace trimming, case normalization

#### 3. Duplicate Detection
**Current**: `DISTINCT` keyword exists in parser but not implemented in mapper.py code generator
**Missing**: Remove duplicate records before processing

### Missing Loop & Iteration Features

#### 1. Nested Loops
**Current**: LOOP construct exists but nested loops not tested
**Missing**: Support for iterating over nested collections

#### 2. Loop Index Access
**Current**: `INDEX` alias exists in parser but not implemented in mapper.py code generator
**Missing**: Access to current iteration index for conditional logic

#### 3. Loop Control Statements
**Current**: `BREAK` and `CONTINUE` exist in parser but not implemented in mapper.py code generator
**Missing**: Early loop termination and skip current iteration

### Missing File & External Operations

#### 1. File Operations
| Function | Description | Priority |
|----------|-------------|----------|
| `read_file(path)` | Read content from external file | HIGH |
| `write_file(value, path)` | Write value to a file | MEDIUM |
| `append_file(value, path)` | Append to existing file | LOW |

#### 2. External References
| Function | Description | Priority |
|----------|-------------|----------|
| `lookup(key, table_path, key_col, val_col)` | Lookup value in external CSV/JSON | HIGH |
| `api_get(url, params_json)` | Fetch data from REST API (GET) | MEDIUM |
| `api_post(url, body_json)` | Send data to REST API (POST) | LOW |
| `env(var_name, default)` | Access system environment variables | HIGH |

### Missing Configuration Features

#### 1. Variables & Constants
**Current**: `VAR` and `CONST` keywords exist in parser but not implemented in mapper.py code generator
**Missing**: User-defined variables and constants for reusable values

#### 2. Macros
**Current**: `MACRO` keyword exists in parser but not implemented in mapper.py code generator
**Missing**: Reusable code snippets with parameters

#### 3. Includes/Imports
**Current**: `INCLUDE` and `IMPORT` keywords exist in parser but not implemented in mapper.py code generator
**Missing**: File inclusion mechanism for modular mappings

### Missing Output Control

#### 1. Output Filtering
**Current**: `FILTER` keyword exists in parser but not implemented in mapper.py code generator
**Missing**: Filter output records after mapping

#### 2. Record Selection
**Current**: `SELECT` keyword exists in parser but not implemented in mapper.py code generator
**Missing**: Filter input records before mapping

#### 3. Multiple Output Files
**Current**: Not supported
**Missing**: Write to multiple output files in single mapping

### Missing Advanced Mapping Patterns

#### 1. Field Aliasing
**Current**: No support for aliasing target fields in output
**Missing**: `AS` aliasing for dynamic field names

#### 2. Dynamic Field Names
**Current**: `(expression)` syntax exists in parser but not implemented in mapper.py code generator
**Missing**: Runtime-determined field names

#### 3. Nested Object Mapping
**Current**: `OBJECT` block exists in parser but not implemented in mapper.py code generator
**Missing**: Group rules under common target prefix

### Missing Testing & Development Features

#### 1. Test Data Generation
**Current**: Not supported
**Missing**: Built-in test data generation for validation

#### 2. Mock Sources
**Current**: Not supported
**Missing**: Way to mock sources for testing

#### 3. Mapping Validation
**Current**: Not supported
**Missing**: Pre-execution validation of mapping logic

## Recommended Feature Additions (Priority Order)

### Critical (Must Have for v1.0)
1. **Fix Code Generator Bug** - Null pointer in component config handling
2. **String Concatenation** - Essential for combining fields
3. **Default Values with ELSE** - Better conditional handling
4. **Error Handling (TRY/CATCH)** - Production-ready error management
5. **Environment Variables** - Deployment configuration

### High Priority (Common Use Cases)
6. **Data Validation Rules** - Ensure data quality
7. **Lookup Table Support** - Reference data integration
8. **Variables & Constants** - Reusable values
9. **Date Functions (now, today, add_days)** - Common transformations
10. **File Operations (read_file)** - External file access

### Medium Priority (Advanced Features)
11. **Aggregation Functions** - Grouping and summarization
12. **Loop Index Access** - Iteration tracking
13. **Macros & Includes** - Code reuse
14. **Window Functions** - Advanced analytics

### Low Priority (Nice to Have)
15. **Switch/Case Statements** - Cleaner multi-condition logic
16. **Testing Framework** - Development support
17. **Nested Object Mapping** - Complex structures

## Detailed Feature Specifications

### 1. String Concatenation
```dml
map first_name, last_name -> full_name 
    TRANSFORM concat(" ")
```

### 2. Enhanced Conditional with ELSE
```dml
map amount -> status
    IF amount > 1000
        DEFAULT "premium"
    ELSE
        DEFAULT "standard"
```

### 3. Data Validation
```dml
RULES {
    VALIDATE email FORMAT "@"
        MESSAGE "Invalid email format"
    map email -> Email
    
    VALIDATE amount > 0
        MESSAGE "Amount must be positive"
    map amount -> Amount
}
```

### 4. Lookup Table Support
```dml
LOOKUP regions { file: "regions.csv", key: "code" }

RULES {
    map region_code -> RegionName
        TRANSFORM lookup("regions", region_code)
}
```

### 5. Variables & Constants
```dml
CONST TAX_RATE = 0.08
VAR default_status = "PENDING"

RULES {
    map total -> TotalWithTax
        TRANSFORM format_number(total * (1 + TAX_RATE), "#,##0.00")
}
```

### 6. Error Handling
```dml
RULES {
    TRY {
        map amount -> Amount AS decimal
    } CATCH AS err {
        DEFAULT 0
        LOG "Conversion error for amount: {err}"
    }
}
```

### 7. Multiple Output Files
```dml
OUTPUT orders { file: "orders.csv" }
OUTPUT customers { file: "customers.xml" }

RULES {
    map id -> ID OUTPUT orders
    map name -> Name OUTPUT customers
}
```

### 8. Date Functions
```dml
map null -> ProcessedAt TRANSFORM now()
map order_date -> FormattedDate 
    TRANSFORM format_date("DD/MM/YYYY")
map null -> DueDate 
    TRANSFORM add_days(order_date, 30)
```

### 9. Environment Variables
```dml
map env("ENV_STAGE", "production") -> metadata/environment
```

### 10. File Operations
```dml
map template_id -> EmailBody 
    TRANSFORM read_file("templates/welcome.txt")
```

## Implementation Notes

### Parser Architecture
- Consider using a proper parser generator (e.g., Lark, ANTLR)
- Add comprehensive error messages with line/column information
- Implement token lookahead for better parsing decisions

### Code Generation
- Support modular code generation with imports
- Add type hints to generated Python code
- Implement efficient data streaming for large files

### Testing Strategy
- Add unit tests for each new feature
- Create integration test suite with sample data
- Implement property-based testing for transformations

## Conclusion

The current DSL provides a solid foundation for basic data mapping tasks. The recommended enhancements focus on:

1. **Fixing critical bugs** - Code generator null pointer issues
2. **Adding common transformation functions** - String, date, numeric operations
3. **Improving data quality and validation capabilities** - Validation rules, cleansing
4. **Supporting more complex mapping patterns** - Aggregation, window functions, macros

These additions would make the DSL production-ready for enterprise data integration scenarios.

## Appendix: Current Implementation Status

### Parser Features (parser.py)
- [x] Basic mapping structure
- [x] Source/target configuration
- [x] Mapping rules with transforms
- [x] Conditional blocks (IF/ELSE)
- [x] Error handling (TRY/CATCH) - dataclass defined
- [x] Switch/Case blocks - dataclass defined
- [x] Loop constructs (LOOP/BREAK/CONTINUE) - dataclass defined
- [x] Aggregation blocks - dataclass defined
- [x] Validation rules - dataclass defined
- [x] Variables & constants - dataclass defined
- [x] Macros - dataclass defined
- [x] File inclusion (INCLUDE/IMPORT) - dataclass defined
- [x] Nested object blocks - dataclass defined

### Code Generator Features (mapper.py)
- [x] Basic CSV/XML/DB/EDI mapping
- [x] Simple transformations (upper, lower, trim)
- [ ] IF/ELSE blocks
- [ ] TRY/CATCH error handling
- [ ] Switch/Case dispatch
- [ ] Loop constructs with index access
- [ ] Aggregation functions
- [ ] Validation rules
- [ ] Data cleansing
- [ ] Variables & constants
- [ ] Macros
- [ ] File inclusion
- [ ] Nested object blocks

### Test Coverage
- [x] Basic CSV to XML mapping
- [x] DB source configuration
- [ ] Complex transformations
- [ ] Conditional rules
- [ ] Nested loops
- [ ] Error handling scenarios


## Additional Findings from Example Files

### Features Referenced in Examples but Not Fully Implemented

#### 1. Environment Variables (data_enrichment.map:9)
```dml
map env("ENV_STAGE", "production") -> metadata/environment
```
**Status**: Referenced in example but `env()` function not implemented in code generator

#### 2. External Table Lookup (data_enrichment.map:13)
```dml
map customer_id -> CustomerName TRANSFORM lookup("customers.csv", "id", "name")
```
**Status**: Referenced in example but `lookup()` function not implemented

#### 3. API Enrichment (data_enrichment.map:17)
```dml
map sku -> ProductDetails TRANSFORM api_get("https://api.inventory.com/products")
```
**Status**: Referenced in example but `api_get()` function not implemented

#### 4. File Read Operation (data_enrichment.map:20)
```dml
map template_id -> EmailBody TRANSFORM read_file("templates/welcome.txt")
```
**Status**: Referenced in example but `read_file()` function not implemented

#### 5. Window Functions (data_enrichment.map:23-24)
```dml
map null -> record_rank TRANSFORM rank()
map null -> seq_id TRANSFORM row_number()
```
**Status**: Referenced in example but window functions not implemented

### Summary of Missing Implementation

| Feature | Example Reference | Code Generator Status |
|---------|-------------------|----------------------|
| `env()` function | data_enrichment.map:9 | Not implemented |
| `lookup()` function | data_enrichment.map:13 | Not implemented |
| `api_get()` function | data_enrichment.map:17 | Not implemented |
| `read_file()` function | data_enrichment.map:20 | Not implemented |
| `rank()` window function | data_enrichment.map:23 | Not implemented |
| `row_number()` window function | data_enrichment.map:24 | Not implemented |

## Implementation Priority Matrix

### Phase 1: Critical Fixes (Week 1)
| Issue | Impact | Effort |
|-------|--------|--------|
| Code generator null pointer bug | High | Low |
| Parser return type consistency | Medium | Medium |

### Phase 2: Core Transformations (Week 2-3)
| Feature | Priority | Effort |
|---------|----------|--------|
| String concatenation (`concat`) | HIGH | Low |
| Environment variables (`env`) | HIGH | Low |
| File operations (`read_file`) | HIGH | Medium |
| Date functions (`now`, `today`, `add_days`) | HIGH | Low |

### Phase 3: Data Quality (Week 4)
| Feature | Priority | Effort |
|---------|----------|--------|
| Data validation rules | HIGH | Medium |
| Lookup table support (`lookup`) | HIGH | Medium |
| Error handling (TRY/CATCH) | HIGH | High |

### Phase 4: Advanced Features (Week 5-6)
| Feature | Priority | Effort |
|---------|----------|--------|
| Aggregation functions | MEDIUM | High |
| Window functions (`rank`, `row_number`) | MEDIUM | High |
| Macros & includes | LOW | Medium |

### Phase 5: Polish (Week 7)
| Feature | Priority | Effort |
|---------|----------|--------|
| Switch/Case dispatch | LOW | Low |
| Multiple output files | LOW | Medium |
| Testing framework | LOW | High |

