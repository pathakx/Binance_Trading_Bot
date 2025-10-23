import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from enhanced_trading_bot import EnhancedTradingBot
from config import API_KEY, API_SECRET, TESTNET, DEFAULT_SYMBOL
from logger import logger

class TradingBotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PrimeTrades - Trading Bot")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Create UI elements first
        self.create_widgets()
        
        # Initialize bot after UI elements are created
        self.bot = None
        self.init_bot()
        
    def init_bot(self):
        """Initialize the trading bot."""
        try:
            self.bot = EnhancedTradingBot(API_KEY, API_SECRET, TESTNET)
            self.update_status("Connected to Binance Futures Testnet", "success")
        except Exception as e:
            self.update_status(f"Failed to connect to Binance API: {e}", "error")
    
    def create_widgets(self):
        """Create all UI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="PrimeTrades - Trading Bot", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Account tab
        account_frame = ttk.Frame(notebook, padding="10")
        notebook.add(account_frame, text="Account")
        
        # Orders tab
        orders_frame = ttk.Frame(notebook, padding="10")
        notebook.add(orders_frame, text="Orders")
        
        # Create account tab widgets
        self.create_account_tab(account_frame)
        
        # Create orders tab widgets
        self.create_orders_tab(orders_frame)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.X, pady=10)
        
        # Status text
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        self.status_text.config(state=tk.DISABLED)
        
        # Update status with initial message
        self.update_status("Ready", "info")
    
    def create_account_tab(self, parent):
        """Create widgets for the account tab."""
        # Account buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Account info button
        account_info_btn = ttk.Button(buttons_frame, text="Get Account Info", 
                                     command=self.get_account_info)
        account_info_btn.pack(side=tk.LEFT, padx=5)
        
        # Balance button
        balance_btn = ttk.Button(buttons_frame, text="Get Balance", 
                                command=self.get_balance)
        balance_btn.pack(side=tk.LEFT, padx=5)
        
        # Asset input for balance
        ttk.Label(buttons_frame, text="Asset:").pack(side=tk.LEFT, padx=(20, 5))
        self.asset_var = tk.StringVar(value="USDT")
        asset_entry = ttk.Entry(buttons_frame, textvariable=self.asset_var, width=10)
        asset_entry.pack(side=tk.LEFT, padx=5)
        
        # Account info display
        account_frame = ttk.LabelFrame(parent, text="Account Information", padding="10")
        account_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.account_text = scrolledtext.ScrolledText(account_frame, height=10, wrap=tk.WORD)
        self.account_text.pack(fill=tk.BOTH, expand=True)
        self.account_text.config(state=tk.DISABLED)
    
    def create_orders_tab(self, parent):
        """Create widgets for the orders tab."""
        # Input frame
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Symbol input
        ttk.Label(input_frame, text="Symbol:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.symbol_var = tk.StringVar(value=DEFAULT_SYMBOL)
        symbol_entry = ttk.Entry(input_frame, textvariable=self.symbol_var, width=15)
        symbol_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Side selection
        ttk.Label(input_frame, text="Side:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.side_var = tk.StringVar(value="BUY")
        side_combo = ttk.Combobox(input_frame, textvariable=self.side_var, values=["BUY", "SELL"], width=10)
        side_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Quantity input
        ttk.Label(input_frame, text="Quantity:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.quantity_var = tk.StringVar(value="0.001")
        quantity_entry = ttk.Entry(input_frame, textvariable=self.quantity_var, width=15)
        quantity_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Price input
        ttk.Label(input_frame, text="Price:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        self.price_var = tk.StringVar()
        price_entry = ttk.Entry(input_frame, textvariable=self.price_var, width=15)
        price_entry.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        
        # Stop price input
        ttk.Label(input_frame, text="Stop Price:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.stop_price_var = tk.StringVar()
        stop_price_entry = ttk.Entry(input_frame, textvariable=self.stop_price_var, width=15)
        stop_price_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Buttons frame
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Market order button
        market_btn = ttk.Button(buttons_frame, text="Place Market Order", 
                               command=self.place_market_order)
        market_btn.pack(side=tk.LEFT, padx=5)
        
        # Limit order button
        limit_btn = ttk.Button(buttons_frame, text="Place Limit Order", 
                              command=self.place_limit_order)
        limit_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop-limit order button
        stop_limit_btn = ttk.Button(buttons_frame, text="Place Stop-Limit Order", 
                                   command=self.place_stop_limit_order)
        stop_limit_btn.pack(side=tk.LEFT, padx=5)
        
        # Open orders button
        open_orders_btn = ttk.Button(buttons_frame, text="Get Open Orders", 
                                    command=self.get_open_orders)
        open_orders_btn.pack(side=tk.LEFT, padx=5)
        
        # Open positions button
        open_positions_btn = ttk.Button(buttons_frame, text="Show Open Positions", 
                                      command=self.show_open_positions)
        open_positions_btn.pack(side=tk.LEFT, padx=5)
        
        # Orders display
        orders_frame = ttk.LabelFrame(parent, text="Orders Information", padding="10")
        orders_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.orders_text = scrolledtext.ScrolledText(orders_frame, height=10, wrap=tk.WORD)
        self.orders_text.pack(fill=tk.BOTH, expand=True)
        self.orders_text.config(state=tk.DISABLED)
    
    def update_status(self, message, status_type="info"):
        """Update the status text area with a message."""
        self.status_text.config(state=tk.NORMAL)
        
        # Add timestamp and format based on status type
        if status_type == "error":
            self.status_text.insert(tk.END, f"ERROR: {message}\n", "error")
            self.status_text.tag_configure("error", foreground="red")
        elif status_type == "success":
            self.status_text.insert(tk.END, f"SUCCESS: {message}\n", "success")
            self.status_text.tag_configure("success", foreground="green")
        else:
            self.status_text.insert(tk.END, f"INFO: {message}\n")
        
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def update_account_text(self, text):
        """Update the account text area."""
        self.account_text.config(state=tk.NORMAL)
        self.account_text.delete(1.0, tk.END)
        self.account_text.insert(tk.END, text)
        self.account_text.config(state=tk.DISABLED)
    
    def update_orders_text(self, text):
        """Update the orders text area."""
        self.orders_text.config(state=tk.NORMAL)
        self.orders_text.delete(1.0, tk.END)
        self.orders_text.insert(tk.END, text)   
        self.orders_text.config(state=tk.DISABLED)
    
    def run_in_thread(self, func, *args, **kwargs):
        """Run a function in a separate thread to avoid UI freezing."""
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
    
    def get_account_info(self):
        """Get account information."""
        self.update_status("Fetching account information...", "info")
        
        def fetch_account():
            try:
                account_info = self.bot.get_account_info()
                
                # Format account info for display
                display_text = "=== Account Information ===\n"
                display_text += f"Account Type: {account_info.get('accountType', 'N/A')}\n"
                display_text += f"Total Initial Margin: {account_info.get('totalInitialMargin', 'N/A')} USDT\n"
                display_text += f"Total Maintenance Margin: {account_info.get('totalMaintMargin', 'N/A')} USDT\n"
                display_text += f"Total Wallet Balance: {account_info.get('totalWalletBalance', 'N/A')} USDT\n"
                display_text += f"Total Unrealized Profit: {account_info.get('totalUnrealizedProfit', 'N/A')} USDT\n"
                display_text += f"Total Margin Balance: {account_info.get('totalMarginBalance', 'N/A')} USDT\n"
                display_text += f"Available Balance: {account_info.get('availableBalance', 'N/A')} USDT\n"
                
                # Update UI
                self.root.after(0, lambda: self.update_account_text(display_text))
                self.root.after(0, lambda: self.update_status("Account information fetched successfully", "success"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Error fetching account info: {e}", "error"))
        
        self.run_in_thread(fetch_account)
    
    def get_balance(self):
        """Get balance for a specific asset."""
        asset = self.asset_var.get()
        self.update_status(f"Fetching balance for {asset}...", "info")
        
        def fetch_balance():
            try:
                balance = self.bot.get_balance(asset)
                
                # Format balance info for display
                display_text = "=== Balance Information ===\n"
                display_text += f"Asset: {asset}\n"
                display_text += f"Available Balance: {balance} {asset}\n"
                
                # Update UI
                self.root.after(0, lambda: self.update_account_text(display_text))
                self.root.after(0, lambda: self.update_status(f"Balance for {asset} fetched successfully", "success"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Error fetching balance: {e}", "error"))
        
        self.run_in_thread(fetch_balance)
    
    def place_market_order(self):
        """Place a market order."""
        symbol = self.symbol_var.get()
        side = self.side_var.get()
        
        try:
            quantity = float(self.quantity_var.get())
        except ValueError:
            self.update_status("Invalid quantity value", "error")
            return
        
        self.update_status(f"Placing {side} market order for {quantity} {symbol}...", "info")
        
        def place_order():
            try:
                order = self.bot.place_market_order(symbol=symbol, side=side, quantity=quantity)
                
                # Format order info for display
                display_text = self._format_order_details(order)
                
                # Update UI
                self.root.after(0, lambda: self.update_orders_text(display_text))
                self.root.after(0, lambda: self.update_status("Market order placed successfully", "success"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Error placing market order: {e}", "error"))
        
        self.run_in_thread(place_order)
    
    def place_limit_order(self):
        """Place a limit order."""
        symbol = self.symbol_var.get()
        side = self.side_var.get()
        
        try:
            quantity = float(self.quantity_var.get())
            price = float(self.price_var.get())
        except ValueError:
            self.update_status("Invalid quantity or price value", "error")
            return
        
        self.update_status(f"Placing {side} limit order for {quantity} {symbol} at {price}...", "info")
        
        def place_order():
            try:
                order = self.bot.place_limit_order(symbol=symbol, side=side, quantity=quantity, price=price)
                
                # Format order info for display
                display_text = self._format_order_details(order)
                
                # Update UI
                self.root.after(0, lambda: self.update_orders_text(display_text))
                self.root.after(0, lambda: self.update_status("Limit order placed successfully", "success"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Error placing limit order: {e}", "error"))
        
        self.run_in_thread(place_order)
    
    def place_stop_limit_order(self):
        """Place a stop-limit order."""
        symbol = self.symbol_var.get()
        side = self.side_var.get()
        
        try:
            quantity = float(self.quantity_var.get())
            price = float(self.price_var.get())
            stop_price = float(self.stop_price_var.get())
        except ValueError:
            self.update_status("Invalid quantity, price, or stop price value", "error")
            return
        
        self.update_status(f"Placing {side} stop-limit order for {quantity} {symbol} at {price} (stop: {stop_price})...", "info")
        
        def place_order():
            try:
                order = self.bot.place_stop_limit_order(
                    symbol=symbol, side=side, quantity=quantity, price=price, stop_price=stop_price
                )
                
                # Format order info for display
                display_text = self._format_order_details(order)
                
                # Update UI
                self.root.after(0, lambda: self.update_orders_text(display_text))
                self.root.after(0, lambda: self.update_status("Stop-limit order placed successfully", "success"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Error placing stop-limit order: {e}", "error"))
        
        self.run_in_thread(place_order)
    
    def get_open_orders(self):
        """Get open orders."""
        symbol = self.symbol_var.get()
        self.update_status(f"Fetching open orders for {symbol}...", "info")
        
        def fetch_orders():
            try:
                orders = self.bot.get_open_orders(symbol)
                
                if not orders:
                    display_text = "No open orders found."
                else:
                    display_text = "=== Open Orders ===\n\n"
                    for order in orders:
                        display_text += self._format_order_details(order) + "\n\n"
                
                # Update UI
                self.root.after(0, lambda: self.update_orders_text(display_text))
                self.root.after(0, lambda: self.update_status("Open orders fetched successfully", "success"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Error fetching open orders: {e}", "error"))
        
        self.run_in_thread(fetch_orders)
    
    def show_open_positions(self):
        """Show all open positions."""
        self.update_status("Fetching open positions...", "info")
        
        def fetch_positions():
            try:
                # Use the existing bot instance to access positions
                positions = self.bot.get_all_positions()
                
                if not positions:
                    display_text = "No open positions found."
                else:
                    display_text = "=== Open Positions ===\n\n"
                    for symbol, quantity in positions.items():
                        display_text += f"Symbol: {symbol}\n"
                        display_text += f"Net Quantity: {quantity}\n"
                        display_text += f"Position Type: {'LONG' if quantity > 0 else 'SHORT'}\n\n"
                
                # Update UI
                self.root.after(0, lambda: self.update_orders_text(display_text))
                self.root.after(0, lambda: self.update_status("Open positions fetched successfully", "success"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"Error fetching open positions: {e}", "error"))
        
        self.run_in_thread(fetch_positions)
    
    def _format_order_details(self, order):
        """Format order details for display."""
        display_text = "=== Order Details ===\n"
        display_text += f"Order ID: {order.get('orderId', 'N/A')}\n"
        display_text += f"Symbol: {order.get('symbol', 'N/A')}\n"
        display_text += f"Side: {order.get('side', 'N/A')}\n"
        display_text += f"Type: {order.get('type', 'N/A')}\n"
        display_text += f"Price: {order.get('price', 'N/A')}\n"
        display_text += f"Original Quantity: {order.get('origQty', 'N/A')}\n"
        display_text += f"Executed Quantity: {order.get('executedQty', 'N/A')}\n"
        display_text += f"Status: {order.get('status', 'N/A')}\n"
        display_text += f"Time In Force: {order.get('timeInForce', 'N/A')}\n"
        
        if 'stopPrice' in order:
            display_text += f"Stop Price: {order.get('stopPrice', 'N/A')}\n"
        
        return display_text

def main():
    root = tk.Tk()
    app = TradingBotUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()