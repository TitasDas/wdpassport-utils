#!/usr/bin/env python
#
# Sujay Phadke, 2015
# email: electronicsguy123@gmail.com
# github: https://github.com/electronicsguy/
#
# Based on the original design by:
# funkypopcorn (https://github.com/funkypopcorn)
#
# Improvements in this fork:
# 1. UI refresh and usability tweaks
# 2. Safer subprocess usage and password handling
# 3. Better drive/utility checks with clearer errors

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSlot
from distutils.spawn import find_executable
import os
import re
import subprocess
import sys
import tempfile

# Store the partition name in this variable
PARTNAME = ''

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKPW_PATH = os.path.join(SCRIPT_DIR, 'cookpw.py')

SCSI_UNLOCK_CMD = [
    'c1', 'e1', '00', '00', '00', '00', '00', '00', '28', '00'
]


def _run_cmd(args, check=False):
    """Run command and return stdout as text (Python 2/3 safe enough here)."""
    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    out, err = proc.communicate()
    if check and proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, args, output=out + err)
    return out.strip(), err.strip(), proc.returncode


def _is_executable_available(binary):
    return find_executable(binary) is not None


class MessageBoxDemo(QtGui.QWidget):
    def __init__(self, title, msg):
        QtGui.QWidget.__init__(self)
        QtGui.QMessageBox.information(self, title, msg)


class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName('Frame')
        Frame.resize(640, 520)
        Frame.setFrameShape(QtGui.QFrame.StyledPanel)
        Frame.setFrameShadow(QtGui.QFrame.Raised)
        Frame.setStyleSheet('''
            QFrame { background-color: #f4f7fb; }
            QLabel#titleLabel { color: #0f2a56; }
            QLabel#header1Label { color: #33507d; }
            QLineEdit {
                border: 1px solid #9fb2ce;
                border-radius: 6px;
                padding: 6px;
                background: #ffffff;
            }
            QTextEdit {
                border: 1px solid #9fb2ce;
                border-radius: 6px;
                background: #ffffff;
            }
            QPushButton {
                background-color: #214e8a;
                color: #ffffff;
                border: 0;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:disabled {
                background-color: #9aa7ba;
            }
            QCheckBox { color: #1f3556; }
        ''')

        myTitleFont = QtGui.QFont()
        myTitleFont.setFamily('Waree')
        myTitleFont.setPointSize(18)
        myTitleFont.setBold(True)

        myHeaderFont = QtGui.QFont()
        myHeaderFont.setFamily('Times')
        myHeaderFont.setPointSize(12)
        myHeaderFont.setBold(True)
        myHeaderFont.setItalic(True)

        self.titleLabel = QtGui.QLabel(Frame)
        self.titleLabel.setGeometry(QtCore.QRect(50, 24, 540, 32))
        self.titleLabel.setFont(myTitleFont)
        self.titleLabel.setObjectName('titleLabel')

        self.header1Label = QtGui.QLabel(Frame)
        self.header1Label.setGeometry(QtCore.QRect(50, 58, 540, 28))
        self.header1Label.setFont(myHeaderFont)
        self.header1Label.setObjectName('header1Label')

        self.pwLabel = QtGui.QLabel(Frame)
        self.pwLabel.setGeometry(QtCore.QRect(52, 118, 85, 24))
        self.pwLabel.setObjectName('pwLabel')

        self.pwBox = QtGui.QLineEdit(Frame)
        self.pwBox.setGeometry(QtCore.QRect(140, 114, 420, 34))
        self.pwBox.setObjectName('pwBox')
        self.pwBox.setEchoMode(QtGui.QLineEdit.Password)
        self.pwBox.setPlaceholderText('Enter password to unlock WD drive')

        self.showPwCheck = QtGui.QCheckBox(Frame)
        self.showPwCheck.setGeometry(QtCore.QRect(140, 152, 180, 24))
        self.showPwCheck.setObjectName('showPwCheck')
        self.showPwCheck.stateChanged.connect(self.togglePasswordVisibility)

        self.decryptBtn = QtGui.QPushButton(Frame)
        self.decryptBtn.setGeometry(QtCore.QRect(40, 192, 160, 50))
        self.decryptBtn.setObjectName('decryptBtn')
        self.decryptBtn.clicked.connect(self.decryptWD)

        self.mountBtn = QtGui.QPushButton(Frame)
        self.mountBtn.setEnabled(False)
        self.mountBtn.setGeometry(QtCore.QRect(220, 192, 160, 50))
        self.mountBtn.setObjectName('mountBtn')
        self.mountBtn.clicked.connect(self.mountWD)

        self.exitBtn = QtGui.QPushButton(Frame)
        self.exitBtn.setGeometry(QtCore.QRect(400, 192, 160, 50))
        self.exitBtn.setObjectName('exitBtn')
        self.exitBtn.clicked.connect(Frame.close)

        self.messageLabel = QtGui.QLabel(Frame)
        self.messageLabel.setGeometry(QtCore.QRect(40, 260, 180, 24))
        self.messageLabel.setObjectName('messageLabel')

        self.clearLogBtn = QtGui.QPushButton(Frame)
        self.clearLogBtn.setGeometry(QtCore.QRect(470, 258, 90, 28))
        self.clearLogBtn.setObjectName('clearLogBtn')
        self.clearLogBtn.clicked.connect(self.clearLogs)

        self.messageBox = QtGui.QTextEdit(Frame)
        self.messageBox.setGeometry(QtCore.QRect(40, 292, 520, 160))
        self.messageBox.setObjectName('messageBox')
        self.messageBox.setReadOnly(True)

        self.disclaimerBtn = QtGui.QPushButton('Disclaimer', Frame)
        self.disclaimerBtn.setGeometry(40, 466, 100, 34)
        self.disclaimerBtn.clicked.connect(self.showDisclaimer)

        self.retranslateUi(Frame)
        self.checkWDdrive()

        QtCore.QObject.connect(self.pwBox, QtCore.SIGNAL('textChanged(QString)'), self.pwBox_text_changed)
        QtCore.QObject.connect(self.pwBox, QtCore.SIGNAL('returnPressed()'), self.pwBox_check_text)
        self.pwBox.setFocus()
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        Frame.setWindowTitle('WD-Security')
        self.decryptBtn.setText('Unlock Drive')
        self.decryptBtn.setEnabled(False)
        self.pwLabel.setText('Password:')
        self.messageLabel.setText('Status / Error Log:')
        self.titleLabel.setText('WD Security for Linux')
        self.header1Label.setText('Unofficial unlock helper')
        self.exitBtn.setText('Exit')
        self.mountBtn.setText('Mount Drive')
        self.disclaimerBtn.setText('Disclaimer')
        self.clearLogBtn.setText('Clear')
        self.showPwCheck.setText('Show password')

    def appendLog(self, msg):
        self.messageBox.append(msg)

    @pyqtSlot(int)
    def togglePasswordVisibility(self, state):
        if state == QtCore.Qt.Checked:
            self.pwBox.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.pwBox.setEchoMode(QtGui.QLineEdit.Password)

    @pyqtSlot()
    def clearLogs(self):
        self.messageBox.clear()

    @pyqtSlot(str)
    def pwBox_text_changed(self, text):
        self.decryptBtn.setEnabled(bool(text))

    @pyqtSlot(str)
    def pwBox_check_text(self):
        if self.pwBox.text().length() > 0:
            self.decryptWD()
        else:
            self.pwBox.setFocus()

    def checkWDdrive(self):
        out, _, _ = _run_cmd(['lsusb'])
        wd_usb_lines = []
        for line in out.splitlines():
            if 'western digital' in line.lower():
                wd_usb_lines.append(line)

        if not wd_usb_lines:
            self.appendLog('No Western Digital drive attached.')
            self.appendLog('Please attach a compatible drive and restart.')
            self.pwBox.setEnabled(False)
            return

        for line in wd_usb_lines:
            self.appendLog('Western Digital drive found at: ' + line)

        lsblk_out, _, _ = _run_cmd(['lsblk'])
        if 'wd unlocker' not in lsblk_out.lower():
            self.appendLog("Either the drive is not locked or doesn't support WD security.")
            self.appendLog('If you believe this is false, reconnect the disk and try again.')
            self.pwBox.setEnabled(False)
            return

        self.appendLog('Checking drive lock status...')
        self.checkUnlockStatus()

    def checkUnlockStatus(self):
        global PARTNAME

        num_lines = self.getPartname()
        if num_lines == 0:
            self.appendLog('Error locating WD drive. Please reconnect and try again.')
        elif num_lines == 1:
            self.appendLog('Drive appears to be locked.')
        else:
            self.appendLog('Drive appears to be already unlocked.')
            self.pwBox.setEnabled(False)
            self.appendLog('Drive device name: ' + PARTNAME)
            self.checkMountStatus()

    def getPartname(self):
        global PARTNAME

        disk_by_id = '/dev/disk/by-id'
        if not os.path.isdir(disk_by_id):
            PARTNAME = ''
            return 0

        partnames = []
        for entry in os.listdir(disk_by_id):
            if 'usb-WD' not in entry:
                continue
            full = os.path.join(disk_by_id, entry)
            if not os.path.islink(full):
                continue
            try:
                target = os.path.realpath(full)
            except OSError:
                continue
            base = os.path.basename(target)
            if re.match(r'^sd[a-z]+$', base):
                partnames.append(base)

        # Stable order for deterministic behavior.
        partnames = sorted(set(partnames))
        if partnames:
            PARTNAME = partnames[0]
        else:
            PARTNAME = ''

        return len(partnames)

    def checkMountStatus(self):
        self.mountBtn.setEnabled(True)

    def decryptWD(self):
        self.callCookingPW()

    def _create_password_blob(self, pw):
        """Generate password payload with cookpw and write it to a secure temp file."""
        fd, path = tempfile.mkstemp(prefix='wdpass_', dir=SCRIPT_DIR)
        os.close(fd)
        os.chmod(path, 0o600)

        proc = subprocess.Popen(
            [sys.executable, COOKPW_PATH, '--stdin'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = proc.communicate(pw)
        if proc.returncode != 0:
            try:
                os.unlink(path)
            except OSError:
                pass
            raise RuntimeError(err.strip() or 'cookpw.py failed')

        handle = open(path, 'wb')
        try:
            handle.write(out)
        finally:
            handle.close()

        return path

    def callCookingPW(self):
        self.appendLog('Preparing password payload...')
        app.processEvents()

        pw = str(self.pwBox.text())
        self.pwBox.clear()

        if not pw:
            self.appendLog('Password cannot be empty.')
            return

        try:
            payload_path = self._create_password_blob(pw)
        except Exception as exc:
            self.appendLog('Cannot prepare password payload: {0}'.format(exc))
            return

        self.appendLog('Sending SCSI commands to unlock the drive...')
        self.unlockDrive(payload_path)

    def _find_sg_devices(self):
        out, _, rc = _run_cmd(['/bin/dmesg'])
        if rc != 0:
            return []

        devices = []
        for line in out.splitlines():
            if 'type 13' not in line:
                continue
            match = re.search(r'\b(sg\d+)\b', line)
            if match:
                devices.append(match.group(1))
        return sorted(set(devices))

    def unlockDrive(self, payload_path):
        try:
            sg_devices = self._find_sg_devices()
            if not sg_devices:
                self.appendLog("Failure: couldn't find an sg 'type 13' device within dmesg.")
                return

            if len(sg_devices) > 1:
                self.appendLog("Multiple SCSI 'type 13' devices recognized.")
                self.appendLog('Please unplug everything except the desired drive and retry.')
                return

            sg_dev = sg_devices[0]
            self.appendLog('Secure hard drive identified at /dev/' + sg_dev)

            cmd = ['sg_raw', '-s', '40', '-i', payload_path, '/dev/' + sg_dev] + SCSI_UNLOCK_CMD
            try:
                _run_cmd(cmd, check=True)
                self.appendLog('The WD drive is now unlocked and can be mounted!')
            except subprocess.CalledProcessError:
                self.appendLog('Failure while sending SCSI decrypt command. Check password and connections.')
                return

            # Drive unlock successful. Try automounting partitions.
            self.pwBox.setEnabled(False)
            self.decryptBtn.setEnabled(False)
            self.mountWD()
        finally:
            try:
                os.unlink(payload_path)
            except OSError:
                pass

    def mountWD(self):
        global PARTNAME

        self.getPartname()
        if not PARTNAME:
            self.appendLog('Cannot determine drive device name. Please mount manually.')
            return

        _run_cmd(['partprobe'])
        self.appendLog('Available devices have been updated.')

        # Keep legacy behavior: attempt to mount partition 1.
        devname = '/dev/' + PARTNAME + '1'
        self.appendLog('Mounting device: ' + devname)
        _, _, mount_rc = _run_cmd(['udisksctl', 'mount', '-b', devname])

        if mount_rc == 0:
            self.appendLog('WD hard drive decrypted and mounted successfully!')
        else:
            self.appendLog('Drive decrypted, but automount failed. Please mount manually.')

        self.appendLog('In some cases partitions may not mount automatically.')
        self.appendLog('If needed, mount them manually using "mount".')
        self.mountBtn.setEnabled(False)

    def showDisclaimer(self):
        MessageBoxDemo(
            'Disclaimer',
            'This utility enables temporary unlock for modern WD drives that support '
            'hardware-level link encryption.\nIt does not support permanent unlock '
            '(removing security) or initial locking.\n\nThis utility is not '
            'officially licensed by Western Digital. Western Digital Security is a '
            'registered trademark of Western Digital.\n\nThis utility has only been '
            'tested with one WD locked drive attached.\nPlease do not connect more '
            'than one locked USB drive.'
        )


def prompt_sudo():
    if os.geteuid() != 0:
        print >> sys.stderr, "This program requires root permissions. Please try again by prefixing 'sudo'."
        sys.exit(1)


def CheckRequiredUtils():
    required_bins = ['sg_raw', 'partprobe', 'lsusb', 'lsblk', 'udisksctl']
    missing = []
    for binary in required_bins:
        if not _is_executable_available(binary):
            missing.append(binary)

    if missing:
        print "Missing required system tools: {0}".format(', '.join(missing))
        print "Please install the required packages and retry."
        sys.exit(1)


if __name__ == '__main__':
    # ref: http://pyqt.sourceforge.net/Docs/PyQt4/qapplication.html
    global app
    app = QtGui.QApplication(sys.argv)
    hFrame = QtGui.QFrame()
    hWin = Ui_Frame()
    hWin.setupUi(hFrame)

    prompt_sudo()
    CheckRequiredUtils()
    hFrame.show()
    status = app.exec_()   # run app, show window, wait for input
    sys.exit(status)       # terminate program with a status code returned from app
