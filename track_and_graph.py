import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import json
import os
import copy
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

print("Imported necessary modules.")

class DailyTrackingApp:
    def __init__(self, root):
        print("Initializing the Daily Tracking App.")
        self.root = root
        self.root.title("Daily Tracking App")
        print("Set the window title.")

        self.data_file = "tracking_data.json"
        self.load_data()
        print("Loaded data from file.")

        self.current_date = datetime.now().strftime("%Y-%m-%d")
        print("Set current date to today:", self.current_date)

        # Check if current date data exists, if not, copy previous day's items without data
        if self.current_date not in self.data:
            print("Current date data not found. Copying items from previous day.")
            self.copy_previous_items_only()

        self.ui_scale = 1.0
        self.ui_padding = 5

        self.create_widgets()
        print("Created the widgets.")

    def load_data(self):
        print("Loading data from file.")
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
                print("Data loaded:", self.data)
        else:
            self.data = {}
            print("No existing data file. Initialized empty data.")

    def save_data(self):
        print("Saving data to file.")
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f)
            print("Data saved:", self.data)

    def create_widgets(self):
        print("Creating widgets.")
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=1, fill='both', padx=self.ui_padding, pady=self.ui_padding)
        print("Created notebook.")

        # Create Tracking tab
        self.tracking_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tracking_frame, text='Tracking')
        print("Created tracking tab.")

        # Create Graphs tab
        self.graphs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.graphs_frame, text='Graphs')
        print("Created graphs tab.")

        # Create Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text='Settings')
        print("Created settings tab.")

        self.create_tracking_tab()
        print("Initialized tracking tab content.")

        self.create_graphs_tab()
        print("Initialized graphs tab content.")

        self.create_settings_tab()
        print("Initialized settings tab content.")

    def create_tracking_tab(self):
        print("Creating tracking tab content.")
        # Date navigation frame
        self.date_nav_frame = ttk.Frame(self.tracking_frame)
        self.date_nav_frame.pack()
        print("Created date navigation frame.")

        # Previous Day Button
        self.prev_day_button = ttk.Button(self.date_nav_frame, text="< Previous Day", command=self.go_to_previous_day)
        self.prev_day_button.pack(side='left')
        print("Created 'Previous Day' button.")

        # Next Day Button
        self.next_day_button = ttk.Button(self.date_nav_frame, text="Next Day >", command=self.go_to_next_day)
        self.next_day_button.pack(side='left')
        print("Created 'Next Day' button.")

        # Display current date
        self.date_label = ttk.Label(self.tracking_frame, text="Date: " + self.current_date)
        self.date_label.pack()
        print("Displayed current date:", self.current_date)

        # Buttons
        self.button_frame = ttk.Frame(self.tracking_frame)
        self.button_frame.pack()
        print("Created button frame.")

        self.add_folder_button = ttk.Button(self.button_frame, text="Add Folder", command=self.add_folder)
        self.add_folder_button.pack(side='left', padx=self.ui_padding, pady=self.ui_padding)
        print("Created 'Add Folder' button.")

        self.add_item_button = ttk.Button(self.button_frame, text="Add Item", command=self.add_item)
        self.add_item_button.pack(side='left', padx=self.ui_padding, pady=self.ui_padding)
        print("Created 'Add Item' button.")

        self.copy_previous_button = ttk.Button(self.button_frame, text="Copy Previous", command=self.copy_previous)
        self.copy_previous_button.pack(side='left', padx=self.ui_padding, pady=self.ui_padding)
        print("Created 'Copy Previous' button.")

        self.items_frame = ttk.Frame(self.tracking_frame)
        self.items_frame.pack(fill='both', expand=True)
        print("Created items frame.")

        # Create Treeview for items
        self.tree = ttk.Treeview(self.items_frame)
        self.tree.pack(fill='both', expand=True)
        print("Created Treeview for items.")

        # Configure Treeview columns
        self.tree['columns'] = ('Value')
        self.tree.heading('#0', text='Item')
        self.tree.heading('Value', text='Value')
        print("Configured Treeview columns.")

        # Bind Treeview events for drag and drop
        self.tree.bind('<ButtonPress-1>', self.on_tree_item_press)
        self.tree.bind('<B1-Motion>', self.on_tree_item_motion)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_item_release)
        print("Bound Treeview events for drag and drop.")

        # Load items for the current date
        self.load_items()
        print("Loaded items for the current date.")

    def on_tree_item_press(self, event):
        print("Treeview item pressed.")
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.dragged_item = item_id
            print("Dragging item:", self.tree.item(item_id)['text'])
        else:
            self.dragged_item = None

    def on_tree_item_motion(self, event):
        if not self.dragged_item:
            return
        self.tree.move(self.dragged_item, self.tree.parent(self.dragged_item), self.tree.index(self.tree.identify_row(event.y)))
        print("Moved item during drag.")

    def on_tree_item_release(self, event):
        print("Treeview item released.")
        if not self.dragged_item:
            return
        target_item = self.tree.identify_row(event.y)
        if target_item and target_item != self.dragged_item:
            print("Dropped on item:", self.tree.item(target_item)['text'])
            self.move_item_in_data(self.dragged_item, target_item)
            self.save_data()
        else:
            print("Dropped on empty space or same item.")
        self.dragged_item = None

    def move_item_in_data(self, item_id, target_item_id):
        print("Moving item in data.")
        item_path = self.tree.set(item_id, "path")
        target_path = self.tree.set(target_item_id, "path")
        print("Item path:", item_path)
        print("Target path:", target_path)

        # Get item data
        item_data = self.get_item_by_path(self.data[self.current_date], item_path.split('/'))
        # Remove item from old location
        self.remove_item_by_path(self.data[self.current_date], item_path.split('/'))
        # Add item to new location
        target_data = self.get_item_by_path(self.data[self.current_date], target_path.split('/'))
        if 'items' not in target_data:
            target_data['items'] = {}
        target_data['items'][self.tree.item(item_id)['text']] = item_data
        print("Moved item in data structure.")

    def get_item_by_path(self, data_dict, path_list):
        print("Getting item by path:", path_list)
        if not path_list:
            return data_dict
        key = path_list[0]
        if 'items' in data_dict and key in data_dict['items']:
            return self.get_item_by_path(data_dict['items'][key], path_list[1:])
        elif key in data_dict:
            return self.get_item_by_path(data_dict[key], path_list[1:])
        else:
            return None

    def remove_item_by_path(self, data_dict, path_list):
        print("Removing item by path:", path_list)
        if len(path_list) == 1:
            key = path_list[0]
            if 'items' in data_dict and key in data_dict['items']:
                del data_dict['items'][key]
                print("Removed item:", key)
        else:
            key = path_list[0]
            if 'items' in data_dict and key in data_dict['items']:
                self.remove_item_by_path(data_dict['items'][key], path_list[1:])

    def add_folder(self):
        print("Adding a new folder.")
        new_folder_window = tk.Toplevel(self.root)
        new_folder_window.title("Add New Folder")
        print("Created new folder window.")

        label = ttk.Label(new_folder_window, text="Folder Name:")
        label.pack()
        print("Created label for folder name.")

        entry = ttk.Entry(new_folder_window)
        entry.pack()
        entry.focus_set()
        print("Created entry for folder name and set focus.")

        def save_folder():
            folder_name = entry.get()
            print("Saving folder:", folder_name)
            if folder_name:
                if self.current_date not in self.data:
                    self.data[self.current_date] = {}
                    print("Initialized data for current date.")
                if 'folders' not in self.data[self.current_date]:
                    self.data[self.current_date]['folders'] = {}
                self.data[self.current_date]['folders'][folder_name] = {'items': {}}
                print("Added folder to data:", folder_name)
                self.save_data()
                self.refresh_items()
                new_folder_window.destroy()
                print("New folder window closed.")

        # Bind Enter key to save the folder
        entry.bind('<Return>', lambda event: save_folder())
        new_folder_window.bind('<Escape>', lambda event: new_folder_window.destroy())

        save_button = ttk.Button(new_folder_window, text="Save", command=save_folder)
        save_button.pack()
        print("Created save button for new folder.")

    def add_item(self):
        print("Adding a new item.")
        new_item_window = tk.Toplevel(self.root)
        new_item_window.title("Add New Item")
        print("Created new item window.")

        label = ttk.Label(new_item_window, text="Item Name:")
        label.pack()
        print("Created label for item name.")

        entry = ttk.Entry(new_item_window)
        entry.pack()
        entry.focus_set()  # Automatically focus on the entry box
        print("Created entry for item name and set focus.")

        # Type selection
        type_label = ttk.Label(new_item_window, text="Item Type:")
        type_label.pack()
        print("Created label for item type.")

        type_var = tk.StringVar(value="complete/incomplete")
        type_options = ["complete/incomplete", "float", "int", "string"]
        type_dropdown = ttk.Combobox(new_item_window, textvariable=type_var, values=type_options, state="readonly")
        type_dropdown.pack()
        type_dropdown.bind('<Key>', self.dropdown_key_navigation)
        print("Created type dropdown menu.")

        def save_item():
            item_name = entry.get()
            item_type = type_var.get()
            print("Saving item:", item_name, "with type:", item_type)
            if item_name:
                if self.current_date not in self.data:
                    self.data[self.current_date] = {}
                    print("Initialized data for current date.")
                # Find selected folder or root
                selected_item = self.tree.selection()
                parent_folder = ''
                if selected_item:
                    selected_id = selected_item[0]
                    parent_folder = self.tree.set(selected_id, "path")
                    print("Selected parent folder:", parent_folder)
                else:
                    print("No folder selected. Adding to root.")
                # Add item to data
                self.add_item_to_data(item_name, item_type, parent_folder)
                self.save_data()
                self.refresh_items()
                new_item_window.destroy()
                print("New item window closed.")

        # Bind Enter key to save the item
        entry.bind('<Return>', lambda event: save_item())
        type_dropdown.bind('<Return>', lambda event: save_item())
        new_item_window.bind('<Escape>', lambda event: new_item_window.destroy())  # Close window on Escape key

        save_button = ttk.Button(new_item_window, text="Save", command=save_item)
        save_button.pack()
        save_button.bind('<Return>', lambda event: save_item())
        print("Created save button for new item.")

        # Set focus traversal order
        entry.focus_set()
        entry.bind('<Tab>', lambda event: type_dropdown.focus_set())
        type_dropdown.bind('<Tab>', lambda event: save_button.focus_set())

    def add_item_to_data(self, item_name, item_type, parent_path):
        print("Adding item to data at path:", parent_path)
        if not parent_path:
            data_dict = self.data[self.current_date]
        else:
            data_dict = self.get_item_by_path(self.data[self.current_date], parent_path.split('/'))
        if 'items' not in data_dict:
            data_dict['items'] = {}
        data_dict['items'][item_name] = {
            'type': item_type,
            'value': self.get_default_value(item_type)
        }
        print("Added item:", item_name, "to data.")

    def dropdown_key_navigation(self, event):
        # Allow arrow keys to navigate dropdown options
        widget = event.widget
        if event.keysym in ('Up', 'Down'):
            widget.event_generate('<KeyPress-%s>' % event.keysym)
            return 'break'

    def copy_previous(self):
        print("Copying previous day's data.")
        previous_date = self.get_previous_date(self.current_date)
        print("Previous date:", previous_date)
        if previous_date and previous_date in self.data:
            # Use deepcopy to avoid shared references
            self.data[self.current_date] = copy.deepcopy(self.data[previous_date])
            print("Copied data from previous date to current date using deepcopy.")
            self.save_data()
            self.refresh_items()
        else:
            print("No previous date to copy from.")

    def copy_previous_items_only(self):
        print("Copying previous day's items without data.")
        previous_date = self.get_previous_date(self.current_date)
        print("Previous date:", previous_date)
        if previous_date and previous_date in self.data:
            # Copy item names and types without values
            self.data[self.current_date] = copy.deepcopy(self.data[previous_date])
            self.clear_values(self.data[self.current_date])
            print("Copied items from previous date without values.")
            self.save_data()
            self.refresh_items()
        else:
            print("No previous date to copy items from.")

    def clear_values(self, data_dict):
        print("Clearing values in data.")
        for key, value in data_dict.items():
            if 'items' in value:
                self.clear_values(value['items'])
            else:
                value['value'] = self.get_default_value(value['type'])
                print("Cleared value for item:", key)

    def get_default_value(self, item_type):
        print("Getting default value for type:", item_type)
        if item_type == "complete/incomplete":
            return False
        elif item_type in ["float", "int"]:
            return 0
        elif item_type == "string":
            return ""
        else:
            return None

    def get_previous_date(self, date_str):
        print("Calculating previous date from:", date_str)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        previous_date_obj = date_obj - timedelta(days=1)
        previous_date_str = previous_date_obj.strftime("%Y-%m-%d")
        print("Previous date is:", previous_date_str)
        return previous_date_str

    def get_next_date(self, date_str):
        print("Calculating next date from:", date_str)
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        next_date_obj = date_obj + timedelta(days=1)
        next_date_str = next_date_obj.strftime("%Y-%m-%d")
        print("Next date is:", next_date_str)
        return next_date_str

    def go_to_previous_day(self):
        print("Navigating to previous day.")
        self.current_date = self.get_previous_date(self.current_date)
        self.date_label.config(text="Date: " + self.current_date)
        print("Updated current date to:", self.current_date)
        if self.current_date not in self.data:
            print("Current date data not found. Copying items from previous day.")
            self.copy_previous_items_only()
        self.refresh_items()

    def go_to_next_day(self):
        print("Navigating to next day.")
        self.current_date = self.get_next_date(self.current_date)
        self.date_label.config(text="Date: " + self.current_date)
        print("Updated current date to:", self.current_date)
        if self.current_date not in self.data:
            print("Current date data not found. Copying items from previous day.")
            self.copy_previous_items_only()
        self.refresh_items()

    def refresh_items(self):
        print("Refreshing items.")
        # Clear the Treeview
        self.tree.delete(*self.tree.get_children())
        print("Cleared Treeview items.")
        # Reload items
        self.load_items()
        print("Reloaded items.")

    def load_items(self):
        print("Loading items.")
        if self.current_date in self.data:
            self.insert_tree_items('', self.data[self.current_date])
        else:
            print("No items for current date.")

    def insert_tree_items(self, parent, data_dict, parent_path=''):
        print("Inserting tree items.")
        if 'folders' in data_dict:
            for folder_name, folder_data in data_dict['folders'].items():
                folder_id = self.tree.insert(parent, 'end', text=folder_name, open=True)
                folder_path = f"{parent_path}/{folder_name}" if parent_path else folder_name
                self.tree.set(folder_id, 'path', folder_path)
                print("Inserted folder:", folder_name)
                self.insert_tree_items(folder_id, folder_data, folder_path)
        if 'items' in data_dict:
            for item_name, item_info in data_dict['items'].items():
                item_id = self.tree.insert(parent, 'end', text=item_name, values=(item_info['value'],))
                item_path = f"{parent_path}/{item_name}" if parent_path else item_name
                self.tree.set(item_id, 'path', item_path)
                print("Inserted item:", item_name)
        else:
            for key, value in data_dict.items():
                if isinstance(value, dict) and 'type' in value:
                    item_name = key
                    item_info = value
                    item_id = self.tree.insert(parent, 'end', text=item_name, values=(item_info['value'],))
                    item_path = f"{parent_path}/{item_name}" if parent_path else item_name
                    self.tree.set(item_id, 'path', item_path)
                    print("Inserted item:", item_name)

    def create_graphs_tab(self):
        print("Creating graphs tab content.")
        # Paned window dividing item selection and graph view
        self.graphs_pane = ttk.PanedWindow(self.graphs_frame, orient=tk.HORIZONTAL)
        self.graphs_pane.pack(fill=tk.BOTH, expand=1)
        print("Created graphs pane.")

        # Item selection pane
        self.item_selection_pane = ttk.Frame(self.graphs_pane, width=200)
        self.graphs_pane.add(self.item_selection_pane, weight=1)
        print("Created item selection pane.")

        # Graph view pane
        self.graph_view_pane = ttk.Frame(self.graphs_pane)
        self.graphs_pane.add(self.graph_view_pane, weight=4)
        print("Created graph view pane.")

        # Treeview for item selection
        self.graph_tree = ttk.Treeview(self.item_selection_pane)
        self.graph_tree.pack(fill=tk.BOTH, expand=1)
        self.graph_tree.bind('<<TreeviewSelect>>', self.plot_item)
        print("Created Treeview for graph item selection.")

        self.populate_graph_tree()
        print("Populated graph Treeview.")

    def populate_graph_tree(self):
        print("Populating graph Treeview.")
        self.graph_tree.delete(*self.graph_tree.get_children())
        # Build a set of all items across dates
        all_items = {}
        for date in self.data:
            self.collect_graph_items('', self.data[date], all_items)
        # Insert items into the Treeview
        self.insert_graph_tree_items('', all_items)
        print("Inserted items into graph Treeview.")

    def collect_graph_items(self, parent_path, data_dict, all_items):
        if 'folders' in data_dict:
            for folder_name, folder_data in data_dict['folders'].items():
                folder_path = f"{parent_path}/{folder_name}" if parent_path else folder_name
                if folder_path not in all_items:
                    all_items[folder_path] = {'folders': {}, 'items': {}}
                self.collect_graph_items(folder_path, folder_data, all_items[folder_path])
        if 'items' in data_dict:
            for item_name, item_info in data_dict['items'].items():
                item_path = f"{parent_path}/{item_name}" if parent_path else item_name
                if item_info['type'] in ["float", "int", "complete/incomplete"]:
                    all_items.setdefault(parent_path, {'folders': {}, 'items': {}})
                    all_items[parent_path]['items'][item_name] = item_info['type']
        else:
            for key, value in data_dict.items():
                if isinstance(value, dict) and 'type' in value:
                    item_name = key
                    item_info = value
                    if item_info['type'] in ["float", "int", "complete/incomplete"]:
                        all_items.setdefault(parent_path, {'folders': {}, 'items': {}})
                        all_items[parent_path]['items'][item_name] = item_info['type']

    def insert_graph_tree_items(self, parent, items_dict):
        for folder_name, folder_data in items_dict.get('folders', {}).items():
            folder_id = self.graph_tree.insert(parent, 'end', text=folder_name, open=True)
            self.insert_graph_tree_items(folder_id, folder_data)
            print("Inserted folder into graph Treeview:", folder_name)
        for item_name in items_dict.get('items', {}):
            item_id = self.graph_tree.insert(parent, 'end', text=item_name)
            print("Inserted item into graph Treeview:", item_name)

    def plot_item(self, event):
        print("Plotting selected item.")
        selected_items = self.graph_tree.selection()
        if not selected_items:
            print("No item selected.")
            return
        item_id = selected_items[0]
        item_name = self.graph_tree.item(item_id)['text']
        print("Selected item:", item_name)

        dates = sorted(self.data.keys())
        values = []
        labels = []
        for date in dates:
            data_dict = self.data[date]
            item_info = self.find_item_in_data(data_dict, item_name)
            if item_info:
                item_type = item_info['type']
                value = item_info['value']
                try:
                    if item_type == "complete/incomplete":
                        value = 1 if value else 0
                        print("Converted boolean value to:", value)
                    else:
                        value = float(value)
                    values.append(value)
                    labels.append(date)
                    print("Date:", date, "Value:", value)
                except ValueError:
                    print("Invalid value on date:", date)
                    continue

        # Clear previous plot
        for widget in self.graph_view_pane.winfo_children():
            widget.destroy()
            print("Cleared previous plot.")

        # Plot the data
        fig = Figure(figsize=(5 * self.ui_scale, 4 * self.ui_scale), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(labels, values)
        ax.set_title(f"Values of {item_name} over time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value")
        fig.autofmt_xdate()

        canvas = FigureCanvasTkAgg(fig, master=self.graph_view_pane)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        print("Plotted item on graph.")

    def find_item_in_data(self, data_dict, item_name):
        if 'folders' in data_dict:
            for folder_data in data_dict['folders'].values():
                result = self.find_item_in_data(folder_data, item_name)
                if result:
                    return result
        if 'items' in data_dict:
            if item_name in data_dict['items']:
                return data_dict['items'][item_name]
        for key, value in data_dict.items():
            if isinstance(value, dict) and 'type' in value and key == item_name:
                return value
        return None

    def create_settings_tab(self):
        print("Creating settings tab content.")
        padding_label = ttk.Label(self.settings_frame, text="UI Padding:")
        padding_label.pack()
        print("Created padding label.")

        padding_var = tk.DoubleVar(value=self.ui_padding)
        padding_spinbox = ttk.Spinbox(self.settings_frame, from_=0, to=50, increment=1, textvariable=padding_var)
        padding_spinbox.pack()
        print("Created padding spinbox.")

        scale_label = ttk.Label(self.settings_frame, text="UI Scale:")
        scale_label.pack()
        print("Created scale label.")

        scale_var = tk.DoubleVar(value=self.ui_scale)
        scale_spinbox = ttk.Spinbox(self.settings_frame, from_=0.5, to=3.0, increment=0.1, textvariable=scale_var)
        scale_spinbox.pack()
        print("Created scale spinbox.")

        def apply_settings():
            self.ui_padding = padding_var.get()
            self.ui_scale = scale_var.get()
            print("Applied settings: UI Padding =", self.ui_padding, ", UI Scale =", self.ui_scale)
            self.refresh_ui()

        apply_button = ttk.Button(self.settings_frame, text="Apply", command=apply_settings)
        apply_button.pack(pady=self.ui_padding)
        print("Created apply settings button.")

    def refresh_ui(self):
        print("Refreshing UI with new settings.")
        # Recreate widgets with new padding and scale
        for widget in self.root.winfo_children():
            widget.destroy()
            print("Destroyed widget:", widget)
        self.create_widgets()
        print("Recreated widgets with updated settings.")

    def run(self):
        self.root.mainloop()
        print("Application closed.")

if __name__ == "__main__":
    print("Starting the application.")
    root = tk.Tk()
    app = DailyTrackingApp(root)
    app.run()
