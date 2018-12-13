# algorithm based on http://psoup.math.wisc.edu/papers/h2l.pdf

import exportmesh
from symmetrichex import SymmetricHex
import random

radius = 500
steps = 300
rho = 0.46
kappa = 0.0025
beta = 1.9
alpha = 0.35
theta = 0.112
mu = 0.06
gamma = 0.00006
sigma = 1e-5

class HexState(object):
    def __init__(self,a,b,c,d,bdy):
        self.a = a
        self.b = b
        self.c = c 
        self.d = d
        self.bdy = bdy
        
    def __bool__(self):
        return bool(self.a)
        
    def clone(self):
        return HexState(self.a,self.b,self.c,self.d,self.bdy)
        
    def __repr__(self):
        return "(%s,%s,%g,%g,%g)" % (self.a,self.bdy,self.b,self.c,self.d)
    
    __nonzero__ = __bool__
    
def initializer(ri):
    r,i = ri
    if r == 0:
        return HexState(a=True,b=0,c=1,d=0,bdy=False)
    elif r == 1:
        return HexState(a=False,b=0,c=0,d=rho,bdy=True)
    else:
        return HexState(a=False,b=0,c=0,d=rho,bdy=False)
        
def outside(ri):
    return OUTSIDE
    
def evolve():
    # i. Diffusion
    for ri in board.getCoordinates():
        hex = board[ri]
        if not hex.a:
            if hex.bdy:
                s = hex.d
                for y in board.getNeighbors(ri):
                    nhex = board[y]
                    if nhex.a:
                        s += hex.d
                    else:
                        s += nhex.d
                scratch[ri] = s / 7.
            else:
                scratch[ri] = (hex.d + sum(board[y].d for y in board.getNeighbors(ri))) / 7.
            
    for ri in board.getCoordinates():
        hex = board[ri]
        
        if not hex.a:
            hex.d = scratch[ri]
    
            # ii. Freezing
            if hex.bdy:
                hex.b += (1-kappa)*hex.d
                hex.c += kappa*hex.d
                hex.d = 0.
                
    # iii. Attachment

    frozeSomething = False
    for ri in board.getCoordinates():
        hex = board[ri]
        if hex.bdy:
            n = board.countFilledNeighbors(ri)
            if ( ( (n == 1 or n == 2) and hex.b >= beta ) or 
                 ( n == 3 and ( hex.b >= 1 or (hex.b >= alpha and hex.d + sum(board[y].d for y in board.getNeighbors(ri)) < theta) ) ) or
                 n >= 4 ):
                hex.a = True
                hex.c += hex.b
                hex.b = 0.
                hex.bdy = False
                frozeSomething = True
                
    for ri in board.getCoordinates():
        hex = board[ri]
        if not hex.a:
            if frozeSomething:
                hex.bdy = any(board[y].a for y in board.getNeighbors(ri))
            
            # iv. Melting
            if hex.bdy:
                hex.d += mu * hex.b + gamma * hex.c
                hex.b *= 1-mu
                hex.c *= 1-gamma

            # v. Noise
            hex.d += random.choice((-1,1))*sigma*hex.d

board = SymmetricHex(radius, initializer=initializer,  
            scale=5, isFilled=lambda hex:hex.a)
scratch = SymmetricHex(radius, initializer=0)
    
for i in range(steps):
    evolve()
    if i % 100 == 0:
        print(i)
        print(board.data[30])
        
exportmesh.saveSTL("flake.stl", board.getMesh(height=5))
