from m5.objects import Cache
    
class L1Cache(Cache):
    assoc = 4
    tag_latency = 2
    data_latency = 3
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    
    def __init__(self, options=None):
    	super(L1Cache, self).__init__()
    	pass
    	
    def connectCPU(self, cpu):
    # need to define this in a base class!
    	raise NotImplementedError

    def connectBus(self, bus):
    	self.mem_side = bus.cpu_side_ports

class L1ICache(L1Cache):
    size = '32kB'
    
    def __init__(self, options=None):
    	super(L1ICache, self).__init__(options)
    	if not options or not options.l1i_size:
        	return
    	self.size = options.l1i_size
    	
    def connectCPU(self, cpu):
        self.cpu_side = cpu.icache_port

class L1DCache(L1Cache):
    size = '32kB'
    
    def __init__(self, options=None):
    	super(L1DCache, self).__init__(options)
    	if not options or not options.l1d_size:
        	return
    	self.size = options.l1d_size
    	
    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port
    
class L2Cache(Cache):
    size = '2MB'
    assoc = 16
    tag_latency = 20
    data_latency = 10
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12
    
    def __init__(self, options=None):
    	super(L2Cache, self).__init__()
    	if not options or not options.l2_size:
        	return
    	self.size = options.l2_size   
        
    def connectCPUSideBus(self, bus):
    	self.cpu_side = bus.mem_side_ports

    def connectMemSideBus(self, bus):
    	self.mem_side = bus.cpu_side_ports