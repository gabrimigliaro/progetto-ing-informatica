from dataclasses import dataclass

@dataclass
class InDataLogin:    # pid 0
    pid: int
    apName: str
    mac: str

@dataclass
class InData:           # pid 10
    pid: int
    apName: str
    uid: int
    bpm: int
    battery: int
    steps: int
    emergency: int
    fall: int
    rssi: int

@dataclass
class InUpdateData:     # pid 2
    pid: int
    apName: str
    uid: int


@dataclass
class OutDataLogin:     # pid 1
    pid: int
    mac: str
    uid: int

    def toLine(self):
        return f"{self.pid},{self.mac},{self.uid}"

@dataclass
class OutUpdateData:    # pid 3
    pid: int
    uid: int
    updateAvailable: int

    def toLine(self):
        return f"{self.pid},{self.uid},{self.updateAvailable}"