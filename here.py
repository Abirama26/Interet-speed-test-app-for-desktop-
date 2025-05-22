import csv
import datetime
import threading
import speedtest
from tkinter import ttk, messagebox, filedialog
import tkinter as tk


class SpeedTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Internet Speed Test with History")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Use basic 'clam' theme (light mode)
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')

        # Fonts
        self.font_title = ("Helvetica", 22, "bold")
        self.font_label = ("Helvetica", 14)
        self.font_status = ("Helvetica", 12, "italic")

        # UI Elements
        ttk.Label(root, text="Internet Speed Test", font=self.font_title).pack(pady=10)

        self.test_button = ttk.Button(root, text="Run Speed Test", command=self.run_speed_test)
        self.test_button.pack(pady=10)

        self.status_label = ttk.Label(root, text="Click 'Run Speed Test' to start.", font=self.font_status, foreground="blue")
        self.status_label.pack()

        # Result labels
        self.download_label = ttk.Label(root, text="Download: -- Mbps", font=self.font_label)
        self.download_label.pack(pady=5)

        self.upload_label = ttk.Label(root, text="Upload: -- Mbps", font=self.font_label)
        self.upload_label.pack(pady=5)

        self.ping_label = ttk.Label(root, text="Ping: -- ms", font=self.font_label)
        self.ping_label.pack(pady=5)

        # History Treeview
        self.tree = ttk.Treeview(root, columns=("Timestamp", "Download", "Upload", "Ping"), show="headings", height=8)
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("Download", text="Download (Mbps)")
        self.tree.heading("Upload", text="Upload (Mbps)")
        self.tree.heading("Ping", text="Ping (ms)")
        self.tree.pack(pady=15, fill=tk.X, padx=20)

        # Export button
        self.export_button = ttk.Button(root, text="Export History to CSV", command=self.export_csv)
        self.export_button.pack(pady=5)

        # Data storage for history
        self.history = []

    def run_speed_test(self):
        self.test_button.config(state="disabled")
        self.status_label.config(text="Running speed test, please wait...", foreground="orange")
        threading.Thread(target=self.speed_test_thread).start()

    def speed_test_thread(self):
        try:
            st = speedtest.Speedtest()
            self.root.after(0, lambda: self.status_label.config(text="Finding best server...", foreground="orange"))
            st.get_best_server()

            self.root.after(0, lambda: self.status_label.config(text="Testing download speed...", foreground="orange"))
            download = st.download() / 1_000_000  # Mbps

            self.root.after(0, lambda: self.status_label.config(text="Testing upload speed...", foreground="orange"))
            upload = st.upload() / 1_000_000      # Mbps

            ping = st.results.ping

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Update UI in main thread
            self.root.after(0, self.update_results, download, upload, ping, timestamp)

        except Exception as e:
            # Show error message on UI
            self.root.after(0, self.show_error, f"Connection error:\n{str(e)}")

    def update_results(self, download, upload, ping, timestamp):
        self.download_label.config(text=f"Download: {download:.2f} Mbps")
        self.upload_label.config(text=f"Upload: {upload:.2f} Mbps")
        self.ping_label.config(text=f"Ping: {ping:.2f} ms")
        self.status_label.config(text="Test complete!", foreground="green")

        # Store in history
        self.history.append((timestamp, f"{download:.2f}", f"{upload:.2f}", f"{ping:.2f}"))
        self.tree.insert("", "end", values=self.history[-1])

        self.test_button.config(state="normal")

    def show_error(self, message):
        self.status_label.config(text=message, foreground="red")
        self.test_button.config(state="normal")

    def export_csv(self):
        if not self.history:
            messagebox.showinfo("No Data", "No test history to export.")
            return

        default_filename = f"speedtest_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=default_filename,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if not file_path:
            return  # User cancelled

        try:
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Download (Mbps)", "Upload (Mbps)", "Ping (ms)"])
                writer.writerows(self.history)
            messagebox.showinfo("Export Success", f"History exported to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeedTestApp(root)
    root.mainloop()
