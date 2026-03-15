import logging
import os
from datetime import datetime
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

class GreenMindLogger:
    def __init__(self):
        self.log_dir = Config.LOG_DIRECTORY
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create a new log file for each session with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"greenmind_session_{timestamp}.log")
        
        # Configure logging
        self.logger = logging.getLogger("GreenMind")
        self.logger.setLevel(logging.INFO)
        
        # Prevent adding multiple handlers if logger already exists
        if not self.logger.handlers:
            # File handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_tool_use(self, tool_name, query, response):
        """Log when a tool is used"""
        self.logger.info(f"TOOL USED: {tool_name}")
        self.logger.info(f"QUERY: {query}")
        # Truncate response if too long
        response_preview = response[:500] + "..." if len(response) > 500 else response
        self.logger.info(f"RESPONSE: {response_preview}")
        self.logger.info("-" * 70)
    
    def log_agent_response(self, query, response, tools_used):
        """Log the final agent response"""
        self.logger.info(f"USER QUERY: {query}")
        self.logger.info(f"TOOLS USED: {', '.join(tools_used) if tools_used else 'No tools used'}")
        self.logger.info(f"AGENT RESPONSE: {response}")
        self.logger.info("=" * 70)
    
    def log_error(self, error_message, tool_name=None):
        """Log errors"""
        if tool_name:
            self.logger.error(f"ERROR in {tool_name}: {error_message}")
        else:
            self.logger.error(f"ERROR: {error_message}")
        self.logger.info("=" * 70)