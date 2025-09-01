import tkinter as tk
from tkinter import ttk
from ..components import Card

class RecentPage(ttk.Frame):
    """Placeholder Recent page."""
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app

        card = Card(self)
        card.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        ttk.Label(card, text="Recent files").pack(anchor="w")
        self.listbox = tk.Listbox(card, height=10)
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=6)

        ttk.Button(card, text="Open selected", command=self._open_selected).pack(anchor="e")

        self.refresh()

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for path in self.app.recent_files[-50:][::-1]:
            self.listbox.insert(tk.END, path)

    def _open_selected(self):
        try:
            sel = self.listbox.get(self.listbox.curselection()[0])
        except Exception:
            return
        self.app.navigate("icon")
        self.app.pages["icon"].open_path(sel)
