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
        
    INTEGER_OFFSETS = ((1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1))
        
    def fromIntegerCoordinates(self,xy):
        # 2 1 
        # 3 x 0
        #   4 5
        x,y = xy
        return self.scale * complex((x + y / 2) * 1.5, y * math.sqrt(3)/2)
        
    def getPaths(self, ri, isFilled):
        segments = set()        
        for r in range(radius+1):
            for i in range(SymmetricHex.perimeter(r)):
                if isFilled(data[r][i]):
                    c = SymmetricHex.getIntegerCoordinates(r,i) # unimplemented
                    for i in range(6):
                        o1 = INTEGER_OFFSETS[i]
                        o2 = INTEGER_OFFSETS[(i+1)%6]
                        p1 = (c[0]+o1[0],c[1]+o1[1])
                        p2 = (c[0]+o2[0],c[1]+o2[1])
                        if (p2,p1) in segments:
                            segments.remove((p2,p1))
                        else:
                            segments.add((p1,p2))
        paths = []
        while segments:
            s = next(iter(segments))
            segments.remove(s)
            path = [s[0],s[1]]
            found = True
            while found:
                found = False
                for s in segments:
                    if s[0] == path[-1]:
                        path.append(s)
                        segments.remove(s)
                        found = true
                        break
        
    @staticmethod
    def equalPoints(a,b):
        return math.abs(a-b) < 0.01
        
    @staticmethod
    def getIntegerCoordinates(ri):
        r,i = ri
        if r==0:
            return (0,0)
        c = (r,0)
        angle = i//r
        for a in range(angle):
            c = (c[0]+r*INTEGER_OFFSETS[a][0],c[1]+r*INTEGER_OFFSETS[a][1])
        offset = i-r*angle
        return (c[0]+offset*INTEGER_OFFSETS[a][0],c[1]+offset*INTEGER_OFFSETS[a][1])
            
    @staticmethod 
    def rowSize(r):
        return math.ceil((r+1)/2.)
        
    @staticmethod
    def perimeter(r):
        return 1 if r==0 else 6*r
        
     
