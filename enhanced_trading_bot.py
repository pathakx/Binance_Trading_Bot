#!/usr/bin/env python
"""
Enhanced Trading Bot with Position Management
This module combines Binance API trading functionality with position management.
"""

from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceRequestException
import requests
import hmac
import hashlib
import time
import urllib.parse
import sys
import json
import os
from datetime import datetime
from logger import logger
from config import API_KEY, API_SECRET, TESTNET, TESTNET_BASE_URL, DEFAULT_SYMBOL

class EnhancedTradingBot:
    def __init__(self, api_key=API_KEY, api_secret=API_SECRET, testnet=TESTNET, positions_file="positions.json"):
        """
        Initialize the enhanced trading bot with both API connectivity and position management.
        
        Args:
            api_key (str): Binance API key
            api_secret (str): Binance API secret
            testnet (bool): Whether to use testnet
            positions_file (str): File to store position data
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.positions_file = positions_file
        
        # Initialize positions tracking
        self.positions = self._load_positions()

        # Initialize Binance client
        self.client = Client(api_key, api_secret, testnet=testnet)

        if testnet:
            # Configure testnet URLs properly
            self.client.API_URL = 'https://testnet.binance.vision/api'
            self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
            self.client.FUTURES_DATA_URL = 'https://testnet.binancefuture.com/futures/data'
            logger.info("Running in TESTNET mode (Futures)")
        else:
            logger.info("Running in PRODUCTION mode")

        # Verify Futures connectivity
        try:
            self.client.futures_ping()
            logger.info("Successfully connected to Binance Futures API")
            print("✅ Futures connection successful")
        except Exception as e:
            logger.error(f"Failed to connect to Binance Futures API: {e}")
            raise

    #
    # Position Management Methods
    #
    
    def _load_positions(self):
        """Load positions from file or initialize with empty positions."""
        abs_path = os.path.abspath(self.positions_file)
        if os.path.exists(abs_path):
            try:
                with open(abs_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading positions: {e}")
                return {}
        return {}
    
    def _save_positions(self):
        """Save positions to file."""
        try:
            # Ensure directory exists (resolve absolute path)
            abs_path = os.path.abspath(self.positions_file)
            dir_path = os.path.dirname(abs_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            with open(abs_path, 'w') as f:
                json.dump(self.positions, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving positions: {e}")
    
    def get_position(self, symbol):
        """
        Get the current net quantity for the given symbol.
        
        Args:
            symbol (str): The asset symbol (e.g., BTC, ETH)
            
        Returns:
            float: The current net quantity
        """
        return float(self.positions.get(symbol, 0.0))
    
    def update_position(self, symbol, quantity, is_buy):
        """
        Update position after a trade.
        
        Args:
            symbol (str): The asset symbol
            quantity (float): The quantity traded
            is_buy (bool): Whether it's a buy order
            
        Returns:
            float: The new position
        """
        # Ensure quantity is positive
        quantity = abs(float(quantity))
        
        # Get current position
        current_position = self.get_position(symbol)
        
        # Update position based on order type
        if is_buy:
            new_position = current_position + quantity
        else:
            new_position = current_position - quantity
            
        self.positions[symbol] = new_position
        
        # Save updated positions
        self._save_positions()
        
        # Log position status
        if new_position == 0:
            logger.info(f"Position in {symbol} is now closed (0).")
        elif new_position < 0:
            logger.info(f"Short position in {symbol} with net position: {new_position}.")
        else:
            logger.info(f"Position in {symbol} is open with {new_position}.")
            
        return new_position
    
    def get_all_positions(self):
        """
        Get all current positions.
        
        Returns:
            dict: All positions with their net quantities
        """
        return {symbol: qty for symbol, qty in self.positions.items() if qty != 0}

    #
    # API Request Methods
    #
    
    def _generate_signature(self, data):
        """Generate signature for API request."""
        query_string = urllib.parse.urlencode(data)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
        
    def _make_futures_request(self, method, endpoint, params=None):
        """Make a direct request to Binance Futures API."""
        base_url = TESTNET_BASE_URL if self.testnet else 'https://fapi.binance.com'
        url = f"{base_url}/fapi/{endpoint}"
        
        # Add timestamp and signature
        params = params or {}
        params['timestamp'] = int(time.time() * 1000)
        params['signature'] = self._generate_signature(params)
        
        # Add API key to headers
        headers = {'X-MBX-APIKEY': self.api_key}
        
        # Make request
        if method == 'GET':
            response = requests.get(url, params=params, headers=headers)
        elif method == 'POST':
            response = requests.post(url, params=params, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, params=params, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
            
        # Check for errors
        if response.status_code != 200:
            logger.error(f"API Error: {response.text}")
            raise Exception(f"API Error: {response.text}")
            
        return response.json()
    
    #
    # Trading API Methods
    #
    
    def get_account_info(self):
        """Get Futures account information."""
        try:
            logger.info("Fetching Futures account info")
            
            # Use direct API request instead of client method
            account_info = self._make_futures_request('GET', 'v2/account')
            
            logger.info(f"Account info: {account_info}")
            return account_info
        except Exception as e:
            logger.error(f"API Error while getting account info: {e}")
            raise
    
    def get_balance(self, asset='USDT'):
        """Get balance for a specific asset."""
        try:
            logger.log_request("get_balance", {"asset": asset})
            account_info = self.client.futures_account()
            
            for balance in account_info['assets']:
                if balance['asset'] == asset:
                    logger.log_response(balance)
                    return float(balance['availableBalance'])
            
            logger.warning(f"Asset {asset} not found in account")
            return 0.0
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.log_error(e)
            raise
    
    def get_market_price(self, symbol=DEFAULT_SYMBOL):
        """Get current market price for a symbol."""
        try:
            logger.log_request("get_market_price", {"symbol": symbol})
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            logger.log_response(ticker)
            return float(ticker['price'])
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.log_error(e)
            raise
    
    def place_market_order(self, symbol=DEFAULT_SYMBOL, side='BUY', quantity=None):
        """Place a market order and update position."""
        try:
            if quantity is None:
                logger.error("Quantity must be specified for market orders")
                raise ValueError("Quantity must be specified for market orders")
            
            params = {
                "symbol": symbol,
                "side": side,
                "type": "MARKET",
                "quantity": quantity
            }
            
            logger.log_request("place_market_order", params)
            order = self.client.futures_create_order(**params)
            logger.log_response(order)
            
            # Get order status
            order_status = self.get_order_status(symbol, order['orderId'])
            
            # Update position
            is_buy = (side.upper() == 'BUY')
            new_position = self.update_position(symbol, quantity, is_buy)
            logger.info(f"{'Bought' if is_buy else 'Sold'} {quantity} {symbol}. Current net quantity: {new_position}")
            
            # Add final quantity to order status for display
            order_status['final_quantity'] = new_position
            
            return order_status
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.log_error(e)
            raise
    
    def place_limit_order(self, symbol=DEFAULT_SYMBOL, side='BUY', quantity=None, price=None):
        """Place a limit order and update position."""
        try:
            if quantity is None or price is None:
                logger.error("Both quantity and price must be specified for limit orders")
                raise ValueError("Both quantity and price must be specified for limit orders")
            
            params = {
                "symbol": symbol,
                "side": side,
                "type": "LIMIT",
                "timeInForce": "GTC",  # Good Till Cancelled
                "quantity": quantity,
                "price": price
            }
            
            logger.log_request("place_limit_order", params)
            order = self.client.futures_create_order(**params)
            logger.log_response(order)
            
            # Get order status
            order_status = self.get_order_status(symbol, order['orderId'])
            
            # Update position (for limit orders, we update when the order is filled)
            # This is a simplification - in a real system, you'd listen for order updates
            is_buy = (side.upper() == 'BUY')
            if order_status.get('status') == 'FILLED':
                new_position = self.update_position(symbol, quantity, is_buy)
                logger.info(f"{'Bought' if is_buy else 'Sold'} {quantity} {symbol}. Current net quantity: {new_position}")
                # Add final quantity to order status for display
                order_status['final_quantity'] = new_position
            
            return order_status
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.log_error(e)
            raise
    
    def place_stop_limit_order(self, symbol=DEFAULT_SYMBOL, side='BUY', quantity=None, 
                              price=None, stop_price=None):
        """Place a stop limit order."""
        try:
            if quantity is None or price is None or stop_price is None:
                logger.error("Quantity, price, and stop_price must be specified for stop limit orders")
                raise ValueError("Quantity, price, and stop_price must be specified for stop limit orders")
            
            params = {
                "symbol": symbol,
                "side": side,
                "type": "STOP",
                "timeInForce": "GTC",  # Good Till Cancelled
                "quantity": quantity,
                "price": price,
                "stopPrice": stop_price
            }
            
            logger.log_request("place_stop_limit_order", params)
            order = self.client.futures_create_order(**params)
            logger.log_response(order)
            
            # Get order status
            order_status = self.get_order_status(symbol, order['orderId'])
            
            # For stop orders, position is updated when the order is triggered and filled
            if order_status.get('status') == 'FILLED':
                is_buy = (side.upper() == 'BUY')
                new_position = self.update_position(symbol, quantity, is_buy)
                logger.info(f"{'Bought' if is_buy else 'Sold'} {quantity} {symbol}. Current net quantity: {new_position}")
                # Add final quantity to order status for display
                order_status['final_quantity'] = new_position
            
            return order_status
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.log_error(e)
            raise
    
    def get_order_status(self, symbol, order_id):
        """Get status of an order."""
        try:
            logger.log_request("get_order_status", {"symbol": symbol, "orderId": order_id})
            order = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            logger.log_response(order)
            return order
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.log_error(e)
            raise
    
    def get_open_orders(self, symbol=DEFAULT_SYMBOL):
        """Get all open orders for a symbol."""
        try:
            logger.log_request("get_open_orders", {"symbol": symbol})
            orders = self.client.futures_get_open_orders(symbol=symbol)
            logger.log_response(orders)
            return orders
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.log_error(e)
            raise
    
    def cancel_order(self, symbol, order_id):
        """Cancel an order."""
        try:
            logger.log_request("cancel_order", {"symbol": symbol, "orderId": order_id})
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            logger.log_response(result)
            return result
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.log_error(e)
            raise


def cli_interface():
    """Command-line interface for the trading bot."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python enhanced_trading_bot.py account")
        print("  python enhanced_trading_bot.py balance [asset]")
        print("  python enhanced_trading_bot.py price [symbol]")
        print("  python enhanced_trading_bot.py market <symbol> <side> <quantity>")
        print("  python enhanced_trading_bot.py limit <symbol> <side> <quantity> <price>")
        print("  python enhanced_trading_bot.py stop <symbol> <side> <quantity> <price> <stop_price>")
        print("  python enhanced_trading_bot.py open_orders [symbol]")
        print("  python enhanced_trading_bot.py cancel <symbol> <order_id>")
        print("  python enhanced_trading_bot.py position <symbol>")
        print("  python enhanced_trading_bot.py positions")
        return
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Initialize bot
    bot = EnhancedTradingBot()
    
    command = sys.argv[1].lower()
    
    try:
        if command == "account":
            account_info = bot.get_account_info()
            print(json.dumps(account_info, indent=2))
            
        elif command == "balance":
            asset = sys.argv[2] if len(sys.argv) > 2 else "USDT"
            balance = bot.get_balance(asset)
            print(f"Balance for {asset}: {balance}")
            
        elif command == "price":
            symbol = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SYMBOL
            price = bot.get_market_price(symbol)
            print(f"Current price for {symbol}: {price}")
            
        elif command == "market" and len(sys.argv) >= 5:
            symbol = sys.argv[2]
            side = sys.argv[3].upper()
            quantity = float(sys.argv[4])
            
            order = bot.place_market_order(symbol=symbol, side=side, quantity=quantity)
            print(f"Market order placed: {order}")
            if 'final_quantity' in order:
                print(f"Final {symbol} position after order: {order['final_quantity']}")
            
        elif command == "limit" and len(sys.argv) >= 6:
            symbol = sys.argv[2]
            side = sys.argv[3].upper()
            quantity = float(sys.argv[4])
            price = float(sys.argv[5])
            
            order = bot.place_limit_order(symbol=symbol, side=side, quantity=quantity, price=price)
            print(f"Limit order placed: {order}")
            if 'final_quantity' in order:
                print(f"Final {symbol} position after order: {order['final_quantity']}")
            
        elif command == "stop" and len(sys.argv) >= 7:
            symbol = sys.argv[2]
            side = sys.argv[3].upper()
            quantity = float(sys.argv[4])
            price = float(sys.argv[5])
            stop_price = float(sys.argv[6])
            
            order = bot.place_stop_limit_order(
                symbol=symbol, side=side, quantity=quantity, price=price, stop_price=stop_price
            )
            print(f"Stop-limit order placed: {order}")
            if 'final_quantity' in order:
                print(f"Final {symbol} position after order: {order['final_quantity']}")
            
        elif command == "open_orders":
            symbol = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SYMBOL
            orders = bot.get_open_orders(symbol)
            
            if not orders:
                print(f"No open orders for {symbol}")
            else:
                print(f"Open orders for {symbol}:")
                for order in orders:
                    print(json.dumps(order, indent=2))
                    
        elif command == "cancel" and len(sys.argv) >= 4:
            symbol = sys.argv[2]
            order_id = int(sys.argv[3])
            
            result = bot.cancel_order(symbol, order_id)
            print(f"Order cancelled: {result}")
            
        elif command == "position" and len(sys.argv) >= 3:
            symbol = sys.argv[2].upper()
            position = bot.get_position(symbol)
            print(f"Current position for {symbol}: {position}")
            
        elif command == "positions":
            positions = bot.get_all_positions()
            if positions:
                print("Current positions:")
                for symbol, quantity in positions.items():
                    print(f"  {symbol}: {quantity}")
            else:
                print("No open positions.")
                
        else:
            print("Invalid command or arguments.")
            print("Use 'python enhanced_trading_bot.py' without arguments to see usage instructions.")
            
    except (BinanceAPIException, BinanceRequestException) as e:
        print(f"API Error: {e}")
    except ValueError as e:
        print(f"Value Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    cli_interface()