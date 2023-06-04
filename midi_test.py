import mido


def print_message(message):
    print(message)


in_port = mido.open_input('Nymphes Bootloader')

while True:
    for msg in in_port.iter_pending():
        print_message(msg)
