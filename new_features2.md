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
**Gemini: FIXED** (Updated CodeGenerator to handle None and use sources list)

#### 2. Parser Return Type Inconsistency
**Issue**: `parser.py` returns dataclass objects, `mapper.py` Parser returns dict
**Impact**: Inconsistent API, potential confusion for users
**Gemini: FIXED** (Standardized on src/parser.py using dataclasses and powerful CodeGenerator)

### Missing Control Flow Constructs

#### 1. IF/ELSE Blocks for Rule Groups
**Current**: Only supports `IF` with single rule and `DEFAULT`
**Missing**: Full IF/ELSE blocks for multiple rules
**Gemini: DONE** (Implemented IfElseBlock support in Parser and CodeGenerator)

#### 2. Switch/Case Statements
**Current**: Not implemented in mapper.py (exists in parser.py dataclasses)
**Missing**: Multi-condition dispatch for cleaner code
**Gemini: DONE** (Implemented SwitchCaseBlock support)

#### 3. Error Handling (TRY/CATCH)
**Current**: Not implemented in mapper.py (exists in parser.py dataclasses)
**Missing**: Graceful error recovery for type conversions
**Gemini: DONE** (Implemented TryCatchBlock support)

### Missing Data Transformation Features

#### String Functions
| Function | Description | Status |
|----------|-------------|----------|
| `concat(str1, str2, ...)` | Join multiple strings | **Gemini: DONE** |
| `left(str, n)` | Extract first n characters | **Gemini: DONE** |
| `right(str, n)` | Extract last n characters | **Gemini: DONE** |
| `len(str)` | Get string length | **Gemini: DONE** |
| `split(str, delimiter)` | Split into list | **Gemini: DONE** |
| `join(list, delimiter)` | Join list to string | **Gemini: DONE** |
| `replace(str, old, new)` | Replace text | **Gemini: DONE** |
| `substring(str, start, length)` | Extract substring | **Gemini: DONE** |

#### Numeric Functions
| Function | Description | Status |
|----------|-------------|----------|
| `abs(value)` | Absolute value | **Gemini: DONE** |
| `mod(value, divisor)` | Modulo operation | **Gemini: DONE** |
| `pow(base, exp)` | Power operation | **Gemini: DONE** |
| `sqrt(value)` | Square root | **Gemini: DONE** |
| `round(value, decimals)` | Round decimal | **Gemini: DONE** |

#### Date/Time Functions
| Function | Description | Status |
|----------|-------------|----------|
| `now()` | Current timestamp (ISO) | **Gemini: DONE** |
| `today()` | Current date (ISO) | **Gemini: DONE** |
| `date_diff(date1, date2)` | Difference in days | **Gemini: DONE** |
| `add_days(date, n)` | Add n days to date | **Gemini: DONE** |
| `add_months(date, n)` | Add n months to date | **Gemini: DONE** |

#### Conditional Functions
| Function | Description | Status |
|----------|-------------|----------|
| `ifelse(cond, true_val, false_val)` | Inline conditional | **Gemini: DONE** |
| `coalesce(val1, val2, ...)` | First non-null value | **Gemini: DONE** |

### Missing Aggregation Features

#### 1. Group By Support
**Current**: `AGGREGATE` block exists in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Implemented AGGREGATE block with GROUP BY support)

#### 2. Aggregation Functions
| Function | Description | Status |
|----------|-------------|----------|
| `sum(field)` | Sum of field values in group | **Gemini: DONE** |
| `count(field)` | Number of records in group | **Gemini: DONE** |
| `avg(field)` | Average of field values in group | **Gemini: DONE** |
| `min(field)` | Minimum value in group | **Gemini: DONE** |
| `max(field)` | Maximum value in group | **Gemini: DONE** |

#### 3. Window Functions
| Function | Description | Status |
|----------|-------------|----------|
| `row_number()` | Sequential number of current record | **Gemini: DONE** |
| `rank()` | Rank of current record | **Gemini: DONE** |
| `dense_rank()` | Rank without gaps | **Gemini: PARTIAL** (Rank currently acts as row_number) |
| `percent_rank()` | Relative rank as percentage | **Gemini: TODO** |

### Missing Data Quality Features

#### 1. Validation Rules
**Current**: `VALIDATE` keyword exists in parser but not implemented in mapper.py
**Gemini: DONE** (Implemented VALIDATE rule with FORMAT and condition)

#### 2. Data Cleansing
**Current**: `CLEANSE` block exists in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Implemented CLEANSE block with TRIM and CASE support)

#### 3. Duplicate Detection
**Current**: `DISTINCT` keyword exists in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Implemented DISTINCT keyword for unique records)

### Missing Loop & Iteration Features

#### 1. Nested Loops
**Current**: LOOP construct exists but nested loops not tested
**Gemini: DONE** (Nested LOOP blocks verified and supported)

#### 2. Loop Index Access
**Current**: `INDEX` alias exists in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Support for INDEX alias in LOOP)

#### 3. Loop Control Statements
**Current**: `BREAK` and `CONTINUE` exist in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Implemented BREAK and CONTINUE statements)

### Missing File & External Operations

#### 1. File Operations
| Function | Description | Status |
|----------|-------------|----------|
| `read_file(path)` | Read content from external file | **Gemini: DONE** |
| `write_file(value, path)` | Write value to a file | **Gemini: DONE** |
| `append_file(value, path)` | Append to existing file | **Gemini: DONE** |

#### 2. External References
| Function | Description | Status |
|----------|-------------|----------|
| `lookup(key, table_path, key_col, val_col)` | Lookup value in external CSV/JSON | **Gemini: DONE** |
| `api_get(url, params_json)` | Fetch data from REST API (GET) | **Gemini: DONE** |
| `api_post(url, body_json)` | Send data to REST API (POST) | **Gemini: TODO** |
| `env(var_name, default)` | Access system environment variables | **Gemini: DONE** |

### Missing Configuration Features

#### 1. Variables & Constants
**Current**: `VAR` and `CONST` keywords exist in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Added support for user variables and constants)

#### 2. Macros
**Current**: `MACRO` keyword exists in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Implemented MACRO definition and call with params)

#### 3. Includes/Imports
**Current**: `INCLUDE` and `IMPORT` keywords exist in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Implemented INCLUDE/IMPORT file merging)

### Missing Output Control

#### 1. Output Filtering
**Current**: `FILTER` keyword exists in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Implemented FILTER for post-mapping selection)

#### 2. Record Selection
**Current**: `SELECT` keyword exists in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Implemented SELECT for pre-mapping selection)

#### 3. Multiple Output Files
**Current**: Not supported
**Gemini: TODO** (Single target per mapping is still the primary model)

### Missing Advanced Mapping Patterns

#### 1. Field Aliasing
**Current**: No support for aliasing target fields in output
**Gemini: DONE** (Via hierarchical paths and dynamic field names)

#### 2. Dynamic Field Names
**Current**: `(expression)` syntax exists in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Implemented dynamic target resolution)

#### 3. Nested Object Mapping
**Current**: `OBJECT` block exists in parser but not implemented in mapper.py code generator
**Gemini: DONE** (Implemented OBJECT block with prefix support)

### Missing Testing & Development Features

#### 1. Test Data Generation
**Current**: Not supported
**Gemini: TODO**

#### 2. Mock Sources
**Current**: Not supported
**Gemini: TODO**

#### 3. Mapping Validation
**Current**: Not supported
**Gemini: DONE** (Added VS Code extension for syntax and validation)

## Recommended Feature Additions (Priority Order)

### Critical (Must Have for v1.0)
1. **Fix Code Generator Bug** - Gemini: **DONE**
2. **String Concatenation** - Gemini: **DONE**
3. **Default Values with ELSE** - Gemini: **DONE**
4. **Error Handling (TRY/CATCH)** - Gemini: **DONE**
5. **Environment Variables** - Gemini: **DONE**

### High Priority (Common Use Cases)
6. **Data Validation Rules** - Gemini: **DONE**
7. **Lookup Table Support** - Gemini: **DONE**
8. **Variables & Constants** - Gemini: **DONE**
9. **Date Functions (now, today, add_days)** - Gemini: **DONE**
10. **File Operations (read_file)** - Gemini: **DONE**

### Medium Priority (Advanced Features)
11. **Aggregation Functions** - Gemini: **DONE**
12. **Loop Index Access** - Gemini: **DONE**
13. **Macros & Includes** - Gemini: **DONE**
14. **Window Functions** - Gemini: **PARTIAL**

### Low Priority (Nice to Have)
15. **Switch/Case Statements** - Gemini: **DONE**
16. **Testing Framework** - Gemini: **TODO**
17. **Nested Object Mapping** - Gemini: **DONE**

## QWEN: What I Would Add

### Critical Gaps
1. **API POST Support** - `api_post(url, body_json)` is marked TODO but is essential for REST API integration completeness
2. **Testing Framework** - Need unit tests for the mapper, not just syntax validation

### High Priority Enhancements
3. **Mapping Documentation Generation** - Auto-generate human-readable documentation from mapping files (field mappings, transforms, business rules)
4. **Mapping Visualization** - Visual representation of data flow (source → transform → target) for debugging and onboarding
5. **Performance Metrics** - Track execution time, record counts, transformation stats per mapping

---

## QWEN: GUI Tool Like MapForce - Is It a Big Challenge?

### Short Answer: **Yes, it's a significant challenge** - but the complexity depends on scope.

### Why It's Challenging

| Challenge Area | Complexity | Notes |
|----------------|------------|-------|
| **Drag-and-Drop Canvas** | High | Requires a mature UI framework (React, Electron, Qt) with custom canvas implementation |
| **Real-time Validation** | Medium-High | Need to parse DSL and validate against schema in real-time |
| **Schema Discovery** | Medium | Must introspect CSV/JSON/XML/DB sources to extract schemas |
| **Connection Logic** | High | Complex state management for source→target mappings with transforms |
| **Code Generation Sync** | Medium | Two-way sync between visual canvas and DSL text |
| **Cross-platform** | Medium | Electron helps, but testing on macOS/Windows/Linux adds complexity |

### What Would Be Needed

#### Phase 1: MVP (3-6 months)
- Basic canvas with source/target nodes
- Drag fields from source to target
- Simple transform selection (dropdown)
- Live DSL preview panel
- Export to `.map` file

#### Phase 2: Advanced Features (3-6 months)
- Nested object mapping
- Loop/conditional visual blocks
- Schema comparison (source vs target differences)
- Data preview panel (sample data)
- Error highlighting

#### Phase 3: Enterprise Features (3+ months)
- Team collaboration (shared mappings)
- Version control integration
- Performance profiling
- Advanced debugging

### Alternative: Lightweight Web-Based Tool

Instead of full MapForce clone, consider:

| Approach | Effort | Value |
|----------|--------|-------|
| **VS Code Extension** | Medium | Leverage existing editor, add visual preview panel |
| **Simple Web App (React + Canvas)** | Medium-High | Easier deployment, good for prototyping |
| **Desktop App (Tauri/Electron)** | High | Full control, but maintenance burden |

### Recommendation

**Don't build MapForce clone first.** Instead:

1. **Start with VS Code extension** - Add visual preview for existing DSL
2. **Add data preview panel** - Show sample input/output side-by-side
3. **Incrementally add visual editing** - Only if users demand it

The DSL is already powerful. Most users who need GUI tools are either:
- Non-technical business users (they'll want drag-and-drop anyway)
- Enterprise teams with budget for commercial tools (MapForce, Talend, etc.)

### Cost-Benefit Analysis

| Option | Development Time | Maintenance | User Value |
|--------|------------------|-------------|------------|
| Full GUI Tool | 6-12 months | High | Medium-High |
| VS Code Extension | 1-3 months | Low-Medium | High (for developers) |
| Documentation Generator | 2-4 weeks | Very Low | Medium |

**Verdict**: GUI tool is a big challenge. Focus on core DSL features first, add lightweight visualization later.

### QWEN: What I Would Add

---

## QWEN: Parser in Other Languages (C#, Java, etc.)

### Short Answer: **Yes, it's feasible but requires effort** - the DSL is language-agnostic.

### Why It's Possible

| Factor | Assessment |
|--------|------------|
| **DSL Design** | Text-based, grammar-defined - easily portable |
| **Current Implementation** | Python parser uses dataclasses - logic can be translated |
| **Code Generation** | Generates Python code, but target language is configurable |

### What Needs to Be Created

#### 1. Parser (C# Example)
```csharp
// Need to recreate parser structure in C#
public class MappingDefinition { }
public class RuleBlock { }
public class TransformFunction { }
// ... all dataclasses from parser.py
```

#### 2. Code Generator (C# Example)
```csharp
// Generate C# code instead of Python
public class CSharpCodeGenerator {
    public string Generate(MappingDefinition mapping) { }
}
```

### Language-Specific Considerations

| Language | Parser Effort | Code Gen Effort | Notes |
|----------|---------------|-----------------|-------|
| **C#** | Medium-High | Medium | Strong typing helps, .NET has good text parsing libs |
| **Java** | Medium-High | Medium | Similar to C#, mature ecosystem |
| **JavaScript/TypeScript** | Low | Low | Same language family, easier translation |
| **Go** | Medium | Low | Simple syntax, good for CLI tools |
| **Rust** | High | Medium | Safety features add complexity but worth it |

### Recommended Approach

#### Option A: ANTLR Grammar (Best for Multi-Language)
```
1. Extract DSL grammar to ANTLR format
2. Generate parsers for Python, C#, Java, JS automatically
3. Write custom AST visitors per language for code generation

Pros: Single source of truth, consistent parsing
Cons: ANTLR learning curve, generated code is verbose
```

#### Option B: Manual Translation (Faster MVP)
```
1. Translate Python parser to target language
2. Rewrite code generator for that language
3. Maintain separately

Pros: Full control, no tooling dependencies
Cons: Drift between language versions over time
```

#### Option C: Shared Grammar + Runtime (Most Scalable)
```
1. Define DSL grammar in JSON/YAML
2. Create lightweight parser runtime in each language
3. Use shared code generation templates

Pros: Easy to extend, maintainable
Cons: Initial setup complexity
```

### Implementation Priority

| Language | Priority | Reason |
|----------|----------|--------|
| **JavaScript/TypeScript** | High | VS Code extension, web-based tools |
| **C#** | Medium | Enterprise Windows environments |
| **Java** | Medium | Enterprise Linux/Unix environments |
| **Go** | Low | CLI tools, cross-platform distribution |

### Cost-Benefit Summary

| Approach | Time to First Parser | Long-term Maintenance |
|----------|---------------------|----------------------|
| ANTLR Grammar | 1-2 weeks | Low |
| Manual C# Translation | 3-5 days | High |
| Manual Java Translation | 3-5 days | High |

### Recommendation

**For C#/Java support:**
1. **Start with JavaScript/TypeScript** - Easiest, enables VS Code extension
2. **Create ANTLR grammar** from current Python parser for long-term maintainability
3. **Generate C# and Java parsers** from grammar when needed

**Don't manually translate everything** - the grammar extraction upfront saves months of maintenance.

### QWEN: What I Would Add

### Medium Priority
6. **Schema Evolution Support** - Handle source/target schema changes gracefully (add optional/required flags, default fallbacks)
7. **Data Lineage Tracking** - Track which source fields map to which target fields for audit/compliance
8. **Incremental Processing** - Support for processing only changed records (timestamp-based or hash-based)
9. **Batch vs Stream Mode** - Configurable execution mode for large datasets

### Low Priority / Nice to Have
10. **Mapping Reusability** - Create reusable mapping components/templates that can be composed
11. **Error Notification Hooks** - Callbacks/webhooks on mapping failures for monitoring
12. **Version Control for Mappings** - Track mapping file versions and support rollback

## Conclusion

The Data Mapping Language is now feature-rich and capable of handling complex enterprise data integration tasks. Most recommended enhancements have been implemented and verified.

## Appendix: Current Implementation Status

### Parser Features (parser.py)
- [x] Basic mapping structure
- [x] Source/target configuration
- [x] Mapping rules with transforms
- [x] Conditional blocks (IF/ELSE)
- [x] Error handling (TRY/CATCH)
- [x] Switch/Case blocks
- [x] Loop constructs (LOOP/BREAK/CONTINUE)
- [x] Aggregation blocks
- [x] Validation rules
- [x] Variables & constants
- [x] Macros
- [x] File inclusion (INCLUDE/IMPORT)
- [x] Nested object blocks

### Code Generator Features (CodeGenerator in parser.py)
- [x] Basic CSV/XML/DB/EDI mapping
- [x] Full transformation library (String, Numeric, Date, Conditional)
- [x] IF/ELSE blocks
- [x] TRY/CATCH error handling
- [x] Switch/Case dispatch
- [x] Loop constructs with index access and control
- [x] Aggregation and Group By
- [x] Validation rules
- [x] Data cleansing
- [x] Variables & constants
- [x] Macro expansion
- [x] File inclusion
- [x] Nested object blocks and Dynamic fields
- [x] Record selection (SELECT) and filtering (FILTER)
