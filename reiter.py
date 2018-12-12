from symmetrichex import SymmetricHex
import random
import exportmesh

alpha = 1.6
beta = 0.7
gamma = 0.003
gamma_variation_amplitude_ratio = 0.5
random_beta_variation = 0.4
radius = 200
steps = 400
seed = 1

random.seed(seed)

def initializer(ri):
    if ri[0] == 0:
        return 1
    else:
        return beta+random.uniform(-random_beta_variation/2,random_beta_variation/2)

board = SymmetricHex(radius, initializer=initializer,  
            scale=5, isFilled=lambda v : v >= 1)
scratch = SymmetricHex(radius, initializer=0)

def receptive(ri):
    for y in board.getNeighborsInclusive(ri):
        if board[y] >= 1:
            return True
    return False
    
def u(ri):
    if receptive(ri):
        return 0
    else:
        return board[ri]

def adjustedGamma():
    return (1+random.uniform(-gamma_variation_amplitude_ratio,gamma_variation_amplitude_ratio)) * gamma
        
def evolve():
    for ri in board.getCoordinates():
        u0 = u(ri)
        scratch[ri] = (adjustedGamma()+board[ri] if u0==0 else (1-alpha/2)*u0) + (alpha/12)*sum(u(y) for y in board.getNeighbors(ri))
    for ri in board.getCoordinates():
        board[ri] = scratch[ri]

for i in range(steps):
    evolve()

exportmesh.saveSTL("reiter.stl", board.getMesh(height=5))

