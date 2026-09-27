"""
T H E - TH CONNECT
Professional GUI for LocalXpose TCP Management
"""

import subprocess
import threading
import tkinter as tk
from tkinter import ttk

# --- Configuration ---
LOCLX_PATH = r"C:\loclx-windows-amd64\loclx.exe"
MAX_SLOTS  = 10

# UI Palette
COLORS = {
    "bg": "#0d0d0d",
    "bg_secondary": "#141414",
    "bg_accent": "#1a1a1a",
    "border": "#2a2a2a",
    "cyan": "#00e5ff",
    "green": "#00e676",
    "yellow": "#ffea00",
    "red": "#ff1744",
    "gray": "#555555",
    "white": "#e0e0e0",
    "dim": "#666666"
}

class THConnectApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TH CONNECT")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)
        
        # Center Window
        width, height = 780, 560
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{width}x{height}+{(sw-width)//2}+{(sh-height)//2}")

        self.slots_data = []
        self.processes = [None] * MAX_SLOTS
        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=COLORS["bg"])
        header_frame.pack(pady=(15, 0))
        
        tk.Label(header_frame, text="TH CONNECT", font=("Consolas", 22, "bold"),
                 bg=COLORS["bg"], fg=COLORS["cyan"]).pack()
        tk.Label(header_frame, text="LocalXpose TCP Manager", font=("Consolas", 10),
                 bg=COLORS["bg"], fg=COLORS["dim"]).pack()
        
        tk.Frame(self.root, bg=COLORS["border"], height=1).pack(fill="x", padx=20, pady=10)

        # Table Header
        table_head = tk.Frame(self.root, bg=COLORS["bg_secondary"])
        table_head.pack(fill="x", padx=20)
        
        cols = [("#", 4), ("ENDPOINT", 12), ("LOCAL PORT", 12), ("STATUS", 15)]
        for text, w in cols:
            tk.Label(table_head, text=text, font=("Consolas", 9, "bold"),
                     bg=COLORS["bg_secondary"], fg=COLORS["dim"], width=w).pack(side="left", padx=5)

        tk.Frame(self.root, bg=COLORS["border"], height=1).pack(fill="x", padx=20, pady=5)

        # Slots Container
        self.container = tk.Frame(self.root, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True, padx=20)

        for i in range(MAX_SLOTS):
            self.create_slot(i)

        # Footer
        tk.Frame(self.root, bg=COLORS["border"], height=1).pack(fill="x", padx=20, pady=10)
        footer = tk.Frame(self.root, bg=COLORS["bg"])
        footer.pack(fill="x", padx=20, pady=(0, 15))

        tk.Button(footer, text="⏹  PARAR TUDO", font=("Consolas", 10, "bold"),
                  bg=COLORS["red"], fg=COLORS["white"], relief="flat", 
                  padx=15, cursor="hand2", command=self.stop_all).pack(side="right")

    def create_slot(self, idx):
        row = tk.Frame(self.container, bg=COLORS["bg_accent"], pady=5, padx=8,
                      highlightbackground=COLORS["border"], highlightthickness=1)
        row.pack(fill="x", pady=2)

        # Index
        tk.Label(row, text=str(idx+1), font=("Consolas", 11, "bold"),
                 bg=COLORS["bg_accent"], fg=COLORS["cyan"], width=3).pack(side="left", padx=5)

        # Inputs
        ep_var = tk.StringVar()
        port_var = tk.StringVar()
        
        ent_ep = tk.Entry(row, textvariable=ep_var, font=("Consolas", 11),
                          bg=COLORS["bg"], fg=COLORS["cyan"], insertbackground=COLORS["cyan"],
                          relief="flat", highlightbackground=COLORS["border"],
                          highlightthickness=1, width=12)
        ent_ep.pack(side="left", padx=5)

        ent_port = tk.Entry(row, textvariable=port_var, font=("Consolas", 11),
                            bg=COLORS["bg"], fg=COLORS["yellow"], insertbackground=COLORS["yellow"],
                            relief="flat", highlightbackground=COLORS["border"],
                            highlightthickness=1, width=10)
        ent_port.pack(side="left", padx=5)

        # Status Label
        lbl_status = tk.Label(row, text="○ vazio", font=("Consolas", 10),
                              bg=COLORS["bg_accent"], fg=COLORS["gray"], width=12, anchor="center")
        lbl_status.pack(side="left", padx=10)

        # Action Buttons
        btn_pause = tk.Button(row, text="PAUSAR", font=("Consolas", 9, "bold"),
                              bg=COLORS["border"], fg=COLORS["gray"], relief="flat", 
                              width=8, state="disabled", cursor="hand2")
        btn_pause.pack(side="right", padx=3)

        btn_act = tk.Button(row, text="ATIVAR", font=("Consolas", 9, "bold"),
                            bg=COLORS["cyan"], fg=COLORS["bg"], relief="flat", 
                            width=8, cursor="hand2")
        btn_act.pack(side="right", padx=3)

        # Store references
        self.slots_data.append({
            "ep": ep_var, "port": port_var, "status": lbl_status,
            "btn_act": btn_act, "btn_pause": btn_pause
        })

        # Commands
        btn_act.config(command=lambda i=idx: self.toggle_slot(i))
        btn_pause.config(command=lambda i=idx: self.pause_slot(i))

    def toggle_slot(self, i):
        slot = self.slots_data[i]
        ep = slot["ep"].get().strip()
        port = slot["port"].get().strip()

        if not ep or not port:
            slot["status"].config(text="Campo vazio", fg=COLORS["red"])
            return

        if self.processes[i]:
            self.pause_slot(i)
            return

        # Start Process
        try:
            cmd = [LOCLX_PATH, "tunnel", "tcp", "--port", ep, "--to", f"localhost:{port}"]
            self.processes[i] = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            slot["status"].config(text="● online", fg=COLORS["green"])
            slot["btn_act"].config(text="PAUSAR", bg=COLORS["yellow"], fg=COLORS["bg"])
            slot["btn_pause"].config(state="normal", bg=COLORS["border"], fg=COLORS["gray"])
        except Exception as e:
            slot["status"].config(text="Erro spawn", fg=COLORS["red"])

    def pause_slot(self, i):
        if self.processes[i]:
            self.processes[i].terminate()
            self.processes[i] = None
            
        slot = self.slots_data[i]
        slot["status"].config(text="⏸ pausado", fg=COLORS["yellow"])
        slot["btn_act"].config(text="RETOMAR", bg=COLORS["green"], fg=COLORS["bg"])
        slot["btn_pause"].config(state="disabled", bg=COLORS["border"], fg=COLORS["gray"])

    def stop_all(self):
        for i in range(MAX_SLOTS):
            self.pause_slot(i)
            self.slots_data[i]["status"].config(text="○ vazio", fg=COLORS["gray"])
            self.slots_data[i]["btn_act"].config(text="ATIVAR", bg=COLORS["cyan"])

    def on_close(self):
        for p in self.processes:
            if p: p.terminate()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = THConnectApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
