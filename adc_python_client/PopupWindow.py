import wx
import image
import math


# ===========================================================================
#   Class MeterGauge
class MeterGauge(wx.Control):
    def __init__(self, parent, *args, **dict_args):
        wx.Control.__init__(self, parent, *args, **dict_args)
        self.direction = None
        self.value = 0.0
        self.unit = 'A'
        self.max = 5
        self.min = 0
        self.pointer_percentage = 0.0
        self.pointer_length = 75
        width, height = self.GetClientSize()
        self.x1 = width // 2 - 15
        self.y1 = height // 2 + 7
        self.mark_length = 102
        self.text_list = \
            [[f"{self.min:.1f} {self.unit}",
              self.x1 + math.cos(math.radians(130)) * self.mark_length,
              self.y1 + math.sin(math.radians(130)) * self.mark_length] ]

        _interval = abs(self.max - self.min) * 0.1
        for _counter in range(2, 12, 2):
            self.text_list.append(
                [f"{_interval * _counter:.1f}  {self.unit}",
                 self.x1 + math.cos(math.radians(130 + _counter * 28)) * self.mark_length,
                 self.y1 + math.sin(math.radians(130 + _counter * 28)) * self.mark_length])
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda _: None)
        wx.CallAfter(self._on_size_callback)

    def set_unit_max_min(self, unit='A', _max=5.0, _min=0):
        self.unit = unit
        self.max = _max
        self.min = _min
        self.text_list[0][0] = f"{self.min:.1f} {self.unit}"
        _interval = abs(self.max - self.min) * 0.2

        for _counter in range(1, len(self.text_list)):
            self.text_list[_counter][0] = f"{_interval * _counter:.1f}  {self.unit}"

    def get_unit_max_min(self):
        return self.unit, self.max, self.min

    def set_value(self, value):
        if value > self.max:
            self.value = self.max
        elif value < self.min:
            self.value = self.min
        else:
            self.value = value
        self.pointer_percentage = (self.value - self.min) / (self.max - self.min) * 100.0


    def set_direction(self, direction):
        self.direction = direction

    def on_paint(self, _=None):
        width, height = self.GetClientSize()
        empty_bitmap = wx.Bitmap(width, height)
        memory_dc = wx.MemoryDC()
        memory_dc.SelectObject(empty_bitmap)
        # memory_dc.SetBrush(wx.Brush(wx.WHITE))
        # memory_dc.DrawRectangle(0, 0, width, height)
        memory_dc.DrawBitmap(image.GAUGE_BG.Bitmap,
                             (width - image.GAUGE_BG.Bitmap.Width) // 2 + 2,
                             (height - image.GAUGE_BG.Bitmap.Height) // 2 + 8)
        memory_dc.SetPen(wx.Pen(wx.BLUE, 3))

        x1 = width // 2
        y1 = height // 2 + 12
        degree = 130 + (2.8 * self.pointer_percentage)  # 0: 130, full: 50
        x2 = int(x1 + math.cos(math.radians(degree)) * self.pointer_length)
        y2 = int(y1 + math.sin(math.radians(degree)) * self.pointer_length)

        memory_dc.DrawLine(x1, y1, x2, y2)
        # memory_dc.DrawLine(center_x, center_y , center_x - self.pointer_length, center_y )
        # memory_dc.DrawLine(center_x, center_y , center_x + self.pointer_length, center_y )
        if self.direction == wx.DOWN:
            arrow = image.ARROW_DN.Bitmap
            arrow.SetMaskColour(wx.WHITE)
            memory_dc.DrawBitmap(arrow, (width - image.ARROW_DN.Bitmap.Width) // 2, 130, True)
        elif self.direction == wx.UP:
            arrow = image.ARROW_UP.Bitmap
            arrow.SetMaskColour(wx.WHITE)
            memory_dc.DrawBitmap(arrow, (width - image.ARROW_UP.Bitmap.Width) // 2, 130, True)

        for _text, _x, _y  in self.text_list:
            memory_dc.DrawText(_text, _x, _y)

        wx.PaintDC(self).Blit(0, 0, width, height, memory_dc, 0, 0)
        memory_dc.SelectObject(wx.NullBitmap)
        memory_dc.Destroy()

    def _on_size_callback(self):
        self.Refresh()
        self.Update()

    def on_size(self, event):
        wx.CallAfter(self._on_size_callback)
        event.Skip()


# ===========================================================================
#   Class MeterGauge
class PopupWindow(wx.PopupWindow):
    """Adds a bit of text and mouse movement to the wx.PopupWindow"""
    ldPos = None
    wPos = None
    def __init__(self, parent, **kwargs):
        wx.PopupWindow.__init__(self, parent, **kwargs)
        self.parent = parent
        self.Position((0, 0), (1150, 0))

        self.gui_size = wx.Size(260, 240)
        self.gui_gauge_size = wx.Size(self.gui_size.width - 20, self.gui_size.height - 40)

        self.pnl = wx.Panel(self)
        self.pnl.SetBackgroundColour("CADET BLUE")
        self.static_text = wx.StaticText(self.pnl, -1,
                                         "C: N/A (A)  V: N/A (V)  P: N/A (W)".center(50),
                                         pos=(-1,10),
                                         style=wx.ALIGN_CENTRE)
        self.meter_gauge = MeterGauge(self.pnl, wx.ID_ANY, pos=(10, 30), size=self.gui_gauge_size)
        self.SetSize(self.gui_size)
        self.pnl.SetSize(self.gui_size)

        event_list = {
            wx.EVT_LEFT_DOWN: self.on_mouse_left_down,
            wx.EVT_MOTION: self.on_mouse_motion,
            wx.EVT_LEFT_UP: self.on_mouse_left_up,
            wx.EVT_RIGHT_UP: self.on_right_up
        }

        gui_list = [self.pnl, self.static_text, self.meter_gauge]
        for _each_gui in gui_list:
            for _message, _callback in event_list.items():
                _each_gui.Bind(_message, _callback)

        wx.CallAfter(self.Refresh)

    def on_mouse_left_down(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0,0))
        self.pnl.CaptureMouse()

    def on_mouse_motion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            d_pos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            n_pos = (self.wPos.x + (d_pos.x - self.ldPos.x),
                    self.wPos.y + (d_pos.y - self.ldPos.y))
            self.Move(n_pos)

    def on_mouse_left_up(self, _):
        if self.pnl.HasCapture():
            self.pnl.ReleaseMouse()

    def on_right_up(self, _):
        self.Show(False)
        wx.CallAfter(self.Destroy)
        self.parent.testing = False
        wx.CallAfter(self.parent.Close, True)
