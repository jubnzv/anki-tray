import os
import socket
import threading
import time

from anki.hooks import addHook
from aqt.qt import *
from aqt import *


class TrayIconManager(QSystemTrayIcon):
    sock_path = '/tmp/anki_tray.sock'
    show_signal = pyqtSignal()

    def __init__(self):
        super(TrayIconManager, self).__init__(mw)
        self._setup_ui()
        self._connect_slots()
        self._other_variables()
        self.close_from_x = True
        #  self.show_signal.connect(self._show_window_all)
        self.show_signal.connect(self.capture_signal_handler)
        self._init_sock()

    def capture_signal_handler(self):
        #  if not self.is_mw_visible:
        #  self._show_window_all()
        if self.is_mw_visible:
            self._hide_window_all()
            try:
                self._show_window_all()
            except:
                pass
        res = aqt.dialogs.open("AddCards", mw)

    def __del__(self):
        self.running = False
        self.thread.join()
        try:
            os.unlink(self.sock_path)
        except:
            pass

    def _init_sock(self):
        try:
            os.unlink(self.sock_path)
        except OSError:
            if os.path.exists(self.sock_path):
                raise

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.sock_path)
        self.sock.listen(1)
        self.running = True
        self.thread = threading.Thread(target=self.listen, args=[]).start()

    def listen(self):
        while self.running:
            conn, addr = self.sock.accept()
            try:
                self.show_signal.emit()
                time.sleep(1)
            finally:
                conn.close()

    def _other_variables(self):
        mw.tray_hidden = []
        self.is_mw_visible = True

    def _setup_icon(self):
        anki_logo = QIcon()
        anki_logo.addPixmap(QPixmap(":/icons/anki.png"),
                            QIcon.Normal, QIcon.Off)
        self.setIcon(anki_logo)

    def _setup_context_menu(self):
        tray_menu = QMenu(mw)
        self.setContextMenu(tray_menu)
        tray_menu.addAction(mw.form.actionExit)

    def _setup_ui(self):
        self._setup_icon()
        self._setup_context_menu()

    def _connect_slots(self):
        mw.closeEvent = self._mw_close_event
        mw.form.actionExit.triggered.disconnect()
        mw.form.actionExit.triggered.connect(self._on_quit_triggered)
        self.activated.connect(self.on_activated)
        mw.app.focusChanged.connect(self._focus_changed)

    def _on_quit_triggered(self):
        self.close_from_x = False
        mw.close()

    def _mw_close_event(self, event):
        """
        Triggers when user hits "X" button on the window
        :param event:
        :return:
        """
        if self.close_from_x:
            if self.is_mw_visible:
                event.ignore()
                self._hide_window_all()
            else:
                self._show_window_all()
        else:
            self.hide()
            if mw.state == "profileManager":
                # If profile manager active, this event may fire via OS X
                # menu bar's quit option
                mw.profileDiag.close()
                event.accept()
            else:
                # Ignore the event for now, as we need time to clean up
                event.ignore()
                mw.unloadProfileAndExit()

    def _focus_changed(self, old, now):
        if not now:
            mw.last_focus = old

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.is_mw_visible:
                self._hide_window_all()
            else:
                self._show_window_all()

    def _show_window_all(self):
        for w in mw.tray_hidden:
            w.showNormal()
        active = mw.last_focus
        active.raise_()
        active.activateWindow()
        self.is_mw_visible = True
        mw.tray_hidden = []

    def _hide_window_all(self):
        mw.tray_hidden = []
        for w in QApplication.topLevelWidgets():
            if w.isWindow() and not w.isHidden():
                if not w.children():
                    continue
                w.hide()
                mw.tray_hidden.append(w)
        self.is_mw_visible = False


def _create_sys_tray():
    if hasattr(mw, 'trayIcon'):
        return
    mw.last_focus = mw
    mw.trayIcon = TrayIconManager()
    mw.trayIcon.show()


addHook("profileLoaded", _create_sys_tray)
