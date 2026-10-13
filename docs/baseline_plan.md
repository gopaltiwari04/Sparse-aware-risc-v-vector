# Baseline Experiment Plan

## Test 1: RVV Vector Addition
- Purpose: Validate compilation and vector instruction generation.
- ISA target: RV64GCV
- ABI: LP64D
- Vector length (VLEN): 256 bits
- Maximum element width (ELEN): 64 bits
- Expected output: 11 22 33 44 55 66 77 88

## Test 2: Sparse Matrix-Vector Multiplication
- Representation: Compressed Sparse Row (CSR)
- Workloads: At least two sparsity levels
- Validation: Compare output against a reference implementation
- Metrics: Simulated execution time and gem5 statistics

## Status
- RISC-V compiler detected.
- RVV compiler macros verified.
- Custom binary execution in gem5: pending.
- SpMV measurements: pending.
