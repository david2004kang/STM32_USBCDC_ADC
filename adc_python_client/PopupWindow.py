import wx



class PopupWindow(wx.PopupWindow):
    """Adds a bit of text and mouse movement to the wx.PopupWindow"""
    ldPos = None
    wPos = None
    def __init__(self, parent, style):
        wx.PopupWindow.__init__(self, parent, style)
        self.parent = parent
        pnl = self.pnl = wx.Panel(self)
        pnl.SetBackgroundColour("CADET BLUE")
        self.static_text = wx.StaticText(pnl, -1, "charging current: 0 mA", pos=(10,10))
        sz = self.static_text.GetBestSize()
        self.SetSize((sz.width + 20, sz.height + 20))
        pnl.SetSize((sz.width + 20, sz.height + 20))

        pnl.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        pnl.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        pnl.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        pnl.Bind(wx.EVT_RIGHT_UP, self.on_right_up)

        self.static_text.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left_down)
        self.static_text.Bind(wx.EVT_MOTION, self.on_mouse_motion)
        self.static_text.Bind(wx.EVT_LEFT_UP, self.on_mouse_left_up)
        self.static_text.Bind(wx.EVT_RIGHT_UP, self.on_right_up)

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

    def on_mouse_left_up(self, evt):
        if self.pnl.HasCapture():
            self.pnl.ReleaseMouse()

    def on_right_up(self, evt):
        self.Show(False)
        wx.CallAfter(self.Destroy)
        self.parent.testing = False
        wx.CallAfter(self.parent.Close, True)
