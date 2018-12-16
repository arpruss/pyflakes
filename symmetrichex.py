import math
import sys

if sys.version_info >= (3,0):
    xrange = range
    
def binarySearch(list, value, start=None, end=None):
    if start is None:
        start = 0
    if end is None:
        end = len(list)
    while start < end:
        mid = (start+end) // 2
        if list[mid] < value:
            start = mid+1
        elif value < list[mid]:
            end = mid
        else:
            if list[mid] != value:
                raise ValueError()
            return mid
    raise ValueError()

class SymmetricHex(object):
    def __init__(self, radius, initializer=0, isFilled=bool):
        self.radius = radius
        init = initializer if callable(initializer) else lambda ri: initializer
        self.count = sum(SymmetricHex.rowSize(r) for r in range(radius+1))
        self.indices = tuple(i for i in range(self.count))
        self.toPolar = tuple( (r,i) for r in range(radius+1) for i in range(SymmetricHex.rowSize(r)) )
        self.toIntegerCoordinates = tuple( SymmetricHex.polarToIntegerCoordinates(ri) for ri in self.toPolar )
        self.data = [ init(self.toPolar[i]) for i in self.indices ]
        self.neighbors = tuple( tuple(self.polarToIndex(y) for y in self._getNeighbors(self.toPolar[i])) for i in self.indices )
        self.uniqueNeighbors = tuple( tuple(set(n)) for n in self.neighbors )
        self.isFilled = isFilled
        
    def getFilledRadius(self):
        r = 0
        for i in self.indices:
            if self.isFilled(self.data[i]):
                r = max(r, abs(self.displayFromIntegerCoordinates(self.toIntegerCoordinates[i])))
        return r+0.5
        
    def polarToIndex(self,ri):
        return binarySearch(self.toPolar,ri)
        
    def reducePolar(self,ri):
        r,i = ri
        if r < 0:
            return (1,0)
        elif r <= 1:
            return (r,0)
        elif r > self.radius:
            r = self.radius
            if 2*i >= r:
                i = SymmetricHex.rowSize(r) - 1
        
        # perimeter is 6*r
        i %= r
        if 2*i >= r:
            return (r,r-i)
        else:
            return (r,i)
        
    def __getitem__(self, i):
        return self.data[i]
            
    def __setitem__(self, i, v):
        self.data[i] = v
            
    def _getNeighbors(self, ri):
        r,i = ri
        
        if r == 0:
            return ((1,0),(1,0),(1,0),(1,0),(1,0),(1,0))
        elif r == 1:
            return ((0,0),(1,0),(1,0),(2,0),(2,1),(2,1))
        else:
            if i == 0:
                nn = ((r,1),(r,1),(r+1,0),(r+1,1),(r+1,1),(r-1,0))
            else:
                nn = ((r,i-1),(r,i+1),(r+1,i),(r+1,i+1),(r-1,i),(r-1,i-1))
            return map(self.reducePolar,nn)
        
    FIRST_NEIGHBOR = (-1,2)
    NEIGHBOR_OFFSETS = ((-1,-1),(1,-2),(2,-1),(1,1),(-1,2),(-2,1))
    CORNERS = ((1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1))
        
    def displayFromIntegerCoordinates(self,xy):
        # 2 1 
        # 3 x 0
        #   4 5
        x,y = xy
        return 0.5 * complex((x + y / 2.) * math.sqrt(3), y * 1.5)
        
    def getHexIntegerCoordinates(self, filter=None):
        if filter is None:
            filter = self.isFilled
        for r in range(self.radius+1):
            for i in range(self.perimeter(r)):
                index = self.polarToIndex(self.reducePolar((r,i)))
                if filter(self.data[index]):
                    yield SymmetricHex.polarToIntegerCoordinates((r,i))
                    
    @staticmethod
    def getHexSegments(c):
        for i in range(6):
            o1 = SymmetricHex.CORNERS[i]
            o2 = SymmetricHex.CORNERS[(i+1)%6]
            p1 = (c[0]+o1[0],c[1]+o1[1])
            p2 = (c[0]+o2[0],c[1]+o2[1])
            yield (p1,p2)
            
    def getScale(self, diameter):
        return diameter / (2.*self.getFilledRadius())
        
    def getPaths(self, diameter=150, filter=None):
        if filter is None:
            filter = self.isFilled
        
        scale = self.getScale(diameter)
        segments = set()
        for c in self.getHexIntegerCoordinates(filter=filter):
            for s0,s1 in SymmetricHex.getHexSegments(c):
                if (s1,s0) in segments:
                    # if a path goes in both directions, it's between two included hexes and isn't needed
                    segments.remove((s1,s0))
                else:
                    segments.add((s0,s1))
        # at this point, segments should consist in a collection of circular non-intersecting paths
        segmentDict = {}
        for s in segments:
            segmentDict[s[0]] = s[1]
        while segmentDict:
            s0 = next(iter(segmentDict))
            s1 = segmentDict[s0]
            path = [s0,s1]
            del segmentDict[s0]
            s0 = s1
            try:
                while True:
                    s1 = segmentDict[s0]
                    del segmentDict[s0]
                    path.append(s1)
                    s0 = s1
                    if s1 == path[0]:
                        raise StopIteration
            except StopIteration:
                pass
            geoPath = []
            for p in path:
                geoPath.append(scale*self.displayFromIntegerCoordinates(p))
            yield tuple(geoPath)
            
    def getSVG(self, units="", stroke="black", fill="blue", strokeWidth=0.3, diameter=150):
        minX = float("inf")
        minY = float("inf")
        maxX = -minX
        maxY = -minY
        
        out = [None, "<path d='"]
        for path in self.getPaths(diameter=diameter):
            for z in path:
                minX = min(minX,z.real)
                minY = min(minY,z.imag)
                maxX = max(maxX,z.real)
                maxY = max(maxY,z.imag)
            out.append("M%.3f,%.3f " % (path[0].real,path[0].imag))
            for xy in path[1:]:
                out.append("L%.3f,%.3f " % (xy.real,xy.imag))
        out.append("'\n stroke='%s' fill='%s' stroke-width='%.3f'/>\n" % (stroke,fill,strokeWidth))
        out.append("</svg>\n")
        maxCoord = max(abs(minX),abs(minY),abs(maxX),abs(maxY))
        out[0] = ("<svg width='%.3f%s' height='%.3f%s' viewBox='%.3f %.3f %.3f %.3f' xmlns='http://www.w3.org/2000/svg'>\n" %
                    (maxCoord*2,units,maxCoord*2,units,-maxCoord,-maxCoord,2*maxCoord,2*maxCoord) )
        return "".join(out)
        
    def getShadedSVG(self, shader, diameter=150, units=""):
        minX = float("inf")
        minY = float("inf")
        maxX = -minX
        maxY = -minY
        
        scale = self.getScale(diameter)
        
        out = [None]
        
        for r in range(self.radius+1):
            for i in range(self.perimeter(r)):
                index = self.polarToIndex(self.reducePolar((r,i)))
                shade = shader(self.data[index])
                if shade is not None:
                    c = SymmetricHex.polarToIntegerCoordinates((r,i))
                    path = "<path d='"
                    for i,s in enumerate(SymmetricHex.getHexSegments(c)):
                        z = scale * self.displayFromIntegerCoordinates(s[0])
                        minX = min(minX,z.real)
                        minY = min(minY,z.imag)
                        maxX = max(maxX,z.real)
                        maxY = max(maxY,z.imag)
                        path += "%s%.3f,%.3f " % ( "M" if i==0 else "L", z.real, z.imag)
                    path += "' fill='%s' stroke='%s' stroke-width='0.1'/>" % (shade,shade)
                    out.append(path)
        out.append("</svg>")
        maxCoord = max(abs(minX),abs(minY),abs(maxX),abs(maxY))
        out[0] = ("<svg width='%.3f%s' height='%.3f%s' viewBox='%.3f %.3f %.3f %.3f' xmlns='http://www.w3.org/2000/svg'>\n" %
                    (maxCoord*2,units,maxCoord*2,units,-maxCoord,-maxCoord,2*maxCoord,2*maxCoord))
        return "\n".join(out)
        
    def getMinMax(self, getHexHeight):
        minHexHeight = float("inf")
        maxHexHeight = float("-inf")
        
        for i in self.indices:
            if self.isFilled(self.data[i]):
                h = getHexHeight(self.data[i])
                minHexHeight = min(minHexHeight,h)
                maxHexHeight = max(maxHexHeight,h)
                
        return minHexHeight,maxHexHeight
        
    def getMesh(self, diameter=150, levels=1, minHeight=1.5, maxHeight=3, getHexHeight=None):
        if maxHeight == minHeight:
            levels = 1
    
        if getHexHeight is None:
            getHexHeight = lambda hex : 1
            minHexHeight = 0
            maxHexHeight = 1
            levels = 1
        else:
            minHexHeight,maxHexHeight = self.getMinMax(getHexHeight)
                
        def getLevel(hex):
            if not self.isFilled(hex):
                return -1
            
            hexHeight = getHexHeight(hex)
            
            l = math.floor((hexHeight-minHexHeight)/(maxHexHeight-minHexHeight)*levels - 1)
            if l < 0:
                return 0
            elif l >= levels:
                return levels-1
            else:
                return int(l)
            
        mesh = []
        
        scale = self.getScale(diameter)
        
        prevOutHeight = 0
        
        for level in range(levels):
            if levels == 1:
                outHeight = maxHeight
            else:
                outHeight = minHeight + level*(maxHeight-minHeight)/(levels-1)

            def atZ(xy,z):
                return (xy.real,xy.imag,z)

            found = False
            
            for path in self.getPaths(diameter=diameter, filter = lambda hex : getLevel(hex) >= level):
                found = True
                for i in range(len(path)-1):
                    a = path[i]
                    b = path[i+1]
                    mesh.append( ( atZ(a,prevOutHeight), atZ(b,prevOutHeight), atZ(b,outHeight) ) )
                    mesh.append( ( atZ(a,prevOutHeight), atZ(b,outHeight), atZ(a,outHeight) ) )
                    
            if not found:
                break
                    
            for c in self.getHexIntegerCoordinates(filter = lambda hex : getLevel(hex) == level):
                centerXY = scale*self.displayFromIntegerCoordinates(c)
                for i in range(6):
                    o1 = SymmetricHex.CORNERS[i]
                    o2 = SymmetricHex.CORNERS[(i+1)%6]
                    xy1 = scale*self.displayFromIntegerCoordinates((c[0]+o1[0],c[1]+o1[1]))
                    xy2 = scale*self.displayFromIntegerCoordinates((c[0]+o2[0],c[1]+o2[1]))
                    mesh.append( ( atZ(centerXY,outHeight), atZ(xy1,outHeight), atZ(xy2,outHeight) ) )
                    mesh.append( ( atZ(centerXY,0), atZ(xy2,0), atZ(xy1,0) ) )             
                    
            prevOutHeight = outHeight

        return mesh
        
    @staticmethod
    def equalPoints(a,b):
        return math.abs(a-b) < 0.01
        
        
    @staticmethod
    def polarToIntegerCoordinates(ri):
        r,i = ri
        if r==0:
            return (0,0)
        c = (r*SymmetricHex.FIRST_NEIGHBOR[0],r*SymmetricHex.FIRST_NEIGHBOR[1])
        angle = i//r
        for a in range(angle):
            c = (c[0]+r*SymmetricHex.NEIGHBOR_OFFSETS[a][0],c[1]+r*SymmetricHex.NEIGHBOR_OFFSETS[a][1])
        offset = i-r*angle
        return (c[0]+offset*SymmetricHex.NEIGHBOR_OFFSETS[angle][0],c[1]+offset*SymmetricHex.NEIGHBOR_OFFSETS[angle][1])
            
    @staticmethod 
    def rowSize(r):
        return int(math.ceil((r+1)/2.))
        
    @staticmethod
    def perimeter(r):
        return 1 if r==0 else 6*r

if __name__ == '__main__':
    import random
    import exportmesh
    
    random.seed(1)

    h = SymmetricHex(15,initializer=lambda ri: ri[0]<3) # random.randint(0,15)==0)
    exportmesh.saveSTL("test.stl", h.getMesh())
    
