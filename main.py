import sys
import fluidsynth

from source_code.ui.main_daw import Ui_MainWindow

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QColor

from sampled_synth import SampledSynth
from patternedit import PatternEdit

from source_code.classes.QtNoteClasses import SeqButton


class MiLiveWindow(Ui_MainWindow, QMainWindow):

    def __init__(self, fs_synth, seq, note_on, note_off, note_sml_on, note_sml_off, seq_on, seq_off):
        super().__init__()
        ##############################################
        self.fs = fs_synth
        self.sequencer = seq
        self.synthSeqID = seq.register_fluidsynth(fs_synth)
        ##############################################
        self.img_path1 = note_on
        self.img_path2 = note_off
        self.note_sml_on = note_sml_on
        self.note_sml_off = note_sml_off
        self.seq_off = seq_off
        self.seq_on = seq_on
        ##############################################
        self.delta_blue = 0
        ##############################################
        self.patterns = []
        self.sequences = []
        ##############################################
        self.setupUI()
        ##############################################

    def setupUI(self):
        super().setupUi(self)
        self.openSynth.clicked.connect(self.open_synth_settings)
        self.add_pattern_btn.clicked.connect(self.create_sequence)
        self.delete_ptrn_btn.clicked.connect(self.remove_sequence)
        for i in range(16):
            for j in range(50):
                self.sequencer_table.setCellWidget(i, j, SeqButton(self.seq_on, self.seq_off))
                self.sequencer_table.cellWidget(i, j).toggled.connect(self.sequence_edit)
        self.play_seq_button.clicked.connect(self.prepare_seq)

    def sequence_edit(self):
        """Метод для создания последовательности из ранее созданных паттернов"""
        i = self.sequencer_table.currentRow()
        j = self.sequencer_table.currentColumn()
        if self.sequencer_table.cellWidget(i, j).isChecked():
            if self.patternView.currentRow() >= 0:
                self.sequencer_table.cellWidget(i, j).index_pattern_set(self.patternView.currentRow())
            else:
                self.statusbar.showMessage(f"Ошибка: не выбрана последовательность", 1000)
                self.sequencer_table.cellWidget(i, j).toggle()

    def create_sequence(self, add_flag):
        """Рекурсивный метод для создания последовательности"""
        if not add_flag:
            self.sequencer_widget = PatternEdit(self.fs, self.seq_on, self.seq_off, self.channel.value() - 1)
            self.sequencer_widget.show()
            self.sequencer_widget.return_sequence.connect(lambda: self.create_sequence(True))
        else:
            self.patterns.append(self.sequencer_widget.get_seq())
            self.patternView.addItem(f"Последовательность №{len(self.patterns)}")
            self.patternView.item(len(self.patterns) - 1).setBackground(QColor(150, 150, abs(250 - self.delta_blue)))
            self.delta_blue += 10

    def remove_sequence(self):
        """Удаление паттерна из списка (при удалении паттерна в последовательности все смещается)"""
        self.patternView.clear()
        try:
            del self.patterns[self.patternView.currentRow()]
            self.statusbar.showMessage(f'Успешно удалено', 2000)
        except Exception as e:
            self.statusbar.showMessage(f"Ошибка при удалении паттерна '{e}'", 2000)
        for i in range(len(self.patterns)):
            self.patternView.addItem(f"Паттерн №{i + 1}")
            self.patternView.item(i).setBackground(QColor(150, 150, abs((250 - self.delta_blue) % 250)))
            self.delta_blue += 10

    def prepare_seq(self):
        """Подготовка последоваетльности перед отправкой секвенцеру FS'а"""
        for i in range(16):
            for j in range(50):
                if self.sequencer_table.cellWidget(i, j).isChecked():
                    try:
                        print(self.sequencer_table.cellWidget(i, j).return_pattern())
                        self.sequences.append(
                            [self.patterns[self.sequencer_table.cellWidget(i, j).return_pattern()], 2000 * j, i])
                    except Exception as e:
                        self.statusbar.showMessage(f"Пустая последовательность '{e}'", 2000)
                        break

        if len(self.sequences) > 0:
            self.statusbar.showMessage(f'Последовательность длинной {len(self.sequences)} подготовлена', 2000)
            self.play_seq()

    def play_seq(self):
        """Проигрывание самой последовательности
        TODO Доабвить возможность играть с какого либо момента времени"""
        for part in self.sequences:
            sequence = part[0]
            abs_time = part[1]
            channel = part[2]
            for sequence_tick in sequence:
                time = sequence_tick[0]
                note = sequence_tick[1]
                self.sequencer.note(time=time + abs_time, duration=150, absolute=False,
                                    channel=channel,
                                    key=note, velocity=127, dest=self.synthSeqID)
        self.sequencer.process(0)
        self.sequences.clear()

    def open_synth_settings(self):
        """Открытие настроек синтезатора"""
        self.synth = SampledSynth(self.fs, self.img_path1, self.img_path2, self.note_sml_on, self.note_sml_off,
                                  self.channel.value() - 1)
        self.synth.show()


if __name__ == '__main__':
    ##############################################
    NOTE_BUTTON_IMG1 = "source_code/icons/on_l.png"
    NOTE_BUTTON_IMG2 = "source_code/icons/off_l.png"
    NOTE_SMALL_ON = "source_code/icons/note_small_on.png"
    NOTE_SMALL_OFF = "source_code/icons/note_small_off.png"
    SEQ_ON = "source_code/icons/seq_v2_on.png"
    SEQ_OFF = "source_code/icons/seq_v2_off.png"
    ##############################################
    fs = fluidsynth.Synth(gain=0.5)
    fs.start()
    seq = fluidsynth.Sequencer(use_system_timer=False)
    ##############################################
    app = QApplication(sys.argv)
    window = MiLiveWindow(fs, seq, NOTE_BUTTON_IMG1, NOTE_BUTTON_IMG2, NOTE_SMALL_ON, NOTE_SMALL_OFF, SEQ_ON, SEQ_OFF)
    window.show()
    sys.exit(app.exec_())
