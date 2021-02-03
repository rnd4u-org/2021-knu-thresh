from number import *
from VSS import *

class Session:

    def __init__(self, n, t, f, tau, params):
        self.n = n
        self.t = t
        self.f = f
        self.tau = tau
        self.params = params
        self.p = None
        self.q = None
        self.g = None
        self.secret = None
        self.setParams(params)
        self.sharePhase = SharePhase(n, t, f, tau, params)

    def setParams(self, params):
        self.p = params['p']
        self.q = params['q']
        self.g = params['g']

    def generateSecret(self):
        self.secret = getRandomRange(1, self.p - 1)

    def shareSecret(self):
        self.sharePhase.share(self.secret)
        C_lst = []
        alphas_lst = []
        for node in self.sharePhase.participants:
            C, alphas = self.sharePhase.send(node, node.C, node.a)
            C_lst.append(C)
            alphas_lst.append(alphas)

        C_lst_echo = []
        alphas_lst_echo = []
        for i in range(self.n):
            node = self.sharePhase.participants[i]
            for j in range(self.n):
                C, alphas = self.sharePhase.echo(node, C_lst[j], j+1, alphas_lst[j][i])
            C_lst_echo.append(C)
            alphas_lst_echo.append(alphas)

        for i in range(self.n):
            node = self.sharePhase.participants[i]
            for j in range(self.n):
                self.sharePhase.ready(node, C_lst_echo[i], i + 1, alphas_lst_echo[i][j])
