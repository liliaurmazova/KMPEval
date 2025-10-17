import os

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

MODEL_NAME = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 3000
TEMPERATURE = 0.7

GOLDEN_DATASET_PATH = "golden_dataset\\KMPWithTests"
GENERATED_OUTPUT_PATH = "golden_dataset\\KMPWithTests\\generated"

