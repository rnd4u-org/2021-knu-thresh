import unittest

from VSS.participants import Node, Dealer
from VSS.session import *
from VSS.VSS_run_session import *
from VSS.session import SessionParameters, SessionError


class VSSTestCase(unittest.TestCase):

    def setUp(self):
        self.session_parameters = SessionParameters(7, 5, 0, 4)
        self.dealer = Dealer()
        self.node = Node()
        self.nodes = session.create_nodes(7)
        for node in self.nodes:
            node.set_session_parameters(self.session_parameters)
            node.set_initialization_parameters(self.nodes.index(node) + 1)
        self.dealer.set_session_parameters(self.session_parameters)
        self.node.set_session_parameters(self.session_parameters)
        self.pd_results_polynoms, self.pd_results_matrix = session.pd_send_messages(self.dealer, self.nodes)
        self.echos_results, self.echos_results_matrix = session.echo_send_messages(self.nodes,
                                                                                   self.dealer.session_parameters.n,
                                                                                   self.pd_results_polynoms,
                                                                                   self.pd_results_matrix)

        session.ready_send_messages(self.nodes, self.session_parameters.n, self.echos_results,
                                    self.echos_results_matrix)
        session.recovering_initialization(self.nodes, self.dealer)
        self.dealer2 = Dealer()
        self.dealer2.generate_secret()
        self.secret = self.dealer2.secret
        self.polynom = self.dealer.generate_polynom()
        self.matrix = self.dealer.generate_matrix_C(self.polynom)
        self.polynoms = list()
        for i in range(1, self.session_parameters.n + 1):
            self.polynoms.append(self.dealer.generate_polynom_i(self.polynom, i))


    def tearDown(self):
        pass

    def test_valid_session_parameters(self):
        s = SessionParameters(5, 3, 0, 4)

    def test_invalid_session_parameters(self):
        with self.assertRaises(SessionError):
            s = SessionParameters(3, 5, 0, 4)

    def test_generate_polynom(self):
        polynom = self.dealer.generate_polynom()

    def test_set_nodes(self):
        for node in self.nodes:
            node.set_session_parameters(self.session_parameters)
            node.set_initialization_parameters(self.nodes.index(node) + 1)

    def test_generate_matrix(self):
        matrix = self.dealer.generate_matrix_C(self.polynom)

    def test_check_session_parameters(self):
        self.assertEqual(self.dealer.session_parameters, self.node.session_parameters)

    def test_check_matrix_len(self):
        self.assertEqual(self.dealer.session_parameters.t + 1, len(self.matrix))

    def test_check_matrix_element_len(self):
        self.assertEqual(self.dealer.session_parameters.t + 1, len(self.matrix[0]))

    def test_check_secret(self):
        self.assertEqual(self.dealer2.secret, self.secret)

    def test_check_polinom_i(self):
        self.assertEqual(len(self.dealer.generate_polynom_i(self.polynom, 1)), self.dealer.session_parameters.t + 1)

    def test_check_call_dealer(self):
        prime_p, gen_g, matrix_CPd, polynoms = self.dealer.call_dealer()

    def test_check_pd_send_messages(self):
        pd_results_polynoms, pd_results_matrix = session.pd_send_messages(self.dealer, self.nodes)

    def test_check_echo_send_messages(self):
        echos_results, echos_results_matrix = session.echo_send_messages(self.nodes, self.session_parameters.n, self.pd_results_polynoms, self.pd_results_matrix)

    def test_check_ready_send_messages(self):
        session.ready_send_messages(self.nodes, self.session_parameters.n, self.echos_results, self.echos_results_matrix)

    def test_check_recovering_initialization(self):
        session.recovering_initialization(self.nodes, self.dealer)
