from nymphes_osc.NymphesMidiOscBridge import NymphesMidiOscBridge
import time


def main():
    #
    # Create the Nymphes OSC Controller
    #
    nymphes = NymphesMidiOscBridge(
        nymphes_midi_channel=1,
        osc_in_port=1237,
        logging_enabled=True,
        log_params_and_performance_controls=False
    )

    #
    # Stay running until manually killed
    #
    while True:
        nymphes.update()
        time.sleep(0.0001)


if __name__ == '__main__':
    main()
