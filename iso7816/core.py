# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

__author__ = 'lem'

import ctypes
import struct
import logging

from iso7816 import constants


PCSC_LIB = "/lib/x86_64-linux-gnu/libpcsclite.so.1"


class Iso7816Exception(Exception):
    """
    The base class for iso7816 exception
    """

    def __init__(self, msg='Iso7816 Exception', error=None):
        self.msg = msg
        if error:
            self.error = error & 0xFFFFFFFF
            try:
                self.msg = constants.DSC_ERROR[self.error] + ' ' + self.msg

            except KeyError:
                logging.info("Error = {:x} - Unknown error code : {}".format(self.error, self.msg))

            else:
                logging.info("Error = {:x} - {}".format(self.error, self.msg))
        else:
            logging.info(self.msg)



class ScardIORequest(ctypes.Structure):
    """
    This class need to compatibility to direct call function form "libpcslite: lib
    """
    _fields_ = [('dwProtocol', ctypes.c_long),
                ('cbPciLength', ctypes.c_long)]


class Iso7816:

    def __init__(self, path_to_lib=PCSC_LIB):
        try:
            self.pcsc_lib = ctypes.CDLL(path_to_lib)

        except OSError:
            print("\nCan't find '{}'".format(path_to_lib))
            exit(0)

        else:
            self.hwnd_app_context = ctypes.c_long()  # Application Context

            self.rv = self.pcsc_lib.SCardEstablishContext(constants.SCARD_SCOPE_SYSTEM,
                                                     None,
                                                     None,
                                                     ctypes.byref(self.hwnd_app_context))

            # error_code = rv & 0xFFFFFFFF
            error_msg = "[initialization]"

            # if error_code:
            if self.rv:
                # try:
                #
                #     error_msg += constants.DSC_ERROR[error_code]
                #
                # except KeyError:
                #     raise Iso7816Exception(error_msg + "Unknown error code: {:X}".format(error_code))
                #
                # else:
                #     raise Iso7816Exception(error_msg, error_code)
                    raise Iso7816Exception(error_msg, self.rv)

            else:
                                                                # '__hwnd_reader' and '__protocol'
                                                                # used to communicate to C-library
                self.__hwnd_reader = ctypes.c_long()
                self.__protocol = ctypes.c_long()               # Established protocol in connection
                                                                # Typical value: T0/T1/RAW

                                                                # 'hwnd_reader' and 'protocol'
                                                                # used to communicate in application in Python
                self.hwnd_reader = None
                self.protocol = None

                logging.basicConfig(format=u'[%(asctime)s]  %(message)s',
                                    filename="iso7816.log",
                                    level=logging.INFO)

    def __del__(self):
        rv = self.pcsc_lib.SCardDisconnect(self.hwnd_reader, constants.SCARD_UNPOWER_CARD)


    # def __check_rv(self, rv, fun=" "):
    def __check_rv(self, fun=" "):
        """
        Check value of "rv"
        :param rv:          returned value of PCSC library
        :param fun:         "name" of function, who call __check_rv
        :return: exception
        """
        error_msg = '[' + fun + '] '

        if self.rv:
            raise Iso7816Exception(error_msg, self.rv)

    # def __check_sw(self, sw1, sw2):
    #     """
    #     Check status word
    #     :param sw1:
    #     :param sw2:
    #     :return:
    #     """
    #     sw = (sw1 << 8) | sw2
    #     # err_msg = ""
    #
    #     if (sw1 != 0x61) and (sw1 != 0x90):
    #         try:
    #             err_msg = '[' + constants.DSC_SW_ERROR[sw] + ']'
    #
    #         except KeyError:
    #             logging.info("Unknown sw1={:02X} sw2={:02X}".format(sw1, sw2))
    #             raise Iso7816Exception("Unknown error code: {:X}".format(sw), sw)
    #
    #         else:
    #             logging.info("sw1={:02X} sw2={:02X}".format(sw1, sw2))
    #             raise Iso7816Exception(err_msg + " {:X} ".format(sw), sw)

    def get_readers(self):
        """
        Returns a list of currently available readers on the system
        :return:
        """
        n_multistrings = ctypes.c_int32()

        # rv = self.pcsc_lib.SCardListReaders(self.hwnd_app_context, None, None, ctypes.byref(n_multistrings))
        self.rv = self.pcsc_lib.SCardListReaders(self.hwnd_app_context, None, None, ctypes.byref(n_multistrings))

        # self.__check_rv(rv, self.get_readers.__name__)
        self.__check_rv(self.get_readers.__name__)

        readers = ctypes.create_string_buffer(n_multistrings.value)

        self.rv = self.pcsc_lib.SCardListReaders(self.hwnd_app_context, None, readers, ctypes.byref(n_multistrings))

        # self.__check_rv(rv, self.get_readers.__name__)
        self.__check_rv(self.get_readers.__name__)

        available_readers = list(filter(None, readers.raw.decode().split('\x00')))

        return available_readers

    def connect(self,
                reader=None,
                mode=constants.SCARD_SHARE_SHARED,
                protocol=constants.SCARD_PROTOCOL_T0 | constants.SCARD_PROTOCOL_T1):
        """
        Establishes a connection to the reader specified in "reader"
        :param reader:      name of reader which to connect
        :param protocol:    type of protocol T0/T1/RAW
        :param mode:        Mode of connection type
        :return:            Handle to this connection
        """
        # rv = self.pcsc_lib.SCardConnect(self.hwnd_app_context,
        self.rv = self.pcsc_lib.SCardConnect(self.hwnd_app_context,
                                        reader.encode(),
                                        mode,
                                        protocol,
                                        ctypes.byref(self.__hwnd_reader),
                                        ctypes.byref(self.__protocol))

        # self.__check_rv(rv, self.connect.__name__)
        self.__check_rv(self.connect.__name__)

        self.hwnd_reader = self.__hwnd_reader.value
        self.protocol = self.__protocol.value

    def disconnect(self):
        rv = self.pcsc_lib.SCardDisconnect(self.hwnd_reader, constants.SCARD_UNPOWER_CARD)

    def get_atr(self):
        """
        Get ATR - Answer To Reset
        :return: list of ATR

        """

        reader_len = ctypes.c_long()
        state_reader = ctypes.c_long()
        atr = ctypes.create_string_buffer(constants.MAX_ATR_SIZE)   # Current ATR of a card in this reade
        atr_len = ctypes.c_long(ctypes.sizeof(atr))                 # Length of ATR

        # rv = self.pcsc_lib.SCardStatus(self.__hwnd_reader,
        self.rv = self.pcsc_lib.SCardStatus(self.__hwnd_reader,
                                       None,
                                       ctypes.byref(reader_len),
                                       ctypes.byref(state_reader),
                                       ctypes.byref(self.__protocol),
                                       atr,
                                       ctypes.byref(atr_len))

        # self.__check_rv(rv, self.get_atr.__name__)
        self.__check_rv(self.get_atr.__name__)

        atr = list(struct.unpack('%dB' % atr_len.value, atr[:atr_len.value]))

        logging.info("ATR: " + " ".join("{:02X}".format(i) for i in atr))

        return atr

    # def __tx_rx_apdu(self, apdu, apdu_len):
    #
    #     # Structure of Protocol Control Information
    #     pio_send_pci = ScardIORequest()
    #     pio_send_pci.dwProtocol = self.__protocol
    #
    #     apdu_rx = ctypes.create_string_buffer(300)
    #     apdu_rx_len = ctypes.c_long(ctypes.sizeof(apdu_rx))
    #
    #     self.rv = self.pcsc_lib.SCardTransmit(self.__hwnd_reader,
    #                                      ctypes.byref(pio_send_pci),
    #                                      apdu,
    #                                      ctypes.c_long(apdu_len),
    #                                      None,
    #                                      apdu_rx,
    #                                      ctypes.byref(apdu_rx_len))
    #
    #     # self.__check_rv(rv, self.transmit.__name__)
    #     self.__check_rv(self.transmit.__name__)
    #
    #     raw_apdu = list(struct.unpack('%dB' % apdu_rx_len.value, apdu_rx[:apdu_rx_len.value]))
    #
    #     return raw_apdu
    #
    # def transmit_old(self, raw_apdu=None, debug=False):
    #     """
    #     Transmit apdu to smart-card and receive answer
    #     :param debug:
    #     :param raw_apdu:    may be string "90 AA BB..."
    #                         or list [0x90, 0x85, 0x4F, ...]
    #     :return:            apdu, sw1, sw2 or exception
    #     """
    #     if raw_apdu is None:
    #         raise Iso7816Exception("Can't transmit empty 'APDU'")
    #
    #     if isinstance(raw_apdu, str):
    #         raw_apdu = raw_apdu.split(" ")
    #         try:
    #             raw_apdu = [int(x, 16) for x in raw_apdu]
    #         except ValueError:
    #             raise Iso7816Exception("Wrong C-APDU {}".format(raw_apdu))
    #
    #     logging.info("tx apdu: " + " ".join("{:02X}".format(i) for i in raw_apdu))
    #
    #     apdu_len = len(raw_apdu)
    #     apdu = struct.pack('%dB' % apdu_len, *raw_apdu)
    #
    #     sw = None
    #     sw1 = None
    #     sw2 = None
    #     sc_response = []
    #
    #     while sw != 0x9000:
    #         raw_rx_apdu = self.__tx_rx_apdu(apdu, apdu_len)
    #
    #         if raw_rx_apdu:
    #             sw2 = raw_rx_apdu.pop()
    #             sw1 = raw_rx_apdu.pop()
    #
    #             if debug:
    #                 print("debug mode: sw1={:02X} sw2={:02X}".format(sw1, sw2))
    #
    #             self.__check_sw(sw1, sw2)
    #
    #             sw = (sw1 << 8) | sw2
    #             sc_response.extend(raw_rx_apdu)
    #
    #             if sc_response:
    #                 logging.info("rx apdu: " +
    #                              " ".join("{:02X}".format(i) for i in sc_response) +
    #                              " {:02X} {:02X}".format(sw1, sw2))
    #             else:
    #                 logging.info("rx apdu: " + "{:02X} {:02X}".format(sw1, sw2))
    #
    #             if sw1 == 0x61:
    #                 apdu = [0x00, 0xC0, 0x00, 0x00, sw2]                # ISO7816 cmd 'GET RESPONSE'
    #                 apdu_len = len(apdu)
    #                 logging.info("tx apdu: " + " ".join("{:02X}".format(i) for i in apdu))
    #                 apdu = struct.pack('%dB' % apdu_len, *apdu)
    #         else:
    #             raise Iso7816Exception("Wrong R-APDU {}".format(raw_rx_apdu))
    #
    #     return sc_response, sw1, sw2
    #
    #
    # # def transmit(self, raw_apdu, debug=False):
    # def transmit2(self, raw_apdu):
    #     """
    #
    #     :param raw_apdu:
    #     :return:
    #     """
    #     if isinstance(raw_apdu, str):
    #         raw_apdu = raw_apdu.split(" ")
    #         try:
    #             raw_apdu = [int(x, 16) for x in raw_apdu]
    #         except ValueError:
    #             raise Iso7816Exception("Wrong C-APDU {}".format(raw_apdu))
    #
    #     apdu_len = len(raw_apdu)
    #     apdu = struct.pack('%dB' % apdu_len, *raw_apdu)
    #
    #     logging.info("TX apdu: " + " ".join("{:02X}".format(i) for i in raw_apdu))
    #     rx_raw_apdu = self.__tx_rx_apdu(apdu, apdu_len)
    #
    #     if rx_raw_apdu:
    #         sw2 = rx_raw_apdu.pop()
    #         sw1 = rx_raw_apdu.pop()
    #         response = rx_raw_apdu[:]
    #
    #         return response, sw1, sw2
    #     else:
    #         raise Iso7816Exception('Error, R-apdu: {}'.format(rx_raw_apdu))


    # def transmit(self, raw_apdu, auto_get_response=False):
    def transmit(self, raw_apdu):
        """

        :param raw_apdu:    APDU which will be send to smart card
                            type string "AA BB CC DD"
                            or   list [0xAA, 0xBB, 0xCC]
        :return:
        """
        if isinstance(raw_apdu, str):
            raw_apdu = raw_apdu.split(" ")
            try:
                raw_apdu = [int(x, 16) for x in raw_apdu]
            except ValueError:
                raise Iso7816Exception("Wrong C-APDU {}".format(raw_apdu))

        apdu_len = len(raw_apdu)
        apdu = struct.pack('%dB' % apdu_len, *raw_apdu)

        # Structure of Protocol Control Information
        pio_send_pci = ScardIORequest()
        pio_send_pci.dwProtocol = self.__protocol

        rx_apdu = ctypes.create_string_buffer(300)
        rx_apdu_len = ctypes.c_long(ctypes.sizeof(rx_apdu))

        logging.info("TX apdu: " + " ".join("{:02X}".format(i) for i in raw_apdu))
        self.rv = self.pcsc_lib.SCardTransmit(self.__hwnd_reader,
                                         ctypes.byref(pio_send_pci),
                                         apdu,
                                         ctypes.c_long(apdu_len),
                                         None,
                                         rx_apdu,
                                         ctypes.byref(rx_apdu_len))


        self.__check_rv(self.transmit.__name__)

        raw_response = list(struct.unpack('%dB' % rx_apdu_len.value, rx_apdu[:rx_apdu_len.value]))

        if raw_response:
            sw2 = raw_response.pop()
            sw1 = raw_response.pop()
            response = raw_response[:]

            # if auto_get_response and sw1 == 0x61:
            #     apdu_get_response = [0x00, 0xC0, 0x00, 0x00, sw2]                # ISO7816 cmd 'GET RESPONSE'
            #     apdu_get_response_len = len(apdu_get_response)
            #     logging.info("tx apdu: " + " ".join("{:02X}".format(i) for i in apdu))
            #     apdu = struct.pack('%dB' % apdu_get_response_len, *apdu_get_response)

            return response, sw1, sw2

        else:
            raise Iso7816Exception('Error, R-apdu: {}'.format(raw_response))

    def analyze_atr(self, raw_atr=None):
        """
        Analaze ATR and show description
        :param raw_atr: string to analyze
        :return: atr = {'TS': <val>,
                        'T0': <val>,
                        'TAi': <val>,
                        'TBi': <val>,
                        'TCi': <val>,
                        'TDi': <val>,
                        'hb' : <val>,
                        'headeres': ['TS', 'T0', 'TA1', 'TB1', 'TC1', 'TD1', 'TA2', ...]
                        }

        """

        if raw_atr is None:
            raw_atr = self.get_atr()

        if isinstance(raw_atr, str):
            raw_atr = raw_atr.split(" ")
            raw_atr = [int(x, 16) for x in raw_atr]

        print("Analyze ATR: " + " ".join("{:02X}".format(i) for i in raw_atr) + '\n')

        if (raw_atr[0] != 0x3B) and (raw_atr[0] != 0x3F):
            raise Iso7816Exception("This is not ATR")

        atr_len = len(raw_atr)


        atr = {}

        atr['headres'] = []
        atr["TS"] = raw_atr[0]

        atr['headres'].append('TS')
        hist_bytes = raw_atr[1] & 0xF

        ptr = 1
        index = 1

        TDi = raw_atr[1]

        atr['T0'] = TDi
        atr['headres'].append('T0')

        while (ptr + hist_bytes) < atr_len:

            # TAi presence
            if TDi & 0x10:
                ptr += 1
                atr["TA%d" % index] = raw_atr[ptr]
                atr['headres'].append('TA%d' % index)

            # TBi presence
            if TDi & 0x20:
                ptr += 1
                atr["TB%d" % index] = raw_atr[ptr]
                atr['headres'].append('TB%d' % index)

            # TCi presence
            if TDi & 0x40:
                ptr += 1
                atr["TC%d" % index] = raw_atr[ptr]
                atr['headres'].append('TC%d' % index)

            if TDi & 0x80:
                ptr += 1
                atr["TD%d" % index] = raw_atr[ptr]
                atr['headres'].append('TD%d' % index)

                index += 1
                TDi = raw_atr[ptr]
            else:
                break

        ptr += 1

        if atr.get('TD1'):
            if (atr['TD1'] & 0xF) != 0:
                atr['TCK'] = raw_atr.pop()

        atr['hb'] = raw_atr[ptr:ptr + hist_bytes]
        atr['headres'].append('hb')

        if atr.get('TCK'):
            atr['headres'].append('TCK')

        for header in atr['headres']:

            if header == 'TS':
                print("TS  = {:>5X} -> {:}".format(atr['TS'], constants.DSC_ATR['TS'][atr['TS']]))

            elif header == 'T0':
                print("T0  = {:>5X}".format(atr['T0']))

            elif header == 'TA1':
                print("TA1 = {:>5X} ->".format(atr['TA1']))
                print("{:>16}Fi = {}".format(' ', (constants.DSC_ATR['FI'][(atr['TA1'] & 0xF0) >> 4])))
                print("{:>16}Di = {}".format(' ', (constants.DSC_ATR['DI'][atr['TA1'] & 0xF])))

            elif header == 'TB1':
                print("TB1 = {:>5X} ->".format(atr['TB1']))
                print("{:>16}II = {}".format(' ', (atr['TB1'] & 0x60) >> 6))
                print("{:>16}Pi = {}".format(' ', atr['TB1'] & 0x1F))

            elif header == 'TC1':
                print("TC1 = {:>5X} -> Extra guard time".format(atr['TC1']))

            elif header == 'TD1':
                print("TD1 = {:>5X} ->".format(atr['TD1']))
                print("{:>16}T = {} - {}".format(' ', atr['TD1'] & 0xF, constants.DSC_ATR['T'][atr['TD1'] & 0xF]))

            elif header == 'hb':
                print("\nH Bytes: {}".format(" ".join('{:02X}'.format(i) for i in atr['hb'])))

            elif header == 'TCK':
                print("TCK = {:>5X}".format(atr['TCK']))

        print(" ")
        return atr

    def get_attrib(self, get_attrib=None):
        """
        Get an attribute from the IFD Handler
        :param get_attrib:
        :param attrib: The 'name_attrib' or <value>
                       if 'get_attrib' is None - return list of available attrib
                       Not all the 'attrib' can be support
        :return: list, which contain raw value of requested attrib
                 or
                 list of possible attributes
        """

        if get_attrib:
            attr_len = ctypes.c_long()                                  # Length of the pbAttr buffer in bytes and
                                                                        # receives the actual length of the received attribute

            if isinstance(get_attrib, str):
                rv = self.pcsc_lib.SCardGetAttrib(self.hwnd_reader,
                                                  constants.ATTRIB_SMART_CARD[get_attrib],
                                                  None,
                                                  ctypes.byref(attr_len))
            elif isinstance(get_attrib, int):
                rv = self.pcsc_lib.SCardGetAttrib(self.hwnd_reader,
                                                  get_attrib,
                                                  None,
                                                  ctypes.byref(attr_len))

            self.__check_rv(rv, self.get_attrib.__name__)

            attrib = ctypes.create_string_buffer(attr_len.value)        # Pointer to a buffer that receives the attribute.
                                                                        # If this value is NULL, SCardGetAttrib()
                                                                        # ignores the buffer length supplied in pcbAttrLen,
                                                                        # writes the length of the buffer
                                                                        # that would have been returned
                                                                        # if this parameter had not been NULL to pcbAttrLen,
                                                                        # and returns a success code

            if isinstance(get_attrib, str):
                rv = self.pcsc_lib.SCardGetAttrib(self.hwnd_reader,
                                                  constants.ATTRIB_SMART_CARD[get_attrib],
                                                  ctypes.byref(attrib),
                                                  ctypes.byref(attr_len))
            elif isinstance(get_attrib, int):
                rv = self.pcsc_lib.SCardGetAttrib(self.hwnd_reader,
                                                  get_attrib,
                                                  ctypes.byref(attrib),
                                                  ctypes.byref(attr_len))

            self.__check_rv(rv, self.get_attrib.__name__)

            raw_attrib = list(struct.unpack('%dB' % attr_len.value, attrib[:attr_len.value]))

            return raw_attrib

        else:
            return sorted(constants.ATTRIB_SMART_CARD.keys())

    @staticmethod
    def validate_byte(raw_value):

        if isinstance(raw_value, int):
            if raw_value in range(0, 0x10000):
                return raw_value
            else:
                raise Iso7816Exception('wrong value of [CLA]/[INS]/[P1]/[P2]/[Lc]/[Le]')

        elif isinstance(raw_value, str):
            try:
                value = int(raw_value, 16)

            except ValueError:
                raise Iso7816Exception('wrong value of [CLA]/[INS]/[P1]/[P2]/[Lc]/[Le]')

            else:
                if value <= 0xFF:
                    return value
                else:
                    raise Iso7816Exception('wrong value of [CLA]/[INS]/[P1]/[P2]/[Lc]/[Le]')

    @staticmethod
    def validate_data(raw_data):
        if isinstance(raw_data, str):
            try:
                data = [int(x, 16) for x in raw_data.split(" ")]

            except ValueError:
                raise Iso7816Exception('wrong format of [data]')

            else:
                return data

