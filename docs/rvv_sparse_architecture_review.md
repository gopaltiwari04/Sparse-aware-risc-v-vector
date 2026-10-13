# RISC-V Vector Extension and Existing Sparse-Computing Architectures

## 1. Introduction

Sparse linear algebra is important in scientific computing, numerical simulation, graph processing, and machine learning. A sparse matrix contains many zero-valued entries. Storing and processing every element wastes memory capacity, memory bandwidth, and computational effort. Sparse algorithms instead store the nonzero values and enough metadata to locate them.

Sparse matrix-vector multiplication (SpMV) computes

\[
y = Ax,
\]

where \(A\) is a sparse matrix, \(x\) is a dense input vector, and \(y\) is the output vector. SpMV is a useful baseline workload because it combines floating-point arithmetic with indirect memory accesses and irregular data movement.

This review covers the RISC-V Vector Extension (RVV), common sparse storage formats, and representative approaches used to accelerate sparse computation.

## 2. RISC-V Vector Extension

The RISC-V Vector Extension, commonly called RVV or the standard `V` extension, adds vector processing to the RISC-V instruction set architecture. It enables one instruction to operate on multiple data elements, with the number of elements processed depending on the implementation's vector capabilities and the selected operation.

### 2.1 Main architectural concepts

- **Vector registers:** RVV provides 32 architectural vector registers.
- **Vector length (VLEN):** the number of bits in each architectural vector register. Supported implementations can have different VLEN values.
- **Element width (SEW):** the selected width of elements processed by a vector operation, such as 32-bit floating-point values.
- **Vector length (`vl`):** the active number of elements for a vector instruction.
- **Vector register grouping (LMUL):** controls how many vector registers are grouped for an operation.
- **Masks and predication:** allow operations to apply to selected elements rather than necessarily to every element in a vector group.
- **Vector memory operations:** load and store vector data, including indexed accesses useful for irregular data layouts.
- **Vector arithmetic and reductions:** support operations such as element-wise multiplication and summing vector elements.

The `vsetvli` instruction configures vector execution parameters and establishes the active vector length. This allows software to process data in chunks and adapt to supported vector lengths rather than relying on a single fixed number of elements.

### 2.2 Relevance to sparse workloads

RVV offers useful building blocks for sparse computation. Vector loads can fetch nonzero matrix values, indexed vector loads can fetch elements of the dense input vector using stored column indices, and vector arithmetic can multiply corresponding values. Reduction operations can combine partial products into a row result.

However, vector instructions alone do not remove all costs associated with sparsity. Indexed loads may access scattered locations, row lengths can vary, and reductions may require extra work. The actual performance depends on the sparse representation, memory hierarchy, compiler output, vector configuration, and implementation of the processor.

## 3. Sparse Matrix Representations

Sparse formats store nonzero values alongside metadata that identifies their locations. Common formats include:

| Format | Basic idea | Advantages | Limitations |
|---|---|---|---|
| Coordinate (COO) | Store row index, column index, and value for every nonzero | Simple representation; convenient for construction | Repeated row indices add metadata overhead |
| Compressed Sparse Row (CSR) | Store values and column indices, plus row pointers | Compact and widely used; naturally supports row-by-row SpMV | Row lengths vary; indexed accesses and load imbalance can limit vector efficiency |
| Compressed Sparse Column (CSC) | Store values and row indices, plus column pointers | Convenient for column-oriented operations | Less direct for conventional row-wise SpMV |
| ELLPACK (ELL) | Allocate a fixed number of entries per row | Regular memory access; can suit SIMD/SIMT execution | Padding wastes space and work when row lengths vary |
| Block Sparse Row (BSR) | Store dense blocks of nonzero values | Can exploit local dense structure and reduce index overhead | Inefficient when blocks contain many zeros |
| Hybrid formats | Combine formats, such as ELL and COO | Can balance regular access and irregular row lengths | More complex representation and implementation |

CSR is a reasonable starting point for a baseline SpMV implementation because it represents the nonzeros compactly and makes the entries for each row contiguous in memory.

## 4. Existing Sparse-Computing Architecture Approaches

### 4.1 General-purpose CPUs with SIMD or vector extensions

Conventional CPUs use SIMD instructions or vector extensions to process multiple values per instruction. CSR-based SpMV can vectorize multiplication of nonzero values, but indirect loads of the input vector and variable row lengths remain difficult. Vectorized CSR variants and alternative sparse formats aim to improve memory locality and reduce irregularity.

RVV belongs to this category: it supplies a programmable vector instruction set within a general-purpose processor rather than requiring a dedicated SpMV-only accelerator.

### 4.2 GPUs

GPUs use many parallel execution lanes and high memory bandwidth to process large workloads. Sparse GPU kernels can assign work to threads or groups of threads and use formats such as CSR, COO, ELL, or hybrid formats.

Their challenges include variation in the number of nonzeros per row, divergence between threads, irregular memory accesses, and balancing work across execution groups. The best format and mapping depend on the matrix structure and target GPU.

### 4.3 FPGA-based accelerators

FPGAs can implement customized data paths, buffering, and scheduling for sparse operations. They may exploit application-specific formats or pipelines to improve data movement and parallel execution. Their effectiveness depends on available logic and memory resources, memory bandwidth, and how well the design handles irregularity and load imbalance.

### 4.4 Dedicated sparse accelerators

Dedicated sparse accelerators customize processing elements, dataflow, scheduling, and memory access to reduce the overheads of sparse computation. Designs may use compressed representations, multiple processing elements, specialized gather mechanisms, or dataflow tailored to particular sparse multiplication algorithms.

The trade-off is specialization: a design optimized for one matrix pattern or operation may not perform equally well across different sparse workloads.

### 4.5 Processing-in-memory and heterogeneous systems

Processing-in-memory approaches attempt to reduce data movement by placing some computation close to memory. Heterogeneous systems combine CPUs, GPUs, FPGAs, or other accelerators, choosing an execution resource based on workload characteristics. Both approaches target the fact that sparse kernels can be limited by memory access rather than arithmetic throughput alone.

## 5. Key Challenges and Optimization Opportunities

Across these architectures, recurring challenges include:

1. **Irregular memory access:** column indices can cause scattered accesses to the dense input vector.
2. **Load imbalance:** rows may contain very different numbers of nonzeros.
3. **Index overhead:** sparse formats need metadata in addition to numerical values.
4. **Memory bandwidth:** moving values and indices can dominate the cost of floating-point arithmetic.
5. **Reduction overhead:** partial products must be accumulated into output elements.
6. **Format dependence:** an encoding that works well for one sparsity pattern may be inefficient for another.
7. **Measurement comparability:** comparisons require the same workload, correctness criteria, processor configuration, and clearly defined timing metrics.

Potential sparse-aware architectural directions include more efficient indexed memory access, improved handling of variable-length rows, reducing index-processing overhead, and scheduling work to reduce idle vector lanes. These are research opportunities, not features implemented by the current baseline.

## 6. Connection to the Current Project

This project establishes a baseline for a sparse-aware RISC-V vector architecture study. The current workload performs SpMV using CSR-like row pointers, column indices, and nonzero values. The compiled program contains RVV instructions for vector configuration, loads, indexed loads, multiplication, and reduction.

The workload was simulated in gem5 with VLEN = 256 bits and ELEN = 64 bits. Two synthetic matrix settings were evaluated: 80% sparsity and 40% sparsity. Both passed comparison against a scalar reference implementation.

These experiments establish functional feasibility and initial performance measurements for the baseline. They do not yet demonstrate a performance improvement from a proposed sparse-aware hardware modification. Such a claim would require implementing and evaluating the modification against an appropriate baseline under controlled conditions.

## 7. Conclusion

RVV provides a flexible vector programming model that can accelerate data-parallel work, including parts of SpMV. Sparse computation nevertheless presents challenges that conventional vector execution does not automatically solve: indirect memory accesses, variable row lengths, index overhead, and reduction costs.

Existing approaches address these challenges through sparse storage formats, vectorized algorithms, GPU parallelism, FPGA data paths, dedicated accelerators, and computation closer to memory. The current project uses RVV and gem5 to establish a reproducible starting point for investigating these design trade-offs.

## References

1. RISC-V International, *The RISC-V Instruction Set Manual: “V” Standard Extension for Vector Operations, Version 1.0*. https://docs.riscv.org/reference/isa/unpriv/v-st-ext.html
2. RISC-V Vector C Intrinsics Task Group, *RISC-V Vector C Intrinsic Specification, Version 1.0*. https://docs.riscv.org/reference/vector-c-intrinsics/v1.0/index.html
3. V. Isaac-Chassande, A. Evans, Y. Durand, and F. Rousseau, *Dedicated Hardware Accelerators for Processing of Sparse Matrices and Vectors: A Survey*, ACM Transactions on Architecture and Code Optimization, 2024. https://doi.org/10.1145/3640542
4. J. Gao, B. Liu, W. Ji, and H. Huang, *A Systematic Literature Survey of Sparse Matrix-Vector Multiplication*, 2024. https://arxiv.org/abs/2404.06047
5. J. Chen et al., *An Efficient SIMD Compression Format for Sparse Matrix-Vector Multiplication*, Concurrency and Computation: Practice and Experience, 2018. https://doi.org/10.1002/cpe.4800
