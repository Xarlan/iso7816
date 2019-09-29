# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

__author__ = 'lem'

import tkinter as tk
from tkinter import ttk

import iso7816


class SmartCardGui(iso7816.Iso7816):

    def __init__(self, parent):
        iso7816.Iso7816.__init__(self)
        self.parent = parent
        self.parent.title("Smart Card GUI tool")

        self.l_cla = ttk.Label(self.parent, text='CLA')
        self.l_cla.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        # self.cla = ttk.Entry(self.parent, width=3, justify=tk.RIGHT, font=22)
        self.cla = ttk.Entry(self.parent, width=4, justify=tk.RIGHT)
        self.cla.grid(row=1, column=0, padx=5)
        self.cla.bind('<FocusOut>', self.gui_check_value)

        self.l_ins = ttk.Label(self.parent, text='INS')
        self.l_ins.grid(row=0, column=1, padx=5, pady=5, sticky='e')
        self.ins = ttk.Entry(self.parent, width=4, justify=tk.RIGHT)
        self.ins.grid(row=1, column=1, padx=5)
        self.ins.bind('<FocusOut>', self.gui_check_value)


        self.l_p1 = ttk.Label(self.parent, text='P1')
        self.l_p1.grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.p1 = ttk.Entry(self.parent, width=4, justify=tk.RIGHT)
        self.p1.grid(row=1, column=2, padx=5)
        self.p1.bind('<FocusOut>', self.gui_check_value)

        self.l_p2 = ttk.Label(self.parent, text='P2')
        self.l_p2.grid(row=0, column=3, padx=5, pady=5, sticky='e')
        self.p2 = ttk.Entry(self.parent, width=4, justify=tk.RIGHT)
        self.p2.grid(row=1, column=3, padx=5)
        self.p2.bind('<FocusOut>', self.gui_check_value)

        self.l_lc = ttk.Label(self.parent, text='Lc')
        self.l_lc.grid(row=0, column=4, padx=5, pady=5, sticky='e')
        self.lc = ttk.Entry(self.parent, width=4, justify=tk.RIGHT)
        self.lc.grid(row=1, column=4, padx=5)
        self.lc.bind('<FocusOut>', self.gui_check_value)

        self.l_le = ttk.Label(self.parent, text='Le')
        self.l_le.grid(row=0, column=5, padx=5, pady=5, sticky='e')
        self.le = ttk.Entry(self.parent, width=4, justify=tk.RIGHT)
        self.le.grid(row=1, column=5, padx=5)
        self.le.bind('<FocusOut>', self.gui_check_value)

        self.l_data = ttk.Label(self.parent, text='Data')
        self.l_data.grid(row=3, padx=5, pady=5, sticky='w')
        self.data = ttk.Entry(self.parent)
        self.data.grid(row=4, padx=5, columnspan=6, sticky='we')
        self.data.bind('<FocusOut>', self.gui_check_data)

        self.bttn_atr = ttk.Button(self.parent, text='Get ATR', command=self.gui_get_atr)
        self.bttn_atr.grid(row=0, column=6, padx=20)

        self.bttn_analyze_atr = ttk.Button(self.parent, text='Analyze ATR')
        self.bttn_analyze_atr.grid(row=1, column=6, padx=20)

        self.lf_reader = ttk.LabelFrame(self.parent, text='Readers', width=30, labelanchor='n')
        self.lf_reader.grid(row=0, column=7, rowspan=2, padx=5, ipady=5)

        try:
            connected_readers = self.get_readers()

        except iso7816.Iso7816Exception:
            connected_readers = ['no readers']

        self.combo_readers = ttk.Combobox(self.lf_reader, value=connected_readers)
        self.combo_readers.grid(padx=5, pady=5, columnspan=2)


        self.lf_apdu_cmd = ttk.LabelFrame(self.parent, text='Cmd APDU', labelanchor='n')
        self.lf_apdu_cmd.grid(row=3, column=7, rowspan=2, padx=5, ipady=5)
        self.combo_apdu_cmd = ttk.Combobox(self.lf_apdu_cmd, value=['temp1', 'temp2', 'temp3'])
        self.combo_apdu_cmd.grid(padx=5, pady=5)

        self.bttn_tx_apdu = ttk.Button(self.parent, text="Send APDU", command=self.gui_send_apdu)
        self.bttn_tx_apdu.grid(row=4, column=6, padx=20)

        self.bttn_connect = ttk.Button(self.parent,
                                       text='Connect',
                                       command=self.connect_to_reader)
        self.bttn_connect.grid(row=0, column=8, padx=5)

        self.bttn_disconnect = ttk.Button(self.parent,
                                          text='Disconnect',
                                          state='disabled',
                                          command=self.disconnect_from_reader)
        self.bttn_disconnect.grid(row=1, column=8, padx=5)


        self.l_raw_apdu = ttk.Label(self.parent, text='Raw APDU')
        self.l_raw_apdu.grid(row=5, column=0, padx=5, pady=5, sticky='w', columnspan=2)
        self.raw_apdu = ttk.Entry(self.parent)
        self.raw_apdu.grid(row=6, padx=5, columnspan=8, sticky='we')

        self.bttn_tx_raw_apdu = ttk.Button(self.parent, text='Tx Raw APDU')
        self.bttn_tx_raw_apdu.grid(row=6, column=8, padx=5)

        self.console_apdu = tk.Text(self.parent)
        self.console_apdu.grid(row=7, column=0, columnspan=9, padx=5, pady=5, sticky='we')
        self.scroll_console = ttk.Scrollbar(command=self.console_apdu.yview)
        self.scroll_console.grid(row=7, column=8, pady=5, ipadx=7, sticky='nse')
        self.console_apdu.config(yscrollcommand=self.scroll_console.set)

    def connect_to_reader(self):
        selected_reader = self.combo_readers.get()
        try:
            self.connect(selected_reader)
        except iso7816.Iso7816Exception as e:
            print(e.msg)
            self.print_console(e.msg)
        else:
            self.bttn_connect.config(state=tk.DISABLED)
            self.bttn_disconnect.config(state=tk.NORMAL)
            self.combo_readers.config(state='disabled')

    def disconnect_from_reader(self):
        self.disconnect()
        self.bttn_disconnect.config(state=tk.DISABLED)
        self.bttn_connect.config(state=tk.NORMAL)
        self.combo_readers.config(state='normal')

    def print_console(self, message):
        self.console_apdu.insert(tk.END, message)
        self.console_apdu.insert(tk.END, '\n')

    def gui_get_atr(self):
        try:
            current_atr = self.get_atr()

        except iso7816.Iso7816Exception as e:
            self.print_console(e.msg)

        else:
            atr = " ".join("{:02X}".format(i) for i in current_atr)
            self.print_console("ATR: " + atr)

    def gui_check_value(self, event):
        current_value = event.widget.get()
        try:
            iso7816.Iso7816.validate_byte(current_value)

        except iso7816.Iso7816Exception as e:
            self.print_console(e.msg)
            event.widget.delete(0, tk.END)

    def gui_check_data(self, event):
        current_data = event.widget.get()
        try:
            iso7816.Iso7816.validate_data(current_data)

        except iso7816.Iso7816Exception as e:
            self.print_console(e.msg)

    def gui_send_apdu(self):
        gui_apdu = " ".join([self.cla.get(), self.ins.get(), self.p1.get(), self.p2.get()])
        if len(self.lc.get()) > 0:
            gui_apdu += " " + self.lc.get()

        if len(self.data.get()) > 0:
            gui_apdu += " " + self.data.get()

        if len(self.le.get()) > 0:
            gui_apdu += " " + self.le.get()

        try:
            response, sw1, sw2 = self.transmit(gui_apdu)

        except iso7816.Iso7816Exception as e:
            self.print_console(e.msg)

        else:
            self.print_console("TX: " + gui_apdu.upper())
            self.print_console("RX: " + " ".join("{:02X}".format(i) for i in response))
            self.print_console("    SW1={:02X}, SW2={:02X}".format(sw1, sw2))




if __name__ == '__main__':
    root = tk.Tk()
    SmartCardGui(root)
    root.mainloop()
