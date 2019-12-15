from collections import defaultdict

from blackbox_recorder.recorder import Recorder

recorders = defaultdict(Recorder)


def get_recorder(name: str) -> Recorder:
    return recorders[name]


def del_recorder(name: str) -> None:
    del recorders[name]
