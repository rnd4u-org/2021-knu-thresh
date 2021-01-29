from random import randint
from sympy import poly
from sympy.abc import x, y
from ThresholdCryptoLib import threshold_crypto
from threshold_crypto import number

def create_nodes(n):
    nodes = []
    for i in range(n):
        nodes.append(Node())
    return nodes



# def create_dealer():
#     dealer = Dealer()
#     return dealer


# def sharing_initialization(dealer):
#     return dealer.call_dealer()


def recovering_initialization(nodes):
    for node in nodes:
        node.call_node_recover()


def send_messages_from_dealer(dealer, nodes):
    matrix_C, polynoms = dealer.call_dealer()
    n = dealer.session_parameters.n
    echos_results = []
    f = True
    for i in range(n):
        temp = nodes[i].call_node("Pd", matrix_C, polynoms[i])
        if temp != 0:
            f = False
        echos_results.append(temp)
    if f == False:
        return echos_results
    ready_results = []
    for i in range(n):
        for j in range(n):
            temp = nodes[i].call_node("echo", echos_results[j][i])
            if temp != 1:
                f = False
            ready_results.append(temp)
    if f == False:
        return  ready_results
    for i in range(n):
        nodes[i].call_node("ready", ready_results)









def session_initialisation(n, t):
    # create tau, session parameters and set it
    tau = randint(1, 9)
    session_parameters = Session_Parameters(n, t, tau)

    # create nodes, dealer and set their parameters
    nodes = create_nodes(n)
    dealer = Dealer()
    dealer.set_session_parameters(session_parameters)

    for node in nodes:
        node.set_session_parameters(session_parameters)

    # send message from dealer
    send_messages_from_dealer(dealer, nodes)
    # get matrix C and polynoms, then set them
    # recovering_initialization()


class Session_Parameters():

    def __init__(self, n, t, tau):
        self.n = n
        self.t = t
        self.tau = tau


class Dealer():

    def __init__(self):
        self.session_parameters = None

    def set_session_parameters(self, session_parameters):
        self.session_parameters = session_parameters

    def call_dealer(self):
        secret = self.generate_secret()
        polynoms = list()
        polynom = self.generate_polynom(secret)
        # range(1, n) - because index 0 is the secret
        for i in range(1, self.session_parameters.n + 1):
            polynoms.append(self.generate_polynom_i(polynom, i))
        matrix_C = self.generate_matrix_C()
        # self.send_message(poly, C, nodes_id)
        return matrix_C, polynoms

    def generate_secret(self):
        secret = 1111
        return secret

    def generate_polynom(self, secret):
        matrix_poly = [[0 for i in range (self.session_parameters.t + 1)] for i in range(self.session_parameters.t + 1)]
        matrix_poly[0][0] = secret

        for i in range(len(matrix_poly[0])):
            for j in range(len(matrix_poly[0])):
                if i != j:
                    matrix_poly[i][j] = matrix_poly[j][i] = randint(1, 5)
                if i == j and i != 0:
                    matrix_poly[i][j] = randint(1, 5)


        # poly = [[secret, 2, 5, 3], [2, -3, 4, 5], [5, 4, 2, 1], [3, 5, 1, -2]]
        #polynom = poly(3*(x**3)*(y**3) + 2*(x**3)*(y**2) + 2*(x**2)*(y**3) + 5*x + 5*y + secret)
        return matrix_poly

    def generate_polynom_i(self, matrix_poly, x_i):
        polynom_i = []
        p = 29
        for i in range(self.session_parameters.t + 1):
            koef = 0
            for j in range(self.session_parameters.t + 1):
                koef += matrix_poly[j][i] * (x_i) ** j
            polynom_i.append(koef % p)

        print(polynom_i)
        polynom_i = number.PolynomMod(polynom_i, p)
        return polynom_i

    def generate_matrix_C(self, polynom):
        C = []
        return C

    # def send_message(self, poly, C, n):
    #     for i in range(n):
    #         poly_i = self.generate_polynom_i(poly, i)
    #         self.send_message_to_P(i, poly_i, C)
    #
    # def send_message_to_P(self, i, poly_i, C):
    #     self.nodes[i].call_node(poly_i, C, request='Pd')


class Node():

    def __init__(self):
        self.is_shared = False
        self.session_parameters = None

    def set_session_parameters(self, session_parameters):
        self.session_parameters = session_parameters

    def set_is_shared(self):
        self.is_shared = True

    def call_node(self, request, *args):
        if request == "Pd":
            matrix_C, polynoms = args
            return self.progress_Pd_echo(matrix_C, polynoms)
        elif request == "echo":
            results = args
            self.progress_echo_ready(results)
        elif request == "ready":
            results = args
            self.progress_ready_share(results)

    def call_node_recover(self):
        pass

    def verify_poly(self):
        return True

    def verify_point(self):
        return True

    # def send_message(self):
    #     pass
    #
    # def send_message_to_Pj(self):
    #     pass

    def progress_Pd_echo(self, matrix_C, polynoms):
        return 0

    def progress_echo_ready(self, results):
        return 1

    def progress_ready_share(self, results):
        self.is_shared = True


dealer = Dealer()
ses = Session_Parameters(5, 3, 1)
dealer.set_session_parameters(ses)
p = dealer.generate_polynom(10)
print(p)
print(dealer.generate_polynom_i(p, 1))
