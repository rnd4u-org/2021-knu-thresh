from session import *
from participants import Dealer
import time

if __name__ == "__main__":
    """
    Call two sessions for the same dealer and nodes, but with different session parameters
    Length of key parameter p is 1024 bites 
    """
    dealer = Dealer()
    nodes = create_nodes(7)

    # n = 7, t = 5, f = 0
    time.perf_counter()
    sharing_initialization(dealer, nodes, 7, 5, 0)
    recovering_initialization(nodes, dealer)
    print(time.process_time(), 'seconds\n')

    # n = 7, t = 3, f = 1
    time.perf_counter()
    sharing_initialization(dealer, nodes, 7, 3, 1)
    recovering_initialization(nodes, dealer)
    print(time.process_time(), 'seconds')
