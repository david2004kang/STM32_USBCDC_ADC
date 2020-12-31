import wx
import PopupWindow
import serial
import serial.tools.list_ports
import logging
from ResultEvent import ResultEvent
import time
import image


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
        _current = 0
        _voltage = 0
        while self.testing:
            try:
                serial_port_list = serial.tools.list_ports.comports()
                comm_port = None
                for _each in serial_port_list:
                    if _each.pid == 0x5740 or _each.pid == 0x8008:
                        comm_port = serial.Serial(_each.device, baudrate=115200)
                        break

                if comm_port is None:
                    time.sleep(1)
                    continue

                while comm_port.isOpen() and self.testing:
                    try:
                        _temp_data = comm_port.readline().decode('utf-8').split()
                        _current = int((_current + int(_temp_data[0], 16)) * 0.5)
                        _voltage = int((_voltage + int(_temp_data[1], 16)) * 0.5)
                        wx.PostEvent(self, ResultEvent(self.EVENT_UPDATE_RESULT, (_current, _voltage)))
                    except:
                        pass
                    # current_data_list.append(int(_temp_data[0], 16))
                    # voltage_data_list.append(int(_temp_data[1], 16))
                    # if not self.testing:
                    #     return
                    # if len(current_data_list) > 2:
                    #     _current = sum(current_data_list)/len(current_data_list)
                    #     _voltage = sum(voltage_data_list)/len(voltage_data_list)
                    #     current_data_list = []
                    #     voltage_data_list = []
                wx.PostEvent(self, ResultEvent(self.EVENT_UPDATE_RESULT, (_current, _voltage)))
            except Exception as _E:
                wx.PostEvent(self, ResultEvent(self.EVENT_UPDATE_RESULT, (0, 0)))
                logging.exception(_E)
            finally:
            #     if counter < 4096:
            #         wx.PostEvent(self, ResultEvent(self.EVENT_UPDATE_RESULT, (counter, 1900)))
            #         counter += 70
            #     else:
            #         counter = 0

                if comm_port and comm_port.isOpen():
                    comm_port.close()

    _old_current = 0.0
    _old_voltage = 0.0
    _no_display_count = 6
    def update_info(self, event):
        if not self.testing:
            return
        try:
            _current_data, _voltage_data = event.data
            if isinstance(_current_data, str):
                if self.win and self.win.static_text:
                    self.win.static_text.SetLabel(_current_data.center(50))
            else:
                _level = 1980
                _data_string = ""
                _current = abs(_current_data - _level) * 0.00318  # ST
                _voltage = _voltage_data * 0.0055
                if abs(_current - self._old_current) > 0.04:
                    self._old_current = _current
                if abs(_voltage - self._old_voltage) > 0.04:
                    self._old_voltage = _voltage
                _power = self._old_current * self._old_voltage
                if self._no_display_count > 0:
                    self._no_display_count -= 1
                    return
                #_data_current = abs(_current_data - 1961) * 0.00362  # Holtech
                if _current_data < 620 and _voltage < 4.5:
                    _data_string = "C: N/A (A)  V: N/A (V)  P: N/A (W)".center(50)
                    self.win.meter_gauge.set_direction(None)
                    self.win.meter_gauge.set_value(0)
                    self.win.meter_gauge.Refresh()
                elif _voltage < 6 and _current < 0.5:
                    _data_string = f"C:{self._old_current:02.02f}(A)  V:{self._old_voltage:02.02f}(V)  P:{_power:02.02f}(W)".center(50)
                    self.win.meter_gauge.set_direction(None)
                    self.win.meter_gauge.set_value(self._old_current)
                    self.win.meter_gauge.Refresh()
                elif _current_data <= _level:
                    _unit, _max, _min = self.win.meter_gauge.get_unit_max_min()
                    if _unit != 'A' or _max != 5.0 or _min != 0.0:
                        self.win.meter_gauge.set_unit_max_min('A', 5.0, 0.0)
                    _data_string = f"↑ C:{self._old_current:02.02f}(A)  V:{self._old_voltage:02.02f}(V)  P:{_power:02.02f}(W)".center(50)
                    self.win.meter_gauge.set_direction(wx.UP)
                    self.win.meter_gauge.set_value(self._old_current)
                    self.win.meter_gauge.Refresh()
                else:
                    _unit, _max, _min = self.win.meter_gauge.get_unit_max_min()
                    if _unit != 'A' or _max != 3.5 or _min != 0.0:
                        self.win.meter_gauge.set_unit_max_min('A', 3.5, 0.0)
                    _data_string = f"↓ C:{self._old_current:02.02f}(A)  V:{self._old_voltage:02.02f}(V)  P:{_power:02.02f}(W)".center(50)
                    self.win.meter_gauge.set_value(self._old_current)
                    self.win.meter_gauge.set_direction(wx.DOWN)
                    self.win.meter_gauge.Refresh()

                if self.win and self.win.static_text:
                    self.win.static_text.SetLabel(_data_string)

        except Exception as _E:
            logging.exception(_E)

    def hide_and_create_popup(self):
        self.Hide()
        self.win = PopupWindow.PopupWindow(self.GetTopLevelParent(),flags=wx.SIMPLE_BORDER)
        self.win.Show(True)
