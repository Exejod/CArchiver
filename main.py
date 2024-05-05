import tkinter as tk
from tkinter import filedialog
import os
import subprocess
import rarfile
import zipfile
import shutil

# Variable to store the default extraction directory
default_extraction_dir = ""


def browse_zip():
    file_path = filedialog.askopenfilename(filetypes=[("Archive files", "*.zip *.rar *.7z")])
    if file_path:
        extract_dir = os.path.splitext(file_path)[0]
        extract_file(file_path, extract_dir)
        show_notification(f'Extracted to {extract_dir}')
        open_extracted_in_finder(extract_dir)
        zip_entry.config(state='normal')
        zip_entry.delete(0, tk.END)
        zip_entry.insert(0, file_path)
        zip_entry.config(state='readonly')
    else:
        zip_entry.config(state='normal')
        zip_entry.delete(0, tk.END)
        zip_entry.insert(0, "Select a ZIP file")
        zip_entry.config(state='readonly')


def extract_file(file_path, extract_dir):
    global default_extraction_dir

    # If the default extraction directory is set, use it; otherwise, use the directory of the archive file
    if default_extraction_dir:
        extract_dir = default_extraction_dir

    # Check file extension and use appropriate extraction method
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.zip':
        extract_zip(file_path, extract_dir)
    elif file_ext == '.rar':
        extract_rar(file_path, extract_dir)
    elif file_ext == '.7z':
        extract_7z(file_path, extract_dir)


def extract_zip(zip_file, extract_dir):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        # Create a directory with the same name as the zip file
        zip_dir_name = os.path.splitext(os.path.basename(zip_file))[0]
        extract_dir = os.path.join(extract_dir, zip_dir_name)
        os.makedirs(extract_dir, exist_ok=True)
        zip_ref.extractall(extract_dir)


def extract_rar(rar_file, extract_dir):
    with rarfile.RarFile(rar_file, 'r') as rar_ref:
        # Create a directory with the same name as the rar file
        rar_dir_name = os.path.splitext(os.path.basename(rar_file))[0]
        extract_dir = os.path.join(extract_dir, rar_dir_name)
        os.makedirs(extract_dir, exist_ok=True)
        rar_ref.extractall(extract_dir)


def extract_7z(archive_file, extract_dir):
    with py7zr.SevenZipFile(archive_file, 'r') as archive_ref:
        # Create a directory with the same name as the 7z file
        archive_dir_name = os.path.splitext(os.path.basename(archive_file))[0]
        extract_dir = os.path.join(extract_dir, archive_dir_name)
        os.makedirs(extract_dir, exist_ok=True)
        archive_ref.extractall(extract_dir)


def compress_file():
    file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.*")])
    if file_path:
        # Compress the selected file
        zip_file_path = shutil.make_archive(os.path.splitext(file_path)[0], 'zip', os.path.dirname(file_path))
        print("Compressed file:", file_path)
        open_compressed_zip_in_finder(zip_file_path)


def compress_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        # Compress the selected folder
        temp_folder_path = os.path.join(os.path.dirname(folder_path), 'temp_folder')
        shutil.copytree(folder_path, temp_folder_path)

        # Set modification time for all files and folders in the temp folder
        for root, dirs, files in os.walk(temp_folder_path):
            for f in files:
                file_path = os.path.join(root, f)
                os.utime(file_path, times=(os.path.getatime(file_path), os.path.getmtime(folder_path)))
            for d in dirs:
                dir_path = os.path.join(root, d)
                os.utime(dir_path, times=(os.path.getatime(dir_path), os.path.getmtime(folder_path)))

        zip_file_path = shutil.make_archive(folder_path, 'zip', temp_folder_path)
        shutil.rmtree(temp_folder_path)
        print("Compressed folder:", folder_path)
        open_compressed_zip_in_finder(zip_file_path)


def set_default_extraction_dir():
    global default_extraction_dir
    default_extraction_dir = filedialog.askdirectory()
    if default_extraction_dir:
        show_notification(f'Default extraction directory set to: {default_extraction_dir}')
        extraction_dir_entry.config(show=f"{extraction_dir_entry}")


def open_extracted_in_finder(path):
    global default_extraction_dir

    if default_extraction_dir:
        subprocess.run(['open', default_extraction_dir])  # Open the default extraction directory in Finder
    else:
        if os.path.isdir(path):
            subprocess.run(['open', path])  # Open the directory in Finder
        else:
            open_in_finder(path)  # Open the file in Finder


def open_in_finder(path):
    subprocess.run(['open', path])  # Open the directory or file in Finder


# Function to set the default extraction directory


# Function to show a notification
def show_notification(message):
    applescript = f'display notification "{message}" with title "CArchive"'
    subprocess.run(['osascript', '-e', applescript], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# Function to create a new file menu
def create_file_menu():
    file_menu = tk.Menu(root)
    file_menu.add_command(label="Exit", command=root.quit)
    file_menu.add_separator()
    file_menu.add_command(label="Set default extraction directory", command=set_default_extraction_dir)
    file_menu.add_separator()
    file_menu.add_command(label="Unarchive a file", command=browse_zip)
    file_menu.add_command(label="Compress File...", command=compress_file)
    file_menu.add_command(label="Compress Folder...", command=compress_folder)
    return file_menu


root = tk.Tk()
root.title("CArchive")
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Add file menu to the menu bar
file_menu = create_file_menu()
menu_bar.add_cascade(label="File", menu=file_menu)

# Set window size
window_width = 800  # Increased width
window_height = 150  # Adjusted height to fit the entry and button
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f'{window_width}x{window_height}+{x}+{y}')


def open_settings():
    # Create a new tkinter Toplevel window
    settings_window = tk.Toplevel(root)
    settings_window.title("Set Extraction Directory")

    # Add widgets and options to the settings window
    label = tk.Label(settings_window, text="Extraction Directory:")
    label.pack()

    global extraction_dir_entry
    extraction_dir_entry = tk.Entry(settings_window, width=800)
    extraction_dir_entry.pack(pady=40)

    # Function to set the default extraction directory when entry is clicked
    def set_extraction_dir_on_click(event):
        set_default_extraction_dir()

    # Bind left mouse button click event to call the function
    extraction_dir_entry.bind("<Button-1>", set_extraction_dir_on_click)

    # Set the geometry of the settings window
    window_width = 800  # Increased width
    window_height = 150  # Adjusted height to fit the entry and button
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    settings_window.geometry(f'{window_width}x{window_height}+{x}+{y}')

    set_button.pack()


def create_settings_menu():
    settings_menu = tk.Menu(root)
    settings_menu.add_command(label="Extracted Output Path", command=open_settings)
    # Add more settings options as needed
    return settings_menu


settings_menu = create_settings_menu()
menu_bar.add_cascade(label="Options", menu=settings_menu)

# Create a frame
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Create a label
label = tk.Label(frame, text="Select an archive file to extract:")
label.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

# Create an entry field
zip_entry = tk.Entry(frame, width=60, state='readonly')  # Adjusted width to fit the window
zip_entry.grid(row=1, column=0, padx=5, pady=5, columnspan=2)  # Spanning two columns

# Create a browse button
browse_button = tk.Button(frame, text="Add file", command=browse_zip, width=10)  # Increased width
browse_button.grid(row=1, column=2, padx=5, pady=5)  # Positioned to the right

label = tk.Label(frame, text="Select a folder to compress:")
label.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

# Create an entry field
zip_entry = tk.Entry(frame, width=60, state='readonly')  # Adjusted width to fit the window
zip_entry.grid(row=1, column=0, padx=5, pady=5, columnspan=2)  # Spanning two columns

# Create a browse button
browse_button = tk.Button(frame, text="Add folder", command=compress_folder, width=10)  # Increased width
browse_button.grid(row=1, column=2, padx=5, pady=5)  # Positioned to the right


def set_default_extraction_dir():
    global default_extraction_dir
    default_extraction_dir = filedialog.askdirectory()
    if default_extraction_dir:
        show_notification(f'Default extraction directory set to: {default_extraction_dir}')
        extraction_dir_entry.config(show=f"{extraction_dir_entry}")


# Run the application
root.mainloop()
