# algorithm based on http://psoup.math.wisc.edu/papers/h2l.pdf

import exportmesh
from symmetrichex import SymmetricHex
import random

#http://mkweb.bcgsc.ca/snowflakes/flake.mhtml?flake=morptel
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

class HexState(object):
    def __init__(self,a,b,c,d,filledNeighbors):
        self.a = a
        self.b = b
        self.c = c 
        self.d = d
        self.filledNeighbors = filledNeighbors
        
    def __bool__(self):
        return bool(self.a)
        
    def clone(self):
        return HexState(self.a,self.b,self.c,self.d,self.filledNeighbors)
        
    def __repr__(self):
        return "(%s,%g,%g,%g,%d)" % (self.a,self.b,self.c,self.d,self.filledNeighbors)
    
    __nonzero__ = __bool__
    
def initializer(ri):
    r,i = ri
    if r == 0:
        return HexState(a=True,b=0,c=1,d=0,filledNeighbors=0)
    elif r == 1:
        return HexState(a=False,b=0,c=0,d=rho,filledNeighbors=1)
    else:
        return HexState(a=False,b=0,c=0,d=rho,filledNeighbors=0)

def evolve():
    global unfilled
    
    # i. Diffusion
    for ri in unfilled:
        hex = board[ri]
        if hex.filledNeighbors:
            s = hex.d
            for y in board.getNeighbors(ri):
                nhex = board[y]
                if nhex.a:
                    s += hex.d
                else:
                    s += nhex.d
            new_d[ri] = s / 7.
        else:
            new_d[ri] = (hex.d + sum(board[y].d for y in board.getNeighbors(ri))) / 7.
            
    for ri in unfilled:
        hex = board[ri]
        d = new_d[ri]
        
        # ii. Freezing
        if hex.filledNeighbors:
            hex.b += (1-kappa)*d
            hex.c += kappa*d
            hex.d = 0.
        else:
            hex.d = d
            
    froze = False
    for ri in unfilled:
        hex = board[ri]
        if hex.filledNeighbors:
            # iii. Attachment
            n = hex.filledNeighbors
            if ( ( hex.b >= beta and n <= 2 ) or 
                 ( n == 3 and ( hex.b >= 1 or (hex.b >= alpha and sum(board[y].d for y in board.getNeighbors(ri)) < theta) ) ) or
                 n >= 4 ):
                hex.a = True
                hex.c += hex.b
                hex.b = 0.
                for y in set(board.getNeighbors(ri)):
                    board[y].filledNeighbors += 1
                froze = True

    if froze:
        unfilled = tuple(y for y in board.getCoordinates() if not board[y].a)
                
    # iv. Melting
    for ri in unfilled:
        hex = board[ri]
        if hex.filledNeighbors:
            hex.d += mu * hex.b + gamma * hex.c
            hex.b *= 1-mu
            hex.c *= 1-gamma

        # v. Noise
        hex.d += random.choice((-1,1))*sigma*hex.d

board = SymmetricHex(radius, initializer=initializer,  
            scale=5, isFilled=lambda hex:hex.a)
new_d = SymmetricHex(radius, initializer=0)
unfilled = tuple(y for y in board.getCoordinates() if not board[y].a)
            
for i in range(steps):
    evolve()
#    if i % 100 == 0:
#        print(i)
#        print(board.data[30])
        
#exportmesh.saveSTL("flake.stl", board.getMesh(height=5))
print(board.getSVG())
