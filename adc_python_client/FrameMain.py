import wx
import PopupWindow
import serial
import serial.tools.list_ports
import logging
from ResultEvent import ResultEvent


# ===========================================================================
#   Class FrameMain
class FrameMain(wx.Frame):
    EVENT_UPDATE_RESULT = wx.NewId()

    def __init__(self, *args, **kwargs):
        if len(args) >= 2:
            self.parent, self.thread_pool = args

        size_min = None
        if 'size_min' in kwargs:
            size_min = kwargs.pop('size_min', None)

        super(FrameMain, self).__init__(self.parent, **kwargs)

        _event_map = {
            self.EVENT_UPDATE_RESULT: self.update_info
        }
        for _event, _func in _event_map.items():
            self.Connect(wx.ID_ANY, wx.ID_ANY, _event, _func)

        if size_min:
            self.SetMinSize(size_min)
        self.win = None
        wx.CallAfter(self.hide_and_create_popup)
        self.testing = True
        wx.CallAfter(lambda :self.thread_pool.submit(self.get_adc_data))

    def get_adc_data(self):
        comm_port = None
        data_line = None
        data_list = []
        while self.testing:
            try:
                serial_port_list = serial.tools.list_ports.comports()
                for _each in serial_port_list:
                    if _each.pid == 0x5740:
                        comm_port = serial.Serial(_each.device, baudrate=115200)
                        break

                while comm_port.isOpen():
                    _temp_data = comm_port.readline().decode('utf-8')
                    data_line = int(_temp_data.split()[0], 16)
                    data_list.append(data_line)
                    if not self.testing:
                        return
                    if len(data_list) > 10:
                        wx.PostEvent(self, ResultEvent(self.EVENT_UPDATE_RESULT, sum(data_list)/len(data_list)))
                        data_list = []
            except Exception as _E:
                comm_port = None
                data_list = []
                wx.PostEvent(self, ResultEvent(self.EVENT_UPDATE_RESULT, "No Current data"))
                logging.exception(_E)
            finally:
                if comm_port and comm_port.isOpen():
                    comm_port.close()

    def update_info(self, event):
        try:
            _original_data = event.data
            if isinstance(_original_data, str):
                if self.win and self.win.static_text:
                    self.win.static_text.SetLabel(_original_data)
            else:
                _data_string = ""
                _data = round((_original_data - 1978) * 0.00278, 2)
                if _original_data < 700:
                    _data_string = "No Current data"
                elif _original_data <= 2000:
                    _data_string = f"Charging current: {abs(_data)} A"
                else:
                    _data_string = f"Output current: {abs(_data)} A"
                if self.win and self.win.static_text:
                    self.win.static_text.SetLabel(_data_string)
        except:
            pass

    def hide_and_create_popup(self):
        self.Hide()
        self.win = PopupWindow.PopupWindow(self.GetTopLevelParent(), wx.SIMPLE_BORDER)
        self.win.Position((0, 0), (1024, 0))
        self.win.Show(True)
