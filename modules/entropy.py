import ctypes
import platform
import math
import string
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecretsDetectorPython:

    BASE64_CHARS = set(string.ascii_letters + string.digits + "+/")

    @staticmethod
    def _calculate_entropy(text: str) -> float:
        if not text:
            return 0.0

        length = len(text)
        counts = Counter(text)
        entropy = 0.0

        for count in counts.values():
            p_x = count / length
            entropy -= p_x * math.log2(p_x)

        return entropy

    @staticmethod
    def _detect_api_key_pattern(text: str) -> bool:
        if len(text) < 20:
            return False

        consecutive_base64 = 0
        max_consecutive = 0

        for char in text:
            if char in SecretsDetectorPython.BASE64_CHARS:
                consecutive_base64 += 1
            else:
                max_consecutive = max(max_consecutive, consecutive_base64)
                consecutive_base64 = 0

        max_consecutive = max(max_consecutive, consecutive_base64)
        return max_consecutive >= 20

    @classmethod
    def analyze_for_secrets(cls, text: str) -> dict:
        length = len(text)
        result = {
            "overall_entropy": 0.0,
            "max_substring_entropy": 0.0,
            "high_entropy_regions": 0,
            "cpp_heuristic_is_secret": False,
            "is_base64_pattern": False,
        }

        if length < 8:
            return result

        result["overall_entropy"] = cls._calculate_entropy(text)

        window_size = 32
        entropy_threshold = 4.5
        max_entropy = 0.0
        high_entropy_count = 0

        if length >= window_size:
            for i in range(length - window_size + 1):
                window = text[i : i + window_size]
                window_entropy = cls._calculate_entropy(window)

                if window_entropy > entropy_threshold:
                    high_entropy_count += 1

                if window_entropy > max_entropy:
                    max_entropy = window_entropy

        result["max_substring_entropy"] = max_entropy
        result["high_entropy_regions"] = high_entropy_count

        result["cpp_heuristic_is_secret"] = (result["overall_entropy"] > 4.0) or (
            high_entropy_count > 0 and result["max_substring_entropy"] > 5.0
        )

        result["is_base64_pattern"] = cls._detect_api_key_pattern(text)

        return result


class EntropyAnalysis(ctypes.Structure):
    _fields_ = [
        ("overall_entropy", ctypes.c_double),
        ("max_substring_entropy", ctypes.c_double),
        ("high_entropy_regions", ctypes.c_int),
        ("likely_secret", ctypes.c_bool),
    ]


def cpp_entropy_loader():
    CPP_OPTIMIZER_LOADED = False
    _analyze_string_for_secrets_cpp = None
    _detect_api_key_pattern_avx2_cpp = None
    try:
        lib_ext = ".dll" if platform.system() == "Windows" else ".so"
        lib_path = f"./simd_entropy{lib_ext}"

        optimizer_lib = ctypes.CDLL(lib_path)

        _analyze_string_for_secrets_cpp = optimizer_lib.analyze_string_for_secrets
        _analyze_string_for_secrets_cpp.argtypes = [ctypes.c_char_p, ctypes.c_int]
        _analyze_string_for_secrets_cpp.restype = EntropyAnalysis

        _detect_api_key_pattern_avx2_cpp = optimizer_lib.detect_api_key_pattern_avx2
        _detect_api_key_pattern_avx2_cpp.argtypes = [ctypes.c_char_p, ctypes.c_int]
        _detect_api_key_pattern_avx2_cpp.restype = ctypes.c_bool

        CPP_OPTIMIZER_LOADED = True
        print("[INFO] C++ secret analysis engine loaded successfully.")

    except (OSError, AttributeError) as e:
        logger.warning(f"C++ analysis engine not found or failed to load ({e}).")
        logger.info("Falling back to slower, pure Python analysis engine.")

    return (
        CPP_OPTIMIZER_LOADED,
        _analyze_string_for_secrets_cpp,
        _detect_api_key_pattern_avx2_cpp,
    )


def cpp_wrapper(text: str):
    (
        CPP_OPTIMIZER_LOADED,
        _analyze_string_for_secrets_cpp,
        _detect_api_key_pattern_avx2_cpp,
    ) = cpp_entropy_loader()

    if CPP_OPTIMIZER_LOADED:
        encoded_text = text.encode("utf-8")
        analysis_result = _analyze_string_for_secrets_cpp(
            encoded_text, len(encoded_text)
        )
        return {
            "overall_entropy": analysis_result.overall_entropy,
            "max_substring_entropy": analysis_result.max_substring_entropy,
            "high_entropy_regions": analysis_result.high_entropy_regions,
            "cpp_heuristic_is_secret": analysis_result.likely_secret,
            "is_base64_pattern": _detect_api_key_pattern_avx2_cpp(
                encoded_text, len(encoded_text)
            ),
        }
    else:
        return None


def analyze_string(text: str) -> dict:
    if not text:
        return {
            "overall_entropy": 0.0,
            "max_substring_entropy": 0.0,
            "high_entropy_regions": 0,
            "cpp_heuristic_is_secret": False,
            "is_base64_pattern": False,
        }

    cpp_result = cpp_wrapper(text)
    if cpp_result:
        return cpp_result
    else:
        return SecretsDetectorPython.analyze_for_secrets(text)
