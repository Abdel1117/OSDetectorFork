import platform
import os
import subprocess


def obtenir_sys_info():
    os_info = platform.uname()
    type_systeme = os_info.system
    node_name = os_info.node
    release = os_info.release
    version = os_info.version
    machine = os_info.machine
    processor = os_info.processor

    system_info = {
        "System Type": type_systeme,
        "Node Name": node_name,
        "Release": release,
        "Version": version,
        "Machine": machine,
        "Processor": processor,
    }

    return system_info


def get_windows_hardware_info():
    try:
        cpu_info = (
            subprocess.check_output("wmic cpu get name", shell=True)
            .decode()
            .strip()
            .split("\n")[1]
            .strip()
        )
        mem_info = (
            subprocess.check_output("wmic memorychip get capacity", shell=True)
            .decode()
            .strip()
            .split("\n")[1:]
        )
        total_memory = sum(int(mem.strip()) for mem in mem_info) / (
            1024**3
        )  # Convert bytes to GB
    except Exception as e:
        cpu_info = "Impossible d'obtenir les informations CPU"
        total_memory = "Impossible d'obtenir les informations Mémoire vive"

    return {"CPU": cpu_info, "Total Memory (GB)": total_memory}


def get_linux_hardware_info():
    try:
        cpu_info = (
            subprocess.check_output("lscpu | grep 'Model name'", shell=True)
            .decode()
            .strip()
            .split(":")[1]
            .strip()
        )
        mem_info = (
            subprocess.check_output("grep MemTotal /proc/meminfo", shell=True)
            .decode()
            .strip()
            .split(":")[1]
            .strip()
        )
        total_memory = int(mem_info.split()[0]) / 1024 / 1024  # Convert kB to GB
    except Exception as e:
        cpu_info = "Impossible d'obtenir les informations CPU"
        total_memory = "Impossible d'obtenir les informations Mémoire vive"

    return {"CPU": cpu_info, "Total Memory (GB)": total_memory}


def main():
    system_info = obtenir_sys_info()
    type_systeme = system_info["System Type"]

    if type_systeme == "Windows":
        hardware_info = get_windows_hardware_info()
    elif type_systeme == "Linux":
        hardware_info = get_linux_hardware_info()
    else:
        print(f"Type de Systèmes non-supporté: {type_systeme}")
        return

    print("Informations Systèmes:")
    for key, value in system_info.items():
        print(f"{key}: {value}")

    print("\nInformations Matérielles:")
    for key, value in hardware_info.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
