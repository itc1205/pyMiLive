import sys

import fluidsynth
from PyQt5.Qt import *

from source_code.classes.QtNoteClasses import NoteButton
from source_code.functions.cc_values import cc_dict_msb
from source_code.functions.db_funcs import *
from source_code.ui.sampled_synth_ui import Ui_Sample_synth


##############################################

# Наш класс воспроизведения звука в реальном времени
# (Рабочий поток с воспроизведением звуковых данных из fluidsynth)
# class SoundThread(QObject):
#     def __init__(self, f_synth, stream):
#         super().__init__()
#         self.fs = f_synth
#         self.stream = stream
#
#     def run(self):
#         while True:
#             s = []
#             s = numpy.append(s, self.fs.get_samples(int(44100 * 0.1)))
#             samps = fluidsynth.raw_audio_string(s)
#             self.stream.write(samps)
#

class SampledSynth(QWidget, Ui_Sample_synth):
    def __init__(self, fs_synth, img_path1, img_path2, sml_note_on, sml_note_off, channel=0):
        super().__init__()

        # Создаем ссылки на наши классы, копируем нужные переменные и проверяем наличие базы данныхself.sml_note_on = sml_note_on
        self.sml_note_on = sml_note_on
        self.sml_note_off = sml_note_off
        self.fs = fs_synth
        self.img_path = img_path1
        self.img_path2 = img_path2
        self.channel = channel
        check_db_exists()
        # Создаем словарь с нумерацией кнопок по октавам
        self.octaves = {}
        for i in range(8):
            self.octaves[i + 1] = [(12 * i + j) for j in range(12)]

        # Собственно запускаем звуковой поток, наш интерфейс и подгружаем базы данных в интерфейс
        # self.fs.start()
        # self.sound_thread_start()
        self.setupUI()
        self.load_db()
        self.cur_octave = self.octave_spin_box.value()

    def setupUI(self):
        super().setupUi(self)
        # Создаем наши кнопки
        self.key1 = NoteButton(self.img_path, self.img_path2)
        self.key_sml1 = NoteButton(self.sml_note_on, self.sml_note_off)
        self.key2 = NoteButton(self.img_path, self.img_path2)
        self.key_sml2 = NoteButton(self.sml_note_on, self.sml_note_off)
        self.key3 = NoteButton(self.img_path, self.img_path2)
        self.key4 = NoteButton(self.img_path, self.img_path2)
        self.key_sml3 = NoteButton(self.sml_note_on, self.sml_note_off)
        self.key5 = NoteButton(self.img_path, self.img_path2)
        self.key_sml4 = NoteButton(self.sml_note_on, self.sml_note_off)
        self.key6 = NoteButton(self.img_path, self.img_path2)
        self.key_sml5 = NoteButton(self.sml_note_on, self.sml_note_off)
        self.key7 = NoteButton(self.img_path, self.img_path2)
        # Добавляем их в список, дабы легче добавить их в layout'ы
        self.first_keys = [self.key1, self.key_sml1, self.key2, self.key_sml2, self.key3]
        self.second_keys = [
            self.key4, self.key_sml3, self.key5, self.key_sml4, self.key6, self.key_sml5, self.key7
        ]
        # Соединяем кнопки к обработчику(к сожалению через цикл они теряют свои уникальные свойства)
        self.key1.pressed.connect(lambda: self.pressed(0))
        self.key_sml1.pressed.connect(lambda: self.pressed(1))
        self.key2.pressed.connect(lambda: self.pressed(2))
        self.key_sml2.pressed.connect(lambda: self.pressed(3))
        self.key3.pressed.connect(lambda: self.pressed(4))
        self.key4.pressed.connect(lambda: self.pressed(5))
        self.key_sml3.pressed.connect(lambda: self.pressed(6))
        self.key5.pressed.connect(lambda: self.pressed(7))
        self.key_sml4.pressed.connect(lambda: self.pressed(8))
        self.key6.pressed.connect(lambda: self.pressed(9))
        self.key_sml5.pressed.connect(lambda: self.pressed(10))
        self.key7.pressed.connect(lambda: self.pressed(11))

        self.key1.released.connect(lambda: self.released(0))
        self.key_sml1.released.connect(lambda: self.released(1))
        self.key2.released.connect(lambda: self.released(2))
        self.key_sml2.released.connect(lambda: self.released(3))
        self.key3.released.connect(lambda: self.released(4))
        self.key4.released.connect(lambda: self.released(5))
        self.key_sml3.released.connect(lambda: self.released(6))
        self.key5.released.connect(lambda: self.released(7))
        self.key_sml4.released.connect(lambda: self.released(8))
        self.key6.released.connect(lambda: self.released(9))
        self.key_sml5.released.connect(lambda: self.released(10))
        self.key7.released.connect(lambda: self.released(11))

        self.reverb_dial.sliderMoved.connect(lambda: self.control_change(cc_dict_msb["reverb"], self.reverb_dial))
        self.vibrato_dial.sliderMoved.connect(lambda: self.control_change(cc_dict_msb["modulation"], self.vibrato_dial))
        self.pan_dial.sliderMoved.connect(lambda: self.control_change(cc_dict_msb["pan"], self.pan_dial))
        self.expression_dial.sliderMoved.connect(lambda: self.control_change(cc_dict_msb["exp"], self.expression_dial))
        self.sustain_dial.sliderMoved.connect(lambda: self.control_change(cc_dict_msb["sustain"], self.sustain_dial))
        self.chorus_dial.sliderMoved.connect(lambda: self.control_change(cc_dict_msb["chorus"], self.chorus_dial))
        self.volume_dial.sliderMoved.connect(lambda: self.control_change(cc_dict_msb["volume"], self.volume_dial))

        self.bank_spinbox.valueChanged.connect(self.program_select)
        self.preset_spinbox.valueChanged.connect(self.program_select)

        self.add_to_db.clicked.connect(self.add_font_to_db)
        self.delete_from_db.clicked.connect(self.del_font_from_db)
        self.fonts_list.itemDoubleClicked.connect(self.set_font)

        self.octave_spin_box.valueChanged.connect(self.octave_change)

        for i in range(5):
            self.fitrst3noteslayout.addWidget(self.first_keys[i])

        for i in range(7):
            self.last4notes_layout.addWidget(self.second_keys[i])

    # def sound_thread_start(self):
    # Рабочий код, убрал изза того что не нужен(пока что)
    # Создаем поток который будет перенаправлять звук из fluidsynth'а в класс PyAudio
    #     self.thread = QThread()
    #     self.worker = SoundThread(self.fs, self.stream)
    #     self.worker.moveToThread(self.thread)
    #     self.thread.started.connect(self.worker.run)
    #     self.thread.start()

    def keyPressEvent(self, event):
        """Биндим кнопки на ноты"""
        if event.key() == Qt.Key_D and not event.isAutoRepeat():
            self.key1.setDown(True)
            self.pressed(0)

        if event.key() == Qt.Key_E and not event.isAutoRepeat():
            self.key_sml1.setDown(True)
            self.pressed(1)

        if event.key() == Qt.Key_F and not event.isAutoRepeat():
            self.key2.setDown(True)
            self.pressed(2)

        if event.key() == Qt.Key_R and not event.isAutoRepeat():
            self.key_sml2.setDown(True)
            self.pressed(3)

        if event.key() == Qt.Key_G and not event.isAutoRepeat():
            self.key3.setDown(True)
            self.pressed(4)

        if event.key() == Qt.Key_H and not event.isAutoRepeat():
            self.key4.setDown(True)
            self.pressed(5)

        if event.key() == Qt.Key_U and not event.isAutoRepeat():
            self.key_sml3.setDown(True)
            self.pressed(6)

        if event.key() == Qt.Key_J and not event.isAutoRepeat():
            self.key5.setDown(True)
            self.pressed(7)

        if event.key() == Qt.Key_I and not event.isAutoRepeat():
            self.key_sml4.setDown(True)
            self.pressed(8)

        if event.key() == Qt.Key_K and not event.isAutoRepeat():
            self.key6.setDown(True)
            self.pressed(9)

        if event.key() == Qt.Key_O and not event.isAutoRepeat():
            self.key_sml5.setDown(True)
            self.pressed(10)

        if event.key() == Qt.Key_L and not event.isAutoRepeat():
            self.key7.setDown(True)
            self.pressed(11)

    def keyReleaseEvent(self, event):
        """Тут тоже бинды ничего интересного"""
        if event.key() == Qt.Key_D and not event.isAutoRepeat():
            self.key1.setDown(False)
            self.released(0)

        if event.key() == Qt.Key_E and not event.isAutoRepeat():
            self.key_sml1.setDown(False)
            self.released(1)

        if event.key() == Qt.Key_F and not event.isAutoRepeat():
            self.key2.setDown(False)
            self.released(2)

        if event.key() == Qt.Key_R and not event.isAutoRepeat():
            self.key_sml2.setDown(False)
            self.released(3)

        if event.key() == Qt.Key_G and not event.isAutoRepeat():
            self.key3.setDown(False)
            self.released(4)

        if event.key() == Qt.Key_H and not event.isAutoRepeat():
            self.key4.setDown(False)
            self.released(5)

        if event.key() == Qt.Key_U and not event.isAutoRepeat():
            self.key_sml3.setDown(False)
            self.released(6)

        if event.key() == Qt.Key_J and not event.isAutoRepeat():
            self.key5.setDown(False)
            self.released(7)

        if event.key() == Qt.Key_I and not event.isAutoRepeat():
            self.key_sml4.setDown(False)
            self.released(8)

        if event.key() == Qt.Key_K and not event.isAutoRepeat():
            self.key6.setDown(False)
            self.released(9)

        if event.key() == Qt.Key_O and not event.isAutoRepeat():
            self.key_sml5.setDown(False)
            self.released(10)

        if event.key() == Qt.Key_L and not event.isAutoRepeat():
            self.key7.setDown(False)
            self.released(11)

    def control_change(self, cc_prog, dial):
        """Обработчик для cс сообщений"""
        self.fs.cc(self.channel, cc_prog, dial.value())

    def octave_change(self):
        """Обработчик изменения октавы"""
        self.cur_octave = self.octave_spin_box.value()

    def released(self, i):
        """Унивирсальный обработчик отпускания нот. Работает как и для клавиатуры так и для программных кнопок"""
        self.fs.noteoff(self.channel, self.octaves.get(self.cur_octave)[i])

    def pressed(self, i):
        """"Унивирсальный обработчик нажатия нот"""
        self.fs.noteon(self.channel, self.octaves.get(self.cur_octave)[i], 127)

    def load_db(self):
        """Метод загрузки базы данных с шрифтами в виде словаря"""
        self.fonts_list.clear()
        self.fonts_dict = get_items_from_fonts_db()
        self.fonts_list.addItems(self.fonts_dict.keys())

    def set_font(self):
        """Обработчик для загрузки музыкальных шрифтов с базы данных"""
        self.sfid = self.fs.sfload(self.fonts_dict[self.fonts_list.currentItem().text()])
        self.fs.program_select(self.channel, self.sfid, self.bank_spinbox.value(), self.preset_spinbox.value())

    def add_font_to_db(self):
        """Метод для загрузки шрифтов в базу данных и перекидывания их в папку с шрифтами"""
        path = QFileDialog.getOpenFileName(
            self, 'Выбрать музыкальный шрифт', '',
            'Soundfont2 (*.sf2);;Все файлы (*)')[0]
        write_into_database(path)
        self.load_db()

    def del_font_from_db(self):
        """Метод для удаления шрифтов из базы данных и последующего удаления из папки с шрифтами"""
        delete_from_db(self.fonts_dict[self.fonts_list.currentItem().text()])
        self.fs.sfunload()
        self.load_db()

    def program_select(self):
        try:
            self.fs.program_select(self.channel, self.sfid, self.bank_spinbox.value(), self.preset_spinbox.value())
        except:
            pass


if __name__ == '__main__':
    ##############################################
    NOTE_BUTTON_IMG1 = "source_code/icons/on_l.png"
    NOTE_BUTTON_IMG2 = "source_code/icons/off_l.png"
    NOTE_SMALL_ON = "source_code/icons/note_small_on.png"
    NOTE_SMALL_OFF = "source_code/icons/note_small_off.png"
    ##############################################
    fs = fluidsynth.Synth()
    ##############################################
    app = QApplication(sys.argv)
    ex = SampledSynth(fs, NOTE_BUTTON_IMG1, NOTE_BUTTON_IMG2, NOTE_SMALL_ON, NOTE_SMALL_OFF)
    ex.show()
    sys.exit(app.exec_())
