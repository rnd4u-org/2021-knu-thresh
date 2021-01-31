from __future__ import division
from __future__ import print_function

from random import randint
from sympy import Poly
from sympy.abc import x
from sympy.polys.polyfuncs import interpolate
from threshold_crypto import number
from wiki import _lagrange_interpolate


def create_nodes(n):
    nodes = []
    for i in range(n):
        nodes.append(Node())
    return nodes


def recovering_initialization(nodes):
    n = nodes[0].session_parameters.n
    reconstruct_list = []
    for i in range(n):
        reconstruct_list.append(nodes[i].call_node_recover("Reconstruct"))

    print('recon', reconstruct_list)
    secret_list = []
    for i in range(n):
        for j in range(n):
            secret = nodes[i].call_node_recover("RecShare", reconstruct_list[j], j)
            if secret != -1:
                secret_list.append(secret)

    print('secret_list ', secret_list)


def send_messages(dealer, nodes):
    gen_g, matrix_CPd, polynoms = dealer.call_dealer()
    print('POLYNOMS', *polynoms, sep="\n")

    n = dealer.session_parameters.n
    pd_results_polynoms = []
    pd_results_matrix = []
    for i in range(n):
        matrix_C, polynom_values = nodes[i].call_node("Pd", gen_g, matrix_CPd, polynoms[i])
        pd_results_matrix.append(matrix_C)
        pd_results_polynoms.append(polynom_values)

    echos_results = [[] for i in range(n)]
    echos_results_matrix = [1 for i in range(n)]
    for i in range(n):
        for j in range(n):
            matrix_C, polynom_values = nodes[i].call_node("echo", pd_results_matrix[j], pd_results_polynoms[j][i],
                                                          j + 1)

            if matrix_C != -1:
                echos_results[i] = polynom_values
                echos_results_matrix[i] = matrix_C

    print("echos results first ", echos_results)

    for i in range(n):
        for j in range(n):
            nodes[j].call_node("ready", echos_results_matrix[i], echos_results[i][j], i + 1)


def session_initialisation(n, t):
    # create tau, session parameters and set it
    tau = randint(1, 9)
    session_parameters = Session_Parameters(n, t, tau)

    # create nodes, dealer and set their parameters
    nodes = create_nodes(n)
    for node in nodes:
        node.set_session_parameters(session_parameters)
        node.set_initialization_parameters(nodes.index(node) + 1)

    dealer = Dealer()
    dealer.set_session_parameters(session_parameters)

    # send message
    send_messages(dealer, nodes)
    # get matrix C and polynoms, then set them
    recovering_initialization(nodes)


class Session_Parameters():

    def __init__(self, n, t, tau):
        self.n = n
        self.t = t
        self.f = 0
        self.tau = tau


class Dealer():

    def __init__(self):
        self.session_parameters = None
        self.secret = None
        self.p = 103
        self.g = 5
        self.polynom_Matrix = None

    def set_session_parameters(self, session_parameters):
        self.session_parameters = session_parameters

    def call_dealer(self):
        self.generate_secret()
        polynoms = list()
        polynom = self.generate_polynom(self.secret)
        print('POLYNOM', polynom)
        # range(1, n) - because index 0 is the secret
        for i in range(1, self.session_parameters.n + 1):
            polynoms.append(self.generate_polynom_i(polynom, i))
        matrix_C = self.generate_matrix_C(polynom)
        # self.send_message(poly, C, nodes_id)
        return self.g, matrix_C, polynoms

    def generate_secret(self):
        secret = randint(1000, 2000) % self.p
        self.secret = secret
        print('SECRET', secret)

    def generate_polynom(self, secret):
        matrix_poly = [[0 for i in range(self.session_parameters.t + 1)] for j in range(self.session_parameters.t + 1)]
        matrix_poly[0][0] = secret

        for i in range(len(matrix_poly[0])):
            for j in range(len(matrix_poly[0])):
                if i != j:
                    matrix_poly[i][j] = matrix_poly[j][i] = randint(1, self.p)
                if i == j and i != 0:
                    matrix_poly[i][j] = randint(1, self.p)
        self.polynom_Matrix = matrix_poly
        return matrix_poly

    def generate_polynom_i(self, matrix_poly, x_i):
        polynom_i = []
        for i in range(self.session_parameters.t + 1):
            koef = 0
            for j in range(self.session_parameters.t + 1):
                koef += matrix_poly[j][i] * (x_i) ** j
            polynom_i.append(koef % (self.p))
        return polynom_i


    def generate_matrix_C(self, polynom):
        C = [[0 for i in range(self.session_parameters.t + 1)] for j in range(self.session_parameters.t + 1)]
        for i in range(self.session_parameters.t + 1):
            for j in range(self.session_parameters.t + 1):
                C[i][j] = pow(self.g, polynom[i][j], self.p)
        return C


class Node():

    def __init__(self):

        self.is_shared = False
        self.session_parameters = None
        self.index = None
        self.g = None
        self.point_list_A = None
        self.echo_c = None
        self.ready_c = None
        self.cnt = None
        self.cnt_l = None
        self.matrix_C = None
        self.polynom = None
        self.c = None
        self.list_S = None

    def set_session_parameters(self, session_parameters):
        self.session_parameters = session_parameters

    def set_initialization_parameters(self, node_index):
        self.index = node_index
        self.point_list_A = []
        self.echo_c = 0
        self.ready_c = 0
        self.cnt = 0
        self.cnt_l = [0 for i in range(self.session_parameters.n)]

    def set_is_shared(self):
        self.is_shared = True

    def call_node(self, request, *args):
        if request == "Pd":
            self.g, self.matrix_C, polynom = args
            return self.progress_Pd_echo(self.matrix_C, polynom)
        elif request == "echo":
            matrix_C, echo_results_other_index, other_index = args
            return self.progress_echo_ready(matrix_C, echo_results_other_index, other_index)
        elif request == "ready":
            matrix_C, echo_results_other_index, other_index = args
            return self.progress_ready_share(matrix_C, echo_results_other_index, other_index)

    def verify_poly(self, matrix_C, self_index, polynom_i):
        return True
        # p = 103
        # for k in range(self.session_parameters.t + 1):
        #     b = 1
        #     for j in range(self.session_parameters.t + 1):
        #         b *= matrix_C[j][k] ** pow(self_index, j)
        #     if pow(self.g, polynom_i[k], p) == b % p:
        #         continue
        #     else:
        #         print("vp", self.g, polynom_i[0], pow(self.g, polynom_i[0], p), b % p)
        #         print("vp", self.g, polynom_i[1], pow(self.g, polynom_i[1], p), b % p)
        #         print("vp", self.g, polynom_i[2], pow(self.g, polynom_i[2], p), b % p)
        #         print("vp", self.g, polynom_i[3], pow(self.g, polynom_i[3], p), b % p)
        #         return False
        # return True

    def verify_point(self, matrix_C, self_index, other_index, echo_result_other_index):
        return True
        # b = 1
        # p = 103
        # for j in range(self.session_parameters.t + 1):
        #     for k in range(self.session_parameters.t + 1):
        #         b *= pow(matrix_C[j][k], (pow(other_index, j) * pow(self_index, k)))
        # if pow(self.g, int(echo_result_other_index), p) != b % 103:
        #     print("vp", echo_result_other_index, pow(self.g, echo_result_other_index, p), b % p)
        #     return False
        # return True

    def verify_share(self, other_index, other_secret_share):
        return True
        #
        # p = 103
        # tmp = 1
        # for i in range(self.session_parameters.t + 1):
        #     tmp *= self.matrix_C[i][0] ** (other_index ** i)
        # if tmp % p == self.g ** other_secret_share % p:
        #     return True
        # else:
        #     print("verify_share", tmp % p, self.g ** other_secret_share % p)

    def progress_Pd_echo(self, matrix_C, polynom):
        """

        :param matrix_C:
        :param polynom:
        :return: matrix_C;
                list of values for a polynom(y) to send to all nodes
                polymon_values[j] == polynom(j+1)
        """
        if self.verify_poly(matrix_C, self.index, polynom):
            polynom_values = []
            for i in range(1, self.session_parameters.n + 1):
                polynom_value = number.PolynomMod(polynom, 103).evaluate(i)
                polynom_values.append(polynom_value)
            print("progress_Pd_echo after", polynom, polynom_values)
            return matrix_C, polynom_values

    def progress_echo_ready(self, matrix_C, echo_result_other_index, other_index):
        """
        progress_echo_ready for node_other_index
        :param matrix_C:
        :param echo_result_other_index:
        :param other_index:
        :return: matrix_C;
                list of values for a interpolated polynom(y) to send to all nodes
                polymon_values[j] == interpolated_polynom(j+1)
        """
        p = 103

        if self.verify_point(matrix_C, self.index, other_index, echo_result_other_index):

            self.point_list_A.append((other_index, echo_result_other_index))
            self.echo_c += 1

            if (self.echo_c == round((self.session_parameters.n + self.session_parameters.t + 1) / 2)
                    and self.ready_c < self.session_parameters.t + 1):
                # interpolated_poly = _lagrange_interpolate(0, [1,2,3,4], [self.point_list_A[0][1], self.point_list_A[1][1],
                #                                                          self.point_list_A[2][1],self.point_list_A[3][1]], p)
                polynom_values = []
                for i in range(1, self.session_parameters.n + 1):
                    value = _lagrange_interpolate(i, [1, 2, 3, 4], [self.point_list_A[0][1], self.point_list_A[1][1],
                                                                    self.point_list_A[2][1], self.point_list_A[3][1]],
                                                  p)
                    polynom_values.append(value)
                return matrix_C, polynom_values
            else:
                return -1, -1

    def progress_ready_share(self, matrix_C, echo_results_other_index, other_index):
        p = 103
        if self.verify_point(matrix_C, self.index, other_index, echo_results_other_index):
            self.point_list_A.append((other_index, echo_results_other_index))
            self.ready_c += 1

            if (self.echo_c < round((self.session_parameters.n + self.session_parameters.t + 1) / 2)
                    and self.ready_c == self.session_parameters.t + 1):

                intrpolated_polynom = interpolate(self.point_list_A[0:4], x)
                intrpolated_polynom = list(reversed(Poly(intrpolated_polynom, x).all_coeffs()))
                intrpolated_polynom = [k % p for k in intrpolated_polynom]

                polynom_values = []
                for i in range(1, self.session_parameters.n + 1):
                    polynom_value = number.PolynomMod(intrpolated_polynom, 103).evaluate(i)
                    polynom_values.append(polynom_value)
                return matrix_C, polynom_values

            elif self.ready_c == self.session_parameters.n - self.session_parameters.t - self.session_parameters.f:

                interpolated_poly = _lagrange_interpolate(0, [1, 2, 3, 4],
                                                          [self.point_list_A[0][1], self.point_list_A[1][1],
                                                           self.point_list_A[2][1], self.point_list_A[3][1]], p)

                polynom_values = []
                for i in range(1, self.session_parameters.n + 1):
                    value = _lagrange_interpolate(i, [1, 2, 3, 4], [self.point_list_A[0][1], self.point_list_A[1][1],
                                                                    self.point_list_A[2][1], self.point_list_A[3][1]],
                                                  p)
                    polynom_values.append(value)

                self.calculated_secret = interpolated_poly
                self.is_shared = True

                print("is_shared", self.calculated_secret)

    def call_node_recover(self, request, *args):
        if request == "Reconstruct":
            return self.progress_reconstruct_share()
        elif request == "RecShare":
            other_secret_share, other_index = args
            return self.progress_reconstruct_secret(other_secret_share, other_index)

    def progress_reconstruct_share(self):
        self.c = 0
        self.list_S = []
        return self.calculated_secret

    def progress_reconstruct_secret(self, other_secret_share, other_index):
        p = 103
        if self.verify_share(other_index, other_secret_share):
            self.list_S.append((other_index + 1, other_secret_share))
            self.c += 1
            if self.c == self.session_parameters.t + 1:
                secret1 = _lagrange_interpolate(0, [1, 2, 3, 4],
                                                [self.list_S[0][1], self.list_S[1][1],
                                                 self.list_S[2][1], self.list_S[3][1]], p)
                polynom_values = []
                for i in range(1, self.session_parameters.n + 1):
                    value = _lagrange_interpolate(i, [1, 2, 3, 4], [self.list_S[0][1], self.list_S[1][1],
                                                                    self.list_S[2][1], self.list_S[3][1]], p)
                    polynom_values.append(value)

                return secret1
        return -1


session_initialisation(6, 3)
