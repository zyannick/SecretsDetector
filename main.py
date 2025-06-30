import os


import sys
import pathlib

import dotenv

dotenv.load_dotenv(pathlib.Path(__file__).parent.parent / ".env")


SECRETS_DETECTOR_ROOT = os.getenv(
    "SECRETS_DETECTOR_ROOT", default=pathlib.Path(__file__).parent.parent
)

sys.path.append(SECRETS_DETECTOR_ROOT)

from modules.entropy import SecretsDetectorPython, cpp_wrapper


if __name__ == "__main__":
    text = "This is a test string with some secrets like API_KEY 12345 and PASSWORD abcdef."
    print("Analyzing string for secrets...")
    python_result = SecretsDetectorPython.analyze_for_secrets(text)
    cpp_result = cpp_wrapper(text)
    print("Python Result:", python_result)
    print("C++ Result:", cpp_result)