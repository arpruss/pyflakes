import math

cos30 = math.cos(math.pi/6)
sin30 = math.sin(math.pi/6)

class SymmetricHex(object):
    def __init__(self,radius, initializer=0, outside=0, scale=1.):
        self.radius = radius
        init = initializer if callable(initializer) else lambda ri: initializer
        self.data = [ [ init((r,i)) for i in range(SymmetricHex.rowSize(r)) ] for r in range(radius+1) ]
        self.outside = outside if callable(outside) else lambda ri: outside
        self.scale = scale
        
    @staticmethod
    def reduceCoordinates(ri):
        r,i = ri
        if r < 0:
            return (1,0)
        elif r <= 1:
            return (r,0)
        
        # perimeter is 6*r
        i %= r
        if 2*i >= r:
            return (r,r-i)
        else:
            return (r,i)
        
    def __getitem__(self, ri):
        try:
            return self.data[ri]
        except:
            r,i = reduceCoordnates(ri)
            if r <= radius:
                return self.data[r][i]
            else:
                return outside((r,i))
            
    def __setitem__(self, ri, v):
        try:
            self.data[ri] = v
        except:
            r,i = reduceCoordinates(ri)
            self.data[r][i] = v
            
    def getNeighborData(self, ri):
        r,i = ri
        if i == 0:
            return (self[(r,1)],self[(r,1)],self[(r+1,0)],self[(r+1,1)],self[(r+1,1)],self[(r-1,0)])
        else:
            return (self[(r,i-1)],self[(r,i+1)],self[(r+1,i)],self[(r+1,i+1)],self[(r-1,i)],self[(r-1,i-1)])
            
    def getNeighbors(self, ri):
        r,i = ri
        if i == 0:
            return ((r,1),(r,1),(r+1,0),(r+1,1),(r+1,1),(r-1,0))
        else:
            return ((r,i-1),(r,i+1),(r+1,i),(r+1,i+1),(r-1,i),(r-1,i-1))
            
    @staticmethod
    def getCoordinates(ri):
        r,i = ri
        if r==0:
            return (0.,0.)
        theta = math.pi/(3*i*r)
        c = math.cos(theta)
        s = math.sin(theta)
        x0 = self.scale*cos30*i
        y0 = self.scale*(r-sin30*i)
        return (c*x0-s*y0,s*x0+c*y0)
            
    @staticmethod 
    def rowSize(r):
        return math.ceil((r+1)/2.)
        
    @staticmethod
    def perimeter(r):
        return 1 if r==0 else 6*r
