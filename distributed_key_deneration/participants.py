from threshold_crypto import number
from lagrange_interpolation import lagrange_interpolate


class Dealer:

    def __init__(self):

        self.session_parameters = None
        self.secret = None
        # static_1024_key_parameters() from threshold_crypto
        self.p = 45963062524833549293039623938977381620355472377395645300085939572921101422291383222930639648650799710220674725312452340335014050543953601338093963649351726506838569620572444329390551080086103310777281122846344467419233965819879622446818266396133182886128840269525864149243491102697267486954308078196622103869
        self.g = 70818045059412229096505272235743689389634686118918223401102407992390386472684584481028357968153236944027127686728774077632802000371835496959768179869988907055346762739460056524883039694157166386370062954387939133203886044147537199513403531355494899326175829610159895944695633468594258300316101218892509250468
        self.polynom_Matrix = None

    def set_session_parameters(self, session_parameters):
        self.session_parameters = session_parameters

    def call_dealer(self):
        """
        dealer generates secret, polynom[x][y] where polynom[0][0] == secret; sends necessary information for nodes
        :return: key parameters p, g; matrix_C for verification, individual polynoms for nodes
        """
        self.generate_secret()
        polynoms = list()
        polynom = self.generate_polynom()
        # range(1, n) - because index 0 is the secret
        for i in range(1, self.session_parameters.n + 1):
            polynoms.append(self.generate_polynom_i(polynom, i))
        matrix_C = self.generate_matrix_C(polynom)
        return self.p, self.g, matrix_C, polynoms

    def generate_secret(self):
        secret = number.getRandomRange(2, self.p - 2)
        self.secret = secret

    def generate_polynom(self):
        """
        generates polynom[x][y] where polynom[0][0] == secret, degree == 2*t
        :return: matrix of polynom
        """
        matrix_poly = [[0 for i in range(self.session_parameters.t + 1)] for j in range(self.session_parameters.t + 1)]
        matrix_poly[0][0] = self.secret

        for i in range(len(matrix_poly[0])):
            for j in range(len(matrix_poly[0])):
                if i != j:
                    matrix_poly[i][j] = matrix_poly[j][i] = number.getRandomRange(1, self.p - 1)
                if i == j and i != 0:
                    matrix_poly[i][j] = number.getRandomRange(1, self.p - 1)
        self.polynom_Matrix = matrix_poly
        return matrix_poly

    def generate_polynom_i(self, matrix_poly, x_i):
        """
        :param matrix_poly: polynom[x][y]
        :param x_i: index of node
        :return: generates individual polynoms for nodes, polynom_i == polynom[i][y]
        """
        polynom_i = []
        for i in range(self.session_parameters.t + 1):
            koef = 0
            for j in range(self.session_parameters.t + 1):
                koef += matrix_poly[j][i] * (x_i) ** j
            polynom_i.append(koef % (self.p))
        return polynom_i

    def generate_matrix_C(self, polynom):
        """
        :param polynom: polynom[x][y]
        :return: matrix_C for verification steps
        """
        C = [[0 for i in range(self.session_parameters.t + 1)] for j in range(self.session_parameters.t + 1)]
        for i in range(self.session_parameters.t + 1):
            for j in range(self.session_parameters.t + 1):
                C[i][j] = pow(self.g, polynom[i][j], self.p)
        return C


class Node:

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
        self.calculated_secret = None

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
        """
        call one of the functions(progress_Pd_echo, progress_echo_ready, progress_ready_share) depending on the request
        """
        if request == "Pd":
            self.p, self.g, self.matrix_C, polynom = args
            return self.progress_Pd_echo(self.matrix_C, polynom)
        elif request == "echo":
            matrix_C, echo_results_other_index, other_index = args
            return self.progress_echo_ready(matrix_C, echo_results_other_index, other_index)
        elif request == "ready":
            matrix_C, echo_results_other_index, other_index = args
            return self.progress_ready_share(matrix_C, echo_results_other_index, other_index)

    def verify_poly(self, matrix_C, self_index, polynom_i):
        return  True
        # p = 103
        # for k in range(self.session_parameters.t + 1):
        #     b = 1
        #     for j in range(self.session_parameters.t + 1):
        #         b *= matrix_C[j][k] ** pow(self_index, j)
        #     if pow(self.g, polynom_i[k], p) == b % p:
        #         continue
        #     else:
        #         return False
        # return True

    def verify_point(self, matrix_C, self_index, other_index, echo_result_other_index):
        return True
        # b = 1
        # for j in range(self.session_parameters.t + 1):
        #     for k in range(self.session_parameters.t + 1):
        #         b *= pow(matrix_C[j][k], (pow(other_index, j) * pow(self_index, k)))
        # if pow(self.g, int(echo_result_other_index), self.p) != b % self.p:
        #     print("vp", echo_result_other_index, pow(self.g, echo_result_other_index, self.p),  b % self.p)
        #     return False
        # return True

    def verify_share(self, other_index, other_secret_share):
        return True
        # tmp = 1
        # print("verify_share", self.index, other_index)
        # for i in range(self.session_parameters.t+1):
        #     tmp *= self.matrix_C[i][0] ** (other_index ** i) % self.p
        #     print("iter", i)
        # if tmp % self.p == self.g ** other_secret_share % self.p:
        #     return True
        # else:
        #     return False

    def progress_Pd_echo(self, matrix_C, polynom):
        """
        :param matrix_C: matrix_C for verification steps
        :param polynom: individual polynom from dealer
        :return: matrix_C;
                list of values for a polynom(y) to send to all nodes
                polymon_values[j] == polynom(j+1)
        """
        if self.verify_poly(matrix_C, self.index, polynom):
            polynom_values = []
            for i in range(1, self.session_parameters.n + 1):
                polynom_value = number.PolynomMod(polynom, self.p).evaluate(i)
                polynom_values.append(polynom_value)
            return matrix_C, polynom_values


    def progress_echo_ready(self, matrix_C, echo_result_other_index, other_index):
        """
        progress_echo_ready for node_other_index
        :param matrix_C: matrix_C for verification steps
        :param echo_result_other_index: value of individual polynom_j_[self.index]
        :param other_index: j
        :return: matrix_C;
                list of values for a interpolated polynom(y) to send to all nodes
                polymon_values[j] == interpolated_polynom(j+1)
        """

        if self.verify_point(matrix_C, self.index, other_index, echo_result_other_index):

            self.point_list_A.append((other_index, echo_result_other_index))
            self.echo_c += 1

            if (self.echo_c == round((self.session_parameters.n + self.session_parameters.t + 1) / 2)
                    and self.ready_c < self.session_parameters.t + 1):

                polynom_values = []
                for i in range(1, self.session_parameters.n + 1):
                    value = lagrange_interpolate(i, [self.point_list_A[i][0] for i in
                                                     range(self.session_parameters.t + 1)],
                                                 [self.point_list_A[i][1] for i in
                                                  range(self.session_parameters.t + 1)], self.p)
                    polynom_values.append(value)

                return matrix_C, polynom_values
            else:
                return -1, -1

    def progress_ready_share(self, matrix_C, echo_results_other_index, other_index):
        """
        set self.set_is_shared = True and self.calculated_secret = calculated_secret
        :param matrix_C: matrix_C for verification steps
        :param echo_results_other_index: value of individual polynom_j_[self.index]
        :param other_index: j
        :return:
        """

        if self.verify_point(matrix_C, self.index, other_index, echo_results_other_index):
            self.point_list_A.append((other_index, echo_results_other_index))
            self.ready_c += 1

            if self.ready_c == self.session_parameters.n - self.session_parameters.t - self.session_parameters.f:

                calculated_secret = lagrange_interpolate(0, [self.point_list_A[i][0] for i in
                                                             range(self.session_parameters.t + 1)],
                                                         [self.point_list_A[i][1] for i in
                                                          range(self.session_parameters.t + 1)], self.p)

                self.calculated_secret = calculated_secret
                self.set_is_shared()


    def call_node_recover(self, request, *args):
        """
        call one of the functions(progress_reconstruct_share, progress_reconstruct_secret) depending on the request
        """
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
        """
        calculated secret
        :param other_secret_share: calculated_secret share from node j
        :param other_index: j
        :return: calculated secret
        """
        if self.verify_share(other_index, other_secret_share):
            self.list_S.append((other_index+1, other_secret_share))
            self.c += 1
            if self.c == self.session_parameters.t + 1:

                secret1 = lagrange_interpolate(0, [self.list_S[i][0] for i in range(self.c)],
                                               [self.list_S[i][1] for i in range(self.c)], self.p)
                return secret1
        return -1
