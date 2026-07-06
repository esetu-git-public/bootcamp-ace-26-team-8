"""
Project Configuration File
Loan Default Prediction System
"""

import os

# Base Project Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dataset Paths
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")

# Model Path
MODEL_PATH = os.path.join(BASE_DIR, "models")

# Reports Path
REPORTS_PATH = os.path.join(BASE_DIR, "reports")

# Random Seed
RANDOM_SEED = 42

# Train-Test Split
TEST_SIZE = 0.2