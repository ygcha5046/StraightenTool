import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2, numpy as np

from worker import FolderWorker


class StraightenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Straighten Tool")
        self.root.geometry("820x520")
        self.root.resizable(False, False)

        self.worker = None
        self.status_var = tk.StringVar(value="OFF")

        # ===== Status =====
        status_frame = tk.Frame(root)
        status_frame.pack(fill="x", pady=5)

        self.status_dot = tk.Label(
            status_frame, text="●", fg="red", font=("Segoe UI", 14, "bold")
        )
        self.status_dot.pack(side="left", padx=(10, 4))

        tk.Label(
            status_frame,
            text="Status:",
            font=("Segoe UI", 11, "bold")
        ).pack(side="left")

        self.status_text = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 11, "bold")
        )
        self.status_text.pack(side="left", padx=5)

        # ===== Main Layout =====
        main = tk.Frame(root)
        main.pack(fill="both", expand=True, padx=10)

        left = tk.LabelFrame(main, text="Settings", padx=10, pady=10)
        left.pack(side="left", fill="y")

        right = tk.LabelFrame(main, text="Preview", padx=10, pady=10)
        right.pack(side="right", fill="both", expand=True)

        # ===== Settings =====
        def row(label, widget, r):
            tk.Label(left, text=label, width=14, anchor="w").grid(row=r, column=0, pady=5)
            widget.grid(row=r, column=1, pady=5, sticky="w")

        self.in_entry = tk.Entry(left, width=32)
        row("Watch Folder", self.in_entry, 0)
        tk.Button(left, text="Select", command=self.browse_in).grid(row=0, column=2)

        self.out_entry = tk.Entry(left, width=32)
        row("Output Folder", self.out_entry, 1)
        tk.Button(left, text="Select", command=self.browse_out).grid(row=1, column=2)

        self.mode = tk.StringVar(value="auto")
        tk.OptionMenu(left, self.mode, "auto", "manual").grid(row=2, column=1, sticky="w")
        tk.Label(left, text="Mode", width=14, anchor="w").grid(row=2, column=0)

        self.angle_entry = tk.Entry(left, width=8)
        self.angle_entry.insert(0, "0")
        tk.Label(left, text="Manual Angle", width=14, anchor="w").grid(row=3, column=0)
        self.angle_entry.grid(row=3, column=1, sticky="w")

        # Buttons
        tk.Button(left, text="Apply", width=14, command=self.apply).grid(row=4, column=0, pady=15)
        tk.Button(left, text="Disable", width=14, command=self.disable).grid(row=4, column=1)

        # ===== Preview =====
        tk.Button(right, text="Image Preview", command=self.preview_image).pack(pady=5)
        self.preview_label = tk.Label(right, bg="#ddd", width=60, height=22)
        self.preview_label.pack(expand=True, fill="both")

    # ===== Handlers =====
    def browse_in(self):
        p = filedialog.askdirectory()
        if p:
            self.in_entry.delete(0, tk.END)
            self.in_entry.insert(0, p)

    def browse_out(self):
        p = filedialog.askdirectory()
        if p:
            self.out_entry.delete(0, tk.END)
            self.out_entry.insert(0, p)

    def set_status(self, on: bool):
        if on:
            self.status_var.set("ON")
            self.status_dot.config(fg="green")
        else:
            self.status_var.set("OFF")
            self.status_dot.config(fg="red")

    def apply(self):
        if self.worker and self.worker.is_alive():
            return

        try:
            angle = float(self.angle_entry.get())
        except:
            angle = 0.0

        self.worker = FolderWorker(
            self.in_entry.get(),
            self.out_entry.get(),
            self.mode.get(),
            angle
        )
        self.worker.start()
        self.set_status(True)

    def disable(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
        self.set_status(False)

    def preview_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png;*.jpg;*.jpeg")]
        )
        if not path:
            return

        img = cv2.cvtColor(
            cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR),
            cv2.COLOR_BGR2RGB
        )
        pil = Image.fromarray(img)
        pil.thumbnail((420, 320))
        self.tkimg = ImageTk.PhotoImage(pil)
        self.preview_label.config(image=self.tkimg)


if __name__ == "__main__":
    root = tk.Tk()
    StraightenApp(root)
    root.mainloop()
