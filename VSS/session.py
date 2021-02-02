from random import randint
from participants import Node


class SessionError(Exception):
    pass


class SessionParameters:

    def __init__(self, n, t, f, tau):
        if t > n:
            raise SessionError('threshold parameter t must be smaller than n')
        if t <= 0:
            raise SessionError('threshold parameter t must be greater than 0')
        self.n = n
        self.t = t
        self.f = f
        self.tau = tau


def create_nodes(n):

    nodes = []
    for i in range(n):
        nodes.append(Node())
    return nodes


def pd_send_messages(dealer, nodes, key_lenght):
    """
    Call dealer to get prime_p, gen_g, matrix_CPd, polynoms, generate secret and send necessary information to nodes
    :param dealer: dealer
    :param nodes: list of participants
    :return:  pd_results_polynoms - individual polynoms Phi[i][y] for each node_i
              pd_results_matrix - matrix to verify dealer and nodes
    """
    prime_p, prime_q, gen_g, matrix_CPd, polynoms = dealer.call_dealer(key_lenght)

    n = dealer.session_parameters.n
    pd_results_polynoms = []
    pd_results_matrix = []
    bad_dealer = 0
    for i in range(n):
        matrix_C, polynom_values = nodes[i].call_node("Pd", prime_p, prime_q, gen_g, matrix_CPd, polynoms[i])
        if matrix_C != -1:
            pd_results_matrix.append(matrix_C)
            pd_results_polynoms.append(polynom_values)
        else:
            bad_dealer += 1
    if bad_dealer >= dealer.session_parameters.t + dealer.session_parameters.f:
        raise SessionError ("BAD DEALER")
    return pd_results_polynoms, pd_results_matrix


def echo_send_messages(nodes, n, pd_results_polynoms, pd_results_matrix):
    """
    First step of sharing secret, send necessary information to nodes
    :param nodes: list of participants
    :param n: number of participants
    :param pd_results_polynoms: individual polynoms Phi[i][y] for each node_i
    :param pd_results_matrix: matrix to verify dealer and nodes
    :return:  echos_results - matrix of polynom_values x = i, y = j, node_i, node_j
              echos_results_matrix - list of matrixes to verify dealer and nodes
    """
    echos_results = [[] for i in range(n)]
    echos_results_matrix = [1 for i in range(n)]
    for i in range(n):
        for j in range(n):
            matrix_C, polynom_values = nodes[i].call_node("echo", pd_results_matrix[j],
                                                          pd_results_polynoms[j][i], j + 1)
            if matrix_C != -1 and matrix_C != 0:
                echos_results[i] = polynom_values
                echos_results_matrix[i] = matrix_C
    return echos_results, echos_results_matrix


def ready_send_messages(nodes, n, echos_results, echos_results_matrix):
    """
    Second step of sharing secret, send necessary information to nodes
    :param nodes: list of participants
    :param n: number of participants
    :param echos_results: matrix of polynom_values x = i, y = j, node_i, node_j
    :param echos_results_matrix: list of matrixes to verify dealer and nodes
    :return:
    """
    for i in range(n):
        for j in range(n):
            nodes[j].call_node("ready", echos_results_matrix[i], echos_results[i][j], i + 1)


def sharing_initialization(dealer, nodes, key_length, n, t, f):
    """
    Provides sharing phase
    :param dealer: dealer
    :param nodes: list of participants
    :param n: number of participants
    :param t: threshold (requires more than t nodes to reconstruct the secret)
    :param f: count of possible crashed nodes
    :param key_length: 512, 1024 or 2048
    :return:
    """
    tau = randint(1, 9)
    session_parameters = SessionParameters(n, t, f, tau)

    for node in nodes:
        node.set_session_parameters(session_parameters)
        node.set_initialization_parameters(nodes.index(node) + 1)

    dealer.set_session_parameters(session_parameters)

    pd_results_polynoms, pd_results_matrix = pd_send_messages(dealer, nodes, key_length)
    echos_results, echos_results_matrix = echo_send_messages(nodes, n, pd_results_polynoms, pd_results_matrix)
    ready_send_messages(nodes, n, echos_results, echos_results_matrix)


def recovering_initialization(nodes, dealer):
    """
    Provides secret reconstruction by t + 1 nodes
    :param nodes: list of participants
    :param dealer: dealer
    :return:
    """
    n = nodes[0].session_parameters.n
    reconstruct_list = []
    for i in range(n):
        reconstruct_list.append(nodes[i].call_node_recover("Reconstruct"))

    secret_list = []
    for i in range(n):
        for j in range(n):
            secret = nodes[i].call_node_recover("RecShare", reconstruct_list[j], j)
            if secret != -1:
                secret_list.append(secret)

    print("secret is valid", dealer.secret == secret_list[0])


def session_initialisation(dealer, nodes, key_length, n, t, f):
    """
    Initiate session
    :param dealer: dealer
    :param nodes: list of participants
    :param n: number of participants
    :param t: threshold (requires more than t nodes to reconstruct the secret)
    :param f: count of possible crashed nodes
    :param key_length: 512, 1024 or 2048
    :return:
    """
    sharing_initialization(dealer, nodes, key_length, n, t, f)
    recovering_initialization(nodes, dealer)
