###########################################
#     ---- Hot Folder Copy ------
# This python script will simply monitor
# a set hot folder and move or copy the 
# files that enter that hot folder to
# the destination
#
# Created by Matt Winer - Glossy Finish
# 4/29/23
########################################### 

import time
import os
import shutil
import tkinter as tk
from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pathlib
import configparser
import platform


class MyHandler(FileSystemEventHandler):
    def __init__(self, destination_path, move_files):
        self.destination_path = destination_path
        self.move_files = move_files

    def on_created(self, event):
        if not event.is_directory:
            source_path = event.src_path
            if self.move_files:
                shutil.move(source_path, self.destination_path)
            else:
                shutil.copy(source_path, self.destination_path)
            print(f"{'Moved' if self.move_files else 'Copied'} {source_path} to {self.destination_path}")


# get the path to the user's AppData folder
app_data_path = os.path.dirname(os.path.abspath(__file__))

# create the config file path
config_file_path = os.path.join(app_data_path, 'config.ini')

# create a config parser instance
config = configparser.ConfigParser()

# create a config parser instance
config = configparser.ConfigParser()

# set the section and option names
section_name = 'Directory'
Hotfolder_option = 'hfPath'
Destfolder_option = 'destPath'
Move_option = 'moveFiles'

# set the default directory path
default_path = os.path.expanduser("~/Desktop")

# read the configuration file if it exists
if os.path.exists('config.ini'):
    config.read('config.ini')
    hf_path = config.get(section_name, Hotfolder_option)
    dest_path = config.get(section_name, Destfolder_option)
    move_files = config.getboolean(section_name, Move_option)
else:
    # create the configuration file with default values
    config.add_section(section_name)
    config.set(section_name, Hotfolder_option, "")
    config.set(section_name,Destfolder_option, "")
    config.set(section_name, Move_option, "True")
    with open('config.ini', 'w') as config_file:
        config.write(config_file)
    hf_path = default_path
    dest_path = default_path
    move_files = True


def browse_folder():
    folder_path = filedialog.askdirectory(initialdir=hf_path)
    folder_var.set(folder_path)
    config.set(section_name, Hotfolder_option, folder_path)
    with open('config.ini', 'w') as config_file:
        config.write(config_file)


def browse_destination():
    destination_path = filedialog.askdirectory(initialdir=dest_path)
    destination_var.set(destination_path)
    config.set(section_name, Destfolder_option, destination_path)
    with open('config.ini', 'w') as config_file:
        config.write(config_file)

def on_radio_button_clicked():
    global move_files
    if move_radio_button_var.get() == True:
        move_files = True
    else:
        move_files = False
    config.set(section_name, Move_option, str(move_files))
    with open('config.ini', 'w') as config_file:
        config.write(config_file)

def start_monitoring():
    global observer
    folder_to_track = folder_var.get()
    destination_path = destination_var.get()
    move_files = move_radio_button_var.get()

    if not folder_to_track or not destination_path:
        status_label.config(text="Please select both folders.")
        return

    event_handler = MyHandler(destination_path, move_files)
    observer = Observer()
    observer.schedule(event_handler, folder_to_track, recursive=True)
    observer.start()
    status_label.config(text=f"Monitoring {folder_to_track} for new files...", fg="green")
    start_button.config(state=tk.DISABLED)
    browse_folder_button.config(state=tk.DISABLED)
    browse_destination_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    move_radio.config(state=tk.DISABLED)
    copy_radio.config(state=tk.DISABLED)


def stop_monitoring():
    observer.stop()
    status_label.config(text="Monitoring stopped.", fg="red")
    start_button.config(state=tk.NORMAL)
    browse_folder_button.config(state=tk.NORMAL)
    browse_destination_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    move_radio.config(state=tk.NORMAL)
    copy_radio.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Hot Folder Copy")
    #root.iconbitmap("GF_Icon.ico")
    root.geometry("600x200")

    folder_var = tk.StringVar()
    destination_var = tk.StringVar()
    move_radio_button_var = tk.BooleanVar()

    if hf_path:
        folder_var.set(hf_path)

    if dest_path: 
        destination_var.set(dest_path)

    folder_frame = tk.Frame(root)
    folder_frame.pack(pady=10)
    folder_label = tk.Label(folder_frame, text="Folder to track:", width=15, anchor='e')
    folder_label.pack(side=tk.LEFT)
    if platform.system() == 'Windows':
        # If on Windows, increase the textbox width
        folder_entry = tk.Entry(folder_frame, textvariable=folder_var, width=50)
    else:
        folder_entry = tk.Entry(folder_frame, textvariable=folder_var, width=30)
    folder_entry.pack(side=tk.LEFT)
    browse_folder_button = tk.Button(folder_frame, text="Browse...", command=browse_folder)
    browse_folder_button.pack(side=tk.LEFT)

    destination_frame = tk.Frame(root)
    destination_frame.pack(pady=10)
    destination_label = tk.Label(destination_frame, text="Destination folder:", width=15, anchor='e')
    destination_label.pack(side=tk.LEFT)
    if platform.system() == 'Windows':
        # If on Windows, increase the textbox width
        destination_entry = tk.Entry(destination_frame, textvariable=destination_var, width=50)
    else:
        destination_entry = tk.Entry(destination_frame, textvariable=destination_var, width=30)
    destination_entry.pack(side=tk.LEFT)
    browse_destination_button = tk.Button(destination_frame, text="Browse...", command=browse_destination)
    browse_destination_button.pack(side=tk.LEFT)

    # Radio buttons to select between copy and move
    radio_frame = tk.Frame(root)
    root.action_var = tk.StringVar()
    root.action_var.set("move")
    radio_frame.pack(pady=0)
    copy_radio = tk.Radiobutton(radio_frame, text="Copy", variable=move_radio_button_var, value="false", command=on_radio_button_clicked)
    move_radio = tk.Radiobutton(radio_frame, text="Move", variable=move_radio_button_var, value="true", command=on_radio_button_clicked)
    copy_radio.pack(side="left", padx=10, pady=0)
    move_radio.pack(side="left", padx=10, pady=0)
    if move_files:
        move_radio_button_var.set(True)
        move_radio.select()
    else:
        move_radio_button_var.set(False)
        copy_radio.select()


    button_frame = tk.Frame(root)
    button_frame.pack(pady=3)
    start_button = tk.Button(button_frame, text="Start Monitoring", command=start_monitoring)
    start_button.pack(side=tk.LEFT)
    stop_button = tk.Button(button_frame, text="Stop Monitoring", command=stop_monitoring, state=tk.DISABLED)
    stop_button.pack(side=tk.LEFT)

    status_label = tk.Label(root, text="Select folders and click 'Start Monitoring' to begin.", fg="red")
    status_label.pack()

    # create the labels
    copyright_label = tk.Label(root, text="Created by Glossy Finish - 2023 - Public Domain")
    version_label = tk.Label(root, text="Version 1.0")

    # configure the font
    font = ("Arial", 8)
    copyright_label.config(font=font)
    version_label.config(font=font)

    # add the labels to the window
    copyright_label.pack(
        side=tk.LEFT,
        anchor=tk.W,
        padx=(10, 0),
        pady=(0, 10)
    )
    version_label.pack(
        side=tk.RIGHT,
        anchor=tk.E,
        padx=(0, 10),
        pady=(0, 10)
    )


    root.mainloop()
