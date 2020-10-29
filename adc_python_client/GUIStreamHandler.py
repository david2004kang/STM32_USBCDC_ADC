import wx
import logging
from ResultEvent import ResultEvent

#########################################################################################################
class GUIStreamHandler(logging.StreamHandler):
    def __init__(self, gui, emit_event):
        logging.StreamHandler.__init__(self)
        self.gui = gui
        self.emit_event = emit_event
        self._start = False

    def start(self, _start=True):
        self._start = _start

    def emit(self, record):
        if self._start:
            # msg = self.format(record)
            if record.msg.strip() == "":
                return
            _msg = record.msg.strip() + "\n"

            wx.PostEvent(self.gui,
                ResultEvent(
                    self.emit_event,
                    f'{record.asctime.split(" ")[-1]}: {record.msg}'
                ))

            if record.exc_text:
                wx.PostEvent(self.gui,
                    ResultEvent(
                        self.emit_events,
                        record.exc_text
                    )
                )
