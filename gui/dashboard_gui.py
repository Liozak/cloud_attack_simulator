import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib
import os
import json

matplotlib.use("TkAgg")

ALERT_LOG_PATH = "../detector/alerts.json.log"

class RealTimeDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cloud Attack Detection Dashboard")
        self.geometry("1100x800")

        ttk.Label(self, text="📊 Real-Time Attack Monitor", font=("Helvetica", 20)).pack(pady=10)

        self.tab_control = ttk.Notebook(self)
        self.chart_tab = ttk.Frame(self.tab_control)
        self.table_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.chart_tab, text="Live Charts")
        self.tab_control.add(self.table_tab, text="Alert Table")
        self.tab_control.pack(expand=1, fill="both")

        # Total alert count and filter
        self.control_frame = ttk.Frame(self.chart_tab)
        self.control_frame.pack(fill="x", pady=5)

        self.total_alert_label = ttk.Label(self.control_frame, text="Total Alerts: 0", font=("Helvetica", 12))
        self.total_alert_label.pack(side="left", padx=10)

        ttk.Label(self.control_frame, text="Filter by Type:").pack(side="left")
        self.alert_filter = ttk.Combobox(self.control_frame, values=[], state="readonly")
        self.alert_filter.set("All")
        self.alert_filter.bind("<<ComboboxSelected>>", lambda e: self.update_dashboard())
        self.alert_filter.pack(side="left", padx=5)

        # Matplotlib chart
        self.fig, self.axs = plt.subplots(2, 1, figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_tab)
        self.canvas.get_tk_widget().pack()

        # Scrollable table frame
        table_container = ttk.Frame(self.table_tab)
        table_container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(table_container, columns=("Time", "Type", "Source IP"), show="headings")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Type", text="Alert Type")
        self.tree.heading("Source IP", text="Source IP")

        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Top 5 attackers
        self.top_ip_label = ttk.Label(self.table_tab, text="Top 5 Attacking IPs:", font=("Helvetica", 12))
        self.top_ip_label.pack(pady=5)

        self.top_ip_listbox = tk.Listbox(self.table_tab, height=5)
        self.top_ip_listbox.pack(fill="x", padx=20)

        self.update_dashboard()

    def parse_logs(self):
        data = []
        if not os.path.exists(ALERT_LOG_PATH):
            return pd.DataFrame(data, columns=["timestamp", "type", "ip"])

        with open(ALERT_LOG_PATH, "r") as f:
            lines = f.readlines()

        for line in lines:
            try:
                entry = json.loads(line.strip())
                data.append([entry["timestamp"], entry["type"], entry["ip"]])
            except (json.JSONDecodeError, KeyError):
                continue

        df = pd.DataFrame(data, columns=["timestamp", "type", "ip"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df

    def update_charts(self, df):
        for ax in self.axs:
            ax.clear()

        if not df.empty:
            if self.alert_filter.get() != "All":
                df = df[df["type"] == self.alert_filter.get()]

            counts = df["type"].value_counts()
            df_chart = df.copy()
            df_chart.set_index("timestamp", inplace=True)
            time_series = df_chart.groupby([pd.Grouper(freq="10s"), "type"]).size().unstack(fill_value=0)

            self.axs[0].pie(counts, labels=counts.index, autopct="%1.1f%%")
            self.axs[0].set_title("Alert Types")

            time_series.plot(ax=self.axs[1])
            self.axs[1].set_title("Alerts Over Time")
            self.axs[1].set_ylabel("Count")
        else:
            self.axs[0].text(0.5, 0.5, "No Data", ha="center", va="center")
            self.axs[1].text(0.5, 0.5, "No Data", ha="center", va="center")

        self.canvas.draw()

    def update_table(self, df):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for _, row in df.tail(50).iterrows():
            self.tree.insert("", "end", values=(row["timestamp"].strftime("%H:%M:%S"), row["type"], row["ip"]))

    def update_top_ips(self, df):
        self.top_ip_listbox.delete(0, tk.END)
        top_ips = df["ip"].value_counts().head(5)
        for ip, count in top_ips.items():
            self.top_ip_listbox.insert(tk.END, f"{ip} - {count} alerts")

    def update_dashboard(self):
        df = self.parse_logs()

        alert_types = sorted(df["type"].unique()) if not df.empty else []
        self.alert_filter["values"] = ["All"] + alert_types
        if self.alert_filter.get() not in self.alert_filter["values"]:
            self.alert_filter.set("All")

        self.total_alert_label.config(text=f"Total Alerts: {len(df)}")

        self.update_charts(df)
        self.update_table(df)
        self.update_top_ips(df)

        self.after(3000, self.update_dashboard)

if __name__ == "__main__":
    app = RealTimeDashboard()
    app.mainloop()
