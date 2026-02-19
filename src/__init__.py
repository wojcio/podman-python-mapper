"""
DML Mapper - A language for describing data mappings between different formats.

This package provides:
- DML Parser: Parses mapping definition files
- Code Generator: Generates executable Python code from mappings
"""

from .mapper import (
    parse_dml_file,
    generate_python_code,
    compile_mapping,
    Parser,
    CodeGenerator,
)

__version__ = "1.0.0"
__all__ = [
    "parse_dml_file",
    "generate_python_code", 
    "compile_mapping",
    "Parser",
    "CodeGenerator",
]