#!/usr/bin/env python3
"""
Cek bahwa netlist hasil KiCad sama persis dengan EXPECTED_NETS di generate_schematic.py.

Jalankan:  python3 verify_netlist.py
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_schematic import EXPECTED_NETS, HERE, PROJECT, parse, find  # noqa: E402


def export_netlist():
    sch = os.path.join(HERE, f"{PROJECT}.kicad_sch")
    out = os.path.join(tempfile.mkdtemp(), "net.net")
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", out, sch],
                   check=True, capture_output=True)
    tree = parse(open(out, encoding="utf-8").read())
    nets = {}
    for net in find(tree, "nets")[1:]:
        name = str(find(net, "name")[1])
        nodes = frozenset((str(find(n, "ref")[1]), str(find(n, "pin")[1]))
                          for n in net if isinstance(n, list) and n[0] == "node")
        nets[name] = nodes
    return nets


def main():
    got = export_netlist()
    got_groups = {nodes: name for name, nodes in got.items() if len(nodes) > 1}
    exp_groups = {frozenset(v): k for k, v in EXPECTED_NETS.items()}
    ok = True
    for nodes, name in exp_groups.items():
        if nodes not in got_groups:
            ok = False
            print(f"[SALAH] net {name} yang diharapkan tidak ditemukan utuh: {sorted(nodes)}")
            for gnodes, gname in got_groups.items():
                if gnodes & nodes:
                    print(f"        bertumpang dengan net KiCad {gname}: {sorted(gnodes)}")
    for nodes, name in got_groups.items():
        if nodes not in exp_groups:
            ok = False
            print(f"[EKSTRA] net KiCad {name} tidak ada di rancangan: {sorted(nodes)}")
    named = sum(1 for n in exp_groups if n in got_groups)
    print(f"net multi-pin: rancangan {len(exp_groups)}, KiCad {len(got_groups)}, cocok {named}")
    print("HASIL:", "NETLIST COCOK 100%" if ok else "ADA PERBEDAAN")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
