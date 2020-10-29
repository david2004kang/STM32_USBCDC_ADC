# -*- encoding: utf-8 -*-
import wx
import logging
import ThreadPool
import FrameMain


__VERSION__ = "1.0.0 (2020/10/28)"
__APP_NAME__ = "ADC test program Ver:{}".format(__VERSION__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s (%(name)s): %(message)s")

if __name__ == "__main__":
    _thread_pool = ThreadPool.ThreadPool()
    try:
        app = wx.App()
        logging.debug("ready to run FrameMain.FrameMain()")
        frame = FrameMain.FrameMain( None, _thread_pool, size=(20, 20))

        frame.Show(True)
        app.MainLoop()
    except Exception as _E:
        logging.exception(_E)
    finally:
        _thread_pool.stop_all()
