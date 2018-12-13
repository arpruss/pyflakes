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
scale = 2
height = 3

random.seed(seed)

def initializer(i):
    if i[0] == 0:
        return 1
    else:
        return beta+random.uniform(-random_beta_variation/2,random_beta_variation/2)

board = SymmetricHex(radius, initializer=initializer,  
            scale=scale, isFilled=lambda v : v >= 1)
scratch = [0 for i in board.indices]

def receptive(i):
    if board[i] >= 1:
        return True
    for y in board.neighbors[i]:
        if board[y] >= 1:
            return True
    return False
    
def u(i):
    if receptive(i):
        return 0
    else:
        return board[i]

def adjustedGamma():
    return (1+random.uniform(-gamma_variation_amplitude_ratio,gamma_variation_amplitude_ratio)) * gamma
        
def evolve():
    for i in board.indices:
        u0 = u(i)
        scratch[i] = (adjustedGamma()+board[i] if u0==0 else (1-alpha/2)*u0) + (alpha/12)*sum(u(y) for y in board.neighbors[i])
    for i in board.indices:
        board[i] = scratch[i]

for i in range(steps):
    evolve()

print(board.getSVG())
exportmesh.saveSTL("reiter.stl", board.getMesh(height=height))
