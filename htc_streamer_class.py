import time
import struct
import socket
import numpy as np
from function import triad_openvr

class htc_streamer_class:
    def __init__(self, modality="mod1", sender_ip="127.0.0.1", sender_port=8051, sample_rate=1/90):

        self.sender_ip = sender_ip
        self.sender_port = sender_port
        self.sample_rate = sample_rate
        self.modality = modality # mod1: [hand], mod2: [hand, forearm], mod3: [hand, forearm, arm], mod4: [hand, forearm, arm, chest], mod5: all
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.v = triad_openvr.triad_openvr()
        self.v.print_discovered_objects()
        self.working_tracker = []
        self.idx_sorted_tracker = []
        self.ID_tracker = ["hand", "forearm", "arm", "chest", "controlatHand"] # these depend on the config file
        self.n_working_tracker = 0
        self.flag = False
        self.last_data = None
        
        # Control value computation parameters
        self.kernel_coeff_values = None
        self.kernel_coordinates = None
        self.mu_all = None
        self.percentile95Value = None
        self.q_start = None
        self.q_end = None
        self.p_start = None
        self.p_end = None
        self.orientation_low = None
        self.orientation_high = None
        self.rotation_low_to_high = None
        
        # Control UDP socket
        self.control_sock = None
        self.control_sender_ip = None
        self.control_sender_port = None
        self.franka_sock = None
        self.franka_sender_ip = None
        self.franka_sender_port = None
        self.frankaCom = False
        
        # Data storage variables
        self.data_storage_list = []
        self.save_data = False
        self.data_file_path = None
        
        self._initialize_trackers()

    def _initialize_trackers(self):

        # Get working trackers
        for name in self.v.object_names.get('Tracker', []):
            if self.v.devices[name].get_pose_quaternion() is not None:
                self.working_tracker.append(name)

        if not all(tracker in self.ID_tracker for tracker in self.working_tracker):
            print("Error: All working trackers must be listed in ID_tracker.")
            raise SystemExit
        
        self.n_trackers = len(self.working_tracker)
        print(f"Number of working trackers: {self.n_trackers}, {self.working_tracker}")
        
        # Adjust ID_tracker based on modality
        if self.modality == "mod1":
            self.ID_tracker = ["hand"]
        elif self.modality == "mod2":
            self.ID_tracker = ["hand", "forearm"]
        elif self.modality == "mod3":
            self.ID_tracker = ["hand", "forearm", "arm"]
        elif self.modality == "mod4":
            self.ID_tracker = ["hand", "forearm", "arm", "chest"]
        
        self.n_working_tracker = self.n_trackers
        
        # Sort trackers for correct package order
        for name in self.ID_tracker:
            self.idx_sorted_tracker.append(self.working_tracker.index(name))
        print("Order of trackers:", self.idx_sorted_tracker)
            
    def stream_to_udp(self):
        
        print("Starting to collect data...")
        start_time = time.time_ns()
        lastSend = 0
        start_message = 1
        try:
            while True:
                data, n_working_tracker = self.get_last_data()
                # Not sending n_working tracker for matlab unpack 
                timestamp = (time.time_ns() - start_time) / 1e9
                format = f"=IfI{len(data)}d"
                # print(len(data))
                packed_data = struct.pack(format, start_message, timestamp, len(self.ID_tracker), *data)
                # print(f"Packed data size: {struct.unpack(format, packed_data)}")
                if (timestamp - lastSend) > self.sample_rate:
                    self.sock.sendto(packed_data, (self.sender_ip, self.sender_port))
                    lastSend = timestamp
        except KeyboardInterrupt:
            print("Stopping the UDP streamer...")
        finally:
            self.sock.close()
            print("UDP streamer closed.")

    def get_last_data(self):
        # This method returns the latest data and the number of working trackers
        n_selected = len(self.ID_tracker)
        # print(f"Getting data for {n_selected} selected trackers.")
        if not hasattr(self, 'quat_last') or self.quat_last.shape[0] != n_selected:
            self.quat_last = np.zeros((n_selected, 4))
        # Track state of each tracker for warning messages
        if not hasattr(self, '_not_working_set'):
            self._not_working_set = set()
        data = np.empty(0)
        n_working_tracker = 0
        for j, tracker_name in enumerate(self.ID_tracker):
            try:
                idx = self.working_tracker.index(tracker_name)
            except ValueError:
                print(f"Tracker '{tracker_name}' not found in working_tracker list.")
                zeros = np.zeros(7)
                data = np.concatenate((data, zeros))
                continue
            tracker_data = self.v.devices[self.working_tracker[idx]].get_pose_quaternion()
            if tracker_data is not None:
                # If tracker was previously not working, print message that it's back
                if tracker_name in self._not_working_set:
                    print(f"Tracker '{tracker_name}' is back online.")
                    self._not_working_set.remove(tracker_name)
                tracker_data_ = np.array(tracker_data)[3:7]
                idx_quat = np.argmax(np.abs(self.quat_last[j]))
                if tracker_data_[idx_quat] * self.quat_last[j, idx_quat] < 0:
                    tracker_data_ = -tracker_data_
                self.quat_last[j] = tracker_data_
                tracker_data[3:7] = tracker_data_
                data = np.concatenate((data, tracker_data))
                n_working_tracker += 1
            else:
                # Only print once if tracker just went offline
                if tracker_name not in self._not_working_set:
                    print(f"Tracker '{tracker_name}' is not working.")
                    self._not_working_set.add(tracker_name)
                zeros = np.zeros(7)
                data = np.concatenate((data, zeros))
        self.last_data = data.copy()
        # print(f"Data: {self.last_data}")
        return self.last_data, n_working_tracker
    

    
    


