"""
Parser for the Data Mapping Language (DML)
Parses mapping files and generates executable Python code.
"""

import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union


@dataclass
class SourceConfig:
    """Configuration for data source."""
    type: str  # XML, CSV, DB, EDI
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TargetConfig:
    """Configuration for data target."""
    type: str  # XML, CSV, DB, EDI
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MappingRule:
    """A single mapping rule."""
    source_field: str
    target_field: str
    transform: Optional[str] = None
    condition: Optional[str] = None
    default_value: Optional[Any] = None
    data_type: Optional[str] = None


@dataclass
class Mapping:
    """Complete mapping definition."""
    name: str
    source: SourceConfig
    target: TargetConfig
    rules: List[MappingRule] = field(default_factory=list)


class Tokenizer:
    """Tokenizes the mapping language input."""
    
    TOKENS = [
        ('MAPPING', r'MAPPING'),
        ('SOURCE', r'SOURCE'),
        ('TARGET', r'TARGET'),
        ('RULES', r'RULES'),
        ('XML', r'XML'),
        ('CSV', r'CSV'),
        ('DB', r'DB'),
        ('EDI', r'EDI'),
        ('IF', r'IF'),
        ('ELSE', r'ELSE'),
        ('TRANSFORM', r'TRANSFORM'),
        ('DEFAULT', r'DEFAULT'),
        ('AS', r'AS'),
        ('MAP', r'map'),
        ('LOOP', r'loop'),
        ('AGGREGATE', r'AGGREGATE'),
        ('FUNCTION', r'FUNCTION'),
        ('WHEN', r'WHEN'),
        ('THEN', r'THEN'),
        ('LBRACE', r'\{'),
        ('RBRACE', r'\}'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('LBRACKET', r'\['),
        ('RBRACKET', r'\]'),
        ('ARROW', r'->'),
        ('COMMA', r','),
        ('COLON', r':'),
        ('GT', r'>'),
        ('LT', r'<'),
        ('GE', r'>='),
        ('LE', r'<='),
        ('EQ', r'=='),
        ('NE', r'!='),
        ('PLUS', r'\+'),
        ('MINUS', r'-'),
        ('STAR', r'\*'),
        ('SLASH', r'/'),
        ('NUMBER', r'-?\d+(\.\d+)?'),
        ('STRING', r'"[^"]*"|\'[^\']*\''),
        ('IDENT', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('SLASHPATH', r'[a-zA-Z_/]+/[a-zA-Z0-9_/.]*'),
        ('WS', r'\s+'),
        ('COMMENT', r'#.*$'),
    ]
    
    def __init__(self, text: str):
        self.text = text
        self.tokens: List[tuple] = []
        
    def tokenize(self) -> List[tuple]:
        """Convert input text into tokens."""
        pos = 0
        while pos < len(self.text):
            match = None
            for token_type, pattern in self.TOKENS:
                regex = re.compile(pattern, re.MULTILINE | re.IGNORECASE)
                match = regex.match(self.text, pos)
                if match:
                    value = match.group(0)
                    if token_type not in ('WS', 'COMMENT'):
                        self.tokens.append((token_type, value))
                    pos = match.end()
                    break
            if not match:
                raise SyntaxError(f"Unexpected character at position {pos}: {self.text[pos]}")
        return self.tokens


class Parser:
    """Parses tokens into a structured mapping definition."""
    
    def __init__(self, text: str):
        self.tokenizer = Tokenizer(text)
        self.tokens = []
        self.pos = 0
        
    def parse(self) -> Mapping:
        """Parse the entire mapping definition."""
        self.tokens = self.tokenizer.tokenize()
        self.pos = 0
        return self.parse_mapping()
    
    def current_token(self) -> Optional[tuple]:
        """Get current token."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def peek_token(self, offset: int = 0) -> Optional[tuple]:
        """Peek at token at offset."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None
    
    def advance(self) -> Optional[tuple]:
        """Advance to next token and return current."""
        token = self.current_token()
        if token:
            self.pos += 1
        return token
    
    def expect(self, token_type: str) -> tuple:
        """Expect a specific token type."""
        token = self.current_token()
        if not token or token[0] != token_type:
            raise SyntaxError(f"Expected {token_type}, got {token}")
        self.advance()
        return token
    
    def match(self, token_type: str) -> Optional[tuple]:
        """Match and consume token if type matches."""
        if self.current_token() and self.current_token()[0] == token_type:
            return self.advance()
        return None
    
    def skip_whitespace(self):
        """Skip whitespace and comments."""
        while self.current_token() and self.current_token()[0] in ('WS', 'COMMENT'):
            self.advance()
    
    def parse_mapping(self) -> Mapping:
        """Parse MAPPING definition."""
        self.expect('MAPPING')
        name = self.expect('IDENT')[1]
        
        # Parse opening brace
        self.skip_whitespace()
        self.expect('LBRACE')
        
        source = None
        target = None
        rules = []
        
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.skip_whitespace()
            
            if self.match('SOURCE'):
                source = self.parse_source_target()
            elif self.match('TARGET'):
                target = self.parse_source_target()
            elif self.match('RULES'):
                rules = self.parse_rules()
            else:
                raise SyntaxError(f"Unexpected token in mapping: {self.current_token()}")
        
        self.expect('RBRACE')
        
        return Mapping(
            name=name,
            source=source or SourceConfig(type='CSV', config={}),
            target=target or TargetConfig(type='CSV', config={}),
            rules=rules
        )
    
    def parse_source_target(self) -> Union[SourceConfig, TargetConfig]:
        """Parse SOURCE or TARGET configuration."""
        config_type = self.expect('IDENT')[1].upper()
        
        self.skip_whitespace()
        self.expect('LBRACE')
        
        config = {}
        
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            key = self.expect('IDENT')[1]
            self.skip_whitespace()
            self.expect('COLON')
            self.skip_whitespace()
            value = self.parse_value()
            config[key] = value
            self.skip_whitespace()
            
            if self.current_token() and self.current_token()[0] == 'COMMA':
                self.advance()
        
        self.expect('RBRACE')
        
        if config_type == 'SOURCE':
            return SourceConfig(type=config.get('type', 'CSV'), config=config)
        else:
            return TargetConfig(type=config.get('type', 'CSV'), config=config)
    
    def parse_value(self) -> Any:
        """Parse a value (string, number, or identifier)."""
        token = self.current_token()
        if not token:
            return None
            
        if token[0] == 'STRING':
            self.advance()
            # Remove quotes
            return token[1][1:-1]
        elif token[0] == 'NUMBER':
            self.advance()
            if '.' in token[1]:
                return float(token[1])
            return int(token[1])
        elif token[0] == 'IDENT':
            self.advance()
            return token[1]
        
        return None
    
    def parse_rules(self) -> List[MappingRule]:
        """Parse mapping rules."""
        self.expect('LBRACE')
        
        rules = []
        
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.skip_whitespace()
            
            rule = self.parse_rule()
            if rule:
                rules.append(rule)
        
        self.expect('RBRACE')
        return rules
    
    def parse_rule(self) -> Optional[MappingRule]:
        """Parse a single mapping rule."""
        if self.match('LOOP'):
            return self.parse_loop_rule()
        
        if not self.match('MAP'):
            return None
        
        # Parse source field(s)
        source_fields = []
        
        while True:
            self.skip_whitespace()
            token = self.current_token()
            
            if token and token[0] in ('STRING', 'IDENT'):
                source_fields.append(self.parse_value())
            elif token and token[0] == 'NULL':
                self.advance()
                source_fields.append(None)
            else:
                break
            
            if not self.match('COMMA'):
                break
        
        self.skip_whitespace()
        
        # Parse arrow
        self.expect('ARROW')
        
        self.skip_whitespace()
        
        # Parse target field
        target_field = None
        token = self.current_token()
        if token and token[0] in ('STRING', 'IDENT'):
            target_field = self.parse_value()
        
        transform = None
        condition = None
        default_value = None
        data_type = None
        
        # Parse optional modifiers
        while True:
            self.skip_whitespace()
            token = self.current_token()
            
            if not token:
                break
            
            if token[0] == 'TRANSFORM':
                self.advance()
                transform = self.parse_function_call()
            elif token[0] == 'IF':
                self.advance()
                condition = self.parse_condition()
            elif token[0] == 'DEFAULT':
                self.advance()
                default_value = self.parse_value()
            elif token[0] == 'AS':
                self.advance()
                data_type = self.expect('IDENT')[1].lower()
            else:
                break
        
        return MappingRule(
            source_field=source_fields[0] if source_fields else '',
            target_field=target_field or '',
            transform=transform,
            condition=condition,
            default_value=default_value,
            data_type=data_type
        )
    
    def parse_function_call(self) -> str:
        """Parse a function call."""
        func_name = self.expect('IDENT')[1]
        self.skip_whitespace()
        self.expect('LPAREN')
        
        args = []
        while self.current_token() and self.current_token()[0] != 'RPAREN':
            arg = self.parse_value()
            if arg is not None:
                args.append(arg)
            self.skip_whitespace()
            
            if self.current_token() and self.current_token()[0] == 'COMMA':
                self.advance()
        
        self.expect('RPAREN')
        
        return f"{func_name}({', '.join(repr(a) for a in args)})"
    
    def parse_condition(self) -> str:
        """Parse a condition expression."""
        # Simple approach: collect tokens until we hit a newline or end
        condition_parts = []
        
        while self.current_token() and self.current_token()[0] not in ('RBRACE', 'TRANSFORM', 'DEFAULT', 'AS'):
            token = self.current_token()
            if token[0] not in ('WS', 'COMMENT'):
                condition_parts.append(token[1])
            self.advance()
        
        return ' '.join(condition_parts)
    
    def parse_loop_rule(self) -> Optional[MappingRule]:
        """Parse a loop rule."""
        source_collection = self.expect('IDENT')[1]
        
        self.skip_whitespace()
        self.expect('LBRACE')
        
        # Collect sub-rules
        sub_rules = []
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            rule = self.parse_rule()
            if rule:
                sub_rules.append(rule)
        
        self.expect('RBRACE')
        
        # Return as a special rule type
        return MappingRule(
            source_field=source_collection,
            target_field='loop',
            transform=f'loop({repr(source_collection)})'
        )


class CodeGenerator:
    """Generates executable Python code from mapping definition."""
    
    def __init__(self, mapping: Mapping):
        self.mapping = mapping
        self.imports = set()
        self.code_lines = []
        
    def generate(self) -> str:
        """Generate complete Python code."""
        self._generate_header()
        self._generate_classes()
        self._generate_functions()
        self._generate_main()
        
        return '\n'.join(self.code_lines)
    
    def _generate_header(self):
        """Generate imports and header."""
        self.imports.add('import csv')
        self.imports.add('import json')
        
        if self.mapping.source.type == 'XML' or self.mapping.target.type == 'XML':
            self.imports.add('import xml.etree.ElementTree as ET')
        
        if self.mapping.source.type == 'DB' or self.mapping.target.type == 'DB':
            self.imports.add('import sqlite3')
        
        if self.mapping.source.type == 'EDI' or self.mapping.target.type == 'EDI':
            self.imports.add('import re')
        
        self.code_lines.extend(self.imports)
        self.code_lines.append('')
        self.code_lines.append(f'# Data Mapping: {self.mapping.name}')
        self.code_lines.append('')
    
    def _generate_classes(self):
        """Generate any necessary classes."""
        pass
    
    def _generate_functions(self):
        """Generate helper functions."""
        self.code_lines.append('def transform_value(value, func_name, *args):')
        self.code_lines.append('    """Apply transformation function to value."""')
        self.code_lines.append('    if value is None:')
        self.code_lines.append('        return None')
        self.code_lines.append('')
        self.code_lines.append('    try:')
        
        # Generate transformation functions
        transforms = {
            'upper': 'return str(value).upper()',
            'lower': 'return str(value).lower()',
            'trim': 'return str(value).strip()',
            'int': 'return int(value)',
            'float': 'return float(value)',
            'str': 'return str(value)',
            'format_date': 'return format_date_func(value, *args)',
            'format_number': 'return format_number_func(value, *args)',
            'substring': 'return str(value)[:int(args[0])] if args else value',
        }
        
        for func, code in transforms.items():
            self.code_lines.append(f'    if func_name == "{func}":')
            self.code_lines.append(f'        {code}')
        
        self.code_lines.append('    except Exception as e:')
        self.code_lines.append('        print(f"Transform error: {{e}}")')
        self.code_lines.append('    return value')
        self.code_lines.append('')
        
        # Date formatter
        self.code_lines.append('def format_date_func(value, fmt):')
        self.code_lines.append('    """Format date value according to format string."""')
        self.code_lines.append('    import datetime')
        self.code_lines.append('    try:')
        self.code_lines.append('        if isinstance(value, str):')
        self.code_lines.append('            # Try common date formats')
        self.code_lines.append('            for fmt_str in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]:')
        self.code_lines.append('                try:')
        self.code_lines.append('                    dt = datetime.datetime.strptime(value, fmt_str)')
        self.code_lines.append('                    return dt.strftime(fmt.replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d"))')
        self.code_lines.append('                except ValueError:')
        self.code_lines.append('                    continue')
        self.code_lines.append('    except Exception:')
        self.code_lines.append('        pass')
        self.code_lines.append('    return value')
        self.code_lines.append('')
        
        # Number formatter
        self.code_lines.append('def format_number_func(value, fmt):')
        self.code_lines.append('    """Format number according to format string."""')
        self.code_lines.append('    try:')
        self.code_lines.append('        num = float(value)')
        self.code_lines.append('        if fmt == "#,##0.00":')
        self.code_lines.append('            return f"{num:,.2f}"')
        self.code_lines.append('        elif fmt == "999999.99":')
        self.code_lines.append('            return f"{num:08.2f}"')
        self.code_lines.append('    except (ValueError, TypeError):')
        self.code_lines.append('        pass')
        self.code_lines.append('    return value')
        self.code_lines.append('')
    
    def _generate_main(self):
        """Generate main mapping function."""
        self.code_lines.append('def execute_mapping(input_data, output_path):')
        self.code_lines.append('    """Execute the mapping and write to output."""')
        
        # Source handling
        source_type = self.mapping.source.type.upper()
        if source_type == 'XML':
            self.code_lines.append('    # Read XML source')
            self.code_lines.append('    tree = ET.parse(input_data)')
            self.code_lines.append('    root = tree.getroot()')
            self.code_lines.append('    data_items = parse_xml_data(root)')
        elif source_type == 'CSV':
            self.code_lines.append('    # Read CSV source')
            self.code_lines.append('    data_items = []')
            self.code_lines.append('    with open(input_data, "r", newline="") as f:')
            self.code_lines.append('        reader = csv.DictReader(f)')
            self.code_lines.append('            for row in reader:')
            self.code_lines.append('                data_items.append(dict(row))')
        elif source_type == 'DB':
            self.code_lines.append('    # Read from database')
            self.code_lines.append('    conn = sqlite3.connect(":memory:")  # Replace with actual connection')
            self.code_lines.append('    cursor = conn.cursor()')
            self.code_lines.append('    cursor.execute("SELECT query")  # Replace with actual query')
            self.code_lines.append('    columns = [desc[0] for desc in cursor.description]')
            self.code_lines.append('    data_items = [dict(zip(columns, row)) for row in cursor.fetchall()]')
        elif source_type == 'EDI':
            self.code_lines.append('    # Read EDI source')
            self.code_lines.append('    with open(input_data, "r") as f:')
            self.code_lines.append('        edi_content = f.read()')
            self.code_lines.append('    data_items = parse_edi_data(edi_content)')
        else:
            self.code_lines.append('    # Unknown source type')
            self.code_lines.append('    data_items = input_data')
        
        self.code_lines.append('')
        
        # Apply mapping rules
        self.code_lines.append('    # Apply mapping rules')
        self.code_lines.append('    output_items = []')
        
        for rule in self.mapping.rules:
            self._generate_rule_code(rule)
        
        # Target handling
        target_type = self.mapping.target.type.upper()
        if target_type == 'XML':
            self.code_lines.append('')
            self.code_lines.append('    # Write XML output')
            self.code_lines.append('    write_xml_output(output_items, output_path)')
        elif target_type == 'CSV':
            self.code_lines.append('')
            self.code_lines.append('    # Write CSV output')
            self.code_lines.append('    write_csv_output(output_items, output_path)')
        elif target_type == 'DB':
            self.code_lines.append('')
            self.code_lines.append('    # Write to database')
            self.code_lines.append('    write_db_output(output_items)')
        elif target_type == 'EDI':
            self.code_lines.append('')
            self.code_lines.append('    # Write EDI output')
            self.code_lines.append('    write_edi_output(output_items, output_path)')
        
        self.code_lines.append('')
        self.code_lines.append('    return output_items')
        self.code_lines.append('')
    
    def _generate_rule_code(self, rule: MappingRule):
        """Generate code for a single mapping rule."""
        if not rule.target_field:
            return
        
        # Check if this is a loop rule
        if 'loop(' in str(rule.transform):
            self.code_lines.append(f'    # Loop through {rule.source_field}')
            return
        
        source_var = f'source_item.get("{rule.source_field}")'
        
        # Build target assignment
        self.code_lines.append(f'    # Rule: {rule.source_field} -> {rule.target_field}')
        
        if rule.condition:
            self.code_lines.append(f'    if {self._translate_condition(rule.condition)}:')
        
        # Build transform chain
        value_expr = source_var
        
        if rule.transform:
            func_name = rule.transform.split('(')[0]
            value_expr = f'transform_value({source_var}, "{func_name}", {rule.transform[len(func_name)+1:-1]})'
        
        if rule.data_type:
            value_expr = f'{rule.data_type}({value_expr})'
        
        # Handle default value
        if rule.default_value is not None:
            self.code_lines.append(f'    target_item["{rule.target_field}"] = {value_expr} if {source_var} else "{rule.default_value}"')
        else:
            self.code_lines.append(f'    target_item["{rule.target_field}"] = {value_expr}')
        
        self.code_lines.append('')
    
    def _translate_condition(self, condition: str) -> str:
        """Translate mapping language condition to Python."""
        # Basic translation - could be expanded
        return condition.replace('AND', 'and').replace('OR', 'or').replace('NOT', 'not')


def parse_dml_file(filepath: str) -> Mapping:
    """Parse a DML mapping file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    parser = Parser(content)
    return parser.parse()


def generate_python_code(mapping: Mapping) -> str:
    """Generate Python code from mapping definition."""
    generator = CodeGenerator(mapping)
    return generator.generate()


def compile_mapping(input_file: str, output_file: str):
    """Compile a mapping file to Python code."""
    mapping = parse_dml_file(input_file)
    python_code = generate_python_code(mapping)
    
    with open(output_file, 'w') as f:
        f.write(python_code)
    
    print(f"Mapping '{mapping.name}' compiled to {output_file}")
    return mapping


# Example usage
if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 3:
        compile_mapping(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python parser.py <input.map> <output.py>")