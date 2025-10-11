import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import csv
import re, os, webbrowser

current_file = None
last_key = ""
quitting = False
mode = "TREE"  # Default mode
search_popup = None
search_var = None
search_listbox = None
search_results = []

command_count = ""
pending_command = ""
yank_buffer = ""
visual_start = None
visual_mode = None  # "char" or "line"



# Help Topics
help_entries = [
    # --- TREE MODE ---
    {"key": "j / k", "mode": "TREE", "description": "Move tree selection down / up"},
    {"key": "l / h", "mode": "TREE", "description": "Expand / collapse folders"},
    {"key": "E / C", "mode": "TREE", "description": "Expand / collapse all"},
    {"key": "J / K", "mode": "TREE", "description": "Move node down / up"},
    {"key": "H / L", "mode": "TREE", "description": "Outdent / indent selected node"},
    {"key": "g g", "mode": "TREE", "description": "Go to first node"},
    {"key": "G", "mode": "TREE", "description": "Go to last node"},
    {"key": "R", "mode": "TREE", "description": "Rename selected node"},
    {"key": "D", "mode": "TREE", "description": "Delete selected node"},
    {"key": "s / S", "mode": "TREE", "description": "Save / Save As"},
    {"key": "o", "mode": "TREE", "description": "Open file"},
    {"key": "/", "mode": "TREE", "description": "Open search dialog"},
    {"key": "?", "mode": "TREE", "description": "Show help dialog"},
    {"key": "i", "mode": "TREE", "description": "Enter NORMAL mode (edit note)"},
    {"key": "v", "mode": "TREE", "description": "Enter VISUAL mode"},
    {"key": "q", "mode": "TREE", "description": "Quit application"},

    # --- NORMAL MODE ---
    {"key": "i", "mode": "NORMAL", "description": "Enter INSERT mode"},
    {"key": "v", "mode": "NORMAL", "description": "Enter VISUAL mode (character)"},
    {"key": "V", "mode": "NORMAL", "description": "Enter VISUAL line mode"},
    {"key": "p", "mode": "NORMAL", "description": "Paste yanked text"},
    {"key": "dd", "mode": "NORMAL", "description": "Delete current line"},
    {"key": "dw", "mode": "NORMAL", "description": "Delete word forward"},
    {"key": "db", "mode": "NORMAL", "description": "Delete word backward"},
    {"key": "gg", "mode": "NORMAL", "description": "Go to start of file"},
    {"key": "G", "mode": "NORMAL", "description": "Go to end of file"},
    {"key": "0", "mode": "NORMAL", "description": "Move to line start"},
    {"key": "$", "mode": "NORMAL", "description": "Move to line end"},
    {"key": "w / b / e", "mode": "NORMAL", "description": "Move forward / back / end of word"},
    {"key": "h / j / k / l", "mode": "NORMAL", "description": "Move left / down / up / right"},
    {"key": "Esc", "mode": "NORMAL", "description": "Return to TREE mode"},

    # --- VISUAL MODE ---
    {"key": "y", "mode": "VISUAL", "description": "Yank (copy) selected text"},
    {"key": "d", "mode": "VISUAL", "description": "Delete selected text (cut)"},
    {"key": "x", "mode": "VISUAL", "description": "Cut selected text"},
    {"key": "p", "mode": "VISUAL", "description": "Paste after selection"},
    {"key": "h / j / k / l", "mode": "VISUAL", "description": "Move selection left / down / up / right"},
    {"key": "w / b / e", "mode": "VISUAL", "description": "Expand / contract selection by word"},
    {"key": "0 / $", "mode": "VISUAL", "description": "Select to line start / line end"},
    {"key": "G / gg", "mode": "VISUAL", "description": "Select to end / start of file"},
    {"key": "Esc", "mode": "VISUAL", "description": "Cancel visual mode"},

    # --- INSERT MODE ---
    {"key": "Any text", "mode": "INSERT", "description": "Type into the editor"},
    {"key": "Esc", "mode": "INSERT", "description": "Return to NORMAL mode (updates node content)"},
]


# File Operations
def newfile():
    global current_file

    for item in tree.get_children():
        tree.delete(item)
    editor.delete(1.0, tk.END)

    current_file = ""

def savefile():
    global current_file
    if not current_file:
        return savefile_as()

    _write_to_csv(current_file)
    print(f"Saved to {current_file}")

def savefile_as():
    global current_file
    filepath = asksaveasfilename(defaultextension=".pyd",
                                 filetypes=[("Pydit Files", "*.pyd"), ("CSV Files", "*.csv")])
    if not filepath:
        return

    _write_to_csv(filepath)
    current_file = filepath
    print(f"Saved As {filepath}")

def quit_app():
    global window, quitting
    try:
        if window and window.winfo_exists():
            quitting = True
            window.destroy()
    except Exception:
        pass



# Links
def open_links_dialog():
    global links_popup

    content = editor.get("1.0", "end-1c")

    # Detect URLs and _note_ patterns
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    urls = re.findall(url_pattern, content)

    note_pattern = r'(?<!\w)_(.+?)_(?!\w)'
    notes = re.findall(note_pattern, content)

    # --- Popup setup ---
    links_popup = tk.Toplevel(window)
    links_popup.configure(bg="black", bd=1, highlightthickness=1, highlightbackground="gray")
    links_popup.overrideredirect(True)
    links_popup.transient(window)
    links_popup.grab_set()

    # Center popup
    win_x, win_y = window.winfo_rootx(), window.winfo_rooty()
    win_w, win_h = window.winfo_width(), window.winfo_height()
    width, height = 500, 300
    x, y = win_x + (win_w - width)//2, win_y + (win_h - height)//2
    links_popup.geometry(f"{width}x{height}+{x}+{y}")

    # Border frame
    border = tk.Frame(links_popup, bg="gray", bd=1)
    border.pack(fill="both", expand=True, padx=1, pady=1)
    
    # Inner container (the black area)
    container = tk.Frame(border, bg="black")
    container.pack(fill="both", expand=True, padx=4, pady=4)

    tk.Label(container, text="Detected Links:", bg="black", fg="white",
             font=("Courier", 11, "bold"), anchor="w").pack(anchor="w", pady=(0, 4))

    listbox = tk.Listbox(
        container, bg="black", fg="white", selectbackground="#333",
        selectforeground="white", relief="flat", highlightthickness=1,
        highlightbackground="gray", activestyle="none", font=("Courier", 10)
    )
    listbox.pack(fill="both", expand=True)

    all_links = []
    for url in urls:
        all_links.append(("url", url))
        listbox.insert(tk.END, f"[URL]  {url}")
    for note in notes:
        all_links.append(("note", note))
        listbox.insert(tk.END, f"[NOTE] {note}")

    if not all_links:
        listbox.insert(tk.END, "No links found in this note.")
        listbox.itemconfig(0, {'fg': 'gray'})
        listbox.configure(state="disabled")
    else:
        listbox.select_set(0)
        listbox.activate(0)
        listbox.see(0)

    def move_selection(offset):
        if not all_links:
            return
        cur = listbox.curselection()
        if not cur:
            return
        idx = cur[0] + offset
        if 0 <= idx < listbox.size():
            listbox.select_clear(0, tk.END)
            listbox.select_set(idx)
            listbox.activate(idx)
            listbox.see(idx)

    def open_selected(event=None):
        if not all_links:
            close_popup()
            return
        sel = listbox.curselection()
        if not sel:
            return
        kind, value = all_links[sel[0]]

        if kind == "url":
            if not value.startswith("http"):
                value = "https://" + value
            webbrowser.open(value)

        elif kind == "note":
            def find_note_by_name(name, parent=""):
                for item in tree.get_children(parent):
                    text = tree.item(item, "text")
                    if text.lower() == name.lower():
                        return item
                    found = find_note_by_name(name, item)
                    if found:
                        return found
                return None

            item = find_note_by_name(value)
            if item:
                tree.selection_set(item)
                tree.focus(item)
                tree.see(item)
                on_tree_select(None)
            elif os.path.exists(value):
                try:
                    if os.name == "nt":
                        os.startfile(value)
                    else:
                        os.system(f'xdg-open "{value}"')
                except Exception as e:
                    print(e)

        close_popup()

    def close_popup(event=None):
        """Close popup and restore key focus."""
        try:
            if links_popup and links_popup.winfo_exists():
                window.unbind("<Button-1>")  # remove global click binding
                links_popup.grab_release()
                links_popup.destroy()
        except Exception:
            pass
        window.focus_force()
        select_tree()

    # Close if click outside popup
    def click_outside(event):
        if not links_popup:
            return
        x1, y1 = links_popup.winfo_rootx(), links_popup.winfo_rooty()
        x2, y2 = x1 + links_popup.winfo_width(), y1 + links_popup.winfo_height()
        if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
            close_popup()

    window.bind("<Button-1>", click_outside)

    # Key bindings
    links_popup.bind("<Escape>", close_popup)
    listbox.bind("<Escape>", close_popup)
    listbox.bind("<Return>", open_selected)
    listbox.bind("j", lambda e: move_selection(1))
    listbox.bind("k", lambda e: move_selection(-1))

    # Force focus
    listbox.focus_set()



# Search Methods
def open_search():
    global search_popup, search_var, search_listbox, search_results

    if search_popup:
        return  # already open

    # Create Toplevel
    search_popup = tk.Toplevel(window)
    search_popup.configure(bg="black", bd=1, highlightthickness=1, highlightbackground="gray")
    search_popup.overrideredirect(True)  # Remove window decorations
    search_popup.transient(window)
    search_popup.grab_set()

    # Center the popup in the middle of the window
    win_x = window.winfo_rootx()
    win_y = window.winfo_rooty()
    win_width = window.winfo_width()
    win_height = window.winfo_height()
    width = 400
    height = 300
    x = win_x + (win_width - width) // 2
    y = win_y + (win_height - height) // 2
    search_popup.geometry(f"{width}x{height}+{x}+{y}")

    # Container
    container = tk.Frame(search_popup, bg="black")
    container.pack(fill="both", expand=True, padx=2, pady=2)

    tk.Label(container, text="Search:", bg="black", fg="white", anchor="w").pack(anchor="w", padx=2, pady=(2, 0))

    search_var = tk.StringVar()
    entry = tk.Entry(
        container,
        textvariable=search_var,
        bg="black",
        fg="white",
        insertbackground="white",
        relief="flat",
        highlightthickness=1,
        highlightbackground="gray",
        highlightcolor="white",
        borderwidth=1,
        font=("Courier", 10)
    )
    entry.pack(fill="x", padx=2, pady=(0, 2))
    entry.focus_set()

    search_listbox = tk.Listbox(
        container,
        bg="black",
        fg="white",
        selectbackground="#333",
        selectforeground="white",
        relief="flat",
        highlightthickness=1,
        highlightbackground="gray",
        activestyle="none",
        font=("Courier", 10)
    )
    search_listbox.pack(fill="both", expand=True, padx=2, pady=(0, 2))

    # Bindings
    search_var.trace_add("write", update_search_results)
    search_popup.bind("<Escape>", close_search)
    search_popup.bind("<Return>", confirm_search_selection)
    search_popup.bind("<Down>", lambda e: move_search_selection(1))
    search_popup.bind("<Up>", lambda e: move_search_selection(-1))

def update_search_results(*args):
    global search_results

    query = search_var.get().strip()
    search_listbox.delete(0, tk.END)
    search_results = []

    name_only = False
    if query.startswith(":"):
        name_only = True
        query = query[1:].strip().lower()
    else:
        query = query.lower()

    def walk_tree(parent_id, path=""):
        for item in tree.get_children(parent_id):
            text = tree.item(item, "text")
            full_path = f"{path}/{text}" if path else text
            values = tree.item(item, "values")
            content = values[0].lower() if values else ""

            if name_only:
                match = query in text.lower()
            else:
                match = query in text.lower() or query in content

            if match:
                search_results.append((full_path, item))
                search_listbox.insert(tk.END, full_path)

            walk_tree(item, full_path)

    walk_tree("")

    if search_results:
        search_listbox.select_set(0)

def move_search_selection(offset):
    cur = search_listbox.curselection()
    if not cur:
        return
    idx = cur[0] + offset
    if 0 <= idx < search_listbox.size():
        search_listbox.select_clear(0, tk.END)
        search_listbox.select_set(idx)
        search_listbox.see(idx)

def confirm_search_selection(event=None):
    global search_popup
    selection = search_listbox.curselection()
    if not selection:
        return
    idx = selection[0]
    _, item_id = search_results[idx]

    # Focus and select the node
    tree.selection_set(item_id)
    tree.focus(item_id)
    tree.see(item_id)
    on_tree_select(None)

    close_search()

def close_search(event=None):
    global search_popup, search_listbox, search_var, search_results
    if search_popup:
        search_popup.destroy()
    search_popup = None
    search_var = None
    search_listbox = None
    search_results = []
    window.focus_force()
    select_tree()



# Mode Method
def set_mode(new_mode):
    global mode
    mode = new_mode
    mode_label.config(text=f"MODE: {mode}")



# Tree Methods
def is_folder(item_id):
    """Return True if the given tree item is a folder (no 'values' content)."""
    return not bool(tree.item(item_id, "values"))

def update_node():
    global tree, editor

    # Ensure tree exists and has a valid selection
    if tree is None:
        return

    try:
        selected = tree.selection()
    except Exception:
        return

    if not selected:
        return

    item = selected[0]

    # Get the editor text and store it in the tree node
    content = editor.get("1.0", "end-1c")

    # If the tree has no 'content' column, store it in the item's 'values'
    current_values = list(tree.item(item, "values"))
    if not current_values:
        current_values = [""]
    if len(current_values) < 1:
        current_values.append("")
    current_values[0] = content
    tree.item(item, values=current_values)

def rename_selected_node(event=None):
    global tree

    selected = tree.selection()
    if not selected:
        return

    item = selected[0]
    x, y, width, height = tree.bbox(item)

    # Get current node name
    old_name = tree.item(item, "text")

    # Create entry widget for renaming
    entry = tk.Entry(tree, fg="white", bg="black", insertbackground="white", borderwidth=0)
    entry.insert(0, old_name)
    entry.select_range(0, tk.END)
    entry.focus_set()
    entry.place(x=x, y=y, width=width, height=height)

    # Commit rename
    def commit_rename(event=None):
        new_name = entry.get().strip()
        if new_name:
            tree.item(item, text=new_name)
        entry.destroy()
        select_tree()

    # Cancel rename
    def cancel_rename(event=None):
        entry.destroy()
        select_tree()

    entry.bind("<Return>", commit_rename)
    entry.bind("<Escape>", cancel_rename)

def select_tree():
    global editor, tree

    selected = tree.selection()

    # If no selection exists, but the tree has items, select the first one
    if not selected:
        items = tree.get_children()
        if items:
            selected = (items[0],)
            tree.selection_set(selected)

    # If there's still nothing to select (tree empty), just move focus to window
    if not selected:
        window.focus_set()
        return "break"

    item = selected[0]
    if item:
        window.after(10, lambda: (tree.focus(item), tree.focus_set()))

def openfile(window):
    global current_file
    filepath = askopenfilename(filetypes=[("Pydit Files", "*.pyd"), ("CSV Files", "*.csv")])
    if not filepath:
        return

    # Clear everything
    for item in tree.get_children():
        tree.delete(item)
    editor.delete(1.0, tk.END)

    current_file = filepath
    window.title(f"Pydit - {filepath}")

    selected_path_to_find = ""
    node_path_map = {}

    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        path = row.get("Path", "").strip()
        node_type = row.get("Type", "").strip()
        content = row.get("Content", "")
        expanded = row.get("Expanded", "").strip().lower() in ("1", "true", "yes")
        selected = row.get("Selected", "").strip().lower() in ("1", "true", "yes")

        if not path:
            continue

        parts = path.split("/")
        name = parts[-1]
        parent_id = ""

        # Traverse the path to find/create parents
        for depth, part in enumerate(parts[:-1]):
            partial_path = "/".join(parts[:depth + 1])
            if partial_path not in node_path_map:
                parent_parent = "/".join(parts[:depth]) if depth > 0 else ""
                parent_node = node_path_map.get(parent_parent, "")
                node_id = tree.insert(parent_node, tk.END, text=part, open=True)
                node_path_map[partial_path] = node_id

        # Insert the final node
        parent_path = "/".join(parts[:-1])
        parent_id = node_path_map.get(parent_path, "")
        if node_type == "folder":
            node_id = tree.insert(parent_id, tk.END, text=name, open=expanded)
        else:  # note
            node_id = tree.insert(parent_id, tk.END, text=name, values=(content,))
        node_path_map[path] = node_id

        if selected:
            selected_path_to_find = path

    # Restore selection
    if selected_path_to_find and selected_path_to_find in node_path_map:
        target_id = node_path_map[selected_path_to_find]
        tree.selection_set(target_id)
        tree.focus(target_id)
        tree.see(target_id)
        on_tree_select(None)

    set_mode("TREE")
    select_tree()

def _write_to_csv(filepath):
    rows = []
    selected_item = tree.selection()
    selected_path = ""

    def get_item_path(item):
        """Return a unique slash-delimited path from root to item."""
        path = []
        while item:
            path.insert(0, tree.item(item, "text"))
            item = tree.parent(item)
        return "/".join(path)

    def write_node(node_id):
        nonlocal selected_path

        text = tree.item(node_id, "text")
        values = tree.item(node_id, "values")
        content = values[0] if values and len(values) > 0 else ""
        expanded = tree.item(node_id, "open")
        path = get_item_path(node_id)

        if selected_item and node_id == selected_item[0]:
            selected_path = path

        # Save folder or note
        if content:  # note
            rows.append([path, "note", content, expanded, selected_path == path])
        else:  # folder
            rows.append([path, "folder", "", expanded, selected_path == path])

        for child in tree.get_children(node_id):
            write_node(child)

    for node in tree.get_children(""):
        write_node(node)

    with open(filepath, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Path", "Type", "Content", "Expanded", "Selected"])
        writer.writerows(rows)

def move_tree_selection(direction):
    """Move up/down (k/j) through visible items."""
    items = tree.get_children("")
    visible_items = []

    # Flatten visible tree (depth-first)
    def add_visible(node):
        visible_items.append(node)
        if tree.item(node, "open"):
            for child in tree.get_children(node):
                add_visible(child)

    for node in items:
        add_visible(node)

    if not visible_items:
        return

    selected = tree.selection()
    if not selected:
        tree.selection_set(visible_items[0])
        tree.focus(visible_items[0])
        return

    current = selected[0]
    try:
        idx = visible_items.index(current)
        new_idx = idx + direction
        if 0 <= new_idx < len(visible_items):
            new_item = visible_items[new_idx]
            tree.selection_set(new_item)
            tree.focus(new_item)
            tree.see(new_item)
    except ValueError:
        pass

def expand_or_enter():
    """If folder collapsed, expand it. Otherwise, focus first child (like Vim 'l')."""
    selected = tree.selection()
    if not selected:
        return
    item = selected[0]

    if not is_folder(item):
        return  # Notes can't be expanded or entered

    if tree.get_children(item):
        if not tree.item(item, "open"):
            tree.item(item, open=True)
        else:
            # Move to first child if already open
            first_child = tree.get_children(item)[0]
            tree.selection_set(first_child)
            tree.focus(first_child)
            tree.see(first_child)

def collapse_or_up():
    """If folder open, collapse it. Otherwise, move to its parent (like Vim 'h')."""
    selected = tree.selection()
    if not selected:
        return
    item = selected[0]

    if is_folder(item) and tree.get_children(item) and tree.item(item, "open"):
        tree.item(item, open=False)
    else:
        parent = tree.parent(item)
        if parent:
            tree.selection_set(parent)
            tree.focus(parent)
            tree.see(parent)

def add_folder():
    """Create a new folder under the selected item (or at root) and trigger rename."""
    global tree

    selected = tree.selection()
    parent = ""

    if selected:
        sel = selected[0]
        is_root = (tree.parent(sel) == "")
        values = tree.item(sel, "values")
        is_note = bool(values)  # notes have a content value tuple

        if is_note:
            # notes → sibling
            parent = tree.parent(sel)
        else:
            # folders → add inside (even if root)
            parent = sel
    else:
        parent = ""  # nothing selected → root-level

    # Insert new folder
    new_id = tree.insert(parent, tk.END, text="New Folder", open=True)

    # Select and rename
    tree.selection_set(new_id)
    tree.focus(new_id)
    tree.see(new_id)
    rename_selected_node()

def add_note():
    """Create a new note under the selected item (or at root) and trigger rename."""
    global tree

    selected = tree.selection()
    parent = ""

    if selected:
        sel = selected[0]
        is_root = (tree.parent(sel) == "")
        values = tree.item(sel, "values")
        is_note = bool(values)

        if is_note:
            # note → sibling
            parent = tree.parent(sel)
        else:
            # folder (even root) → inside it
            parent = sel
    else:
        parent = ""  # nothing selected → root-level

    # Insert new note (store empty content)
    new_id = tree.insert(parent, tk.END, text="New Note", values=("",))

    # Select and rename
    tree.selection_set(new_id)
    tree.focus(new_id)
    tree.see(new_id)
    rename_selected_node()

def delete_selected_node():
    """Delete the currently selected node (and children if folder)."""
    selected = tree.selection()
    if not selected:
        return
    item = selected[0]
    parent = tree.parent(item)
    tree.delete(item)
    if parent:
        tree.selection_set(parent)
        tree.focus(parent)
        tree.see(parent)

def select_first_node():
    global tree
    first_node = tree.get_children()[0]
    tree.selection_set(first_node)
    tree.focus(first_node)

def select_last_node():
    last_node = tree.get_children()[-1]
    tree.selection_set(last_node)
    tree.focus(last_node)

def expand_all(tree):
    for item in tree.get_children():
        tree.item(item, open=True)
        expand_all(tree)

def collapse_all(tree):
    for item in tree.get_children():
        tree.item(item, open=False)
        collapse_all(tree)

def expand_all_with_children(tree, parent):
    for child in tree.get_children(parent):
        tree.item(child, open=True)
        expand_all_with_children(tree, child)

def collapse_all_with_children(tree, parent):
    for child in tree.get_children(parent):
        tree.item(child, open=False)
        collapse_all_with_children(tree, child)
    select_first_node()




# Help Methods
def open_help_dialog():
    global help_popup

    # Prevent duplicates
    if "help_popup" in globals() and help_popup and help_popup.winfo_exists():
        return

    help_popup = tk.Toplevel(window)
    help_popup.configure(bg="black", bd=1, highlightthickness=1, highlightbackground="gray")
    help_popup.overrideredirect(True)
    help_popup.transient(window)
    help_popup.grab_set()

    # Center
    win_x = window.winfo_rootx()
    win_y = window.winfo_rooty()
    win_width = window.winfo_width()
    win_height = window.winfo_height()
    
    # Make help window fill about 3/4 of main window width, and 3/4 of height
    width = int(win_width * 0.75)
    height = int(win_height * 0.75)
    
    # Center it
    x = win_x + (win_width - width) // 2
    y = win_y + (win_height - height) // 2
    
    help_popup.geometry(f"{width}x{height}+{x}+{y}")

    container = tk.Frame(help_popup, bg="black")
    container.pack(fill="both", expand=True, padx=6, pady=6)

    tk.Label(container, text="Key Bindings", fg="white", bg="black",
             font=("Courier", 12, "bold"), anchor="w").pack(anchor="w", pady=(0, 5))

    # Frame to hold listbox + scrollbar
    scroll_frame = tk.Frame(container, bg="black")
    scroll_frame.pack(fill="both", expand=True)
    
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")
    
    listbox = tk.Listbox(
        scroll_frame,
        bg="black",
        fg="white",
        relief="flat",
        selectbackground="#333",
        font=("Courier", 10),
        highlightthickness=1,
        highlightbackground="gray",
        activestyle="none",
        yscrollcommand=scrollbar.set
    )
    listbox.pack(fill="both", expand=True)
    scrollbar.config(command=listbox.yview)
    listbox.focus_set()

    # Header row
    header = f"{'KEY':<12} {'MODE':<8} DESCRIPTION"
    listbox.insert(tk.END, header)
    listbox.insert(tk.END, "-" * 60)
    
    # Items
    for h in help_entries:
        entry = f"{h['key']:<12} {h['mode']:<8} {h['description']}"
        listbox.insert(tk.END, entry)
    
    # Highlight header rows
    listbox.itemconfig(0, {'fg': 'cyan'})
    listbox.itemconfig(1, {'fg': 'gray'})
    
    # Initial selection (first actual entry, skipping header)
    if listbox.size() > 2:
        listbox.select_set(2)
        listbox.activate(2)
        listbox.see(2)
    
    def move_selection(offset):
        cur = listbox.curselection()
        if not cur:
            idx = 2
        else:
            idx = cur[0] + offset
        if idx < 2:
            idx = 2
        elif idx >= listbox.size():
            idx = listbox.size() - 1
        listbox.select_clear(0, tk.END)
        listbox.select_set(idx)
        listbox.activate(idx)
        listbox.see(idx)
    
    # Navigation keys
    help_popup.bind("j", lambda e: move_selection(1))
    help_popup.bind("k", lambda e: move_selection(-1))
    help_popup.bind("<Down>", lambda e: move_selection(1))
    help_popup.bind("<Up>", lambda e: move_selection(-1))
    
    # Close on Escape (from anywhere)
    help_popup.bind("<Escape>", lambda e: close_help_dialog())
    window.bind("<Escape>", lambda e: close_help_dialog())
    
    def close_help_dialog():
        global help_popup
        try:
            if help_popup and help_popup.winfo_exists():
                help_popup.destroy()
        except Exception:
            pass
        help_popup = None
        # Unbind the Escape key used to close help
        window.unbind("<Escape>")
        window.focus_force()
        select_tree()



# Vim Movement
def move_cursor_down(n=1):
    editor.mark_set("insert", f"{editor.index('insert')} +{n}line")
    editor.see("insert")

def move_cursor_up(n=1):
    editor.mark_set("insert", f"{editor.index('insert')} -{n}line")
    editor.see("insert")

def move_cursor_left(n=1):
    editor.mark_set("insert", f"{editor.index('insert')} -{n}char")
    editor.see("insert")

def move_cursor_right(n=1):
    editor.mark_set("insert", f"{editor.index('insert')} +{n}char")
    editor.see("insert")

def move_to_line_start():
    editor.mark_set("insert", "insert linestart")

def move_to_line_end(count=1):
    move_cursor_down(count - 1)
    line_index = editor.index("insert").split(".")[0]
    editor.mark_set("insert", f"{line_index}.end")
    editor.see("insert")
    if mode == "VISUAL":
        update_visual_selection()

def move_to_start_of_file():
    editor.mark_set("insert", "1.0")

def move_to_end_of_file():
    editor.mark_set("insert", "end")

def move_word_forward(n=1):
    for _ in range(n):
        editor.mark_set("insert", "insert wordend +1c")

def move_word_backward(n=1):
    for _ in range(n):
        editor.mark_set("insert", "insert wordstart -1c")

def move_to_word_end(n=1):
    for _ in range(n):
        editor.mark_set("insert", "insert wordend")

def delete_current_line(n=1):
    index = editor.index("insert linestart")
    editor.delete(index, f"{index} +{n}lines")

def delete_word(n=1):
    start = editor.index("insert")
    editor.delete(start, f"{start} wordend +{n-1}word")

def delete_prev_word(n=1):
    start = editor.index("insert wordstart -{0}word".format(n-1))
    editor.delete(start, "insert")



# Visual Helpers
def start_visual_mode(kind="char"):
    global mode, visual_start, visual_mode
    mode = "VISUAL"
    visual_mode = kind
    visual_start = editor.index("insert")

    editor.tag_remove("sel", "1.0", "end")

    if kind == "line":
        # Select the full current line
        line_start = editor.index("insert linestart")
        line_end = editor.index("insert lineend +1c")
        editor.tag_add("sel", line_start, line_end)
    else:
        # Charwise — start from cursor position
        editor.tag_add("sel", visual_start, "insert")

def update_visual_selection():
    global visual_start, visual_mode
    editor.tag_remove("sel", "1.0", "end")

    if visual_mode == "line":
        # Figure out which direction the cursor moved
        start_line = int(visual_start.split(".")[0])
        current_line = int(editor.index("insert").split(".")[0])

        if current_line >= start_line:
            start = f"{start_line}.0"
            end = f"{current_line}.0 lineend +1c"
        else:
            start = f"{current_line}.0"
            end = f"{start_line}.0 lineend +1c"

        editor.tag_add("sel", start, end)

    else:
        # Characterwise selection
        editor.tag_add("sel", visual_start, "insert")

def cancel_visual_mode():
    global mode, visual_start, visual_mode
    editor.tag_remove("sel", "1.0", "end")
    visual_start = None
    visual_mode = None
    set_mode("NORMAL")

def yank_selection():
    global yank_buffer
    try:
        yank_buffer = editor.get("sel.first", "sel.last")
    except Exception:
        pass  # nothing selected

def delete_selection():
    global yank_buffer
    try:
        yank_buffer = editor.get("sel.first", "sel.last")
        editor.delete("sel.first", "sel.last")
    except Exception:
        pass

def cut_selection():
    global yank_buffer
    try:
        yank_buffer = editor.get("sel.first", "sel.last")
        editor.delete("sel.first", "sel.last")
    except Exception:
        pass

def yank_current_line(n=1):
    global yank_buffer
    start = editor.index("insert linestart")
    end = editor.index(f"{start} +{n}lines")
    yank_buffer = editor.get(start, end)

def delete_current_line(n=1):
    global yank_buffer
    start = editor.index("insert linestart")
    end = editor.index(f"{start} +{n}lines")
    yank_buffer = editor.get(start, end)
    editor.delete(start, end)

def paste_text():
    global yank_buffer
    if yank_buffer:
        editor.insert("insert", yank_buffer)



# Key Handling
def on_tree_key(event):
    global editor, tree, window, last_key

    if mode != "TREE":
        return

    key = event.keysym
    selected = tree.selection()
    if not selected:
        return
    item = selected[0]

    parent = tree.parent(item)
    siblings = list(tree.get_children(parent))
    index = siblings.index(item)
    
    if mode == "TREE":
        if key == "q":
            quit_app()
            return "break"
        elif key == "question":
            if event.state & 0x0001 or event.state & 0x0002 or event.state & 0x0004 or event.state & 0x0008 or event.state & 0x00010:
                # Shift or modifier likely held – interpret as '?'
                open_help_dialog()
                return "break"
        elif key == "s":
            savefile()
        elif key == "S":
            savefile_as()
        elif key == "o":
            openfile(window)
        elif key == "n":
            newfile()
        elif key == "C":
            collapse_all_with_children(tree, "")
        elif key == "E":
            expand_all_with_children(tree, "")
        elif key == "j":
            move_tree_selection(1)
            return "break"
        elif key == "k":
            move_tree_selection(-1)
            return "break"
        elif key == "l":
            expand_or_enter()
            return "break"
        elif key == "h":
            collapse_or_up()
            return "break"
        elif key == "g":
            if last_key != "g":
                last_key = "g"
                return false
            else:
                select_first_node()
                last_key = ""
        elif key == "G":
            select_last_node()
        elif key == "J":  # move node down
            if index < len(siblings) - 1:
                tree.move(item, parent, index + 1)
        elif key == "K":  # move node up
            if index > 0:
                tree.move(item, parent, index - 1)
        elif key == "H":  # outdent
            if parent:
                grandparent = tree.parent(parent)
                parent_siblings = list(tree.get_children(grandparent))
                parent_index = parent_siblings.index(parent)
                tree.move(item, grandparent, parent_index + 1)

        elif key == "L":  # indent (make child of previous sibling)
            if index > 0:
                prev_sibling = siblings[index - 1]
                tree.move(item, prev_sibling, "end")
                tree.item(prev_sibling, open=True)
        elif key == "A":
            add_folder()
        elif key == "a":
            add_note()
        elif key == "R":
            rename_selected_node()
        elif key == "D":
            delete_selected_node()
            return "break"
        elif key == "slash":
            open_search()
            return "break"
        elif key == "numbersign":
            open_links_dialog()
        elif key == "v":
            set_mode("VISUAL")
        elif key == "i":
            set_mode("NORMAL")
            editor.focus_set()
            editor

def on_editor_key(event):
    global editor, tree, command_count, pending_command
    global yank_buffer, visual_start, visual_mode, mode

    key = event.keysym

    # ---------------------------------------
    # INSERT MODE
    # ---------------------------------------
    if mode == "INSERT":
        if key == "Escape":
            set_mode("NORMAL")
            update_node()
            return "break"

        return

    # ---------------------------------------
    # NORMAL / VISUAL SHARED LOGIC
    # ---------------------------------------
    elif mode in ("NORMAL", "VISUAL"):

        # VISUAL-only shortcuts (y/d/p)
        if mode == "VISUAL":
            if key == "Escape":
                cancel_visual_mode()
                return "break"
            elif key == "y":
                yank_selection()
                cancel_visual_mode()
                return "break"
            elif key == "d":
                delete_selection()
                cancel_visual_mode()
                return "break"
            elif key == "x":
                cut_selection()
                cancel_visual_mode()
                return "break"
            elif key == "p":
                paste_text()
                cancel_visual_mode()
                return "break"


        # NORMAL-only shortcuts
        if mode == "NORMAL":
            if key == "Escape":
                set_mode("TREE")
                update_node()
                select_tree()
                return "break"

            if key.isdigit():
                if not (key == "0" and command_count == ""):
                    command_count += key
                    return "break"

            if key == "i":
                set_mode("INSERT")
                return "break"
            elif key == "p":
                paste_text()
                return "break"
            elif key == "v":
                start_visual_mode("char")
                return "break"
            elif key == "V":
                start_visual_mode("line")
                return "break"

        # Handle multi-key combos
        if pending_command:
            count = int(command_count) if command_count else 1
            combo = pending_command + key
            pending_command = ""
            command_count = ""

            if combo == "gg":
                move_to_start_of_file()
                if mode == "VISUAL": update_visual_selection()
                return "break"

            elif combo == "dd" and mode == "NORMAL":
                delete_current_line(count)
                return "break"

            elif combo == "dw" and mode == "NORMAL":
                delete_word(count)
                return "break"

            elif combo == "db" and mode == "NORMAL":
                delete_prev_word(count)
                return "break"

        # ---------------------------------------
        # Movement (shared)
        # ---------------------------------------
        count = int(command_count) if command_count else 1
        command_count = ""

        moved = True

        if key in ("j"):
            move_cursor_down(count)
        elif key in ("k"):
            move_cursor_up(count)
        elif key in ("h"):
            move_cursor_left(count)
        elif key in ("l"):
            move_cursor_right(count)
        elif key == "w":
            move_word_forward(count)
        elif key == "b":
            move_word_backward(count)
        elif key == "e":
            move_to_word_end(count)
        elif key == "0":
            move_to_line_start()
        elif key == "$":
            move_to_line_end()
        elif key == "G":
            move_to_end_of_file()
        elif key in ("g", "d", "y"):
            pending_command = key
        else:
            moved = False

        # After movement — update selection in VISUAL mode
        if mode == "VISUAL" and moved:
            update_visual_selection()

        if mode != "INSERT":
            return "break"

    # ---------------------------------------
    # TREE MODE (handled elsewhere)
    # ---------------------------------------
    return "break"

def on_window_key(event):
    global editor, tree
    selected = tree.selection()

    key = event.keysym

    if mode == "TREE" and not selected:
        if key == "s":
            savefile()
        elif key == "A":
            add_folder()
        elif key == "a":
            add_note()
        elif key == "q":
            window.destroy()
            return "break"
        elif key == "S":
            savefile_as()
        elif key == "o":
            openfile(window)
        elif key == "i":
            set_mode("INSERT")
            editor.focus_set()
            return "break"   # stops focus conflicts
        elif key == "v":
            set_mode("VISUAL")
            return "break"

    elif mode == "NORMAL":
        if key == "Escape":
            set_mode("TREE")
            return "break"



# Clicks
def on_editor_click(event):
    set_mode("INSERT")

def on_tree_click(event):
    set_mode("TREE")
    select_tree()



# General
def on_tree_select(event):
    set_mode("TREE")
    selected = tree.selection()
    if not selected:
        return
    item = selected[0]
    editor.delete(1.0, tk.END)
    parent = tree.parent(item)
    if parent:
        content = tree.item(item, "values")[0]
        editor.insert(tk.END, content)

def apply_dark_theme(tree):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="black",
                    fieldbackground="black",
                    foreground="white",
                    rowheight=20,
                    borderwidth=0)
    style.map("Treeview", background=[("selected", "#333")])

def main():
    global tree, editor, mode_label, window, quitting

    window = tk.Tk()
    window.title("Pydit")
    window.geometry("800x500")
    window.configure(bg="black")

    window.columnconfigure(1, weight=1)
    window.rowconfigure(0, weight=1)

    # Left side: treeview
    tree = ttk.Treeview(window, show="tree")
    tree.grid(row=0, column=0, sticky="ns")
    tree.bind("<<TreeviewSelect>>", on_tree_select)
    apply_dark_theme(tree)

    # Right side: text editor
    editor = tk.Text(window, fg="white", bg="black", insertbackground="white", wrap="word")
    editor.grid(row=0, column=1, sticky="nsew")

    # Mode label
    mode_label = tk.Label(window, text=f"MODE: {mode}", fg="white", bg="black")
    mode_label.grid(row=1, column=0, columnspan=2, sticky="w")

    #t  label
    mode_label = tk.Label(window, text=f"MODE: {mode}", fg="white", bg="black")
    mode_label.grid(row=1, column=0, columnspan=2, sticky="w")

    # Global key handling
    window.bind("<Key>", on_window_key)
    window.bind("?", lambda e: open_help_dialog())
    window.bind("<Shift-slash>", lambda e: open_help_dialog())  # fallback for Shift+/ systems
    tree.bind("<Key>", on_tree_key)
    editor.bind("<Key>", on_editor_key)

    editor.bind("<Button-1>", on_editor_click)
    tree.bind("<Button-1>", on_tree_click)

    window.after(100, select_tree)

    window.mainloop()

if __name__ == "__main__":
    main()
