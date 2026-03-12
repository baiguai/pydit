# Table Formatting Feature in Pydit

## Overview
The table formatting feature allows you to quickly convert selected text into properly formatted ASCII tables with borders.

## Usage

### Key Binding
- **Ctrl+;** - Format selected text as table

### Modes Supported
- **INSERT mode** - Format current line or selected text
- **NORMAL mode** - Format current line or selected text  
- **VISUAL mode** - Format selected text (exits visual mode after formatting)

## Input Formats Supported

### 1. Pipe-separated values with manual header
```
Name | Age | City
---- | --- | ----
John | 25 | New York
Jane | 30 | Los Angeles
```

### 2. Whitespace-separated values with manual header (2+ spaces or tabs)
```
Name  Age  City
----  ---  ----
John  25   New York
Jane  30   Los Angeles
```

### 3. Markdown-style tables with manual header
```
| Name | Age | City |
| ---- | --- | ---- |
| John | 25 | New York |
| Jane | 30 | Los Angeles |
```

### 4. Tables without headers (no automatic header creation)
```
Name | Age | City
John | 25 | New York
Jane | 30 | Los Angeles
```

## Output Format
All input formats are converted to ASCII tables with:
- `+` corners and intersections
- `-` horizontal borders
- `|` vertical borders
- `=` header separator
- Auto-calculated column widths

### Example Output
```
+-------+-----+-------------+
| Name  | Age | City        |
+=======+=====+=============+
| John  | 25  | New York    |
| Jane  | 30  | Los Angeles |
+-------+-----+-------------+
```

### Example Output (without header)
```
+-------+-----+-------------+
| Name  | Age | City        |
| John  | 25  | New York    |
| Jane  | 30  | Los Angeles |
+-------+-----+-------------+
```

## How to Use

1. **In INSERT or NORMAL mode:**
   - Position cursor on any line containing table data
   - Press **Ctrl+;**
   - The current line will be formatted as a table

2. **In VISUAL mode:**
   - Select multiple lines of table data
   - Press **Ctrl+;**
   - Selected lines will be formatted as a table
   - Visual mode will be exited automatically

3. **For single-line tables:**
   - Type or paste a line with pipe or whitespace separators
   - Press **Ctrl+;**
   - The line will be converted to a single-row table

4. **For tables with headers:**
   - Add header row with data
   - Add separator row with `----` (or equivalent dashes)
   - Add data rows
   - Press **Ctrl+;** to format

## Tips
- Use consistent separators in your data for best results
- The function automatically detects pipe vs whitespace separation
- Empty cells are handled gracefully
- Mixed input formats (some lines with pipes, others with spaces) are supported
- **No automatic headers**: Use `----` (or `---- | --- | ----`) to create header separators
- Headers are optional - tables work without separators too

## Error Handling
- If no table data is detected, a message will be shown
- If the selected text is empty, a message will be shown
- Any formatting errors will be displayed in the message area