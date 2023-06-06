from nymphes_osc.NymphesMidiOscBridge import NymphesMidiOscBridge
from nymphes_osc.BasicControlParameter import BasicControlParameter


nymphes_bridge = NymphesMidiOscBridge(incoming_host='192.168.4.30',
                                      incoming_port=1237,
                                      outgoing_host='juno.local',
                                      outgoing_port=1236,
                                      nymphes_midi_channel=0)

