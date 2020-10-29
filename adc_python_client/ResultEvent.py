import wx


class ResultEvent(wx.PyEvent):
    def __init__(self, event, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(event)
        self.data = data