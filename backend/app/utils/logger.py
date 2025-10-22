import logging

logger = logging.getLogger("document_translation_app")
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

# Optionally, you can add a file handler to log to a file
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)