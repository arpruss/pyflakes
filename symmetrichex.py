import math

class SymmetricHex(object):
    def __init__(self,radius, initializer=0, outside=0, scale=1., isFilled=bool):
        self.radius = radius
        init = initializer if callable(initializer) else lambda ri: initializer
        self.data = [ [ init((r,i)) for i in range(SymmetricHex.rowSize(r)) ] for r in range(radius+1) ]
        self.outside = outside if callable(outside) else lambda ri: outside
        self.scale = scale
        self.isFilled = isFilled
        
    def importData(self, h):
        self.data = tuple( a[:] for a in h.data )
        
    def clone(self):
        h = SymmetricHex(self.radius, outside=self.outside, scale=self.scale, isFilled=self.isFilled)
        h.data = tuple( [b.clone() for b in a] for a in self.data )
        return h
        
    def getCoordinates(self):
        for r in range(self.radius):
            for i in range(SymmetricHex.rowSize(r)):
                yield (r,i)
                
    def countFilledNeighbors(self, ri):
        return sum(1 for n in self.getNeighbors(ri) if self.isFilled(self[n]))
        
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
        
    def getData(self, ri):
        try:
            return self.data[ri]
        except:
            r,i = SymmetricHex.reduceCoordinates(ri)
            if r <= self.radius:
                return self.data[r][i]
            else:
                return self.outside((r,i))
            
    def __getitem__(self, ri):
        return self.data[ri[0]][ri[1]]
            
    def __setitem__(self, ri, v):
        self.data[ri[0]][ri[1]] = v
            
    def getNeighbors(self, ri):
        r,i = ri
        
        if r == 0:
            return ((1,0),(1,0),(1,0),(1,0),(1,0),(1,0))
        elif r == 1:
            return ((0,0),(1,0),(1,0),(2,0),(2,1),(2,1))
        else:
            if i == 0:
                return ((r,1),(r,1),(r+1,0),(r+1,1),(r+1,1),(r-1,0))
            elif i >= SymmetricHex.rowSize(r)-2:
                return map(SymmetricHex.reduceCoordinates,((r,i-1),(r,i+1),(r+1,i),(r+1,i+1),(r-1,i),(r-1,i-1)))
            else:
                return ((r,i-1),(r,i+1),(r+1,i),(r+1,i+1),(r-1,i),(r-1,i-1))
        
    def getNeighborsInclusive(self, ri):
        yield ri
        for y in self.getNeighbors(ri):
            yield y
        
    FIRST_NEIGHBOR = (-1,2)
    NEIGHBOR_OFFSETS = ((-1,-1),(1,-2),(2,-1),(1,1),(-1,2),(-2,1))
    CORNERS = ((1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1))
        
    def fromIntegerCoordinates(self,xy):
        # 2 1 
        # 3 x 0
        #   4 5
        x,y = xy
        return 0.5 * self.scale * complex((x + y / 2.) * math.sqrt(3), y * 1.5)
        
    def getTriangleIntegerCoordinates(self):
        for r in range(self.radius+1):
            for i in range(SymmetricHex.perimeter(r)):
                if self.isFilled(self.getData((r,i))):
                    yield SymmetricHex.getIntegerCoordinates((r,i))
        
    def getPaths(self):
        segments = set()
        for c in self.getTriangleIntegerCoordinates():
            for i in range(6):
                o1 = SymmetricHex.CORNERS[i]
                o2 = SymmetricHex.CORNERS[(i+1)%6]
                p1 = (c[0]+o1[0],c[1]+o1[1])
                p2 = (c[0]+o2[0],c[1]+o2[1])
                if (p2,p1) in segments:
                    segments.remove((p2,p1))
                else:
                    segments.add((p1,p2))   
        while segments:
            s = next(iter(segments))
            segments.remove(s)
            path = [s[0],s[1]]
            found = True
            while found:
                found = False
                for s in segments:
                    if s[0] == path[-1]:
                        path.append(s[1])
                        segments.remove(s)
                        found = True
                        break
            geoPath = []
            for p in path:
                geoPath.append(self.fromIntegerCoordinates(p))
            yield geoPath               
            
    def getSVG(self, units="", stroke="black", fill="blue", strokeWidth=0.3):
        minX = float("inf")
        minY = float("inf")
        maxX = -minX
        maxY = -minY
        
        out = "<path d='"
        for path in self.getPaths():
            for z in path:
                minX = min(minX,z.real)
                minY = min(minY,z.imag)
                maxX = max(maxX,z.real)
                maxY = max(maxY,z.imag)
            out += "M%.3f,%.3f " % (path[0].real,path[0].imag)
            for xy in path[1:]:
                out += "L%.3f,%.3f " % (xy.real,xy.imag)
        out += "'\n stroke='%s' fill='%s' stroke-width='%.3f'/>\n" % (stroke,fill,strokeWidth)
        out += "</svg>"
        maxCoord = max(abs(minX),abs(minY),abs(maxX),abs(maxY))
        out = ("<svg width='%.3f%s' height='%.3f%s' viewBox='%.3f %.3f %.3f %.3f' xmlns='http://www.w3.org/2000/svg'>\n" %
                    (maxCoord*2,units,maxCoord*2,units,-maxCoord,-maxCoord,2*maxCoord,2*maxCoord)
                    + out)
        return out
        
    def getMesh(self, height=1):
        mesh = []
        
        def level(xy,z):
            return (xy.real,xy.imag,z)

        for path in self.getPaths():
            for i in range(len(path)):
                a = path[i]
                b = path[(i+1)%len(path)]
                mesh.append( ( level(a,0), level(b,0), level(b,height) ) )
                mesh.append( ( level(a,0), level(b,height), level(a,height) ) )
                
        for c in self.getTriangleIntegerCoordinates():
            centerXY = self.fromIntegerCoordinates(c)
            for i in range(6):
                o1 = SymmetricHex.CORNERS[i]
                o2 = SymmetricHex.CORNERS[(i+1)%6]
                xy1 = self.fromIntegerCoordinates((c[0]+o1[0],c[1]+o1[1]))
                xy2 = self.fromIntegerCoordinates((c[0]+o2[0],c[1]+o2[1]))
                mesh.append( ( level(centerXY,height), level(xy1,height), level(xy2,height) ) )
                mesh.append( ( level(centerXY,0), level(xy2,0), level(xy1,0) ) )             

        return mesh
        
    @staticmethod
    def equalPoints(a,b):
        return math.abs(a-b) < 0.01
        
        
    @staticmethod
    def getIntegerCoordinates(ri):
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

    h = SymmetricHex(15,initializer=lambda ri: True or ri[0]<=5 and random.randint(0,2)!=0,outside=False,scale=10)
    print(h.getSVG())
    exportmesh.saveSTL("test.stl", h.getMesh())
    
