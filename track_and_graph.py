import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json
import os

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
        self.notebook.pack(expand=1, fill='both')
        print("Created notebook.")

        # Create Tracking tab
        self.tracking_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tracking_frame, text='Tracking')
        print("Created tracking tab.")

        # Create Graphs tab
        self.graphs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.graphs_frame, text='Graphs')
        print("Created graphs tab.")

        self.create_tracking_tab()
        print("Initialized tracking tab content.")

        self.create_graphs_tab()
        print("Initialized graphs tab content.")

    def create_tracking_tab(self):
        print("Creating tracking tab content.")
        # Display current date
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.date_label = ttk.Label(self.tracking_frame, text="Date: " + self.current_date)
        self.date_label.pack()
        print("Displayed current date:", self.current_date)

        # Buttons
        self.button_frame = ttk.Frame(self.tracking_frame)
        self.button_frame.pack()
        print("Created button frame.")

        self.add_item_button = ttk.Button(self.button_frame, text="Add Item", command=self.add_item)
        self.add_item_button.pack(side='left')
        print("Created 'Add Item' button.")

        self.copy_previous_button = ttk.Button(self.button_frame, text="Copy Previous", command=self.copy_previous)
        self.copy_previous_button.pack(side='left')
        print("Created 'Copy Previous' button.")

        self.items_frame = ttk.Frame(self.tracking_frame)
        self.items_frame.pack()
        print("Created items frame.")

        # Load items for the current date
        self.load_items()
        print("Loaded items for the current date.")

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
        print("Created entry for item name.")

        def save_item():
            item_name = entry.get()
            print("Saving item:", item_name)
            if item_name:
                if self.current_date not in self.data:
                    self.data[self.current_date] = {}
                    print("Initialized data for current date.")
                self.data[self.current_date][item_name] = False
                print("Added item to data:", item_name)
                self.save_data()
                self.refresh_items()
                new_item_window.destroy()
                print("New item window closed.")

        save_button = ttk.Button(new_item_window, text="Save", command=save_item)
        save_button.pack()
        print("Created save button for new item.")

    def copy_previous(self):
        print("Copying previous day's items.")
        dates = sorted(self.data.keys())
        print("Available dates:", dates)
        if len(dates) >= 1:
            previous_date = dates[-1]
            print("Previous date:", previous_date)
            if previous_date != self.current_date:
                self.data[self.current_date] = self.data[previous_date].copy()
                print("Copied data from previous date to current date.")
                self.save_data()
                self.refresh_items()
            else:
                print("No previous date to copy from.")
        else:
            print("No data available to copy.")

    def refresh_items(self):
        print("Refreshing items.")
        for widget in self.items_frame.winfo_children():
            widget.destroy()
            print("Destroyed existing item widget.")

        self.load_items()
        print("Reloaded items.")

    def load_items(self):
        print("Loading items.")
        self.check_vars = {}
        if self.current_date in self.data:
            for item_name, completed in self.data[self.current_date].items():
                var = tk.BooleanVar(value=completed)
                print("Loaded item:", item_name, "Completed:", completed)

                cb = ttk.Checkbutton(self.items_frame, text=item_name, variable=var, command=lambda name=item_name, var=var: self.update_item(name, var))
                cb.pack(anchor='w')
                print("Created checkbox for item:", item_name)
                self.check_vars[item_name] = var
        else:
            print("No items for current date.")

    def update_item(self, item_name, var):
        print("Updating item:", item_name)
        self.data[self.current_date][item_name] = var.get()
        print("Set item to:", var.get())
        self.save_data()

    def create_graphs_tab(self):
        print("Creating graphs tab content.")
        # Placeholder for item selection pane and graph view pane
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

        # For simplicity, we'll just show a label in the graph view
        label = ttk.Label(self.graph_view_pane, text="Graphs will be displayed here.")
        label.pack()
        print("Created placeholder for graphs.")

if __name__ == "__main__":
    print("Starting the application.")
    root = tk.Tk()
    app = DailyTrackingApp(root)
    root.mainloop()
    print("Application closed.")
