import logging
import os
from datetime import datetime
from config import LOG_LEVEL, LOG_FILE

class Logger:
    def __init__(self, name='trading_bot'):
        """Initialize logger with the given name."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # File handler with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_handler = logging.FileHandler(f'logs/{timestamp}_{LOG_FILE}')
        file_handler.setLevel(getattr(logging, LOG_LEVEL))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, LOG_LEVEL))
        
        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """Log info level message."""
        self.logger.info(message)
    
    def error(self, message):
        """Log error level message."""
        self.logger.error(message)
    
    def warning(self, message):
        """Log warning level message."""
        self.logger.warning(message)
    
    def debug(self, message):
        """Log debug level message."""
        self.logger.debug(message)
    
    def critical(self, message):
        """Log critical level message."""
        self.logger.critical(message)
        
    def log_request(self, endpoint, params=None):
        """Log API request details."""
        self.logger.info(f"API Request: {endpoint}, Params: {params}")
    
    def log_response(self, response):
        """Log API response details."""
        self.logger.info(f"API Response: {response}")
    
    def log_error(self, error):
        """Log API error details."""
        self.logger.error(f"API Error: {error}")

# Create a global logger instance
logger = Logger()