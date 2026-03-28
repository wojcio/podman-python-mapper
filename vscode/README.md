# DML Mapper VS Code Extension

This extension provides syntax highlighting and validation for the Data Mapping Language (DML) used in this project.

## Features

- **Syntax Highlighting**: Colorizes keywords, types, strings, numbers, and operators in `.map` files.
- **Real-time Validation**: Automatically runs the Python parser on save to highlight syntax errors.

## Installation

1.  Copy the `vscode` directory to your local machine.
2.  Open the directory in VS Code.
3.  Press `F5` to run the extension in a new [Extension Development Host] window.
4.  Alternatively, you can package it using `vsce` or simply link it to your `.vscode/extensions` folder.

## Configuration

The extension uses the `src/parser.py` file in the project root for validation.

- `dml.pythonPath`: Path to the Python executable (default: `python3`).

## Requirements

- VS Code 1.75.0 or higher.
- Python 3.x installed and accessible in the system path.
