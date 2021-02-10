from threshold_crypto_lib import number
from random import randint, randrange
import hashlib
from pairings import bn256
from Signature import lagrange_interpolation as li


def g1_hash_to_point(msg):

    # constants
    sqrt_neg_3 = bn256.sqrt_mod_p(bn256.p - 3)
    inv_2 = bn256.inv_mod_p(2)
    b = bn256.curve_B.value()

    # compute t in F_q
    sha = hashlib.sha512()
    sha.update(msg)
    t = int(sha.hexdigest(), 16) % bn256.p

    if t == 0:
        # TODO handle this case as described in paper
        assert False

    t2 = (t * t) % bn256.p

    chi_t = bn256.legendre(t)

    w = sqrt_neg_3 * t * bn256.inv_mod_p(1 + b + t2)

    def g(x):
        return (x * x * x + b) % bn256.p

    x1 = ((sqrt_neg_3 - 1) * inv_2 - t * w) % bn256.p
    g_x1 = g(x1)
    if bn256.legendre(g_x1) == 1:
        x1_sqrt = bn256.sqrt_mod_p(g_x1)
        return bn256.curve_point(bn256.gfp_1(x1),
                           bn256.gfp_1(chi_t * x1_sqrt))

    x2 = (-1 - x1) % bn256.p
    g_x2 = g(x2)

    if bn256.legendre(g_x2) == 1:
        x2_sqrt = bn256.sqrt_mod_p(g_x2)
        return bn256.curve_point(bn256.gfp_1(x2),
                           bn256.gfp_1(chi_t * x2_sqrt))

    x3 = 1 + bn256.inv_mod_p(w * w)
    g_x3 = g(x3)

    assert bn256.legendre(g_x3) == 1
    x3_sqrt = bn256.sqrt_mod_p(g_x3)
    return bn256.curve_point(bn256.gfp_1(x3),
                       bn256.gfp_1(chi_t * x3_sqrt))


def g1_hash_to_point_2(msg):
    # sha = hashlib.sha512() => sha = hashlib.sha256()

    # constants
    sqrt_neg_3 = bn256.sqrt_mod_p(bn256.p - 3)
    inv_2 = bn256.inv_mod_p(2)
    b = bn256.curve_B.value()

    # compute t in F_q
    sha = hashlib.sha256()
    sha.update(msg)
    t = int(sha.hexdigest(), 16) % bn256.p

    if t == 0:
        # TODO handle this case as described in paper
        assert False

    t2 = (t * t) % bn256.p

    chi_t = bn256.legendre(t)

    w = sqrt_neg_3 * t * bn256.inv_mod_p(1 + b + t2)

    def g(x):
        return (x * x * x + b) % bn256.p

    x1 = ((sqrt_neg_3 - 1) * inv_2 - t * w) % bn256.p
    g_x1 = g(x1)
    if bn256.legendre(g_x1) == 1:
        x1_sqrt = bn256.sqrt_mod_p(g_x1)
        return bn256.curve_point(bn256.gfp_1(x1),
                           bn256.gfp_1(chi_t * x1_sqrt))

    x2 = (-1 - x1) % bn256.p
    g_x2 = g(x2)

    if bn256.legendre(g_x2) == 1:
        x2_sqrt = bn256.sqrt_mod_p(g_x2)
        return bn256.curve_point(bn256.gfp_1(x2),
                           bn256.gfp_1(chi_t * x2_sqrt))

    x3 = 1 + bn256.inv_mod_p(w * w)
    g_x3 = g(x3)

    assert bn256.legendre(g_x3) == 1
    x3_sqrt = bn256.sqrt_mod_p(g_x3)
    return bn256.curve_point(bn256.gfp_1(x3),
                       bn256.gfp_1(chi_t * x3_sqrt))


def inv_mod_p(number, p):
    # Fermat
    return pow(number, p - 2, p)


def calculate_message_hash(message):
    # hash1 != hash2
    hash1 = g1_hash_to_point(message)
    hash2 = g1_hash_to_point_2(message)
    return [hash1, hash2]


def create_players(n):

    players = []
    for i in range(n):
        players.append(Player())
        players[i].index = i + 1
    return players


def session(players):

    sp = SessionParameters(0, 0, 0, 0, 0, 0, 0, 0)
    message = b'Hello'

    for player in players:
        player.set_session_parameters(sp)
        player.create_polynomials()

    matrix_w_list, polynom_values_list = first_message(players)
    verificate_list = second_message(players, matrix_w_list, polynom_values_list)
    honest_indexes_list = third_message(players, verificate_list)
    verification_keys = fourth_message(players, honest_indexes_list)
    sigma_i_list, signers_indexes_list_S = share_verification_all(players, verification_keys, message, honest_indexes_list)
    print('share', sigma_i_list)
    print("honest players", signers_indexes_list_S)
    sigma = combine_shares(players, sigma_i_list, signers_indexes_list_S)
    print()
    print(sigma)
    verify_signature(players[0].public_key, message, sigma, players[0].SP.g2_z, players[0].SP.g2_r)



def first_message(players):
    matrix_w_list = []
    polynom_values_list = []
    for player in players:
        matrix_w, polynom_values = player.send_W_and_points()
        matrix_w_list.append(matrix_w)
        polynom_values_list.append(polynom_values)
    return matrix_w_list, polynom_values_list


def second_message(players, matrix_w_list, polynom_values_list):
    verificate_list = []
    for player in players:
        j = player.index - 1
        lst = []
        for i in range(player.SP.n):
            lst.append(polynom_values_list[i][j])
        verificate_list.append(player.verification_W_and_points(matrix_w_list, lst))
    return verificate_list[0]


def third_message(players, verificate_list):
    honest_indexes_list = []
    for i in verificate_list:
        if i[1] == True:
            honest_indexes_list.append(i[0])
    for player in players:
        player.set_honest_Q(honest_indexes_list)
        player.calculate_public_key()
        player.calculate_private_key()
    return honest_indexes_list


def fourth_message(players, honest_indexse_list):

    verification_keys = []
    print("ttttt", type(bn256.gfp_6_zero), bn256.gfp_6_zero)
    for i in range(1, players[0].SP.n + 1):
        if i not in honest_indexse_list:
            VK = [bn256.gfp_6_zero, bn256.gfp_6_zero] ######
            verification_keys.append(VK)
        else:
            VK = players[i-1].calculate_self_verification_key()
            # print(i, VK)
            verification_keys.append(VK)

    for player in players:
        player.set_verification_key(verification_keys)

    return verification_keys


# Share-Verify (PK, VK, message,(i, σi))
def share_verification(VK, message, sigma_i, g2_z, g2_r):

    hash1, hash2 = calculate_message_hash(message)
    a = bn256.optimal_ate(g2_z, sigma_i[0])
    b = bn256.optimal_ate(g2_r, sigma_i[1])
    c = bn256.optimal_ate(VK[0], hash1)
    d = bn256.optimal_ate(VK[1], hash2)
    e = a.mul(b)
    e = e.mul(c)
    e = e.mul(d)
    print(type(e))
    print(e.is_one())
    return True


def share_verification_all(players, verification_keys, message, honest_indexes_list):
    sigma_i_list = []
    signers_indexes_list_S = []
    for i in honest_indexes_list:
        sigma_i = players[i-1].calculate_share_signature(message)
        if share_verification(verification_keys[i-1], message, sigma_i, players[0].SP.g2_z, players[0].SP.g2_r):
            sigma_i_list.append(sigma_i)
            signers_indexes_list_S.append(i)
    return sigma_i_list, signers_indexes_list_S


# Combine(PK, VK, M, {(i, σi)}i∈S):
def combine_shares(players, sigma_i_list, signers_indexes_list_S):
    # Given a (t+1)-set with valid shares {(i, σi)}i∈S,
    # compute (z, r) by Lagrange interpolation in the exponent.
    values1 = []
    values2 = []
    for i in signers_indexes_list_S:
        value1, value2 = players[i-1].interpolate_two_points()
        values1.append(value1)
        values2.append(value2)
    z = sigma_i_list[0][0].scalar_mul(values1[0])
    r = sigma_i_list[0][1].scalar_mul(values2[0])
    for i in range(1, len(signers_indexes_list_S)):
        z = z.add((sigma_i_list[i][0].scalar_mul(values1[i])))
        r = r.add((sigma_i_list[i][1].scalar_mul(values1[i])))
    return [z, r]


# Verify (PK, message, σ)
def verify_signature(PK, message, sigma, g2_z, g2_r):
    # Given a purported signature σ = (z, r) ∈ G2
    # compute (H1, H2) = H(M) ∈ G×G
    # and return 1 if and only if the following equality holds:
    # e(z, gˆz) · e(r, gˆr) · e(H1, gˆ1) · e(H2, gˆ2) = 1GT
    hash1, hash2 = calculate_message_hash(message)
    a = bn256.optimal_ate(g2_z, sigma[0])
    b = bn256.optimal_ate(g2_r, sigma[1])
    c = bn256.optimal_ate(PK[0], hash1)
    d = bn256.optimal_ate(PK[1], hash2)
    print("verify_signature")
    e = a.mul(b)
    print(e)
    e = e.mul(c)
    print(e)
    e = e.mul(d)
    print(e)
    print(type(e))
    print(e.is_one())

    return True


class SessionError(Exception):
    pass


class SessionParameters:

    def __init__(self, asymmetric_bilinear_group, prime_p, g2_z, g2_r, hash_func, lambda_param, n, t):
        """
        :param asymmetric_bilinear_group: (G, Gˆ, Gt)
        :param prime_p: order of asymmetric_bilinear_group
        :param g2_z: generator of Gˆ
        :param g2_r: generator of Gˆ
        :param hash_func:  H: {0, 1}∗ → G2
        :param lambda_param: security parameter
        :param n: number of players, n ≥ 2t + 1,
        :param t: threshold (requires >t)
        """
        # if t > (n-1)//2:
        #     raise SessionError('threshold parameter t must be smaller than n')
        # if t <= 0:
        #     raise SessionError('threshold parameter t must be greater than 0')
        self.n = 6
        self.t = 2
        asymmetric_bilinear_group = None
        self.B_group = asymmetric_bilinear_group
        prime_p = bn256.order
        self.p = prime_p
        self.q = bn256.p
        a, g2_z = bn256.g2_random()
        b, g2_r = bn256.g2_random()
        self.g2_z = g2_z
        self.g2_r = g2_r
        hash_func = bn256.g1_hash_to_point
        self.Hash = hash_func
        self.lambda_ = None


class Player:

    def __init__(self):
        self.index = None
        self.SP = None
        self.is_shared = False
        self.polynomials = None
        self.matrix_W = None
        self.honest_Q = None
        self.all_W = None
        self.other_points = None
        self.public_key = None
        self.private_key = None
        self.verification_key = None

    def set_session_parameters(self, session_parameters):
        self.SP = session_parameters

    def set_is_shared(self):
        self.is_shared = True

    def create_random_polynomial(self):
        coefficients = [randint(1, self.SP.p - 1) for i in range(0, self.SP.t + 1)]
        return coefficients

    def create_polynomials(self):
        self.polynomials = {}
        coefficients_A_1 = self.create_random_polynomial()
        self.polynomials["A1"] = coefficients_A_1
        coefficients_A_2 = self.create_random_polynomial()
        self.polynomials["A2"] = coefficients_A_2
        coefficients_B_1 = self.create_random_polynomial()
        self.polynomials["B1"] = coefficients_B_1
        coefficients_B_2 = self.create_random_polynomial()
        self.polynomials["B2"] = coefficients_B_2

    def calculate_W(self):
        self.matrix_W = {1: [0 for i in range(self.SP.t + 1)], 2: [0 for i in range(self.SP.t + 1)]}
        for i in range(self.SP.t + 1):
            self.matrix_W[1][i] = bn256.point_add(self.SP.g2_z.scalar_mul(self.polynomials["A1"][i]),
                                                  self.SP.g2_r.scalar_mul(self.polynomials["B1"][i]))
            self.matrix_W[2][i] = bn256.point_add(self.SP.g2_z.scalar_mul(self.polynomials["A2"][i]),
                                                  self.SP.g2_r.scalar_mul(self.polynomials["B2"][i]))
        #return self.matrix_W

    def calculate_polynomial_values(self, index: int):
        values = dict()
        values[1] = [number.PolynomMod(self.polynomials["A1"], self.SP.p).evaluate(index),
                     number.PolynomMod(self.polynomials["B1"], self.SP.p).evaluate(index)]
        values[2] = [number.PolynomMod(self.polynomials["A2"], self.SP.p).evaluate(index),
                     number.PolynomMod(self.polynomials["B2"], self.SP.p).evaluate(index)]
        return values

    def send_W_and_points(self):
        self.calculate_W()
        polynomial_values = []
        for i in range(1, self.SP.n + 1):
            polynomial_value = self.calculate_polynomial_values(i)
            polynomial_values.append(polynomial_value)
        return self.matrix_W, polynomial_values

    def partial_verification_W_and_points(self, other_W, other_points):  # repeat n times
        W1 = other_W[1][0]
        W2 = other_W[2][0]
        for i in range(1, self.SP.t + 1):
            W1 = bn256.g2_add(W1, other_W[1][i].scalar_mul(pow(self.index, i)))
            W2 = bn256.g2_add(W2, other_W[2][i].scalar_mul(pow(self.index, i)))
        a = bn256.g2_add(self.SP.g2_z.scalar_mul(other_points[1][0]),
                             self.SP.g2_r.scalar_mul(other_points[1][1]))
        b = bn256.g2_add(self.SP.g2_z.scalar_mul(other_points[2][0]),
                                 self.SP.g2_r.scalar_mul(other_points[2][1]))
        if a.force_affine() == W1.force_affine() and b.force_affine() == W2.force_affine():
            return True
        return False

    def verification_W_and_points(self, other_W, other_points):
        is_verified = []
        self.all_W = other_W
        self.other_points = other_points
        # print(self.other_points)
        for i in range(1, self.SP.n + 1):
            is_verified.append((i, self.partial_verification_W_and_points(other_W[i - 1], other_points[i - 1])))
        return is_verified

    def set_honest_Q(self, honest_players):
        self.honest_Q = honest_players

    def calculate_public_key(self):
        zero = bn256.gfp_2_zero
        g1 = bn256.curve_twist(zero, zero, zero)
        g2 = bn256.curve_twist(zero, zero, zero)
        for i in self.honest_Q:
            W = self.all_W[i - 1]
            g1 = bn256.g2_add(g1, W[1][0])
            g2 = bn256.g2_add(g2, W[2][0])
        print(type(g1), g1)
        self.public_key = [g1, g2]

    def calculate_private_key(self):
        self.private_key = self.calculate_polynomial_values(self.index)

    def calculate_self_verification_key(self):
        g1 = bn256.g2_add(self.SP.g2_z.scalar_mul(int(self.private_key[1][0])),
                             self.SP.g2_r.scalar_mul(int(self.private_key[1][1])))
        g2 = bn256.g2_add(self.SP.g2_z.scalar_mul(int(self.private_key[2][0])),
                             self.SP.g2_r.scalar_mul(int(self.private_key[2][1])))
        self.verification_key = [g1, g2]
        # print("verification_key",self.index, self.verification_key)
        return self.verification_key

    def set_verification_key(self, verification_key_list):
        # print("verification_key", *verification_key_list, sep="\n")
        self.verification_key = verification_key_list

    # DO YOU WANT TO SIGN?
    # Share-Sign(i, SKi, M):

    def calculate_share_signature(self, message):

        hash1, hash2 = calculate_message_hash(message)
        # print()
        # print(hash1)
        # print(hash2)
        a1 = inv_mod_p(self.private_key[1][0], self.SP.p)
        # print("aaa", self.private_key[1][0]*a1 % self.SP.p)
        a2 = inv_mod_p(self.private_key[2][0], self.SP.p)
        b1 = inv_mod_p(self.private_key[1][1], self.SP.p)
        b2 = inv_mod_p(self.private_key[2][1], self.SP.p)
        z_i = bn256.g1_add(hash1.scalar_mul(a1), hash2.scalar_mul(a2))
        r_i = bn256.g1_add(hash1.scalar_mul(b1), hash2.scalar_mul(b2))
        sigma_i = (z_i, r_i)
        return sigma_i

    def interpolate_two_points(self):
        points1_x = []
        points1_y = []
        for i in range(len(self.other_points)):
            points1_x.append(self.other_points[i][1][0])
            points1_y.append(self.other_points[i][1][1])

        points2_x = []
        points2_y = []
        for i in range(len(self.other_points)):
            points2_x.append(self.other_points[i][2][0])
            points2_y.append(self.other_points[i][2][1])

        value_1 = li.lagrange_interpolate(0, points1_x, points1_y, self.SP.p)
        value_2 = li.lagrange_interpolate(0, points2_x, points2_y, self.SP.p)
        return value_1, value_2


players = create_players(6)
session(players)