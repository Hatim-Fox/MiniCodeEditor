
# Mini Code Editor

A lightweight, professional Python code editor built with `PyQt6`, featuring a VS Code-inspired dark theme, file explorer, and syntax highlighting.

## Application Structure

- `main.py`: Entry point and main window layout.
- `editor.py`: Code editor widget with syntax highlighting (using `pygments`) and line numbers.
- `file_manager.py`: File explorer sidebar implementation.
- `styles.py`: QSS Stylesheet for the dark theme.

## Prerequisites

You need Python installed. Then, install the required dependencies:

```bash
pip install PyQt6 pygments
```

## Running the Application

Navigate to the project directory and run:

```bash
python main.py
```

## Features

- **Dark Mode**: Sleek interface inspired by VS Code.
- **File Explorer**: Browse your file system and open files with double-click.
- **Syntax Highlighting**: Python code highlighting (and others via Pygments).
- **Tabbed Editing**: Open multiple files simultaneously.
- **Line Numbers**: Essential for coding.
