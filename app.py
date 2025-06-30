import tkinter as tk
from tkinter import ttk, messagebox
import requests

class ExchangeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Currency to Points Converter")
        self.geometry("600x400")
        self.language = tk.StringVar(value="en")
        self.exchange_rates = {}

        self.create_widgets()
        self.update_language()

    def create_widgets(self):
        lang_frame = ttk.Frame(self)
        lang_frame.pack(pady=5, anchor="w", padx=10)
        ttk.Label(lang_frame, text="Language / Язык:").pack(side=tk.LEFT)
        ttk.Radiobutton(lang_frame, text="English", variable=self.language, value="en", command=self.update_language).pack(side=tk.LEFT)
        ttk.Radiobutton(lang_frame, text="Русский", variable=self.language, value="ru", command=self.update_language).pack(side=tk.LEFT)

        self.fetch_button = ttk.Button(self, text="", command=self.fetch_rates)
        self.fetch_button.pack(pady=5, anchor="w", padx=10)

        self.rates_frame = ttk.Frame(self)
        self.rates_frame.pack(pady=5, anchor="w", padx=10)
        self.rate_labels = {}

        for currency in ["USD", "EUR", "PLN", "UAH", "RUB"]:
            lbl = ttk.Label(self.rates_frame, text="", font=("Courier", 10))
            lbl.pack(anchor="w")
            self.rate_labels[currency] = lbl

        io_frame = ttk.Frame(self)
        io_frame.pack(pady=15, fill="x", padx=10)

        left_frame = ttk.Frame(io_frame)
        left_frame.pack(side=tk.LEFT, fill="y", padx=5)

        self.input_label = ttk.Label(left_frame, text="")
        self.input_label.pack(anchor="w")

        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(left_frame, textvariable=self.amount_var, font=("Arial", 14), width=20)
        self.amount_entry.pack(pady=2, ipady=10, fill="x")
        self.amount_entry.bind("<FocusIn>", self.select_all_text)
        self.amount_var.trace_add("write", lambda *args: self.convert_to_points())

        self.currency_var = tk.StringVar(value="USD")
        for c in ["USD", "EUR", "PLN", "UAH", "RUB"]:
            ttk.Radiobutton(left_frame, text=c, variable=self.currency_var, value=c, command=self.convert_to_points).pack(anchor=tk.W)

        right_frame = ttk.Frame(io_frame)
        right_frame.pack(side=tk.LEFT, padx=20, fill="both", expand=True)

        self.points_label = ttk.Label(right_frame, text="")
        self.points_label.pack(anchor="w")

        self.result_var = tk.StringVar()
        self.result_entry = ttk.Entry(right_frame, textvariable=self.result_var, font=("Arial", 14),
                                     justify='center')
        self.result_entry.pack(ipady=10, fill="x")
        self.result_entry.bind("<Button-1>", self.on_result_click)

    def update_language(self):
        lang = self.language.get()
        if lang == "en":
            self.fetch_button.config(text="Fetch Exchange Rates")
            self.result_var.set("Enter amount and select currency")
            self.input_label.config(text="Input your values there")
            self.points_label.config(text="Points")
        else:
            self.fetch_button.config(text="Получить курсы валют")
            self.result_var.set("Введите сумму и выберите валюту")
            self.input_label.config(text="Введите значения здесь")
            self.points_label.config(text="Поинты")
        self.amount_entry.delete(0, tk.END)

    def select_all_text(self, event):
        self.amount_entry.select_range(0, tk.END)
        return "break"

    def fetch_rates(self):
        try:
            url = "https://exchange-rates-v1.onrender.com/exchange?base=USD&currencies=EUR,PLN,UAH,RUB"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            if "rates" in data:
                self.exchange_rates = data["rates"]
                self.exchange_rates["USD"] = 1.0

                for cur, val in self.exchange_rates.items():
                    self.rate_labels[cur].config(text=f"1 USD = {val:.4f} {cur}")

                messagebox.showinfo(
                    "Success" if self.language.get() == "en" else "Успех",
                    "Exchange rates fetched successfully!" if self.language.get() == "en" else "Курсы валют успешно получены!"
                )
                self.convert_to_points()
            else:
                raise Exception("Invalid data format")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch exchange rates.\n{e}")

    def convert_to_points(self):
        if not self.exchange_rates:
            self.result_var.set("")
            return
        try:
            amount = float(self.amount_var.get())
            currency = self.currency_var.get()
            rate_to_usd = self.exchange_rates.get(currency)
            if not rate_to_usd:
                self.result_var.set("")
                return
            usd_amount = amount / rate_to_usd
            points = int(usd_amount * 100000)
            self.result_var.set(str(points))
        except ValueError:
            self.result_var.set("")

    def on_result_click(self, event):
        self.result_entry.selection_range(0, tk.END)
        self.clipboard_clear()
        self.clipboard_append(self.result_var.get())

        # Create popup notification near cursor
        popup = tk.Toplevel(self)
        popup.overrideredirect(True)  # Remove window decorations
        popup.attributes("-topmost", True)  # Keep on top

        label = ttk.Label(popup, text="Copied to clipboard", background="#ffffe0", relief="solid", borderwidth=1)
        label.pack(ipadx=5, ipady=2)

        # Position near cursor (slightly offset so it doesn't cover mouse)
        x = event.x_root + 10
        y = event.y_root + 10
        popup.geometry(f"+{x}+{y}")

        # Destroy popup after 1 second
        popup.after(1000, popup.destroy)

        return "break"


if __name__ == "__main__":
    app = ExchangeApp()
    app.mainloop()
