import sys
import fluidsynth
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSignal
from source_code.ui.sequence_ui import Ui_sequence_creator_window
from source_code.classes.QtNoteClasses import SeqButton


class PatternEdit(QWidget, Ui_sequence_creator_window):
    # Сигнал о том что можно взять последовательность
    return_sequence = pyqtSignal()

    def __init__(self, fs, on, off, channel=0, tracktime=0):
        super().__init__()
        self.COLUMNS = 40
        self.NOTES = 96
        self.on = on
        self.off = off
        self.fs = fs
        self.seq = fluidsynth.Sequencer(use_system_timer=False)
        self.synthID = self.seq.register_fluidsynth(fs)
        self.ticktime = 50
        self.tracktime = tracktime
        self.channel = channel
        self.sequence = []
        self.tracktime = []
        self.setupUI()

    def setupUI(self):
        super().setupUi(self)
        self.tableWidget.setColumnCount(self.COLUMNS)
        self.tableWidget.setRowCount(self.NOTES)

        self.play_sequence.clicked.connect(self.record_seq)
        self.add_sequence.clicked.connect(lambda: self.return_sequence.emit())

        for i in range(self.NOTES):
            for j in range(self.COLUMNS):
                self.tableWidget.setCellWidget(i, j, SeqButton(self.on, self.off))

    def record_seq(self, record_state=False):
        """Для проигрывания последовательности"""
        self.sequence.clear()
        for i in range(self.NOTES):
            for j in range(self.COLUMNS):
                if self.tableWidget.cellWidget(i, j).isChecked():
                    self.sequence.append([self.ticktime * j, i + 1])
        if not record_state:
            self.play_seq()

    def play_seq(self):
        """Загрузка в секвенцер который принадлежит именно этому окну"""
        for i in range(len(self.sequence)):
            self.seq.note(time=self.sequence[i][0], duration=200, absolute=False, channel=self.channel,
                          key=self.sequence[i][1], velocity=127, dest=self.synthID)
        self.seq.process(0)

    def get_seq(self):
        """Возврат созданного паттерна"""
        self.record_seq(True)
        return self.sequence


if __name__ == '__main__':
    #########################################
    SEQ_ON = "source_code/icons/seq_on.png"
    SEQ_OFF = "source_code/icons/seq_off.png"
    ##############################################
    fs = fluidsynth.Synth()
    fs.start()
    sfid = fs.sfload("example.sf2")
    fs.program_select(0, sfid, 0, 0)
    ##############################################
    app = QApplication(sys.argv)
    ex = PatternEdit(fs, SEQ_ON, SEQ_OFF)
    ex.show()
    sys.exit(app.exec_())
