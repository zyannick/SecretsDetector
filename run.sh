#!/bin/bash

set -e

echo "Compiling C++ module..."
g++ -O3 -mavx2 -shared -o simd_entropy.so -fPIC modules/simd_entropy.cc

echo "Running DVC pipeline..."
dvc repro