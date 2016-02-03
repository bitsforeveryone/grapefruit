# IDS
system to detect exploits in a PCAP and replay them on other targets

```bash
mv *.pcap grapefruit/ids/data
make all
./run.py
```

#### CTF Regexes
| Regex            | Purpose |
| -------------    | ------------- |
| ([0-9a-f]){32}    | 32 hex characters in sequence |
