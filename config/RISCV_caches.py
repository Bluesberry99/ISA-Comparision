from m5.objects import Cache
    
class L1Cache(Cache):
    assoc = 4
    tag_latency = 2
    data_latency = 1
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
    size = '8kB'
    
    def __init__(self, options=None):
    	super(L1ICache, self).__init__(options)
    	if not options or not options.l1i_size:
        	return
    	self.size = options.l1i_size

    	
    def connectCPU(self, cpu):
        self.cpu_side = cpu.icache_port

class L1DCache(L1Cache):
    size = '16kB'
    
    def __init__(self, options=None):
    	super(L1DCache, self).__init__(options)
    	if not options or not options.l1d_size:
        	return
    	self.size = options.l1d_size
    	
    def connectCPU(self, cpu):
        self.cpu_side = cpu.dcache_port

