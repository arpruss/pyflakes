# algorithm based on http://psoup.math.wisc.edu/papers/h2l.pdf

from __future__ import print_function
import exportmesh
import symmetrichex
import random
import sys

class HexState(object):
    def __init__(self,a,b,c,d,filledNeighbors):
        self.a = a
        self.b = b
        self.c = c 
        self.d = d
        self.filledNeighbors = filledNeighbors
        
    def __bool__(self):
        return self.a
        
    def clone(self):
        return HexState(self.a,self.b,self.c,self.d,self.filledNeighbors)
        
    def __repr__(self):
        return "(%s,%g,%g,%g,%d)" % (self.a,self.b,self.c,self.d,self.filledNeighbors)
    
    __nonzero__ = __bool__

#defaults: http://mkweb.bcgsc.ca/snowflakes/flake.mhtml?flake=morptel
def gravner_griffeath(radius = 400,
        rho = 0.4293822506,
        kappa = 0.0022182122,
        mu = 0.1170975026,
        gamma = 0.0000685220,
        alpha = 0.0718350008,
        beta = 1.0949972145,
        theta = 0.0591767342,
        sigma = 0, # 1e-5
        steps = 11849,
        progress = True):        

    def initializer(i):
        r,i = i
        if r == 0:
            return HexState(a=True,b=0,c=1,d=0,filledNeighbors=0)
        elif r == 1:
            return HexState(a=False,b=0,c=0,d=rho,filledNeighbors=1)
        else:
            return HexState(a=False,b=0,c=0,d=rho,filledNeighbors=0)

    def evolve():
        # i. Diffusion
        for i in unfilled:
            hex = board[i]
            if hex.filledNeighbors:
                s = hex.d
                for y in board.neighbors[i]:
                    nhex = board[y]
                    if nhex.a:
                        s += hex.d
                    else:
                        s += nhex.d
                scratch[i] = s / 7.
            else:
                scratch[i] = (hex.d + sum(board[y].d for y in board.neighbors[i])) / 7.
                
        for i in unfilled:
            hex = board[i]
            d = scratch[i]
            
            # ii. Freezing
            if hex.filledNeighbors:
                hex.b += (1-kappa)*d
                hex.c += kappa*d
                hex.d = 0.
            else:
                hex.d = d
                
            # for next step
            scratch[i] = False
                
        froze = False
        for i in unfilled:
            hex = board[i]
            if hex.filledNeighbors:
                # iii. Attachment
                n = abs(hex.filledNeighbors)
                if ( ( hex.b >= beta and n <= 2 ) or 
                     ( n == 3 and ( hex.b >= 1 or (hex.b >= alpha and sum(board[y].d for y in board.neighbors[i]) < theta) ) ) or
                     n >= 4 ):
                    hex.a = True
                    hex.c += hex.b
                    hex.b = 0.
                    for i in board.neighbors[i]:
                        scratch[i] = True
                    froze = True

        if froze:
            del unfilled[:]
            for i in board.indices:
                hex = board[i]
                if not hex.a:
                    unfilled.append(i)
                    if scratch[i]:
                        hex.filledNeighbors = 0
                        for y in board.neighbors[i]:
                            if board[y].a:
                                hex.filledNeighbors += 1
                    
        # iv. Melting
        for i in unfilled:
            hex = board[i]
            if hex.filledNeighbors:
                hex.d += mu * hex.b + gamma * hex.c
                hex.b *= 1-mu
                hex.c *= 1-gamma

            # v. Noise
            hex.d += random.choice((-1,1))*sigma*hex.d

    board = symmetrichex.SymmetricHex(radius, initializer=initializer, isFilled=lambda hex:hex.a)
    scratch = [0 for i in board.indices]
    unfilled = [y for y in board.indices if not board[y].a]
                
    progressSteps = steps // 20
    if steps == 0:
        progress = False
                
    for i in range(steps):
        evolve()
        if progress and i % progressSteps == 0:
            print(("[%.0f%%]" % (100.*i/steps)), file=sys.stderr, end="")            
        
    print("[100%]", file=sys.stderr)            
    return board
    
if __name__ == '__main__':
    radius = 400
    rho = 0.4293822506
    kappa = 0.0022182122
    mu = 0.1170975026
    gamma = 0.0000685220
    alpha = 0.0718350008
    beta = 1.0949972145
    theta = 0.0591767342
    sigma = 0 # 1e-5
    steps = 11849

    seed = 1
    name = "morptel"
    targetSize = 190
    maxHeight = 3
    minHeight = 0.5
            

    random.seed(seed)
    
    board = gravner_griffeath(radius=radius, rho=rho, kappa=kappa, mu=mu, gamma=gamma, alpha=alpha, beta=beta, theta=theta, sigma=sigma,
                steps=steps)

    minC = float("inf")
    maxC = float("-inf")
    for hex in board.data:
        if hex.a:
            minC = min(minC, hex.c)
            maxC = max(maxC, hex.c)

    def shader(hex):
        def interpolateColor(y0,y1,c0,c1,y):
            def clampColor(c):
                ci = int(c+0.5)
                if ci < 0:
                    return 0
                elif ci > 255:
                    return 255
                else:
                    return 255
            out = tuple((c1[i]-c0[i])*float(y-y0)/(y1-y0)+c0[i] for i in range(3))
            return "rgb(%d,%d,%d)" % out
            
        if hex.a:
            return interpolateColor(minC,maxC,(220,220,255),(0,0,255),hex.c)
        else:
            return None              
            
    exportmesh.saveSTL(name+".stl", board.getMesh(minHeight=minHeight,maxHeight=maxHeight,levels=5,diameter=targetSize,getHexHeight=lambda hex:hex.c))
    print("Saving %s.svg" % name)
    with open(name+".svg", "w") as f:
        f.write(board.getSVG(diameter=targetSize))


