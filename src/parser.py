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
    type: str  # XML, CSV, DB, EDI, JSON
    alias: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TargetConfig:
    """Configuration for data target."""
    type: str  # XML, CSV, DB, EDI, JSON
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentConfig:
    """Configuration for intermediate component."""
    type: str  # DB
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
class IfElseBlock:
    """Conditional block with IF and optional ELSE."""
    condition: str
    if_rules: List[Any]
    else_rules: List[Any] = field(default_factory=list)


@dataclass
class TryCatchBlock:
    """Error handling block with TRY and CATCH."""
    try_rules: List[Any]
    catch_rules: List[Any]
    error_var: Optional[str] = None


@dataclass
class SwitchCaseBlock:
    """Multi-condition dispatch block with SWITCH and CASE."""
    expression: str
    cases: Dict[str, List[Any]]
    default_rules: List[Any] = field(default_factory=list)


@dataclass
class Mapping:
    """Complete mapping definition."""
    name: str
    sources: List[SourceConfig] = field(default_factory=list)
    target: Optional[TargetConfig] = None
    component: Optional[ComponentConfig] = None
    rules: List[MappingRule] = field(default_factory=list)


class Tokenizer:
    """Tokenizes the mapping language input."""
    
    TOKENS = [
        ('WS', r'\s+'),
        ('BLOCK_COMMENT', r'/\*[\s\S]*?\*/'),
        ('COMMENT', r'#.*$'),
        ('MAPPING', r'[Mm][Aa][Pp][Pp][Ii][Nn][Gg]\b'),
        ('SOURCE', r'[Ss][Oo][Uu][Rr][Cc][Ee]\b'),
        ('TARGET', r'[Tt][Aa][Rr][Gg][Ee][Tt]\b'),
        ('RULES', r'[Rr][Uu][Ll][Ee][Ss]\b'),
        ('XML', r'[Xx][Mm][Ll]\b'),
        ('CSV', r'[Cc][Ss][Vv]\b'),
        ('DB', r'[Dd][Bb]\b'),
        ('EDI', r'[Ee][Dd][Ii]\b'),
        ('JSON', r'[Jj][Ss][Oo][Nn]\b'),
        ('COMPONENT', r'[Cc][Oo][Mm][Pp][Oo][Nn][Ee][Nn][Tt]\b'),
        ('TRY', r'[Tt][Rr][Yy]\b'),
        ('CATCH', r'[Cc][Aa][Tt][Cc][Hh]\b'),
        ('SWITCH', r'[Ss][Ww][Ii][Tt][Cc][Hh]\b'),
        ('CASE', r'[Cc][Aa][Ss][Ee]\b'),
        ('IF', r'[Ii][Ff]\b'),
        ('ELSE', r'[Ee][Ll][Ss][Ee]\b'),
        ('TRANSFORM', r'[Tt][Rr][Aa][Nn][Ss][Ff][Oo][Rr][Mm]'),
        ('DEFAULT', r'[Dd][Ee][Ff][Aa][Uu][Ll][Tt]'),
        ('AS', r'[Aa][Ss]\b'),
        ('MAP', r'[Mm][Aa][Pp]\b'),
        ('LOOP', r'[Ll][Oo][Oo][Pp]'),
        ('AGGREGATE', r'[Aa][Gg][Gg][Rr][Ee][Gg][Aa][Tt][Ee]'),
        ('FUNCTION', r'[Ff][Uu][Nn][Cc][Tt][Ii][Oo][Nn]'),
        ('WHEN', r'[Ww][Hh][Ee][Nn]'),
        ('THEN', r'[Tt][Hh][Ee][Nn]'),
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
        ('SLASHPATH', r'[a-zA-Z0-9_/-]+/[a-zA-Z0-9_/]*'),
        ('IDENT', r'[a-zA-Z_][a-zA-Z0-9_]*'),
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
                    if token_type not in ('WS', 'COMMENT', 'BLOCK_COMMENT'):
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
        
        sources = []
        target = None
        component = None
        rules = []
        
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.skip_whitespace()
            
            if self.match('SOURCE'):
                res = self.parse_source_target()
                sources.append(SourceConfig(type=res['type'], alias=res['alias'], config=res['config']))
            elif self.match('TARGET'):
                res = self.parse_source_target()
                target = TargetConfig(type=res['type'], config=res['config'])
            elif self.match('COMPONENT'):
                res = self.parse_source_target()
                component = ComponentConfig(type=res['type'], config=res['config'])
            elif self.match('RULES'):
                rules = self.parse_rules()
            else:
                raise SyntaxError(f"Unexpected token in mapping: {self.current_token()}")
        
        self.expect('RBRACE')
        
        return Mapping(
            name=name,
            sources=sources if sources else [SourceConfig(type='CSV', config={})],
            target=target or TargetConfig(type='CSV', config={}),
            component=component,
            rules=rules
        )
    
    def parse_source_target(self) -> Union[SourceConfig, TargetConfig, ComponentConfig]:
        """Parse SOURCE, TARGET, or COMPONENT configuration."""
        type_token = self.current_token()
        if not type_token:
            raise SyntaxError("Expected configuration type (XML, CSV, DB, EDI, JSON)")
            
        if type_token[0] in ('XML', 'CSV', 'DB', 'EDI', 'JSON', 'IDENT'):
            config_type = type_token[1].upper()
            self.advance()
        else:
            raise SyntaxError(f"Unexpected token for configuration type: {type_token}")
        
        self.skip_whitespace()
        
        alias = None
        if self.match('AS'):
            self.skip_whitespace()
            alias = self.expect('IDENT')[1]
            self.skip_whitespace()
            
        self.expect('LBRACE')
        
        config = {}
        
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.skip_whitespace()
            key_token = self.advance()
            if not key_token or key_token[0] not in ('IDENT', 'TYPE', 'QUERY'): # Allow some keywords as keys
                key = key_token[1]
            else:
                key = key_token[1]
                
            self.skip_whitespace()
            self.expect('COLON')
            self.skip_whitespace()
            value = self.parse_value()
            if isinstance(value, str) and (value.startswith('"') or value.startswith("'")):
                value = value[1:-1]
            config[key] = value
            self.skip_whitespace()
            
            if self.current_token() and self.current_token()[0] == 'COMMA':
                self.advance()
        
        self.expect('RBRACE')
        
        # We don't know if it was SOURCE, TARGET or COMPONENT from inside this method 
        # unless we pass it in, but we can infer or let the caller wrap it.
        # Actually, let's just return the components and let the caller wrap them.
        return {
            'type': config_type,
            'alias': alias,
            'config': config
        } # Changed return type to Dict temporarily to make it easier for the caller
    
    def parse_value(self) -> Any:
        """Parse a value (string, number, or identifier)."""
        token = self.current_token()
        if not token:
            return None
            
        if token[0] == 'STRING':
            self.advance()
            # Keep quotes so CodeGenerator knows it is a literal
            return token[1]
        elif token[0] == 'NUMBER':
            self.advance()
            if '.' in token[1]:
                return float(token[1])
            return int(token[1])
        elif token[0] == 'IDENT':
            self.advance()
            return token[1]
        elif token[0] == 'SLASHPATH':
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
            else:
                raise SyntaxError(f"Unexpected token in rules: {self.current_token()}")
        
        self.expect('RBRACE')
        return rules
    
    def parse_rule(self) -> Union[MappingRule, IfElseBlock, TryCatchBlock, SwitchCaseBlock, Optional[Any]]:
        """Parse a single mapping rule or control flow block."""
        self.skip_whitespace()
        token = self.current_token()
        if not token:
            return None
            
        if self.match('LOOP'):
            return self.parse_loop_rule()
            
        if self.match('IF'):
            return self.parse_if_else_block()
            
        if self.match('TRY'):
            return self.parse_try_catch_block()
            
        if self.match('SWITCH'):
            return self.parse_switch_case_block()
        
        if not self.match('MAP'):
            return None
        
        # Parse source field(s)
        source_fields = []
        
        while True:
            self.skip_whitespace()
            token = self.current_token()
            
            if token and token[0] in ('STRING', 'IDENT', 'SLASHPATH'):
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
        if token and token[0] in ('STRING', 'IDENT', 'SLASHPATH'):
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
    
    def parse_if_else_block(self) -> IfElseBlock:
        """Parse IF condition { rules } [ELSE { rules }] block."""
        condition = self.parse_condition()
        self.skip_whitespace()
        self.expect('LBRACE')
        
        if_rules = []
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.skip_whitespace()
            rule = self.parse_rule()
            if rule: if_rules.append(rule)
            self.skip_whitespace()
        self.expect('RBRACE')
        
        else_rules = []
        self.skip_whitespace()
        if self.match('ELSE'):
            self.skip_whitespace()
            if self.match('LBRACE'):
                while self.current_token() and self.current_token()[0] != 'RBRACE':
                    self.skip_whitespace()
                    rule = self.parse_rule()
                    if rule: else_rules.append(rule)
                    self.skip_whitespace()
                self.expect('RBRACE')
            else:
                rule = self.parse_rule()
                if rule: else_rules.append(rule)
        
        return IfElseBlock(condition=condition, if_rules=if_rules, else_rules=else_rules)

    def parse_try_catch_block(self) -> TryCatchBlock:
        """Parse TRY { rules } CATCH [AS error] { rules } block."""
        self.skip_whitespace()
        self.expect('LBRACE')
        try_rules = []
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.skip_whitespace()
            rule = self.parse_rule()
            if rule: try_rules.append(rule)
            self.skip_whitespace()
        self.expect('RBRACE')
        
        self.skip_whitespace()
        self.expect('CATCH')
        
        error_var = None
        if self.match('AS'):
            error_var = self.expect('IDENT')[1]
            
        self.skip_whitespace()
        self.expect('LBRACE')
        catch_rules = []
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.skip_whitespace()
            rule = self.parse_rule()
            if rule: catch_rules.append(rule)
            self.skip_whitespace()
        self.expect('RBRACE')
        
        return TryCatchBlock(try_rules=try_rules, catch_rules=catch_rules, error_var=error_var)

    def parse_switch_case_block(self) -> SwitchCaseBlock:
        """Parse SWITCH expression { CASE value: { rules } DEFAULT: { rules } } block."""
        self.skip_whitespace()
        expr_token = self.advance()
        expression = expr_token[1] if expr_token else ""
        
        self.skip_whitespace()
        self.expect('LBRACE')
        
        cases = {}
        default_rules = []
        
        while self.current_token() and self.current_token()[0] != 'RBRACE':
            self.skip_whitespace()
            if self.match('CASE'):
                val = self.parse_value()
                # If it's a quoted string, use the value inside
                if isinstance(val, str) and (val.startswith('"') or val.startswith("'")):
                    val = val[1:-1]
                self.expect('COLON')
                self.skip_whitespace()
                self.expect('LBRACE')
                rules = []
                while self.current_token() and self.current_token()[0] != 'RBRACE':
                    self.skip_whitespace()
                    rule = self.parse_rule()
                    if rule: rules.append(rule)
                    self.skip_whitespace()
                self.expect('RBRACE')
                cases[str(val)] = rules
            elif self.match('DEFAULT'):
                self.expect('COLON')
                self.skip_whitespace()
                self.expect('LBRACE')
                while self.current_token() and self.current_token()[0] != 'RBRACE':
                    self.skip_whitespace()
                    rule = self.parse_rule()
                    if rule: default_rules.append(rule)
                    self.skip_whitespace()
                self.expect('RBRACE')
            else:
                raise SyntaxError(f"Expected CASE or DEFAULT in SWITCH block, got {self.current_token()}")
            self.skip_whitespace()
            
        self.expect('RBRACE')
        return SwitchCaseBlock(expression=expression, cases=cases, default_rules=default_rules)

    def parse_condition(self) -> str:
        """Parse a condition expression."""
        # Simple approach: collect tokens until we hit LBRACE or other delimiters
        condition_parts = []
        
        while self.current_token() and self.current_token()[0] not in ('LBRACE', 'RBRACE', 'TRANSFORM', 'DEFAULT', 'AS'):
            token = self.current_token()
            if token[0] not in ('WS', 'COMMENT', 'BLOCK_COMMENT'):
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
        
        main_source = self.mapping.sources[0] if self.mapping.sources else None
        main_target = self.mapping.target
        
        if (main_source and main_source.type == 'XML') or (main_target and main_target.type == 'XML'):
            self.imports.add('import xml.etree.ElementTree as ET')
        
        if (main_source and main_source.type == 'DB') or (main_target and main_target.type == 'DB'):
            self.imports.add('import sqlite3')
        
        if (main_source and main_source.type == 'EDI') or (main_target and main_target.type == 'EDI'):
            self.imports.add('import re')
        
        self.code_lines.extend(sorted(list(self.imports)))
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
        self.code_lines.append('    # Some functions don\'t need a value')
        self.code_lines.append('    if value is None and func_name not in ("now", "today", "coalesce"):')
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
            'concat': 'return str(value) + "".join(str(a) for a in args)',
            'left': 'return str(value)[:int(args[0])] if args else value',
            'right': 'return str(value)[-int(args[0]):] if args else value',
            'len': 'return len(str(value))',
            'split': 'return str(value).split(args[0]) if args else str(value).split()',
            'join': 'return args[0].join(value) if args and isinstance(value, list) else "".join(value) if isinstance(value, list) else value',
            'abs': 'return abs(float(value))',
            'mod': 'return float(value) % float(args[0]) if args else value',
            'pow': 'return float(value) ** float(args[0]) if args else value',
            'sqrt': 'import math; return math.sqrt(float(value))',
            'now': 'import datetime; return datetime.datetime.now().isoformat()',
            'today': 'import datetime; return datetime.date.today().isoformat()',
            'date_diff': 'return date_diff_func(value, *args)',
            'add_days': 'return date_add_func(value, days=int(args[0])) if args else value',
            'add_months': 'return date_add_func(value, months=int(args[0])) if args else value',
            'ifelse': 'return args[0] if value else args[1] if len(args) > 1 else None',
            'coalesce': 'return value if value is not None else next((a for a in args if a is not None), None)',
        }
        
        for func, code in transforms.items():
            self.code_lines.append(f'    if func_name == "{func}":')
            self.code_lines.append(f'        {code}')
        
        self.code_lines.append('    except Exception as e:')
        self.code_lines.append('        print(f"Transform error: {{e}}")')
        self.code_lines.append('    return value')
        self.code_lines.append('')
        
        # Date helper functions
        self.code_lines.append('def _to_datetime(value):')
        self.code_lines.append('    import datetime')
        self.code_lines.append('    if isinstance(value, datetime.datetime): return value')
        self.code_lines.append('    if isinstance(value, datetime.date): return datetime.datetime.combine(value, datetime.time())')
        self.code_lines.append('    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"]:')
        self.code_lines.append('        try: return datetime.datetime.strptime(str(value), fmt)')
        self.code_lines.append('        except ValueError: continue')
        self.code_lines.append('    return None')
        self.code_lines.append('')
        
        self.code_lines.append('def date_diff_func(v1, v2):')
        self.code_lines.append('    d1 = _to_datetime(v1)')
        self.code_lines.append('    d2 = _to_datetime(v2)')
        self.code_lines.append('    if d1 and d2: return (d1 - d2).days')
        self.code_lines.append('    return None')
        self.code_lines.append('')
        
        self.code_lines.append('def date_add_func(v, days=0, months=0):')
        self.code_lines.append('    import datetime')
        self.code_lines.append('    d = _to_datetime(v)')
        self.code_lines.append('    if not d: return v')
        self.code_lines.append('    if days: d += datetime.timedelta(days=days)')
        self.code_lines.append('    if months:')
        self.code_lines.append('        month = d.month - 1 + months')
        self.code_lines.append('        year = d.year + month // 12')
        self.code_lines.append('        month = month % 12 + 1')
        self.code_lines.append('        day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])')
        self.code_lines.append('        d = d.replace(year=year, month=month, day=day)')
        self.code_lines.append('    return d.isoformat()')
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
        main_source = self.mapping.sources[0] if self.mapping.sources else SourceConfig(type='CSV')
        source_type = main_source.type.upper()
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
        self.code_lines.append('    for source_item in data_items:')
        self.code_lines.append('        target_item = {}')
        
        for rule in self.mapping.rules:
            self._generate_rule_code(rule, indent_level=2)
            
        self.code_lines.append('        output_items.append(target_item)')
        
        # Target handling
        main_target = self.mapping.target or TargetConfig(type='CSV')
        target_type = main_target.type.upper()
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
    
    def _generate_rule_code(self, rule: Any, indent_level: int = 2):
        """Generate code for a single mapping rule or control flow block."""
        indent = "    " * indent_level
        
        if isinstance(rule, IfElseBlock):
            self.code_lines.append(f'{indent}# IF Block')
            self.code_lines.append(f'{indent}if {self._translate_condition(rule.condition)}:')
            for sub_rule in rule.if_rules:
                self._generate_rule_code(sub_rule, indent_level + 1)
            
            if rule.else_rules:
                self.code_lines.append(f'{indent}else:')
                for sub_rule in rule.else_rules:
                    self._generate_rule_code(sub_rule, indent_level + 1)
            return

        if isinstance(rule, TryCatchBlock):
            self.code_lines.append(f'{indent}# TRY Block')
            self.code_lines.append(f'{indent}try:')
            for sub_rule in rule.try_rules:
                self._generate_rule_code(sub_rule, indent_level + 1)
            
            err_var = rule.error_var or "e"
            self.code_lines.append(f'{indent}except Exception as {err_var}:')
            for sub_rule in rule.catch_rules:
                self._generate_rule_code(sub_rule, indent_level + 1)
            return

        if isinstance(rule, SwitchCaseBlock):
            self.code_lines.append(f'{indent}# SWITCH Block')
            expr = f'source_item.get("{rule.expression}")'
            self.code_lines.append(f'{indent}switch_val = {expr}')
            
            first = True
            for val, sub_rules in rule.cases.items():
                prefix = "if" if first else "elif"
                self.code_lines.append(f'{indent}{prefix} switch_val == {repr(val)}:')
                for sub_rule in sub_rules:
                    self._generate_rule_code(sub_rule, indent_level + 1)
                first = False
            
            if rule.default_rules:
                self.code_lines.append(f'{indent}else:')
                for sub_rule in rule.default_rules:
                    self._generate_rule_code(sub_rule, indent_level + 1)
            return

        if not isinstance(rule, MappingRule) or not rule.target_field:
            return
        
        # Check if this is a loop rule
        if 'loop(' in str(rule.transform):
            self.code_lines.append(f'{indent}# Loop through {rule.source_field}')
            return
        
        # Check if source_field is a literal or a field name
        if rule.source_field and (rule.source_field.startswith('"') or rule.source_field.startswith("'")):
            source_var = rule.source_field
            is_literal = True
        else:
            source_var = f'source_item.get("{rule.source_field}")'
            is_literal = False
        
        # Build target assignment
        self.code_lines.append(f'{indent}# Rule: {rule.source_field} -> {rule.target_field}')
        
        # In nested blocks, we might want to skip the 'if' if it was already handled by block
        if rule.condition:
            self.code_lines.append(f'{indent}if {self._translate_condition(rule.condition)}:')
            indent += "    "
        
        # Build transform chain
        value_expr = source_var
        
        if rule.transform:
            func_name = rule.transform.split('(')[0]
            value_expr = f'transform_value({source_var}, "{func_name}", {rule.transform[len(func_name)+1:-1]})'
        
        if rule.data_type:
            value_expr = f'{rule.data_type}({value_expr})'
        
        # Handle default value
        if rule.default_value is not None:
            check_var = "True" if is_literal else source_var
            self.code_lines.append(f'{indent}target_item["{rule.target_field}"] = {value_expr} if {check_var} else {repr(rule.default_value)}')
        else:
            self.code_lines.append(f'{indent}target_item["{rule.target_field}"] = {value_expr}')
        
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