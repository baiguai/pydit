import re

def format_table(text):
    """
    Formats the given text into an ASCII table.
    Handles pipe-separated, whitespace-separated, and markdown-style tables.
    Automatically calculates column widths and adds proper borders.
    Detects manual header separators (`----`) to draw a `+===+` line.
    """
    lines = [line.strip() for line in text.strip().split('\n')]
    
    if not lines:
        return text

    # Define a sentinel for row separators
    ROW_SEPARATOR = ['__SEPARATOR__']

    # --- Pass 1: Parse all lines into a structured list of cells ---
    all_rows = []
    has_header_separator = False

    for i, line in enumerate(lines):
        if not line.strip():
            continue

        # Explicit row separator '----' on its own line
        if line.strip() == '----':
            all_rows.append(ROW_SEPARATOR)
            continue

        # Markdown-style header separator: |---|---| or --- --- --- or |:---|:---|
        is_potential_header_separator = all(c in '-:| ' for c in line) and any(c == '-' for c in line)
        
        if is_potential_header_separator:
            # We are looking for a true header separator, which means there should have been
            # content rows before this line that can act as a header.
            # `all_rows` will contain only actual content cells or ROW_SEPARATORs at this point.
            # If all_rows is not empty and the last added item was not a ROW_SEPARATOR,
            # then the line before this separator can be considered a header.
            if all_rows and all_rows[-1] != ROW_SEPARATOR:
                has_header_separator = True
                continue # Skip adding the separator line to all_rows


        # Regular data row
        cells = []
        # Pipe-separated, including lines that start/end with pipes
        if '|' in line:
            # Strip leading/trailing pipes and then split
            processed_line = line
            if processed_line.startswith('|'): processed_line = processed_line[1:]
            if processed_line.endswith('|'): processed_line = processed_line[:-1]
            cells = [cell.strip() for cell in processed_line.split('|')]
        # Fallback to whitespace-separated (2+ spaces)
        else:
            cells = [cell.strip() for cell in re.split(r'\s{2,}', line) if cell.strip()]
        
        if cells:
            all_rows.append(cells)

    # Filter out any empty rows that might have been added
    all_rows = [row for row in all_rows if row]
    
    if not all_rows:
        return text

    # --- Pass 2: Separate header and data, calculate column widths ---
    header_rows = []
    data_rows = []

    if has_header_separator:
        # Find the first non-separator row and treat it as the header
        first_content_row_idx = -1
        for i, row in enumerate(all_rows):
            if row != ROW_SEPARATOR:
                first_content_row_idx = i
                break
        
        if first_content_row_idx != -1:
            # Header is the first line of content
            header_rows = [all_rows[first_content_row_idx]]
            # Data is everything after
            data_rows = all_rows[first_content_row_idx + 1:]
        else: # No content rows found
            data_rows = all_rows
    else:
        data_rows = all_rows

    # Calculate column widths from all non-separator rows
    content_for_width_calc = [row for row in all_rows if row != ROW_SEPARATOR]
    if not content_for_width_calc:
        return text

    num_columns = max(len(row) for row in content_for_width_calc) if content_for_width_calc else 0
    col_widths = [0] * num_columns
    for row in content_for_width_calc:
        # Pad rows that have fewer columns
        while len(row) < num_columns:
            row.append('')
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # --- Pass 3: Build the formatted table string ---
    def make_line(char="-"):
        return "+" + "+".join(char * (w + 2) for w in col_widths) + "+"

    output = []
    # Top border
    output.append(make_line())

    # Header
    if header_rows:
        for row in header_rows:
            padded_cells = [cell.ljust(col_widths[i]) for i, cell in enumerate(row)]
            output.append("| " + " | ".join(padded_cells) + " |")
        # Header/data separator
        output.append(make_line("="))
    
    # Data
    for row in data_rows:
        if row == ROW_SEPARATOR:
            # Only add a separator line if the output is not empty and the last line isn't already a separator
            if output and output[-1] != make_line():
                output.append(make_line())
        else:
            # Pad rows with fewer columns before formatting
            while len(row) < num_columns:
                row.append('')
            padded_cells = [cell.ljust(col_widths[i]) for i, cell in enumerate(row)]
            output.append("| " + " | ".join(padded_cells) + " |")

    # Only add bottom border if the output is not empty and the last line isn't already a border
    if output and output[-1] != make_line():
        output.append(make_line())
    elif not output and (header_rows or data_rows): # Handle case where table might be empty but still needs borders
        output.append(make_line())

    return "\n".join(output)
