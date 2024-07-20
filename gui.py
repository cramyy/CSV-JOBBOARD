import tkinter as tk
from tkinter import messagebox
import subprocess

def run_update_script():
    link = entry.get().strip()
    if link:
        root.destroy()
        subprocess.run(['python', 'update_jobs.py', link])
    else:
        messagebox.showerror("Error", "Please enter a valid link.")

root = tk.Tk()
root.title("Job Board Updater")
root.geometry("400x150")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(expand=True, fill='both')

label = tk.Label(frame, text="Please enter the Google Sheet shareable link:")
label.pack(pady=(0, 10))

entry = tk.Entry(frame, width=50)
entry.pack(pady=(0, 10))
entry.focus()

update_button = tk.Button(frame, text="Update Job Board", command=run_update_script)
update_button.pack(side='left', padx=(0, 10))

cancel_button = tk.Button(frame, text="Cancel", command=root.destroy)
cancel_button.pack(side='right')

root.bind('<Return>', lambda event: run_update_script())

if __name__ == '__main__':
    root.mainloop()