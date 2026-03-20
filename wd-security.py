#!/usr/bin/env python3
#
# WD Security unlock helper for Linux
# Modernized to Python3 + PyQt5.

import os
import re
import shutil
import subprocess
import sys
import tempfile

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
)

PARTNAME = ''
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COOKPW_PATH = os.path.join(SCRIPT_DIR, 'cookpw.py')
SCSI_UNLOCK_CMD = ['c1', 'e1', '00', '00', '00', '00', '00', '00', '28', '00']


def run_cmd(args, check=False):
    proc = subprocess.run(args, capture_output=True, text=True)
    out = (proc.stdout or '').strip()
    err = (proc.stderr or '').strip()
    if check and proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, args, output=out + err)
    return out, err, proc.returncode


def is_executable_available(binary):
    return shutil.which(binary) is not None


class WDSecurityWindow:
    def setup_ui(self, frame):
        frame.setObjectName('Frame')
        frame.resize(640, 520)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        frame.setStyleSheet('''
            QFrame { background-color: #f4f7fb; }
            QLabel#titleLabel { color: #0f2a56; }
            QLabel#headerLabel { color: #33507d; }
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

        title_font = QFont('Waree', 18)
        title_font.setBold(True)

        header_font = QFont('Times', 12)
        header_font.setBold(True)
        header_font.setItalic(True)

        self.title_label = QLabel(frame)
        self.title_label.setGeometry(50, 24, 540, 32)
        self.title_label.setFont(title_font)
        self.title_label.setObjectName('titleLabel')

        self.header_label = QLabel(frame)
        self.header_label.setGeometry(50, 58, 540, 28)
        self.header_label.setFont(header_font)
        self.header_label.setObjectName('headerLabel')

        self.pw_label = QLabel(frame)
        self.pw_label.setGeometry(52, 118, 85, 24)

        self.pw_box = QLineEdit(frame)
        self.pw_box.setGeometry(140, 114, 420, 34)
        self.pw_box.setEchoMode(QLineEdit.Password)
        self.pw_box.setPlaceholderText('Enter password to unlock WD drive')

        self.show_pw_check = QCheckBox(frame)
        self.show_pw_check.setGeometry(140, 152, 180, 24)
        self.show_pw_check.stateChanged.connect(self.toggle_password_visibility)

        self.decrypt_btn = QPushButton(frame)
        self.decrypt_btn.setGeometry(40, 192, 160, 50)
        self.decrypt_btn.clicked.connect(self.decrypt_wd)

        self.mount_btn = QPushButton(frame)
        self.mount_btn.setEnabled(False)
        self.mount_btn.setGeometry(220, 192, 160, 50)
        self.mount_btn.clicked.connect(self.mount_wd)

        self.exit_btn = QPushButton(frame)
        self.exit_btn.setGeometry(400, 192, 160, 50)
        self.exit_btn.clicked.connect(frame.close)

        self.message_label = QLabel(frame)
        self.message_label.setGeometry(40, 260, 180, 24)

        self.clear_log_btn = QPushButton(frame)
        self.clear_log_btn.setGeometry(470, 258, 90, 28)
        self.clear_log_btn.clicked.connect(self.clear_logs)

        self.message_box = QTextEdit(frame)
        self.message_box.setGeometry(40, 292, 520, 160)
        self.message_box.setReadOnly(True)

        self.disclaimer_btn = QPushButton('Disclaimer', frame)
        self.disclaimer_btn.setGeometry(40, 466, 100, 34)
        self.disclaimer_btn.clicked.connect(self.show_disclaimer)

        self.apply_texts(frame)

        self.pw_box.textChanged.connect(self.pw_box_text_changed)
        self.pw_box.returnPressed.connect(self.pw_box_check_text)
        self.pw_box.setFocus()

        self.check_wd_drive()

    def apply_texts(self, frame):
        frame.setWindowTitle('WD-Security')
        self.decrypt_btn.setText('Unlock Drive')
        self.decrypt_btn.setEnabled(False)
        self.pw_label.setText('Password:')
        self.message_label.setText('Status / Error Log:')
        self.title_label.setText('WD Security for Linux')
        self.header_label.setText('Unofficial unlock helper')
        self.exit_btn.setText('Exit')
        self.mount_btn.setText('Mount Drive')
        self.disclaimer_btn.setText('Disclaimer')
        self.clear_log_btn.setText('Clear')
        self.show_pw_check.setText('Show password')

    def append_log(self, msg):
        self.message_box.append(msg)

    @pyqtSlot(int)
    def toggle_password_visibility(self, state):
        mode = QLineEdit.Normal if state == Qt.Checked else QLineEdit.Password
        self.pw_box.setEchoMode(mode)

    @pyqtSlot()
    def clear_logs(self):
        self.message_box.clear()

    @pyqtSlot(str)
    def pw_box_text_changed(self, text):
        self.decrypt_btn.setEnabled(bool(text))

    @pyqtSlot()
    def pw_box_check_text(self):
        if self.pw_box.text():
            self.decrypt_wd()
        else:
            self.pw_box.setFocus()

    def check_wd_drive(self):
        out, _, _ = run_cmd(['lsusb'])
        wd_usb_lines = [line for line in out.splitlines() if 'western digital' in line.lower()]

        if not wd_usb_lines:
            self.append_log('No Western Digital drive attached.')
            self.append_log('Please attach a compatible drive and restart.')
            self.pw_box.setEnabled(False)
            return

        for line in wd_usb_lines:
            self.append_log('Western Digital drive found at: ' + line)

        lsblk_out, _, _ = run_cmd(['lsblk'])
        if 'wd unlocker' not in lsblk_out.lower():
            self.append_log("Either the drive is not locked or doesn't support WD security.")
            self.append_log('If this is wrong, reconnect the disk and try again.')
            self.pw_box.setEnabled(False)
            return

        self.append_log('Checking drive lock status...')
        self.check_unlock_status()

    def check_unlock_status(self):
        global PARTNAME

        num_lines = self.get_partname()
        if num_lines == 0:
            self.append_log('Error locating WD drive. Please reconnect and try again.')
        elif num_lines == 1:
            self.append_log('Drive appears to be locked.')
        else:
            self.append_log('Drive appears to be already unlocked.')
            self.pw_box.setEnabled(False)
            self.append_log('Drive device name: ' + PARTNAME)
            self.check_mount_status()

    def get_partname(self):
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

        partnames = sorted(set(partnames))
        PARTNAME = partnames[0] if partnames else ''
        return len(partnames)

    def check_mount_status(self):
        self.mount_btn.setEnabled(True)

    def decrypt_wd(self):
        self.call_cooking_pw()

    def create_password_blob(self, password):
        fd, path = tempfile.mkstemp(prefix='wdpass_', dir=SCRIPT_DIR)
        os.close(fd)
        os.chmod(path, 0o600)

        proc = subprocess.run(
            [sys.executable, COOKPW_PATH, '--stdin'],
            input=password.encode('utf-8'),
            capture_output=True
        )

        if proc.returncode != 0:
            try:
                os.unlink(path)
            except OSError:
                pass
            stderr_text = (proc.stderr or b'').decode('utf-8', errors='replace').strip()
            raise RuntimeError(stderr_text or 'cookpw.py failed')

        with open(path, 'wb') as handle:
            handle.write(proc.stdout)

        return path

    def call_cooking_pw(self):
        self.append_log('Preparing password payload...')
        QApplication.processEvents()

        password = self.pw_box.text()
        self.pw_box.clear()

        if not password:
            self.append_log('Password cannot be empty.')
            return

        try:
            payload_path = self.create_password_blob(password)
        except Exception as exc:
            self.append_log(f'Cannot prepare password payload: {exc}')
            return

        self.append_log('Sending SCSI commands to unlock the drive...')
        self.unlock_drive(payload_path)

    def find_sg_devices(self):
        out, _, rc = run_cmd(['/bin/dmesg'])
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

    def unlock_drive(self, payload_path):
        try:
            sg_devices = self.find_sg_devices()
            if not sg_devices:
                self.append_log("Failure: couldn't find an sg 'type 13' device in dmesg.")
                return

            if len(sg_devices) > 1:
                self.append_log("Multiple SCSI 'type 13' devices recognized.")
                self.append_log('Unplug other devices and retry.')
                return

            sg_dev = sg_devices[0]
            self.append_log('Secure hard drive identified at /dev/' + sg_dev)

            cmd = ['sg_raw', '-s', '40', '-i', payload_path, '/dev/' + sg_dev] + SCSI_UNLOCK_CMD
            try:
                run_cmd(cmd, check=True)
                self.append_log('The WD drive is now unlocked and can be mounted!')
            except subprocess.CalledProcessError:
                self.append_log('SCSI decrypt command failed. Check password and connections.')
                return

            self.pw_box.setEnabled(False)
            self.decrypt_btn.setEnabled(False)
            self.mount_wd()
        finally:
            try:
                os.unlink(payload_path)
            except OSError:
                pass

    def mount_wd(self):
        global PARTNAME

        self.get_partname()
        if not PARTNAME:
            self.append_log('Cannot determine drive device name. Please mount manually.')
            return

        run_cmd(['partprobe'])
        self.append_log('Available devices have been updated.')

        devname = '/dev/' + PARTNAME + '1'
        self.append_log('Mounting device: ' + devname)
        _, _, mount_rc = run_cmd(['udisksctl', 'mount', '-b', devname])

        if mount_rc == 0:
            self.append_log('WD hard drive decrypted and mounted successfully!')
        else:
            self.append_log('Drive decrypted, but automount failed. Please mount manually.')

        self.append_log('If needed, mount partitions manually using "mount".')
        self.mount_btn.setEnabled(False)

    def show_disclaimer(self):
        QMessageBox.information(
            None,
            'Disclaimer',
            'This utility enables temporary unlock for modern WD drives that support '
            'hardware-level link encryption.\nIt does not support permanent unlock '
            '(removing security) or initial locking.\n\nThis utility is not '
            'officially licensed by Western Digital.\n\nThis utility has only been '
            'tested with one WD locked drive attached.\nPlease do not connect more '
            'than one locked USB drive.'
        )


def prompt_sudo():
    if os.geteuid() != 0:
        print("This program requires root permissions. Please run with sudo or pkexec.", file=sys.stderr)
        sys.exit(1)


def check_required_utils():
    required_bins = ['sg_raw', 'partprobe', 'lsusb', 'lsblk', 'udisksctl']
    missing = [binary for binary in required_bins if not is_executable_available(binary)]
    if missing:
        print(f"Missing required system tools: {', '.join(missing)}")
        print('Please install the required packages and retry.')
        sys.exit(1)


if __name__ == '__main__':
    prompt_sudo()
    check_required_utils()

    app = QApplication(sys.argv)
    frame = QFrame()
    ui = WDSecurityWindow()
    ui.setup_ui(frame)
    frame.show()
    sys.exit(app.exec_())
