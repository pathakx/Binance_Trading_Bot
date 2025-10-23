import argparse
import sys
from colorama import init, Fore, Style
from trading_bot import BasicBot
from config import API_KEY, API_SECRET, TESTNET, DEFAULT_SYMBOL
from logger import logger

# Initialize colorama
init()

class TradingBotCLI:
    def __init__(self):
        """Initialize the CLI interface."""
        self.bot = None
        self.parser = self._create_parser()
    
    def _create_parser(self):
        """Create command line argument parser."""
        parser = argparse.ArgumentParser(
            description='PrimeTrades - A simplified trading bot for Binance Futures',
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        # Main commands
        subparsers = parser.add_subparsers(dest='command', help='Command to execute')
        
        # Account info command
        account_parser = subparsers.add_parser('account', help='Get account information')
        
        # Balance command
        balance_parser = subparsers.add_parser('balance', help='Get account balance')
        balance_parser.add_argument('--asset', type=str, default='USDT', help='Asset to check balance for (default: USDT)')
        
        # Price command
        price_parser = subparsers.add_parser('price', help='Get current market price')
        price_parser.add_argument('--symbol', type=str, default=DEFAULT_SYMBOL, help=f'Trading symbol (default: {DEFAULT_SYMBOL})')
        
        # Market order command
        market_parser = subparsers.add_parser('market', help='Place a market order')
        market_parser.add_argument('--symbol', type=str, default=DEFAULT_SYMBOL, help=f'Trading symbol (default: {DEFAULT_SYMBOL})')
        market_parser.add_argument('--side', type=str, choices=['BUY', 'SELL'], required=True, help='Order side (BUY or SELL)')
        market_parser.add_argument('--quantity', type=float, required=True, help='Order quantity')
        
        # Limit order command
        limit_parser = subparsers.add_parser('limit', help='Place a limit order')
        limit_parser.add_argument('--symbol', type=str, default=DEFAULT_SYMBOL, help=f'Trading symbol (default: {DEFAULT_SYMBOL})')
        limit_parser.add_argument('--side', type=str, choices=['BUY', 'SELL'], required=True, help='Order side (BUY or SELL)')
        limit_parser.add_argument('--quantity', type=float, required=True, help='Order quantity')
        limit_parser.add_argument('--price', type=float, required=True, help='Limit price')
        
        # Stop limit order command
        stop_limit_parser = subparsers.add_parser('stop', help='Place a stop limit order')
        stop_limit_parser.add_argument('--symbol', type=str, default=DEFAULT_SYMBOL, help=f'Trading symbol (default: {DEFAULT_SYMBOL})')
        stop_limit_parser.add_argument('--side', type=str, choices=['BUY', 'SELL'], required=True, help='Order side (BUY or SELL)')
        stop_limit_parser.add_argument('--quantity', type=float, required=True, help='Order quantity')
        stop_limit_parser.add_argument('--price', type=float, required=True, help='Limit price')
        stop_limit_parser.add_argument('--stop_price', type=float, required=True, help='Stop price')
        
        # Open orders command
        open_orders_parser = subparsers.add_parser('open_orders', help='Get open orders')
        open_orders_parser.add_argument('--symbol', type=str, default=None, help='Trading symbol (default: all symbols)')
        
        # Cancel order command
        cancel_parser = subparsers.add_parser('cancel', help='Cancel an order')
        cancel_parser.add_argument('--symbol', type=str, required=True, help='Trading symbol')
        cancel_parser.add_argument('--order_id', type=int, required=True, help='Order ID to cancel')
        
        return parser
    
    def _initialize_bot(self):
        """Initialize the trading bot."""
        if self.bot is None:
            try:
                self.bot = BasicBot(API_KEY, API_SECRET, TESTNET)
                print(f"{Fore.GREEN}✓ Connected to Binance {'TESTNET' if TESTNET else 'PRODUCTION'}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}✗ Failed to connect to Binance API: {e}{Style.RESET_ALL}")
                sys.exit(1)
    
    def _print_account_info(self, account_info):
        """Print account information in a formatted way."""
        print(f"\n{Fore.CYAN}=== Account Information ==={Style.RESET_ALL}")
        print(f"Account Type: {account_info.get('accountType', 'N/A')}")
        print(f"Total Initial Margin: {account_info.get('totalInitialMargin', 'N/A')} USDT")
        print(f"Total Maintenance Margin: {account_info.get('totalMaintMargin', 'N/A')} USDT")
        print(f"Total Wallet Balance: {account_info.get('totalWalletBalance', 'N/A')} USDT")
        print(f"Total Unrealized Profit: {account_info.get('totalUnrealizedProfit', 'N/A')} USDT")
        print(f"Total Margin Balance: {account_info.get('totalMarginBalance', 'N/A')} USDT")
        print(f"Available Balance: {account_info.get('availableBalance', 'N/A')} USDT")
    
    def _print_order_details(self, order):
        """Print order details in a formatted way."""
        print(f"\n{Fore.CYAN}=== Order Details ==={Style.RESET_ALL}")
        print(f"Order ID: {order.get('orderId', 'N/A')}")
        print(f"Symbol: {order.get('symbol', 'N/A')}")
        print(f"Side: {order.get('side', 'N/A')}")
        print(f"Type: {order.get('type', 'N/A')}")
        print(f"Price: {order.get('price', 'N/A')}")
        print(f"Original Quantity: {order.get('origQty', 'N/A')}")
        print(f"Executed Quantity: {order.get('executedQty', 'N/A')}")
        print(f"Status: {order.get('status', 'N/A')}")
        print(f"Time In Force: {order.get('timeInForce', 'N/A')}")
        if 'stopPrice' in order:
            print(f"Stop Price: {order.get('stopPrice', 'N/A')}")
    
    def run(self):
        """Run the CLI interface."""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return
        
        self._initialize_bot()
        
        try:
            if args.command == 'account':
                account_info = self.bot.get_account_info()
                self._print_account_info(account_info)
                
            elif args.command == 'balance':
                balance = self.bot.get_balance(args.asset)
                print(f"\n{Fore.CYAN}=== Balance Information ==={Style.RESET_ALL}")
                print(f"Asset: {args.asset}")
                print(f"Available Balance: {balance} {args.asset}")
                
            elif args.command == 'price':
                price = self.bot.get_market_price(args.symbol)
                print(f"\n{Fore.CYAN}=== Price Information ==={Style.RESET_ALL}")
                print(f"Symbol: {args.symbol}")
                print(f"Current Price: {price}")
                
            elif args.command == 'market':
                order = self.bot.place_market_order(
                    symbol=args.symbol,
                    side=args.side,
                    quantity=args.quantity
                )
                self._print_order_details(order)
                
            elif args.command == 'limit':
                order = self.bot.place_limit_order(
                    symbol=args.symbol,
                    side=args.side,
                    quantity=args.quantity,
                    price=args.price
                )
                self._print_order_details(order)
                
            elif args.command == 'stop':
                order = self.bot.place_stop_limit_order(
                    symbol=args.symbol,
                    side=args.side,
                    quantity=args.quantity,
                    price=args.price,
                    stop_price=args.stop_price
                )
                self._print_order_details(order)
                
            elif args.command == 'open_orders':
                orders = self.bot.get_open_orders(args.symbol)
                print(f"\n{Fore.CYAN}=== Open Orders ==={Style.RESET_ALL}")
                if not orders:
                    print("No open orders found.")
                else:
                    for order in orders:
                        self._print_order_details(order)
                        print()
                        
            elif args.command == 'cancel':
                result = self.bot.cancel_order(args.symbol, args.order_id)
                print(f"\n{Fore.GREEN}✓ Order {args.order_id} cancelled successfully{Style.RESET_ALL}")
                
        except Exception as e:
            print(f"\n{Fore.RED}✗ Error: {e}{Style.RESET_ALL}")
            logger.error(f"CLI Error: {e}")

if __name__ == "__main__":
    cli = TradingBotCLI()
    cli.run()