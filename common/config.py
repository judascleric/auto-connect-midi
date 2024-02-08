"""
config - data structures and methods for reading and writing connect configs
"""
from dataclasses import dataclass, field
import os
import subprocess
import sys
from typing import List

from alsa_midi import SequencerClient
from dataclasses_json import dataclass_json


DEFAULT_CONFIG_PATH = os.path.expanduser("~/.config/auto-connect-midi.json")

@dataclass_json
@dataclass
class Device:
    name: str = ""
    client_id: int = 0

@dataclass_json
@dataclass
class Connection:
    input: Device
    output: Device

@dataclass_json
@dataclass
class Config:
    connections: List[Connection] = field(default_factory=list)


def read_config(config_path):
    if not os.path.exists(config_path):
        return Config()
    with open(config_path) as f:
        config_json = f.read()
    # pylint: disable=no-member
    config = Config.from_json(config_json)
    return config


def connect(config_path):
    config = read_config(config_path)
    client = SequencerClient("auto-connect-midi-common")
    for conn in config.connections:
        if conn.input.client_id == 0:
            in_port = get_in_port_by_name(conn.input.name, client)
        else:
            in_port = conn.input.client_id
        if conn.output.client_id == 0:
            out_port = get_out_port_by_name(conn.output.name, client)
        else:
            out_port = conn.outupt.client_id

        if in_port is None:
            print(f"Could not find input port for connection named: {conn.input.name}", file=sys.stderr)
            continue
        if out_port is None:
            print(f"Could not find output port for connection named: {conn.output.name}", file=sys.stderr)
            continue
        cmd = ["aconnect", f"{in_port}:0", f"{out_port}:0"]
        print(" ".join(cmd))
        subprocess.run(["aconnect", f"{in_port}:0", f"{out_port}:0"], check=False)


def get_port_by_name(client_name, is_input=False, client=None):
    if client is None:
        client = SequencerClient("auto-connect-midi-common")
    if is_input:
        ports = client.list_ports(input=True)
    else:
        ports = client.list_ports(output=True)
    for port in ports:
        if port.client_name == client_name:
            return port.client_id
    return None


def get_in_port_by_name(dev_name, client=None):
    return get_port_by_name(dev_name, True, client)


def get_out_port_by_name(dev_name, client=None):
    return get_port_by_name(dev_name, False, client)

