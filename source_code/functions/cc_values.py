"""Отедльный словарь с номермаи midi_cc"""
# Все значения для MSB (Most_significant_byte) - Грубые изменения
cc_dict_msb = {
    "modulation": 1,  #
    "breath": 2,  #
    "foot_ctrl": 4,  #
    "portamento_time": 5,  #
    "volume": 7,  #
    "balance": 8,
    "pan": 10,  #
    "exp": 11,  #
    "sustain": 64,  #
    "reverb": 91,  #
    "chorus": 93  #
}
# <63 - выкл, >64 - вкл
cc_dict_on_off = {
    "dmpr_pedal": 64,
    "portamento": 65,
    "sustenuto": 66,
    "soft_pedal": 67,
    "legato_footswich": 68,
    "hold_2": 69,  # Nice
}
# Незаюзал, в будующем мб че нибудь сделаю хз
cc_dict_lsb = {}
