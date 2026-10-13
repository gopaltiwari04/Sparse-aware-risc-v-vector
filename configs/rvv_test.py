import argparse
import os

from m5.objects import RiscvO3CPU

from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.memory import SingleChannelDDR3_1600
from gem5.components.processors.base_cpu_core import BaseCPUCore
from gem5.components.processors.base_cpu_processor import BaseCPUProcessor
from gem5.isas import ISA
from gem5.resources.resource import FileResource
from gem5.simulate.simulator import Simulator


class RVVCore(BaseCPUCore):
    def __init__(self, elen, vlen):
        super().__init__(core=RiscvO3CPU(), isa=ISA.RISCV)
        self.core.isa[0].elen = elen
        self.core.isa[0].vlen = vlen


parser = argparse.ArgumentParser()
parser.add_argument("--binary", required=True)
parser.add_argument("--vlen", type=int, default=256)
parser.add_argument("--elen", type=int, default=64)
parser.add_argument("--program-args", nargs="*", default=[])
args = parser.parse_args()

binary_path = os.path.abspath(args.binary)
if not os.path.isfile(binary_path):
    raise FileNotFoundError(binary_path)

cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="32KiB",
    l1i_size="32KiB",
    l2_size="512KiB",
)

memory = SingleChannelDDR3_1600()

processor = BaseCPUProcessor(
    cores=[RVVCore(args.elen, args.vlen)]
)

board = SimpleBoard(
    clk_freq="1GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

board.set_se_binary_workload(
    FileResource(local_path=binary_path),
    arguments=args.program_args,
)

simulator = Simulator(board=board)
print("Starting RVV test simulation")
print(f"Binary: {binary_path}")
print(f"VLEN={args.vlen}, ELEN={args.elen}")
simulator.run()
