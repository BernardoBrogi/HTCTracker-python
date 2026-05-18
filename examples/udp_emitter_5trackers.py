import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from htc_streamer_class import htc_streamer_class
trackers = htc_streamer_class(modality="mod1", sender_ip="192.168.1.135", sender_port=5005)

trackers.stream_to_udp()