#! /usr/bin/env python3
"""
midi_config: cli tool to manage the auto-connect-midi configuration
"""

import json
import os
import subprocess
import sys

from alsa_midi import SequencerClient
from simple_term_menu import TerminalMenu

from common.config import Config, Connection, Device, read_config, connect, DEFAULT_CONFIG_PATH

IGNORE_PORT_NAMES = ["Midi Through"]

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
    in_ports = [port for port in client.list_ports(input=True) if port.client_name not in IGNORE_PORT_NAMES]
    print(in_ports)
    in_names = [f"[{port.client_id}] {port.client_name}" for port in in_ports] + ["Cancel"]
    in_conn_menu = TerminalMenu(in_names, title="Select an input device")
    selected_in_id = in_conn_menu.show()
    if selected_in_id >= len(in_ports):
        return
    in_port = in_ports[selected_in_id]
    in_dev = Device(name=in_port.client_name, client_id=in_port.client_id)
    port_options = [f"Connect first device named {in_dev.name}", f"Only for port {in_dev.client_id}"]
    port_select = TerminalMenu(port_options, title="Match device name or use specific port?")
    port_select_id = port_select.show()
    if port_select_id == 0:
        in_dev.client_id = 0

    out_ports = [port for port in client.list_ports(output=True) if port.client_name not in IGNORE_PORT_NAMES]
    out_names = [f"[{port.client_id}] {port.client_name}" for port in out_ports] + ["Cancel"]
    out_conn_menu = TerminalMenu(out_names, title="Select an output device")
    selected_out_id = out_conn_menu.show()
    if selected_out_id >= len(out_ports):
        return
    out_port = out_ports[selected_out_id]
    out_dev = Device(name=out_port.client_name, client_id=out_port.client_id)
    port_options = [f"Connect first device named {out_dev.name}", f"Only for port {out_dev.client_id}"]
    port_select = TerminalMenu(port_options, title="Match device name or use specific port?")
    port_select_id = port_select.show()
    if port_select_id == 0:
        out_dev.client_id = 0

    config_dir = os.path.dirname(os.path.realpath(config_path))
    if not os.path.isdir(config_dir):
        os.makedirs(config_dir)

    connection = Connection(input=in_dev, output=out_dev)

    old_config = read_config(config_path)
    connections = old_config.connections + [connection]

    config = Config(connections=connections)
    with open(config_path, "w") as f:
        # pylint: disable=no-member
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


if __name__ == "__main__":
    main()
