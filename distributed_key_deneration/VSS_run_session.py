from session import *
from participants import Dealer
import time

if __name__ == "__main__":
    """
    Call 3 sessions for the same dealer and nodes but with different session parameters
    Length of key parameters: 512 bites 
    """
    dealer = Dealer()
    nodes = create_nodes(5)

    # n = 5 = 2t+f+1, t = 2, f = 1
    time.perf_counter()
    sharing_initialization(dealer, nodes, 512, 5, 2, 1)
    recovering_initialization(nodes, dealer)
    print(time.process_time(), 'seconds\n')

    # n = 5, t = 3, f = 0
    time.perf_counter()
    sharing_initialization(dealer, nodes, 512, 5, 3, 0)
    recovering_initialization(nodes, dealer)
    print(time.process_time(), 'seconds\n')

    # n = 5, t = 4, f = 0
    time.perf_counter()
    sharing_initialization(dealer, nodes, 512, 5, 4, 0)
    recovering_initialization(nodes, dealer)
    print(time.process_time(), 'seconds\n')

    # Length of key parameters: 2048 bites
    # n = 10, t = 7, f = 0
    dealer = Dealer()
    nodes = create_nodes(10)

    time.perf_counter()
    sharing_initialization(dealer, nodes, 2048, 10, 7, 0)
    recovering_initialization(nodes, dealer)
    print(time.process_time(), 'seconds')

"""
RESULTS:  verify_poly+, verify_point+; verify_share- 

I
secret is valid True
2.234375 seconds

II
secret is valid True
9.203125 seconds

III
too long time

IV    verify_poly-, verify_point-, verify_share-
secret is valid True
6.390625 seconds
"""
