# iso7816

The main idea - write direct wrapper in Python for "libpcsclite.so" which used to communicate with smart-card.

## Keywords
* smart-card
* ISO7816
* PC/SC

## Additional info
[pcsc-lite](https://pcsclite.apdu.fr/api/index.html)

[pyscard](https://github.com/LudovicRousseau/pyscard)

[pyResMan](https://github.com/JavaCardOS/pyResMan)

## How to use
* $sudo apt install pcsc-tools
* $sudo apt install pcscd
* $pcscd

Example:

import iso7816

my_card = iso7816.Iso7816()

reader = my_card.get_readers()

my_card.connect_to_reader(reader)

print my_card.get_atr()

rx, sw1, sw2 = my_card.transmit('80 90 1B 13')

or

rx, sw1, sw2 = my_card.transmit([0x80, 0x90, 0x1B, 0x13])

