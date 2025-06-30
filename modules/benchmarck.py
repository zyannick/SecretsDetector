import timeit
import random
import string
import ctypes
import platform
import math
from collections import Counter

def py_calculate_entropy(data: str) -> float:
    if not data:
        return 0.0
    
    length = len(data)
    counts = Counter(data)
    entropy = 0.0
    
    for count in counts.values():
        p_x = count / length
        entropy -= p_x * math.log2(p_x)
        
    return entropy

CPP_LOADED = False
calculate_entropy_func_cpp = None
try:
    lib_ext = ".dll" if platform.system() == "Windows" else ".so"
    lib_path = f"./simd_entropy{lib_ext}"
    optimizer_lib = ctypes.CDLL(lib_path)
    
    calculate_entropy_func_cpp = optimizer_lib.calculate_entropy_for_secrets
    calculate_entropy_func_cpp.argtypes = [ctypes.c_char_p, ctypes.c_int]
    calculate_entropy_func_cpp.restype = ctypes.c_double

    print("Successfully loaded the C++ library.")
    CPP_LOADED = True # type: ignore
    
except OSError as e:
    print(f"Failed to load C++ library: {e}")

def generate_test_string(length: int) -> str:
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )

if __name__ == "__main__":
    if not CPP_LOADED:
        print("\nExiting benchmark: C++ library is not available.")
        print("Please compile simd_entropy.cc first using the run.sh script or g++ command.")
    else:
        STRING_LENGTH = 1024
        NUMBER_OF_RUNS = 10000

        print("\n--- Entropy Calculation Benchmark ---")
        print(f"String Length: {STRING_LENGTH} characters")
        print(f"Number of Runs: {NUMBER_OF_RUNS}")
        print("-------------------------------------")

        test_string_py = generate_test_string(STRING_LENGTH)
        test_string_cpp_bytes = test_string_py.encode('utf-8')

        python_setup = "from __main__ import py_calculate_entropy, test_string_py"
        python_stmt = "py_calculate_entropy(test_string_py)"
        python_time = timeit.timeit(
            stmt=python_stmt, setup=python_setup, number=NUMBER_OF_RUNS
        )

        print(f"Python Total Time: {python_time:.4f} seconds")
        print(
            f"Python Avg Time/Run: {(python_time / NUMBER_OF_RUNS) * 1e6:.4f} microseconds"
        )

        cpp_setup = "from __main__ import calculate_entropy_func_cpp, test_string_cpp_bytes, STRING_LENGTH"
        cpp_stmt = "calculate_entropy_func_cpp(test_string_cpp_bytes, STRING_LENGTH)"
        cpp_time = timeit.timeit(stmt=cpp_stmt, setup=cpp_setup, number=NUMBER_OF_RUNS)

        print(f"\nC++ Total Time:    {cpp_time:.4f} seconds")
        print(f"C++ Avg Time/Run:    {(cpp_time / NUMBER_OF_RUNS) * 1e6:.4f} microseconds")

        print("-------------------------------------")
        if cpp_time > 0:
            speedup = python_time / cpp_time
            print(f"Conclusion: The C++/SIMD version is {speedup:.1f}x faster.")
        else:
            print("C++ version was too fast to measure accurately.")

