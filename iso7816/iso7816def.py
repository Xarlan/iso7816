
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

MAX_ATR_SIZE            = 33                # Maximum ATR size

SCARD_UNPOWER_CARD      = 0x0002            # Power down on close

SCARD_SCOPE_USER        = 0x0000            # Scope in user space
SCARD_SCOPE_TERMINAL    = 0x0001            # Scope in terminal
SCARD_SCOPE_SYSTEM      = 0x0002            # Scope in system
SCARD_SCOPE_GLOBAL      = 0x0003            # Scope is global

SCARD_PROTOCOL_T0       = 0x0001            # T=0 active protocol.
SCARD_PROTOCOL_T1       = 0x0002            # T=1 active protocol.
SCARD_PROTOCOL_RAW      = 0x0004            # Raw active protocol

SCARD_SHARE_EXCLUSIVE   = 0x0001            # This application will NOT allow others to share the reader
SCARD_SHARE_SHARED      = 0x0002            # This application will allow others to share the reader
SCARD_SHARE_DIRECT      = 0x0003            # Direct control of the reader, even without a card

# Define Error
SCARD_F_INTERNAL_ERROR          = 0x80100001        # An internal consistency check failed
SCARD_E_INVALID_HANDLE          = 0x80100003        # The supplied handle was invalid
SCARD_E_INVALID_PARAMETER       = 0x80100004        # One or more of the supplied parameters
                                                    # could not be properly interpreted
SCARD_E_NO_MEMORY               = 0x80100006        # Not enough memory available to complete this command
SCARD_E_INSUFFICIENT_BUFFER     = 0x80100008        #
SCARD_E_UNKNOWN_READER          = 0x80100009        # The specified reader name is not recognized
SCARD_E_SHARING_VIOLATION       = 0x8010000B        # The smart card cannot be accessed because of
                                                    # other connections outstanding
SCARD_E_NO_SMARTCARD            = 0x8010000C        # The operation requires a Smart Card,
                                                    # but no Smart Card is currently in the device
SCARD_E_PROTO_MISMATCH          = 0x8010000F        # The requested protocols are incompatible with
                                                    # the protocol currently in use with the smart card
SCARD_E_INVALID_VALUE           = 0x80100011        # One or more of the supplied parameters values
                                                    # could not be properly interpreted
SCARD_F_COMM_ERROR              = 0x80100013        # An internal communications error has been detected
SCARD_E_READER_UNAVAILABLE      = 0x80100017        # The specified reader is not currently available for use
SCARD_E_NO_SERVICE              = 0x8010001D        # The Smart card resource manager is not running
SCARD_E_UNSUPPORTED_FEATURE     = 0x8010001F        # This smart card does not support the requested feature
SCARD_E_NO_READERS_AVAILABLE    = 0x8010002E        # Cannot find a smart card reader
SCARD_W_UNRESPONSIVE_CARD       = 0x80100066        # The smart card is not responding to a reset
SCARD_W_UNPOWERED_CARD          = 0x80100067        # Power has been removed from the smart card,
                                                    # so that further communication is not possible


DSC_ERROR = {
    0x80100001: "An internal consistency check failed",
    0x80100003: "The supplied handle was invalid",
    0x80100004: "One or more of the supplied parameters could not be properly interpreted",
    0x80100006: "Not enough memory available to complete this command",
    0x80100008: "The data buffer to receive returned data is too small for the returned data",
    0x80100009: "The specified reader name is not recognized",
    0x8010000B: "The smart card cannot be accessed because of other connections outstanding",
    0x8010000C: "The operation requires a Smart Card, but no Smart Card is currently in the device",
    0x8010000F: "The requested protocols are incompatible with the protocol currently in use with the smart card",
    0x80100011: "One or more of the supplied parameters values could not be properly interpreted",
    0x80100013: "An internal communications error has been detected",
    0x80100017: "The specified reader is not currently available for use",
    0x8010001D: "The Smart card resource manager is not running",
    0x8010001F: "This smart card does not support the requested feature",
    0x8010002E: "Cannot find a smart card reader",
    0x80100066: "The smart card is not responding to a reset",
    0x80100067: "Power has been removed from the smart card, so that further communication is not possible"
            }

DSC_SW_ERROR = {
    0x6200: "No information given (NV-Ram not changed)",
    0x6201: "NV-Ram not changed 1",
    0x6281: "Part of returned data may be corrupted",
    0x6282: "End of file/record reached before reading Le bytes",
    0x6283: "Selected file invalidated",
    0x6284: "Selected file is not valid. FCI not formated according to ISO",
    0x6285: "No input data available from a sensor on the card. No Purse Engine enslaved for R3bc",
    0x62A2: "Wrong R-MAC",
    0x62A4: "Card locked (during reset( ))",
    0x62F1: "Wrong C-MAC",
    0x62F3: "Internal reset",
    0x62F5: "Default agent locked",
    0x62F7: "Cardholder locked",
    0x62F8: "Basement is current agent",
    0x62F9: "CALC Key Set not unblocked",
  
    0x6E00: "Class not supported"
  
}

DSC_ATR = {
        'TS': {
            0x3B: 'Direct Convention',
            0x3F: 'Inverse Convention'
              },

        # clock rate conversion (Fi)
        'FI': {
            0x0: 'internal clk',
            0x1: 372,
            0x2: 558,
            0x3: 744,
            0x4: 1116,
            0x5: 1488,
            0x6: 1860,
            0x7: 'RFU',
            0x8: 'RFU',
            0x9: 512,
            0xA: 768,
            0xB: 1024,
            0xC: 1536,
            0xD: 2048,
            0xE: 'RFU',
            0xF: 'RFU'
        },

        # baud rate adjustment (Di)
        'DI': {
            0x0: 'RFU',
            0x1: 1,
            0x2: 2,
            0x3: 4,
            0x4: 8,
            0x5: 16,
            0x6: 32,
            0x7: 64,
            0x8: 12,
            0x9: 20,
            0xA: 'RFU',
            0xB: 'RFU',
            0xC: 'RFU',
            0xD: 'RFU',
            0xE: 'RFU',
            0xF: 'RFU'
        },

        # transmission protocol
        'T': {
            0x0: 'The half-duplex transmission of characters',
            0x1: 'The half-duplex transmission of blocks',
            0x2: 'Reserved for future full-duplex operations',
            0x3: 'Reserved for future full-duplex operations',
            0x4: 'Reserved for an enhanced half-duplex transmission of characters',
            0x5: 'Reserved for future use by ISO/IEC JTC 1/SC 17',
            0x6: 'Reserved for future use by ISO/IEC JTC 1/SC 17',
            0x7: 'Reserved for future use by ISO/IEC JTC 1/SC 17',
            0x8: 'Reserved for future use by ISO/IEC JTC 1/SC 17',
            0x9: 'Reserved for future use by ISO/IEC JTC 1/SC 17',
            0xA: 'Reserved for future use by ISO/IEC JTC 1/SC 17',
            0xB: 'Reserved for future use by ISO/IEC JTC 1/SC 17',
            0xC: 'Reserved for future use by ISO/IEC JTC 1/SC 17',
            0xD: 'Reserved for future use by ISO/IEC JTC 1/SC 17',
            0xE: 'Transmission protocols not standardized by ISO/IEC JTC 1/SC 17',
            0xF: 'Not refer to a transmission protocol, but only qualifies global interface bytes',

        }
    }