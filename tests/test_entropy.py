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
import pytest


def test_entropy_empty_string():
    result = SecretsDetectorPython.analyze_for_secrets("")
    assert result["overall_entropy"] == 0.0
    assert result["max_substring_entropy"] == 0.0
    assert result["high_entropy_regions"] == 0
    assert not result["cpp_heuristic_is_secret"]
    assert not result["is_base64_pattern"]


def test_entropy_low_entropy():
    result = SecretsDetectorPython.analyze_for_secrets("abcde")
    assert result["overall_entropy"] < 1.0
    assert result["max_substring_entropy"] < 1.0
    assert result["high_entropy_regions"] == 0
    assert not result["cpp_heuristic_is_secret"]
    assert not result["is_base64_pattern"]


def test_python_vs_cpp_entropy():
    text = "a" * 100 + "b" * 100 + "c" * 100
    python_result = SecretsDetectorPython.analyze_for_secrets(text)
    cpp_result = cpp_wrapper(text)
    assert python_result["overall_entropy"] == cpp_result["overall_entropy"]
    assert python_result["max_substring_entropy"] == cpp_result["max_substring_entropy"]
    assert python_result["high_entropy_regions"] == cpp_result["high_entropy_regions"]
    assert (
        python_result["cpp_heuristic_is_secret"]
        == cpp_result["cpp_heuristic_is_secret"]
    )
    print(python_result)
    print(cpp_result)
