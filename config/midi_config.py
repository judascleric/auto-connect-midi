#! /usr/bin/env python3
"""
midi_config: cli tool to manage the auto-connect-midi configuration
"""

from dataclasses import dataclass, field
import json
import os
import subprocess
import sys
from typing import List

from alsa_midi import SequencerClient
from dataclasses_json import dataclass_json
from simple_term_menu import TerminalMenu

IGNORE_PORT_NAMES = ["Midi Through"]
DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/auto-connect-midi.json")

@dataclass_json
@dataclass
class Device:
    name: str = ""
    port_id: int = 0

@dataclass_json
@dataclass
class Connection:
    input: Device
    output: Device

@dataclass_json
@dataclass
class Config:
    connections: List[Connection] = field(default_factory=list)


def main():
    config_path=os.environ.get("ACM_CONFIG_PATH", DEFAULT_CONFIG_PATH)

    client = SequencerClient("auto-connect-midi-config")
    options=[
        "Add Connection",
        "Show Config",
        "Clear Config",
        "Connect Now",
        "Done",
    ]
    terminal_menu = TerminalMenu(options, title="auto-connect-midi Configuration")
    while True:
        menu_entry_index = terminal_menu.show()
        if menu_entry_index == 0:
            add_connection(client, config_path)
        elif menu_entry_index == 1:
            show_config(config_path)
        elif menu_entry_index == 2:
            clear_config(config_path)
        elif menu_entry_index == 3:
            connect(config_path)
        else:
            sys.exit(0)


# pylint: disable=too-many-locals
def add_connection(client, config_path):
    in_ports = [port for port in client.list_ports(input=True) if port.name not in IGNORE_PORT_NAMES]
    in_names = [port.name for port in in_ports] + ["Cancel"]
    in_conn_menu = TerminalMenu(in_names, title="Select an input device")
    selected_in_id = in_conn_menu.show()
    if selected_in_id >= len(in_ports):
        return

    out_ports = [port for port in client.list_ports(output=True) if port.name not in IGNORE_PORT_NAMES]
    out_names = [port.name for port in out_ports] + ["Cancel"]
    out_conn_menu = TerminalMenu(out_names, title="Select an output device")
    selected_out_id = out_conn_menu.show()
    if selected_out_id >= len(out_ports):
        return

    config_dir = os.path.dirname(os.path.realpath(config_path))
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)

    in_port = in_ports[selected_in_id]
    in_dev = Device(name=in_port.name, port_id=in_port.port_id)
    out_port = out_ports[selected_out_id]
    out_dev = Device(name=out_port.name, port_id=out_port.port_id)
    connection = Connection(input=in_dev, output=out_dev)

    if os.path.exists(config_path):
        with open(config_path) as f:
            old_config = json.load(f)
        connections = old_config.connections + [connection]
    else:
        connections = [connection]

    config = Config(connections=connections)
    with open(config_path, "w") as f:
        json.dump(config.to_dict(), f, indent="  ")

    print(f"Added connection {in_dev} -> {out_dev} to {config_path}")


def show_config(config_path):
    if os.path.exists(config_path):
        with open(config_path) as f:
            print(f.read())
    else:
        print("{}")


def clear_config(config_path):
    if os.path.exists(config_path):
        print(f"Removing {config_path}")
        os.remove(config_path)


def connect(config_path):
    if not os.path.exists(config_path):
        print(f"Config file not found at {config_path}")
    with open(config_path) as f:
        config_json = f.read()
    config = Config.from_json(config_json)
    for conn in config.connections:
        cmd = ["aconnect", f"{conn.input.port_id}:0", f"{conn.output.port_id}:0"]
        print(" ".join(cmd))
        subprocess.run(["aconnect", f"{conn.input.port_id}:0", f"{conn.output.port_id}:0"])


if __name__ == "__main__":
    main()
