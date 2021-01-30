from random import randint
from sympy import Poly
from sympy.abc import x
from sympy.polys.polyfuncs import interpolate
from threshold_crypto import number


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
    is_shared = 0

    n = dealer.session_parameters.n
    t = dealer.session_parameters.t
    pd_results_polynoms = []
    pd_results_matrix = []
    for i in range(n):
        matrix_C, polynom_values = nodes[i].call_node("Pd", gen_g, matrix_CPd, polynoms[i])
        pd_results_matrix.append(matrix_C)
        pd_results_polynoms.append(polynom_values)

    print("dealer", pd_results_matrix, pd_results_polynoms)

    echos_results = [1 for i in range(n)]
    echos_results_matrix = [1 for i in range(n)]
    for i in range(n):
        for j in range(n):
            matrix_C, polynom_values = nodes[i].call_node("echo", pd_results_matrix[j], pd_results_polynoms[j][i],
                                                          j + 1)

            if matrix_C != -1:
                echos_results[i] = polynom_values
                echos_results_matrix[i] = matrix_C



    print("echos results first ", echos_results)
    # for i in range(n):
    #     for j in range(n):
    #         if (i, j) in coefs:
    #             print(i, j)
    #             matrix_C, polynom_values = nodes[j].call_node("echo", pd_results_matrix[i], pd_results_polynoms[i][j],
    #                                                           i + 1)
    #             echos_results[i] = polynom_values
    #             echos_results_matrix[i] = matrix_C
    #             break
    #
    # print("echos results", echos_results)

    for i in range(n):
        for j in range(n):
            nodes[j].call_node("ready", echos_results_matrix[i], echos_results[i][j], i + 1)

    # test_polynoms = []
    # for i in range(5):
    #     test_polynoms.append(dealer.generate_polynom_j(dealer.polynom_Matrix, i))
    # print(*test_polynoms, sep="\n")
    #recovering_initialization(nodes)


def session_initialisation(n, t):
    # create tau, session parameters and set it
    tau = randint(1, 9)
    session_parameters = Session_Parameters(n, t, tau)

    # create nodes, dealer and set their parameters
    nodes = create_nodes(n)
    for node in nodes:
        node.set_session_parameters(session_parameters)
        node.set_initialization_parameters(nodes.index(node) + 1)
        #print(nodes.index(node))

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
        matrix_poly = [[0 for i in range (self.session_parameters.t + 1)] for j in range(self.session_parameters.t + 1)]
        matrix_poly[0][0] = secret

        for i in range(len(matrix_poly[0])):
            for j in range(len(matrix_poly[0])):
                if i != j:
                    matrix_poly[i][j] = matrix_poly[j][i] = randint(1, 5) % self.p
                if i == j and i != 0:
                    matrix_poly[i][j] = randint(1, 5) % self.p
        self.polynom_Matrix = matrix_poly
        return matrix_poly

    def generate_polynom_i(self, matrix_poly, x_i):
        polynom_i = []
        for i in range(self.session_parameters.t + 1):
            koef = 0
            for j in range(self.session_parameters.t + 1):
                koef += matrix_poly[j][i] * (x_i) ** j
            polynom_i.append(koef % (self.p - 1))
        return polynom_i

    def generate_polynom_j(self, matrix_poly, x_i):
        polynom_i = []
        for i in range(self.session_parameters.t + 1):
            koef = 0
            for j in range(self.session_parameters.t + 1):
                koef += matrix_poly[i][j] * (x_i) ** j
            polynom_i.append(koef % (self.p - 1))
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
            #print("call_node", polynom, self.progress_Pd_echo(self.matrix_C, polynom))
            return self.progress_Pd_echo(self.matrix_C, polynom)
        elif request == "echo":
            matrix_C, echo_results_other_index, other_index = args
            return self.progress_echo_ready(matrix_C, echo_results_other_index, other_index)
        elif request == "ready":
            matrix_C, echo_results_other_index, other_index = args
            return self.progress_ready_share(matrix_C, echo_results_other_index, other_index)



    def verify_poly(self, matrix_C, self_index, polynom_i):
        #print(self.index)
        p = 103
        for k in range(self.session_parameters.t + 1):
            b = 1
            for j in range(self.session_parameters.t + 1):
                b *= matrix_C[j][k] ** pow(self_index, j)
            if pow(self.g, polynom_i[k], p) == b % p:
                continue
            else:
                return False
        #print("verify_poly", self_index, polynom_i)
        return True

    def verify_point(self, matrix_C, self_index, other_index, echo_result_other_index):
        b = 1
        p = 103
        for j in range(self.session_parameters.t + 1):
            for k in range(self.session_parameters.t + 1):
                b *= pow(matrix_C[j][k], (pow(other_index, j) * pow(self_index, k)))
        #print('index', echo_result_other_index)
        if pow(self.g, int(echo_result_other_index), p) != b % 103:
            #print("vp", echo_result_other_index, pow(self.g, echo_result_other_index, p),  b % p)
            return False
        return True

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
                polynom_value = number.PolynomMod(polynom, 102).evaluate(i)
                polynom_values.append(polynom_value)
            print("progress_Pd_echo after", polynom, polynom_values)
            return matrix_C, polynom_values

    def progress_echo_ready(self, matrix_C, echo_result_other_index, other_index):
        """
        progress_echo_ready for node_other_index
        :param matrix_C:
        :param echo_resultsother_index:
        :param other_index:
        :return: matrix_C;
                list of values for a interpolated polynom(y) to send to all nodes
                polymon_values[j] == interpolated_polynom(j+1)
        """
        p = 103

        if self.verify_point(matrix_C, self.index, other_index, echo_result_other_index):
            self.point_list_A.append((other_index, echo_result_other_index))
            if self.echo_c == round((self.session_parameters.n + self.session_parameters.t + 1) / 2):
                pass
            else:
                self.echo_c += 1


            if (self.echo_c == round((self.session_parameters.n + self.session_parameters.t + 1) / 2)
                    and self.ready_c < self.session_parameters.t + 1):
                #print("progress_echo_ready before", self.index, echo_result_other_index, other_index)

                intrpolated_polynom = interpolate(self.point_list_A, x)
                intrpolated_polynom = list(reversed(Poly(intrpolated_polynom, x).all_coeffs()))
                intrpolated_polynom = number.PolynomMod(intrpolated_polynom, p)

                polynom_values = []
                for i in range(1, self.session_parameters.n + 1):
                    polynom_value = intrpolated_polynom.evaluate(i)
                    polynom_values.append(polynom_value)
                return matrix_C, polynom_values
            else:
                return -1, -1

    def progress_ready_share(self, matrix_C, echo_results_other_index, other_index):

        p = 103
        #print("progress_ready_share before", other_index)
        if self.verify_point(matrix_C, self.index, other_index, echo_results_other_index):
            self.point_list_A.append((other_index, echo_results_other_index))
            self.ready_c += 1

            if (self.echo_c < round((self.session_parameters.n + self.session_parameters.t + 1) / 2)
                    and self.ready_c == self.session_parameters.t + 1):

                intrpolated_polynom = interpolate(self.point_list_A, x)
                intrpolated_polynom = list(reversed(Poly(intrpolated_polynom, x).all_coeffs()))
                intrpolated_polynom = number.PolynomMod(intrpolated_polynom, p)

                polymon_values = []
                for i in range(1, self.session_parameters.n + 1):
                    polymon_value = intrpolated_polynom.evaluate(i)
                    polymon_values.append(polymon_value)
                return matrix_C, polymon_values

            elif self.ready_c == self.session_parameters.n - self.session_parameters.t - self.session_parameters.f:
                print("is_ready", self.index)
                intrpolated_polynom = interpolate(self.point_list_A[0:4], x)
                print('interpolate_polynom', intrpolated_polynom)
                intrpolated_polynom = list(reversed(Poly(intrpolated_polynom, x).coeffs()))

                self.calculated_secret = intrpolated_polynom[0]
                self.is_shared = True

                print("is_shared", self.calculated_secret % 103)

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

        if True:
            self.list_S.append((other_index, other_secret_share))
            self.c += 1
            if self.c == self.session_parameters.t + 1:
                print('list_S', self.list_S)

                interpolated_polynom = interpolate(self.list_S[0:4], x)
                print('interpolated_polynom', interpolated_polynom)
                interpolated_polynom = list(reversed(Poly(interpolated_polynom, x).all_coeffs()))
                #interpolated_polynom = number.PolynomMod(interpolated_polynom, p - 1)

                #interpolated_polynom = list(reversed(Poly(interpolated_polynom, x).coeffs()))
                print('secret?', interpolated_polynom[0] % (p))

                return interpolated_polynom[0] % (p)
        return -1

dealer = Dealer()
nodes = create_nodes(5)
session_initialisation(5, 4)





# from random import randint
# from sympy import Poly
# from sympy.abc import x, y
# from sympy.polys.polyfuncs import interpolate
# from ThresholdCryptoLib import threshold_crypto
# from threshold_crypto import number
#
#
# def create_nodes(n):
#     nodes = []
#     for i in range(n):
#         nodes.append(Node())
#     return nodes
#
# # def create_dealer():
# #     dealer = Dealer()
# #     return dealer
#
#
# # def sharing_initialization(dealer):
# #     return dealer.call_dealer()
#
#
# def recovering_initialization(nodes):
#     for node in nodes:
#         node.call_node_recover()
#
#
# def send_messages(dealer, nodes):
#     gen_g, matrix_CPd, polynoms = dealer.call_dealer()
#     n = dealer.session_parameters.n
#     t = dealer.session_parameters.t
#     pd_results_polynoms = []
#     pd_results_matrix = []
#     is_shared = 0
#     # f = True
#     for i in range(n):
#         matrix_C, polynom_values = nodes[i].call_node("Pd", gen_g, matrix_CPd, polynoms[i]._coefficients)
#         # if poly != 0:
#         #     f = False
#         pd_results_matrix.append(matrix_C)
#         pd_results_polynoms.append(polynom_values)
#     # if f == False:
#     #     return echos_results
#     echos_results = [0 for i in range (n)]
#     echos_results_matrix = [0 for i in range (n)]
#     coefs = []
#     for i in range(n):
#         for j in range(0, n):
#             matrix_C, polynom_values = nodes[j].call_node("echo", pd_results_matrix[i], pd_results_polynoms[i][j], i + 1)
#             if matrix_C != -1:
#                 echos_results[i] = polynom_values
#                 echos_results_matrix[i] = matrix_C
#             else:
#                 coefs.append((i,j))
#     for i in range(n):
#         for j in range(n):
#             if (i,j) in coefs:
#                 matrix_C, polynom_values = nodes[j].call_node("echo", pd_results_matrix[i], pd_results_polynoms[i][j], i + 1)
#                 echos_results[i] = polynom_values
#                 echos_results_matrix[i] = matrix_C
#             # if temp != 1:
#             #     f = False
#
#     # if f == False:
#     #     return  ready_results
#     for i in range(n):
#         for j in range(n):
#             is_shared += nodes[j].call_node("ready", echos_results_matrix[i], echos_results[i][j], i + 1)
#
#
#
#
#
#
# def session_initialisation(n, t):
#     # create tau, session parameters and set it
#     tau = randint(1, 9)
#     session_parameters = Session_Parameters(n, t, tau)
#
#     # create nodes, dealer and set their parameters
#     nodes = create_nodes(n)
#     for node in nodes:
#         node.set_session_parameters(session_parameters)
#         node.set_initialization_parameters(nodes.index(node) + 1)
#         print(nodes.index(node))
#
#     dealer = Dealer()
#     dealer.set_session_parameters(session_parameters)
#
#     # send message
#     send_messages(dealer, nodes)
#     # get matrix C and polynoms, then set them
#     recovering_initialization(nodes)
#
#
# class Session_Parameters():
#
#     def __init__(self, n, t, tau):
#         self.n = n
#         self.t = t
#         self.tau = tau
#
#
# class Dealer():
#
#     def __init__(self):
#         self.session_parameters = None
#         self.secret = None
#         self.p = 29
#         self.g = 5
#
#
#     def set_session_parameters(self, session_parameters):
#         self.session_parameters = session_parameters
#
#     def call_dealer(self):
#         self.generate_secret()
#         polynoms = list()
#         polynom = self.generate_polynom(self.secret)
#         # range(1, n) - because index 0 is the secret
#         for i in range(1, self.session_parameters.n + 1):
#             polynoms.append(self.generate_polynom_i(polynom, i))
#         matrix_C = self.generate_matrix_C(polynom)
#         # self.send_message(poly, C, nodes_id)
#         return self.g, matrix_C, polynoms
#
#     def generate_secret(self):
#         secret = randint(1000, 2000) % self.p
#         self.secret = secret
#
#     def generate_polynom(self, secret):
#         matrix_poly = [[0 for i in range (self.session_parameters.t + 1)] for i in range(self.session_parameters.t + 1)]
#         matrix_poly[0][0] = secret
#
#         for i in range(len(matrix_poly[0])):
#             for j in range(len(matrix_poly[0])):
#                 if i != j:
#                     matrix_poly[i][j] = matrix_poly[j][i] = randint(1, 5) % self.p
#                 if i == j and i != 0:
#                     matrix_poly[i][j] = randint(1, 5) % self.p
#
#         return matrix_poly
#
#     def generate_polynom_i(self, matrix_poly, x_i):
#         polynom_i = []
#         for i in range(self.session_parameters.t + 1):
#             koef = 0
#             for j in range(self.session_parameters.t + 1):
#                 koef += matrix_poly[j][i] * (x_i) ** j
#             polynom_i.append(koef % self.p)
#
#         polynom_i = number.PolynomMod(polynom_i, self.p)
#         return polynom_i
#
#     def generate_matrix_C(self, polynom):
#         C = [[0 for i in range(self.session_parameters.t + 1)] for j in range(self.session_parameters.t + 1)]
#         for i in range(self.session_parameters.t + 1):
#             for j in range(self.session_parameters.t + 1):
#                 C[i][j] = pow(self.g, polynom[i][j], self.p)
#         return C
#
#     # def send_message(self, poly, C, n):
#     #     for i in range(n):
#     #         poly_i = self.generate_polynom_i(poly, i)
#     #         self.send_message_to_P(i, poly_i, C)
#     #
#     # def send_message_to_P(self, i, poly_i, C):
#     #     self.nodes[i].call_node(poly_i, C, request='Pd')
#
#
# class Node():
#
#     def __init__(self):
#
#         self.is_shared = False
#         self.session_parameters = None
#         self.index = None
#         self.g = None
#         self.point_list_A = None
#         self.echo_c = None
#         self.ready_c = None
#         self.cnt = None
#         self.cnt_l = None
#         self.matrix_C = None
#         self.polynom = None
#
#
#     def set_session_parameters(self, session_parameters):
#         self.session_parameters = session_parameters
#
#     def set_initialization_parameters(self, node_index):
#         self.index = node_index
#         self.point_list_A = []
#         self.echo_c = 0
#         self.ready_c = 0
#         self.cnt = 0
#         self.cnt_l = [0 for i in range(self.session_parameters.n)]
#
#
#     def set_is_shared(self):
#         self.is_shared = True
#
#     def call_node(self, request, *args):
#         if request == "Pd":
#             self.g, self.matrix_C, self.polynom = args
#             return self.progress_Pd_echo(self.matrix_C, self.polynom)
#         elif request == "echo":
#             results = args
#             self.progress_echo_ready(results)
#         elif request == "ready":
#             results = args
#             self.progress_ready_share(results)
#
#     def verify_poly(self, matrix_C, self_index, polynom_i):
#         p = 29
#         for k in range(self.session_parameters.t + 1):
#             b = 1
#             for j in range(self.session_parameters.t + 1):
#                 b *= matrix_C[j][k] ** pow(self_index, j)
#             if pow(self.g, polynom_i[k], p) == b:
#                 continue
#             else:
#                 return False
#         return True
#
#     def verify_point(self, matrix_C, self_index, other_index, echo_result_other_index):
#         b = 1
#         p = 29
#         for j in range(self.session_parameters.t + 1):
#             for k in range(self.session_parameters.t + 1):
#                 b *= pow(matrix_C[j][k], pow(other_index, j) * pow(self_index, k))
#         if pow(self.g, echo_result_other_index, p) == b:
#             return True
#         else:
#             return False
#
#     def progress_Pd_echo(self, matrix_C, polynom):
#         """
#
#         :param matrix_C:
#         :param polynom:
#         :return: matrix_C;
#                 list of values for a polynom(y) to send to all nodes
#                 polymon_values[j] == polynom(j+1)
#         """
#         if self.verify_poly(matrix_C, self.index, polynom):
#             polymon_values = []
#             for i in range(1, self.session_parameters.n + 1):
#                 polymon_value = polynom.evaluate(i)
#                 polymon_values.append(polymon_value)
#             return matrix_C, polymon_values
#
#     def progress_echo_ready(self, matrix_C, echo_result_other_index, other_index):
#         """
#         progress_echo_ready for node_other_index
#         :param matrix_C:
#         :param echo_resultsother_index:
#         :param other_index:
#         :return: matrix_C;
#                 list of values for a interpolated polynom(y) to send to all nodes
#                 polymon_values[j] == interpolated_polynom(j+1)
#         """
#         if self.verify_point(matrix_C, self.index, other_index, echo_result_other_index):
#             self.point_list_A.append((other_index, echo_result_other_index))
#             self.echo_c += 1
#             if self.echo_c == round((self.session_parameters.n + self.session_parameters.t + 1) / 2)\
#                     and self.ready_c < self.session_parameters.t + 1:
#                 interpolated_polynom = interpolate(self.point_list_A, x)
#                 intrpolated_polynom = list(reversed(Poly(interpolated_polynom, x).all_coeffs()))
#                 #polymon_values =
#
#                 # for i in range(1, self.session_parameters.n + 1):
#                 #     polymon_value = intrpolated_polynom.evaluate(i)
#                 #     polymon_values.append(polymon_value)
#                 # return matrix_C, polymon_values
#             else:
#                 return -1, -1
#
#
#     def progress_ready_share(self, matrix_C, echo_results_other_index, other_index):
#         if self.verify_point(matrix_C, self.index, other_index, echo_results_other_index):
#             self.point_list_A.append((other_index, echo_results_other_index))
#             self.ready_c += 1
#
#             if (self.echo_c < round((self.session_parameters.n + self.session_parameters.t + 1) / 2)
#                     and self.ready_c == self.session_parameters.t + 1):
#                 intrpolated_polynom = number.PolynomMod([1, 2, 3, 4], 3)
#                 # intrpolated_polynom = number.build_lagrange_coefficients() from Ac
#                 polymon_values = []
#                 for i in range(1, self.session_parameters.n + 1):
#                     polymon_value = intrpolated_polynom.evaluate(i)
#                     polymon_values.append(polymon_value)
#                 return matrix_C, polymon_values
#             elif self.ready_c == self.session_parameters.n - self.session_parameters.t - self.session_parameters.f:
#                 intrpolated_polynom = number.PolynomMod([1, 2, 3, 4], 3)
#                 # intrpolated_polynom = number.build_lagrange_coefficients() from Ac
#                 # какой полином использовать!?
#                 self.calculated_secret = intrpolated_polynom[0]
#                 self.is_shared = True
#
#     # def send_message(self):
#     #     pass
#     #
#     # def send_message_to_Pj(self):
#     #     pass
#
#     def call_node_recover(self):
#         pass
#
#
# session_initialisation(5,3)









# dealer = Dealer()
# ses = Session_Parameters(5, 3, 1)
# dealer.set_session_parameters(ses)


# p = dealer.generate_polynom(10)
# print(p)
# print(dealer.generate_polynom_i(p, 1))


# from random import randint
# from sympy import poly
# from sympy.abc import x, y
# from ThresholdCryptoLib import threshold_crypto
# from threshold_crypto import number
#
# def create_nodes(n):
#     nodes = []
#     for i in range(n):
#         nodes.append(Node())
#     return nodes
#
#
#
# # def create_dealer():
# #     dealer = Dealer()
# #     return dealer
#
#
# # def sharing_initialization(dealer):
# #     return dealer.call_dealer()
#
#
# def recovering_initialization(nodes):
#     for node in nodes:
#         node.call_node_recover()
#
#
# def send_messages_from_dealer(dealer, nodes):
#     matrix_C, polynoms = dealer.call_dealer()
#     n = dealer.session_parameters.n
#     echos_results = []
#     f = True
#     for i in range(n):
#         temp = nodes[i].call_node("Pd", matrix_C, polynoms[i])
#         if temp != 0:
#             f = False
#         echos_results.append(temp)
#     if f == False:
#         return echos_results
#     ready_results = []
#     for i in range(n):
#         for j in range(n):
#             temp = nodes[i].call_node("echo", echos_results[j][i])
#             if temp != 1:
#                 f = False
#             ready_results.append(temp)
#     if f == False:
#         return  ready_results
#     for i in range(n):
#         nodes[i].call_node("ready", ready_results)
#
#
#
#
#
#
#
#
#
# def session_initialisation(n, t):
#     # create tau, session parameters and set it
#     tau = randint(1, 9)
#     session_parameters = Session_Parameters(n, t, tau)
#
#     # create nodes, dealer and set their parameters
#     nodes = create_nodes(n)
#     dealer = Dealer()
#     dealer.set_session_parameters(session_parameters)
#
#     for node in nodes:
#         node.set_session_parameters(session_parameters)
#
#     # send message from dealer
#     send_messages_from_dealer(dealer, nodes)
#     # get matrix C and polynoms, then set them
#     # recovering_initialization()
#
#
# class Session_Parameters():
#
#     def __init__(self, n, t, tau):
#         self.n = n
#         self.t = t
#         self.tau = tau
#
#
# class Dealer():
#
#     def __init__(self):
#         self.session_parameters = None
#
#     def set_session_parameters(self, session_parameters):
#         self.session_parameters = session_parameters
#
#     def call_dealer(self):
#         secret = self.generate_secret()
#         polynoms = list()
#         polynom = self.generate_polynom(secret)
#         # range(1, n) - because index 0 is the secret
#         for i in range(1, self.session_parameters.n + 1):
#             polynoms.append(self.generate_polynom_i(polynom, i))
#         matrix_C = self.generate_matrix_C()
#         # self.send_message(poly, C, nodes_id)
#         return matrix_C, polynoms
#
#     def generate_secret(self):
#         secret = 1111
#         return secret
#
#     def generate_polynom(self, secret):
#         matrix_poly = [[0 for i in range (self.session_parameters.t + 1)] for i in range(self.session_parameters.t + 1)]
#         matrix_poly[0][0] = secret
#
#         for i in range(len(matrix_poly[0])):
#             for j in range(len(matrix_poly[0])):
#                 if i != j:
#                     matrix_poly[i][j] = matrix_poly[j][i] = randint(1, 5)
#                 if i == j and i != 0:
#                     matrix_poly[i][j] = randint(1, 5)
#
#
#         # poly = [[secret, 2, 5, 3], [2, -3, 4, 5], [5, 4, 2, 1], [3, 5, 1, -2]]
#         #polynom = poly(3*(x**3)*(y**3) + 2*(x**3)*(y**2) + 2*(x**2)*(y**3) + 5*x + 5*y + secret)
#         return matrix_poly
#
#     def generate_polynom_i(self, matrix_poly, x_i):
#         polynom_i = []
#         p = 29
#         for i in range(self.session_parameters.t + 1):
#             koef = 0
#             for j in range(self.session_parameters.t + 1):
#                 koef += matrix_poly[j][i] * (x_i) ** j
#             polynom_i.append(koef % p)
#
#         print(polynom_i)
#         polynom_i = number.PolynomMod(polynom_i, p)
#         return polynom_i
#
#     def generate_matrix_C(self, polynom):
#         C = []
#         return C
#
#     # def send_message(self, poly, C, n):
#     #     for i in range(n):
#     #         poly_i = self.generate_polynom_i(poly, i)
#     #         self.send_message_to_P(i, poly_i, C)
#     #
#     # def send_message_to_P(self, i, poly_i, C):
#     #     self.nodes[i].call_node(poly_i, C, request='Pd')
#
#
# class Node():
#
#     def __init__(self):
#         self.is_shared = False
#         self.session_parameters = None
#
#     def set_session_parameters(self, session_parameters):
#         self.session_parameters = session_parameters
#
#     def set_is_shared(self):
#         self.is_shared = True
#
#     def call_node(self, request, *args):
#         if request == "Pd":
#             matrix_C, polynoms = args
#             return self.progress_Pd_echo(matrix_C, polynoms)
#         elif request == "echo":
#             results = args
#             self.progress_echo_ready(results)
#         elif request == "ready":
#             results = args
#             self.progress_ready_share(results)
#
#     def call_node_recover(self):
#         pass
#
#     def verify_poly(self):
#         return True
#
#     def verify_point(self):
#         return True
#
#     # def send_message(self):
#     #     pass
#     #
#     # def send_message_to_Pj(self):
#     #     pass
#
#     def progress_Pd_echo(self, matrix_C, polynoms):
#         return 0
#
#     def progress_echo_ready(self, results):
#         return 1
#
#     def progress_ready_share(self, results):
#         self.is_shared = True
#
#
# dealer = Dealer()
# ses = Session_Parameters(5, 3, 1)
# dealer.set_session_parameters(ses)
# p = dealer.generate_polynom(10)
# print(p)
# print(dealer.generate_polynom_i(p, 1))
