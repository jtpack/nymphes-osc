import logging
import os
from pathlib import Path


# Create logs directory if necessary
logs_directory_path = Path(os.path.expanduser('~')) / 'nymphes-osc-logs/'
if not logs_directory_path.exists():
    logs_directory_path.mkdir()

# Formatter for logs
log_formatter = logging.Formatter(
    '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Handler for writing to a log file
file_handler = logging.FileHandler(logs_directory_path / 'log.txt', mode='w')
file_handler.setFormatter(log_formatter)

# Handler for logging to the console
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

logger = logging.getLogger('nymphes-osc')
logger.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
