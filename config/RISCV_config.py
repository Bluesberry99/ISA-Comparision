import m5
import argparse
from m5.objects import *
from x86_caches import *

parser = argparse.ArgumentParser(description='A simple system with 2-level cache.')
parser.add_argument("binary", nargs="?", type=str,
                    help="Path to the binary to execute.")
parser.add_argument("--cpu", default="timing", choices=["timing", "minor", "o3"],
                    help="Choose the CPU model: 'timing' for TimingSimpleCPU or 'minor' for MinorCPU.")
parser.add_argument("--l1i_size",
                    help="L1 instruction cache size. Default: 32kB.")
parser.add_argument("--l1d_size",
                    help="L1 data cache size. Default: 32kB.")
parser.add_argument("--l2_size",
                    help="L2 cache size. Default: 1.5MB.")
parser.add_argument("--frequency", default="2GHz", type=str,
                    help="CPU clock frequency. Default: 2GHz.")
parser.add_argument("--mem_type", default="DDR3_1600_8x8", choices=["DDR3_1600_8x8", "DDR3_2133_8x8", "DDR4_2400_16x4", "LPDDR2_S4_1066_1x32", "HBM_1000_4H_1x64","HBM_2000_4H_1x64"],
                    help="Main memory configuration. Default: DDR3_1600_8x8.")
#linpack input
parser.add_argument("--size", type=str, default="10",
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

system.l2bus = L2XBar()

system.cpu.icache.connectBus(system.l2bus)
system.cpu.dcache.connectBus(system.l2bus)

system.l2cache = L2Cache(options)
system.l2cache.connectCPUSideBus(system.l2bus)
system.membus = SystemXBar()
system.l2cache.connectMemSideBus(system.membus)

system.cpu.createInterruptController()

system.system_port = system.membus.cpu_side_ports

# Choose memory configuration based on --mem_type argument
if options.mem_type == "DDR3_1600_8x8":
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
elif options.mem_type == "DDR3_2133_8x8":
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_2133_8x8()
elif options.mem_type == "DDR4_2400_16x4":
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR4_2400_16x4()
elif options.mem_type == "LPDDR2_S4_1066_1x32":
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = LPDDR2_S4_1066_1x32()
elif options.mem_type == "HBM_1000_4H_1x64":
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = HBM_1000_4H_1x64()
elif options.mem_type == "HBM_2000_4H_1x64":
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = HBM_2000_4H_1x64()

system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# for gem5 V21 and beyond
system.workload = SEWorkload.init_compatible(options.binary)

# Process setup
#binary_path = os.path.abspath(options.binary)
#process = Process()
#process.executable = binary_path
#process.cmd = [binary_path] + options.options.split()
#print("Binary path:", binary_path)  # Debug
#print("Command to execute:", process.cmd)
#system.workload = SEWorkload.init_compatible(binary_path)
#system.cpu.workload = process
#system.cpu.createThreads()
#system.workload = SEWorkload.init_compatible(options.binary)
# for gem5 V21 and beyond
#system.workload = SEWorkload.init_compatible(options.binary)

process = Process()
process.cmd = [options.binary]
system.cpu.workload = process
system.cpu.createThreads()

system.workload = SEWorkload.init_compatible(options.binary)

root = Root(full_system=False, system=system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()

print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))

