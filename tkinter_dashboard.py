import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# -------------------------
# Sample Data
# -------------------------
data = {
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "Sales": [150, 200, 180, 90, 300, 250],
    "Profit": [50, 80, 60, 100, 150, 120],
}
df = pd.DataFrame(data)

# -------------------------
# Tkinter Window
# -------------------------
root = tk.Tk()
root.title("Dashboard Example")
root.geometry("900x600")

# -------------------------
# Frame Layout
# -------------------------
top_frame = ttk.Frame(root)
top_frame.pack(fill="x", padx=10, pady=5)

table_frame = ttk.Frame(root)
table_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)

chart_frame = ttk.Frame(root)
chart_frame.pack(side="right", fill="both", expand=True, padx=10, pady=5)

# -------------------------
# Table (Treeview)
# -------------------------
tree = ttk.Treeview(table_frame, columns=list(df.columns), show="headings", height=10)

for col in df.columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=100)

for _, row in df.iterrows():
    tree.insert("", "end", values=list(row))

tree.pack(fill="both", expand=True)

# -------------------------
# Matplotlib Charts
# -------------------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 6), dpi=100)

# Bar chart - Sales
ax1.bar(df["Month"], df["Sales"], color="skyblue")
ax1.set_title("Monthly Sales")
ax1.set_ylabel("Sales")

# Line chart - Profit
ax2.plot(df["Month"], df["Profit"], marker="o", color="green")
ax2.set_title("Monthly Profit")
ax2.set_ylabel("Profit")

fig.tight_layout()

# Embed in tkinter
canvas = FigureCanvasTkAgg(fig, master=chart_frame)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True)

# -------------------------
# Run
# -------------------------
root.mainloop()