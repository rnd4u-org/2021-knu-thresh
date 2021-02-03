import numpy as np
from number import *
from lagrange_interpolate import *

class SharePhase:

    @staticmethod
    def verify_poly(C, i, a):
        #C = np.array(C)
        #a = np.array(a)
        #deg = i**np.arange(a.shape[0] + 1)
        #val1 = self.g**np.mod(a, self.q)
        #C1 = np.power(C, deg)
        #val2 = np.prod(C1, axis=0)
        #return val1==val2
        return True

    @staticmethod
    def verify_point(C, i, m, alpha):
        #val1 = self.g**alpha
        #l = np.arange(self.t)
        #j = np.arange(self.t)
        #ar1 = np.array([np.power(m, j)])
        #ar2 = np.array([np.power(i, l)])
        #deg = ar1.T@ar2
        #C = np.array(C)
        #val2 = np.prod(np.power(C, deg))
        #return val1 == val2
        return True

    def __init__(self, n, t, f, tau, params):
        self.n = n
        self.t = t
        self.f = f
        self.p = None
        self.q = None
        self.g = None
        self.setParams(params)
        self.tau = tau
        self.participants = []
        for i in range(self.n):
            self.participants.append(Node(i+1))

    def setParams(self, params):
        self.p = params['p']
        self.q = params['q']
        self.g = params['g']

    def share(self, s):
        phi = [[getRandomRange(1, self.p - 1) for _ in range(0, self.t + 1)] for __ in range(0, self.t + 1)]
        phi[0][0] = s
        #C = np.power(g, phi)
        C = []
        for i in range(self.t + 1):
            C.append([])
            for j in range(self.t + 1):
                val = pow(self.g, phi[i][j], self.p)
                #print("val = ", val)
                C[i].append(val)
        for j in range(self.n):
            #x = j**np.arange(1, n+1)
            x = []
            for i in range(1, self.n+1):
                x.append((j + 1)**i)
            matr = C
            for i in range(self.t + 1):
                for l in range(self.t + 1):
                    matr[i][l] = (matr[i][l] * x[l]) % self.p
            a = []
            for i in range(self.t + 1):
                a.append(0)
                for l in range(self.t + 1):
                    a[i] = (a[i] + matr[l][i]) % self.p
            #matr = phi*x
            #a = np.sum(matr, axis=0)
            print("sending to ", j)
            #self.send(self.participants[j], C, a)
            self.participants[j].C = C
            self.participants[j].a = a

    def send(self, node, C, a):
        i = node.id
        if self.verify_poly(C, i, a):
            alphas = []
            for j in range(self.n):
                print(j, self.n, len(self.participants))
                node_ = self.participants[j]
                #y = (j + 1)**np.arange(n+1)
                #alpha = np.mod(np.sum(a*y), self.q)
                alpha = 0
                for k in range(self.t + 1):
                    alpha += a[k] * ((j+1)**k)
                alpha = alpha % self.q
                alphas.append(alpha)
                print("echo to ", j)
                #self.echo(node_, C, i, alpha)
            return C, alphas

    def echo(self, node, C, m, alpha):
        i = node.id
        if self.verify_point(C, i, m, alpha):
            #np.anppend(node.Ac, np.array([m, alpha]))
            node.Ac.append([m, alpha])
            node.e_c += 1
            if node.e_c == int((self.n + self.t + 1) / 2) + 1 and node.r_c < self.t + 1:
                a_list = []
                for j in range(self.n):
                    node_ = self.participants[j]
                    #a_ = lagrange_interpolate(j+1, list(node.Ac[:, :1].reshape((1, node.Ac.shape[0]))[0]),
                    #                          list(node.Ac[:, 1:].reshape((1, node.Ac.shape[0]))[0]), p)
                    x = [el[0] for el in node.Ac]
                    y = [el[1] for el in node.Ac]
                    a_ = lagrange_interpolate(j+1, x, y, self.p)
                    print("ready to ", j)
                    #self.ready(node_, C, i, a_)
                    a_list.append(alpha)
                return C, a_list

    def ready(self, node, C, m, alpha):
        i = node.id
        if self.verify_point(C, i, m, alpha):
            #np.anppend(node.Ac, np.array([m, alpha]))
            node.Ac.append([m, alpha])
            node.r_c += 1
            if node.r_c == self.t + 1 and node.e_c < int((self.n + self.t + 1) / 2):
                for j in range(n):
                    node_ = self.participants[j]
                    #a_ = lagrange_interpolate(j+1, list(node.Ac[:, :1].reshape((1, node.Ac.shape[0]))[0]),
                    #                          list(node.Ac[:, 1:].reshape((1, node.Ac.shape[0]))[0]), p)
                    x = [el[0] for el in node.Ac]
                    y = [el[1] for el in node.Ac]
                    a_ = lagrange_interpolate(j+1, x, y, self.p)
                    print("readyyy to ", j)
                    self.ready(node_, C, i, a_)
            elif node.r_c == self.n - self.t - self.f:
                x = [el[0] for el in node.Ac]
                y = [el[1] for el in node.Ac]
                print("secret shares ", i)
                self.s = lagrange_interpolate(j+1, x, y, self.p)
                #self.s = lagrange_interpolate(0, list(node.Ac[:, :1].reshape((1, node.Ac.shape[0]))[0]),
                #                              list(node.Ac[:, 1:].reshape((1, node.Ac.shape[0]))[0]), p)

class ReconstructionPhase:

    def __init__(self, sharePhase):
        self.n = sharePhase.n
        self.t = sharePhase.t
        self.f = sharePhase.f
        self.p = sharePhase.p
        self.q = sharePhase.q
        self.g = sharePhase.g
        self.tau = sharePhase.tau
        self.participants = sharePhase.participants

    def reconstruct(self, i):
        node_i = self.participants[i]
        node_i.c = 0
        node_i.S = np.array([])
        for node in self.participants:
            self.reconstructShare(node, node_i, self.participants[i].s)

    def reconstructShare(self, node, node_i, s):
        m = node_i.id
        #val1 = np.power(self.g, np.mod(s, self.q))
        #mj = m**np.arange(self.t + 1)
        #val2 = np.mod(np.prod(np.power(node_i.C[:, :1].reshape(1, node_i.C.shape[0])[0], mj)), p)
        #val1 = g ** (s % self.q)
        #if val1 == val2:
        if True:
            #np.append(node.S, np.array([m, s]))
            node.S.append([m, s])
            node.c += 1
            if node.c == self.t+1:
                x = [el[0] for el in node.S]
                y = [el[1] for el in node.S]
                node.z = lagrange_interpolate(0, x, y, p)