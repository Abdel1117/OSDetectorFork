# test_system_info.py
import platform
import subprocess
import pytest

# Importez les fonctions à tester depuis votre module.
# Ici, on suppose que votre code se trouve dans system_info.py.
from os_detector import (
    obtenir_sys_info,
    get_windows_hardware_info,
    get_linux_hardware_info,
    main,
)


##########################################
# Tests pour la fonction obtenir_sys_info
##########################################
def test_obtenir_sys_info(monkeypatch):
    # Création d'une classe factice pour simuler le résultat de platform.uname()
    class FakeUname:
        def __init__(self, system, node, release, version, machine, processor):
            self.system = system
            self.node = node
            self.release = release
            self.version = version
            self.machine = machine
            self.processor = processor

    fake_uname = FakeUname(
        "FakeOS",
        "FakeNode",
        "FakeRelease",
        "FakeVersion",
        "FakeMachine",
        "FakeProcessor",
    )
    monkeypatch.setattr(platform, "uname", lambda: fake_uname)

    info = obtenir_sys_info()
    assert info["System Type"] == "FakeOS"
    assert info["Node Name"] == "FakeNode"
    assert info["Release"] == "FakeRelease"
    assert info["Version"] == "FakeVersion"
    assert info["Machine"] == "FakeMachine"
    assert info["Processor"] == "FakeProcessor"


##########################################
# Tests pour get_windows_hardware_info
##########################################
def fake_check_output_windows(command, shell):
    if command.startswith("wmic cpu"):
        # Simulation de la sortie de "wmic cpu get name"
        return b"Name\nFake CPU"
    elif command.startswith("wmic memorychip"):
        # Simulation de la sortie de "wmic memorychip get capacity"
        # Deux barrettes de 1073741824 octets (1 Go chacune)
        return b"Capacity\n1073741824\n1073741824"
    else:
        raise ValueError("Commande inattendue dans le test Windows")


def test_get_windows_hardware_info(monkeypatch):
    monkeypatch.setattr(subprocess, "check_output", fake_check_output_windows)
    hardware_info = get_windows_hardware_info()
    assert hardware_info["CPU"] == "Fake CPU"
    # 1073741824 * 2 / (1024**3) = 2.0 Go
    assert hardware_info["Total Memory (GB)"] == 2.0


##########################################
# Tests pour get_linux_hardware_info
##########################################
def fake_check_output_linux(command, shell):
    if "lscpu" in command:
        # Simulation de la sortie de "lscpu | grep 'Model name'"
        return b"Model name: Fake CPU"
    elif "grep MemTotal" in command:
        # Simulation de la sortie de "grep MemTotal /proc/meminfo"
        # Par exemple, "MemTotal: 2097152 kB" qui correspond à 2.0 Go
        return b"MemTotal: 2097152 kB"
    else:
        raise ValueError("Commande inattendue dans le test Linux")


def test_get_linux_hardware_info(monkeypatch):
    monkeypatch.setattr(subprocess, "check_output", fake_check_output_linux)
    hardware_info = get_linux_hardware_info()
    assert hardware_info["CPU"] == "Fake CPU"
    # 2097152 kB / (1024*1024) = 2.0 Go
    assert hardware_info["Total Memory (GB)"] == 2.0


##########################################
# Tests pour la gestion des exceptions
##########################################
def fake_check_output_raise(command, shell):
    raise Exception("Commande échouée")


def test_get_windows_hardware_info_exception(monkeypatch):
    monkeypatch.setattr(subprocess, "check_output", fake_check_output_raise)
    hardware_info = get_windows_hardware_info()
    assert hardware_info["CPU"] == "Impossible d'obtenir les informations CPU"
    assert (
        hardware_info["Total Memory (GB)"]
        == "Impossible d'obtenir les informations Mémoire vive"
    )


def test_get_linux_hardware_info_exception(monkeypatch):
    monkeypatch.setattr(subprocess, "check_output", fake_check_output_raise)
    hardware_info = get_linux_hardware_info()
    assert hardware_info["CPU"] == "Impossible d'obtenir les informations CPU"
    assert (
        hardware_info["Total Memory (GB)"]
        == "Impossible d'obtenir les informations Mémoire vive"
    )


##########################################
# Tests pour la fonction main
##########################################
def test_main_windows(monkeypatch, capsys):
    # Création d'une fausse réponse pour platform.uname() indiquant un système Windows
    class FakeUname:
        def __init__(self, system, node, release, version, machine, processor):
            self.system = system
            self.node = node
            self.release = release
            self.version = version
            self.machine = machine
            self.processor = processor

    fake_uname = FakeUname(
        "Windows",
        "FakeWinNode",
        "WinRelease",
        "WinVersion",
        "WinMachine",
        "WinProcessor",
    )
    monkeypatch.setattr(platform, "uname", lambda: fake_uname)
    monkeypatch.setattr(subprocess, "check_output", fake_check_output_windows)

    # Exécution de main() et capture de la sortie
    main()
    captured = capsys.readouterr().out
    assert "Informations Systèmes:" in captured
    assert "System Type: Windows" in captured
    assert "Node Name: FakeWinNode" in captured
    assert "Informations Matérielles:" in captured
    assert "CPU: Fake CPU" in captured
    assert "Total Memory (GB): 2.0" in captured


def test_main_linux(monkeypatch, capsys):
    # Création d'une fausse réponse pour platform.uname() indiquant un système Linux
    class FakeUname:
        def __init__(self, system, node, release, version, machine, processor):
            self.system = system
            self.node = node
            self.release = release
            self.version = version
            self.machine = machine
            self.processor = processor

    fake_uname = FakeUname(
        "Linux",
        "FakeLinuxNode",
        "LinuxRelease",
        "LinuxVersion",
        "LinuxMachine",
        "LinuxProcessor",
    )
    monkeypatch.setattr(platform, "uname", lambda: fake_uname)
    monkeypatch.setattr(subprocess, "check_output", fake_check_output_linux)

    main()
    captured = capsys.readouterr().out
    assert "Informations Systèmes:" in captured
    assert "System Type: Linux" in captured
    assert "Node Name: FakeLinuxNode" in captured
    assert "Informations Matérielles:" in captured
    assert "CPU: Fake CPU" in captured
    assert "Total Memory (GB): 2.0" in captured
