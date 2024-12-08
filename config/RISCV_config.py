import m5
import argparse
from m5.objects import *
from RISCV_caches import *

parser = argparse.ArgumentParser(description='A simple system with 2-level cache.')
parser.add_argument("binary", type=str,
                    help="Path to the binary to execute.")
parser.add_argument("--cpu", default="timing", choices=["timing", "minor", "o3"],
                    help="Choose the CPU model: 'timing' for TimingSimpleCPU or 'minor' for MinorCPU.")
parser.add_argument("--l1i_size",
                    help="L1 instruction cache size. Default: 8kB.")
parser.add_argument("--l1d_size",
                    help="L1 data cache size. Default: 16kB.")
parser.add_argument("--l2_size",
                    help="L2 cache size. Default: 1.5MB.")
parser.add_argument("--frequency", default="160MHz", type=str,
                    help="CPU clock frequency. Default: 160MHz.")
parser.add_argument("--mem_type", default="SRAM", choices=["DDR3_1600_8x8", "DDR3_2133_8x8", "DDR4_2400_16x4", "LPDDR2_S4_1066_1x32", "HBM_1000_4H_1x64","HBM_2000_4H_1x64","SRAM"],
                    help="Main memory configuration. Default: DDR3_1600_8x8.")
#linpack input
parser.add_argument("--size", type=str, default="\n 1 \n",
                    help="Size of the array to use in the workload.")


options = parser.parse_args()

system = System()

system.clk_domain = SrcClockDomain()
system.clk_domain.clock = options.frequency  # Set clock based on command-line argument
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# Choose CPU model based on the --cpu argument
if options.cpu == "timing":
    system.cpu = TimingSimpleCPU()
elif options.cpu == "minor":
    system.cpu = MinorCPU()
elif options.cpu == "o3":
	system.cpu = O3CPU()

system.cpu.icache = L1ICache(options)
system.cpu.dcache = L1DCache(options)

system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)

# 创建主总线
system.membus = SystemXBar()

# 将 L1 缓存直接连接到总线，而不使用 L2 缓存
system.cpu.icache.mem_side = system.membus.cpu_side_ports
system.cpu.dcache.mem_side = system.membus.cpu_side_ports

# 不连接 L2 缓存和主存
# 设置主存控制器
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()  # 可根据需求选择内存类型
system.mem_ctrl.dram.range = system.mem_ranges[0]

# 连接主存到总线
system.mem_ctrl.port = system.membus.mem_side_ports

# 系统端口直接连接到总线
system.system_port = system.membus.cpu_side_ports

system.cpu.createInterruptController()

# Process setup
system.workload = SEWorkload.init_compatible(options.binary)
binary_path = os.path.abspath(options.binary)
process = Process()
process.executable = options.binary
#process.cmd = [options.binary, options.size]
process.cmd = options.binary
print("Binary path:", options.binary)  # Debug
print("Command to execute:", process.cmd)
system.cpu.workload = process
system.cpu.createThreads()
system.workload = SEWorkload.init_compatible(options.binary)
# for gem5 V21 and beyond
#system.workload = SEWorkload.init_compatible(options.binary)

#process = Process()
#process.cmd = [options.binary]
#system.cpu.workload = process
#system.cpu.createThreads()

#system.workload = SEWorkload.init_compatible(options.binary)

root = Root(full_system=False, system=system)
m5.instantiate()


print("Beginning simulation!")
exit_event = m5.simulate()

print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))

