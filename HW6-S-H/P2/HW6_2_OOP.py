# region imports
import numpy as np
import math
from scipy.optimize import fsolve
import random as rnd
# endregion

# region class definitions
class Fluid():
    def __init__(self, mu=0.00089, rho=1000):
        self.mu = mu
        self.rho = rho
        self.nu = mu / rho

class Node():
    def __init__(self, Name='a', Pipes=[], ExtFlow=0):
        self.name = Name
        self.pipes = Pipes
        self.extFlow = ExtFlow

    def getNetFlowRate(self):
        Qtot = self.extFlow
        for p in self.pipes:
            Qtot += p.getFlowIntoNode(self.name)
        return Qtot

class Loop():
    def __init__(self, Name='A', Pipes=[]):
        self.name = Name
        self.pipes = Pipes

    def getLoopHeadLoss(self):
        deltaP = 0
        startNode = self.pipes[0].startNode
        for p in self.pipes:
            phl = p.getFlowHeadLoss(startNode)
            deltaP += phl
            startNode = p.endNode if startNode != p.endNode else p.startNode
        return deltaP

class Pipe():
    def __init__(self, Start='A', End='B', L=100, D=200, r=0.00025, fluid=Fluid()):
        self.startNode = min(Start, End)
        self.endNode = max(Start, End)
        self.length = L
        self.r = r
        self.fluid = fluid
        self.d = D / 1000.0
        self.relrough = self.r / self.d
        self.A = math.pi / 4.0 * self.d**2
        self.Q = 10
        self.vel = self.V()
        self.reynolds = self.Re()

    def V(self):
        return self.Q / self.A

    def Re(self):
        return self.fluid.rho * self.V() * self.d / self.fluid.mu

    def FrictionFactor(self):
        def CB(f):
            return 1 / (f**0.5) + 2.0 * np.log10(self.relrough / 3.7 + 2.51 / (self.Re() * f**0.5))

        def lam():
            return 64 / self.Re()

        if self.Re() >= 4000:
            return fsolve(CB, 0.01)[0]
        if self.Re() <= 2000:
            return lam()

        CBff = fsolve(CB, 0.01)[0]
        Lamff = lam()
        mean = Lamff + ((self.Re() - 2000) / (4000 - 2000)) * (CBff - Lamff)
        sig = 0.2 * mean
        return rnd.normalvariate(mean, sig)

    def frictionHeadLoss(self):
        g = 9.81
        ff = self.FrictionFactor()
        hl = ff * self.length * self.V()**2 / (2 * g)
        return hl

    def getFlowHeadLoss(self, s):
        nTraverse = 1 if s == self.startNode else -1
        nFlow = 1 if self.Q >= 0 else -1
        return nTraverse * nFlow * self.frictionHeadLoss()

    def Name(self):
        return self.startNode + '-' + self.endNode

    def oContainsNode(self, node):
        return self.startNode == node or self.endNode == node

    def printPipeFlowRate(self):
        print('The flow in segment {} is {:0.4f} m^3/s'.format(self.Name(), self.Q))

    def getFlowIntoNode(self, n):
        if n == self.startNode:
            return -self.Q
        return self.Q


class PipeNetwork():
    def __init__(self, Pipes=[], Loops=[], Nodes=[], fluid=Fluid()):
        self.loops = Loops
        self.nodes = Nodes
        self.Fluid = fluid
        self.pipes = Pipes

    def findFlowRates(self):
        N = len(self.nodes) + len(self.loops)
        Q0 = np.full(N, 10)

        def fn(q):
            for i in range(len(self.pipes)):
                self.pipes[i].Q = q[i]
            L = self.getNodeFlowRates() + self.getLoopHeadLosses()
            return L

        FR = fsolve(fn, Q0)
        return FR

    def getNodeFlowRates(self):
        qNet = [n.getNetFlowRate() for n in self.nodes]
        return qNet

    def getLoopHeadLosses(self):
        lhl = [l.getLoopHeadLoss() for l in self.loops]
        return lhl

    def getPipe(self, name):
        for p in self.pipes:
            if name == p.Name():
                return p

    def getNodePipes(self, node):
        l = []
        for p in self.pipes:
            if p.oContainsNode(node):
                l.append(p)
        return l

    def nodeBuilt(self, node):
        for n in self.nodes:
            if n.name == node:
                return True
        return False

    def getNode(self, name):
        for n in self.nodes:
            if n.name == name:
                return n

    def buildNodes(self):
        for p in self.pipes:
            if not self.nodeBuilt(p.startNode):
                self.nodes.append(Node(p.startNode, self.getNodePipes(p.startNode)))
            if not self.nodeBuilt(p.endNode):
                self.nodes.append(Node(p.endNode, self.getNodePipes(p.endNode)))

    def printPipeFlowRates(self):
        for p in self.pipes:
            p.printPipeFlowRate()

    def printNetNodeFlows(self):
        for n in self.nodes:
            print('Net flow into node {} is {:0.2e} m^3/s'.format(n.name, n.getNetFlowRate()))

    def printLoopHeadLoss(self):
        for l in self.loops:
            print('Head loss for loop {} is {:0.2e} m^3/s'.format(l.name, l.getLoopHeadLoss()))


# endregion

# region function definitions
def main():
    water = Fluid()
    roughness = 0.00025

    PN = PipeNetwork()
    PN.pipes.append(Pipe('a', 'b', 250, 300, roughness, water))
    PN.pipes.append(Pipe('a', 'c', 100, 200, roughness, water))
    PN.pipes.append(Pipe('b', 'e', 100, 200, roughness, water))
    PN.pipes.append(Pipe('c', 'd', 125, 200, roughness, water))
    PN.pipes.append(Pipe('c', 'f', 100, 150, roughness, water))
    PN.pipes.append(Pipe('d', 'e', 125, 200, roughness, water))
    PN.pipes.append(Pipe('d', 'g', 100, 150, roughness, water))
    PN.pipes.append(Pipe('e', 'h', 100, 150, roughness, water))
    PN.pipes.append(Pipe('f', 'g', 125, 250, roughness, water))
    PN.pipes.append(Pipe('g', 'h', 125, 250, roughness, water))

    PN.buildNodes()

    PN.getNode('a').extFlow = 60
    PN.getNode('d').extFlow = -30
    PN.getNode('f').extFlow = -15
    PN.getNode('h').extFlow = -15

    PN.loops.append(Loop('A', [PN.getPipe('a-b'), PN.getPipe('b-e'), PN.getPipe('d-e'), PN.getPipe('c-d'), PN.getPipe('a-c')]))
    PN.loops.append(Loop('B', [PN.getPipe('c-d'), PN.getPipe('d-g'), PN.getPipe('f-g'), PN.getPipe('c-f')]))
    PN.loops.append(Loop('C', [PN.getPipe('d-e'), PN.getPipe('e-h'), PN.getPipe('g-h'), PN.getPipe('d-g')]))

    PN.findFlowRates()

    PN.printPipeFlowRates()
    print()
    print('Check net node flows:')
    PN.printNetNodeFlows()
    print()
    print('Check loop head loss:')
    PN.printLoopHeadLoss()


# endregion

# region function calls
if __name__ == "__main__":
    main()
# endregion
