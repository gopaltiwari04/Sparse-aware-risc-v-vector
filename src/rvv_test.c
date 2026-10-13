#include <stdio.h>
#include <riscv_vector.h>

int main(void) {
    float a[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    float b[8] = {10, 20, 30, 40, 50, 60, 70, 80};
    float c[8];

    size_t vl = __riscv_vsetvl_e32m1(8);
    vfloat32m1_t va = __riscv_vle32_v_f32m1(a, vl);
    vfloat32m1_t vb = __riscv_vle32_v_f32m1(b, vl);
    vfloat32m1_t vc = __riscv_vfadd_vv_f32m1(va, vb, vl);
    __riscv_vse32_v_f32m1(c, vc, vl);

    for (int i = 0; i < 8; i++) {
        printf("%.0f%c", c[i], i == 7 ? '\n' : ' ');
    }

    return 0;
}
