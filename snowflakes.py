# algorithm based on http://psoup.math.wisc.edu/papers/h2l.pdf

import exportmesh
from symmetrichex import SymmetricHex
import random

radius = 500
steps = 10000
rho = 0.38
kappa = 0.001
beta = 1.06
alpha = 0.35
theta = 0.112
mu = 0.14
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
            scratch[ri].d = sum(board[y].d for y in board.getNeighborsInclusive(ri)) / 7.
    for ri in board.getCoordinates():
        hex = board[ri]
        if not hex.a:
            board[ri].d = scratch[ri].d
        
    # ii. Freezing
    for ri in board.getCoordinates():
        hex = board[ri]
        if hex.bdy:
            hex.b += (1-kappa)*hex.d
            hex.c += kappa*hex.d
            hex.d = 0

    # iii. Attachment
    for ri in board.getCoordinates():
        hex = board[ri]
        if hex.bdy:
            n = board.countFilledNeighbors(ri)
            if ( ( (n == 1 or n == 2) and hex.b >= beta ) or 
                 ( n == 3 and ( hex.b >= 1 or (hex.b >= alpha and sum(board[y].d for y in board.getNeighborsInclusive(ri)) < theta) ) ) or
                 n >= 4 ):
                hex.a = True
                hex.c = hex.b + hex.c
                hex.b = 0
                
    for ri in board.getCoordinates():
        hex = board[ri]
        if hex.a:
            hex.bdy = False
        else:
            hex.bdy = any(board[y].a for y in board.getNeighbors(ri))

    # iv. Melting
    for ri in board.getCoordinates():
        hex = board[ri]
        if hex.bdy:
            hex.b = (1-mu)*hex.b
            hex.c = (1-gamma)*hex.c 
            hex.d = hex.d + mu * hex.b + gamma * hex.c
        
    # v. Noise
    for ri in board.getCoordinates():
        hex = board[ri]
        hex.d += random.choice((-1,1))*sigma*hex.d
        
board = SymmetricHex(radius, initializer=initializer, outside=HexState(a=0,b=0,c=0,d=rho,bdy=False), 
            scale=5, isFilled=lambda hex:hex.a)
scratch = board.clone()
    
for i in range(steps):
    evolve()
    if i % 100 == 0:
        print(i)
        
exportmesh.saveSTL("flake.stl", board.getMesh(height=5))
