from NymphesMidiOscBridge import NymphesMidiOscBridge
from .ControlParameter_Basic import ControlParameter_Basic


nymphes_bridge = NymphesMidiOscBridge(incoming_host='192.168.4.30',
                                      incoming_port=1237,
                                      outgoing_host='juno.local',
                                      outgoing_port=1236,
                                      nymphes_midi_channel=0)

