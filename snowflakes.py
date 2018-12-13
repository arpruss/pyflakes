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
    # i. Diffusion
    for ri in board.getCoordinates():
        hex = board[ri]
        if not hex.a:
            if hex.filledNeighbors:
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
            if hex.filledNeighbors:
                hex.b += (1-kappa)*hex.d
                hex.c += kappa*hex.d
                hex.d = 0.
                
    # iii. Attachment

    for ri in board.getCoordinates():
        hex = board[ri]
        if hex.filledNeighbors and not hex.a:
            n = hex.filledNeighbors
            if ( ( hex.b >= beta and n <= 2 ) or 
                 ( n == 3 and ( hex.b >= 1 or (hex.b >= alpha and hex.d + sum(board[y].d for y in board.getNeighbors(ri)) < theta) ) ) or
                 n >= 4 ):
                hex.a = True
                hex.c += hex.b
                hex.b = 0.
                for y in board.getNeighbors(ri):
                    board[y].filledNeighbors += 1
                
    # iv. Melting
    for ri in board.getCoordinates():
        hex = board[ri]
        if not hex.a:
            if hex.filledNeighbors:
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
