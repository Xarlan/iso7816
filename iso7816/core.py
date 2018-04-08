# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import ctypes
import struct
import logging

import iso7816def


class ScardEx(Exception):
    def __init__(self):
        pass


class Iso7816():

    def __init__(self, path_to_lib):
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

            if (rv & 0xFFFFFFFF) == iso7816def.SCARD_F_INTERNAL_ERROR:
                pass

            elif (rv & 0xFFFFFFFF) == iso7816def.SCARD_E_INVALID_PARAMETER:
                pass

            elif (rv & 0xFFFFFFFF) == iso7816def.SCARD_E_NO_MEMORY:
                pass

            elif (rv & 0xFFFFFFFF) == iso7816def.SCARD_E_INVALID_VALUE:
                pass

            elif (rv & 0xFFFFFFFF) == iso7816def.SCARD_F_COMM_ERROR:
                pass

            elif (rv & 0xFFFFFFFF) == iso7816def.SCARD_E_NO_SERVICE:
                pass

            else:
                # '__hwnd_reader' and '__protocol' used to communicate to C-library
                self.__hwnd_reader = ctypes.c_long()
                self.__protocol = ctypes.c_long()  # Established protocol in connection
                # Typical value: T0/T1/RAW

                # 'hwnd_reader' and 'protocol' used to communicate in application in Python
                self.hwnd_reader = None
                self.protocol = None

    def __check_rv(self, rv):
        """
        Check value of "rv"
        :param rv: returned value of PCSC library
        :return: exception
        """
        error_code = rv & 0xFFFFFFFF

        if error_code:
            try:
                error_msg = iso7816def.DSC_ERROR[error_code]

            except KeyError:
                print "Unknown error code: {:X}".format(error_code)
                raise Exception

            else:
                print error_msg
                raise Exception

    def get_readers(self):
        """
        Returns a list of currently available readers on the system
        :return:
        """
        n_multistrings = ctypes.c_int32()

        rv = self.pcsc_lib.SCardListReaders(self.hwnd_app_context, None, None, ctypes.byref(n_multistrings))

        self.__check_rv(rv)

        readers = ctypes.create_string_buffer(n_multistrings.value)

        rv = self.pcsc_lib.SCardListReaders(self.hwnd_app_context, None, readers, ctypes.byref(n_multistrings))

        self.__check_rv(rv)

        # print "Available readres: {}".format(readers.value)
        return readers.value

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

        self.__check_rv(rv)

        self.hwnd_reader = self.__hwnd_reader.value
        self.protocol = self.__protocol.value

    def get_atr(self):
        """
        Get ATR - Answer To Reset
        :return: list of ART

        """

        reader_len = ctypes.c_long()
        state_reader = ctypes.c_long()
        atr = ctypes.create_string_buffer(iso7816def.MAX_ATR_SIZE)      # Current ATR of a card in this reade
        atr_len = ctypes.c_long(ctypes.sizeof(atr))                     # Length of ATR

        rv = self.pcsc_lib.SCardStatus(self.__hwnd_reader,
                                       None,
                                       ctypes.byref(reader_len),
                                       ctypes.byref(state_reader),
                                       ctypes.byref(self.__protocol),
                                       atr,
                                       ctypes.byref(atr_len))

        self.__check_rv(rv)

        return list(struct.unpack('%dB' % atr_len.value, atr[:atr_len.value]))
