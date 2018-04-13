# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import ctypes
import struct
import logging

import iso7816def

PCSC_LIB = "/lib/x86_64-linux-gnu/libpcsclite.so.1"


class Iso7816Exception(Exception):
    """
    The base class for iso7816 exception
    """

    def __init__(self, msg='Iso7816 Exception', error=None):
        self.msg = msg
        self.error = error & 0xFFFFFFFF


class ScardIORequest(ctypes.Structure):
    """
    This class need to compatibility to direct call function form "libpcslite: lib
    """
    _fields_ = [('dwProtocol', ctypes.c_long),
                ('cbPciLength', ctypes.c_long)]


class Iso7816():

    def __init__(self, path_to_lib=PCSC_LIB):
        try:
            self.pcsc_lib = ctypes.CDLL(path_to_lib)

        except OSError:
            print "\nCan't find {}".format(path_to_lib)
            exit(0)

        else:
            self.hwnd_app_context = ctypes.c_long()  # Application Context

            rv = self.pcsc_lib.SCardEstablishContext(iso7816def.SCARD_SCOPE_SYSTEM,
                                                     None,
                                                     None,
                                                     ctypes.byref(self.hwnd_app_context))

            error_code = rv & 0xFFFFFFFF
            error_msg = "[initialization]"

            if error_code:
                try:

                    error_msg += iso7816def.DSC_ERROR[error_code]

                except KeyError:
                    raise Iso7816Exception(error_msg + "Unknown error code: {:X}".format(error_code))

                else:
                    raise Iso7816Exception(error_msg)


            else:
                # '__hwnd_reader' and '__protocol' used to communicate to C-library
                self.__hwnd_reader = ctypes.c_long()
                self.__protocol = ctypes.c_long()  # Established protocol in connection
                # Typical value: T0/T1/RAW

                # 'hwnd_reader' and 'protocol' used to communicate in application in Python
                self.hwnd_reader = None
                self.protocol = None

    def __del__(self):
        rv = self.pcsc_lib.SCardDisconnect(self.hwnd_reader, iso7816def.SCARD_UNPOWER_CARD)


    def __check_rv(self, rv, fun=" "):
        """
        Check value of "rv"
        :param rv:          returned value of PCSC library
        :param fun:    "name of function, who call __check_rv
        :return: exception
        """
        error_code = rv & 0xFFFFFFFF

        error_msg = '[' + fun + '] '

        if error_code:
            try:
                error_msg += iso7816def.DSC_ERROR[error_code]

            except KeyError:
                raise Iso7816Exception(error_msg + "Unknown error code: {:X}".format(error_code))

            else:
                raise Iso7816Exception(error_msg)

    def __check_sw(self, sw1, sw2):
        """
        Check status word
        :param sw1:
        :param sw2:
        :return:
        """
        sw = (sw1 << 8) | sw2
        err_msg = ""

        if (sw1 != 0x61) and (sw1 != 0x90):
            try:
                err_msg = '[' + iso7816def.DSC_SW_ERROR[sw] + ']'

            except KeyError:
                raise Iso7816Exception("Unknown error code: {:X}".format(sw))

            else:
                # raise Iso7816Exception("[Error] {:X} ".format(sw) + err_msg)
                raise Iso7816Exception(err_msg + " {:X} ".format(sw))

    def get_readers(self):
        """
        Returns a list of currently available readers on the system
        :return:
        """
        n_multistrings = ctypes.c_int32()

        rv = self.pcsc_lib.SCardListReaders(self.hwnd_app_context, None, None, ctypes.byref(n_multistrings))

        self.__check_rv(rv, self.get_readers.__name__)

        readers = ctypes.create_string_buffer(n_multistrings.value)

        rv = self.pcsc_lib.SCardListReaders(self.hwnd_app_context, None, readers, ctypes.byref(n_multistrings))

        self.__check_rv(rv, self.get_readers.__name__)

        available_readers = filter(None, readers[:].split('\x00'))

        return available_readers

    def connect_to_reader(self,
                          reader=None,
                          mode=iso7816def.SCARD_SHARE_SHARED,
                          protocol=iso7816def.SCARD_PROTOCOL_T0 | iso7816def.SCARD_PROTOCOL_T1):
        """
        Establishes a connection to the reader specified in "reader"
        :param reader:      name of reader which to connect
        :param protocol:    type of protocol T0/T1/RAW
        :param mode:        Mode of connection type
        :return:            Handle to this connection
        """
        rv = self.pcsc_lib.SCardConnect(self.hwnd_app_context,
                                        reader,
                                        mode,
                                        protocol,
                                        ctypes.byref(self.__hwnd_reader),
                                        ctypes.byref(self.__protocol))

        self.__check_rv(rv, self.connect_to_reader.__name__)

        self.hwnd_reader = self.__hwnd_reader.value
        self.protocol = self.__protocol.value

    def get_atr(self):
        """
        Get ATR - Answer To Reset
        :return: list of ART

        """

        reader_len = ctypes.c_long()
        state_reader = ctypes.c_long()
        atr = ctypes.create_string_buffer(iso7816def.MAX_ATR_SIZE)  # Current ATR of a card in this reade
        atr_len = ctypes.c_long(ctypes.sizeof(atr))                 # Length of ATR

        rv = self.pcsc_lib.SCardStatus(self.__hwnd_reader,
                                       None,
                                       ctypes.byref(reader_len),
                                       ctypes.byref(state_reader),
                                       ctypes.byref(self.__protocol),
                                       atr,
                                       ctypes.byref(atr_len))

        self.__check_rv(rv, self.get_atr.__name__)

        return list(struct.unpack('%dB' % atr_len.value, atr[:atr_len.value]))

    def __tx_rx_apdu(self, apdu, apdu_len):

        # Structure of Protocol Control Information
        pio_send_pci = ScardIORequest()
        pio_send_pci.dwProtocol = self.__protocol

        apdu_rx = ctypes.create_string_buffer(200)
        apdu_rx_len = ctypes.c_long(ctypes.sizeof(apdu_rx))

        rv = self.pcsc_lib.SCardTransmit(self.__hwnd_reader,
                                         ctypes.byref(pio_send_pci),
                                         apdu,
                                         ctypes.c_long(apdu_len),
                                         None,
                                         apdu_rx,
                                         ctypes.byref(apdu_rx_len))

        self.__check_rv(rv, self.transmit.__name__)

        raw_apdu = list(struct.unpack('%dB' % apdu_rx_len.value, apdu_rx[:apdu_rx_len.value]))

        return raw_apdu

    def transmit(self, raw_apdu=None):
        """
        Transmit apdu to smart-card and receive answer
        :param raw_apdu:    may be string "90 AA BB..."
                            or list [0x90, 0x85, 0x4F, ...]
        :return:            apdu, sw1, sw2 or exception
        """
        if raw_apdu is None:
            raise Iso7816Exception("Can't transmit empty 'APDU'")

        if isinstance(raw_apdu, str):
            raw_apdu = raw_apdu.split(" ")
            raw_apdu = [int(x, 16) for x in raw_apdu]

        apdu_len = len(raw_apdu)
        apdu = struct.pack('%dB' % apdu_len, *raw_apdu)

        sw = None
        sw1 = None
        sw2 = None
        sc_response = []

        while sw != 0x9000:
            raw_rx_apdu = self.__tx_rx_apdu(apdu, apdu_len)

            if raw_rx_apdu:
                sw2 = raw_rx_apdu.pop()
                sw1 = raw_rx_apdu.pop()

                # if (sw1 != 0x90) or (sw1 != 0x61):
                self.__check_sw(sw1, sw2)

                sw = (sw1 << 8) | sw2
                sc_response.extend(raw_rx_apdu)

                if sw1 == 0x61:
                    apdu = [0x00, 0xC0, 0x00, 0x00, sw2]
                    apdu_len = len(apdu)
                    apdu = struct.pack('%dB' % apdu_len, *apdu)
            else:
                raise Iso7816Exception("Wrong apdu")

        return sc_response, sw1, sw2

    def analyze_atr(self, raw_atr=None):

        if raw_atr is None:
            raw_atr = self.get_atr()
            # print "ATR: " + " ".join("{:02X}".format(i) for i in raw_atr) + '\n'

        if isinstance(raw_atr, str):
            raw_atr = raw_atr.split(" ")
            raw_atr = [int(x, 16) for x in raw_atr]

        print "Analyze ATR: " + " ".join("{:02X}".format(i) for i in raw_atr) + '\n'

        if (raw_atr[0] != 0x3B) and (raw_atr[0] != 0x3F):
            raise Iso7816Exception("This is not ATR")

        atr_len = len(raw_atr)


        atr = {}
        atr_header = []
        atr["TS"] = raw_atr[0]
        atr_header.append('TS')
        hist_bytes = raw_atr[1] & 0xF

        ptr = 1
        index = 1

        TDi = raw_atr[1]
        atr['T0'] = TDi
        atr_header.append('T0')

        while (ptr + hist_bytes) < atr_len:

            # TAi presence
            if TDi & 0x10:
                ptr += 1
                atr["TA%d" % index] = raw_atr[ptr]
                atr_header.append('TA%d' % index)

            # TBi presence
            if TDi & 0x20:
                ptr += 1
                atr["TB%d" % index] = raw_atr[ptr]
                atr_header.append('TB%d' % index)

            # TCi presence
            if TDi & 0x40:
                ptr += 1
                atr["TC%d" % index] = raw_atr[ptr]
                atr_header.append('TC%d' % index)

            if TDi & 0x80:
                ptr += 1
                atr["TD%d" % index] = raw_atr[ptr]
                atr_header.append('TD%d' % index)

                index += 1
                TDi = raw_atr[ptr]
            else:
                break

        atr['hb'] = raw_atr[ptr+1:ptr + hist_bytes+2]
        atr_header.append('hb')

        print sorted(atr)

        for header in atr_header:

            if header == 'TS':
                print "TS  = {:>5X} -> {:}".format(atr['TS'], iso7816def.DSC_ATR['TS'][atr['TS']])

            elif header == 'T0':
                print "T0  = {:>5X}".format(atr['T0'])

            elif header == 'TA1':
                print "TA1 = {:>5X} ->".format(atr['TA1'])
                print "{:>16}Fi = {}".format(' ', (iso7816def.DSC_ATR['FI'][(atr['TA1'] & 0xF0) >> 4]))
                print "{:>16}Di = {}".format(' ', (iso7816def.DSC_ATR['DI'][atr['TA1'] & 0xF]))

            elif header == 'TB1':
                print "TB1 = {:>5X} ->".format(atr['TB1'])
                print "{:>16}II = {}".format(' ', (atr['TB1'] & 0x60) >> 6)
                print "{:>16}Pi = {}".format(' ', atr['TB1'] & 0x1F)

            elif header == 'TC1':
                print "TC1 = {:>5X} -> Extra guard time".format(atr['TC1'])

            elif header == 'hb':
                print "Historical bytes: {}".format(" ".join('{:02X}'.format(i) for i in atr['hb']))

        return atr