# grapefruit

This is a suite of tools written by a few members of BitsForEveryone for use in an Attack-Defend style CTF. It was written very quickly, and there are bugs; however, we believe it addresses the basic components needed to simplify Attack-Defense CTFs. There are 4 basic components and all function independently.

## Grapefruit IDS
A simple IDS designed with ctf in mind. Pcaps are parsed with tcpflow, and flows are databased with sqlite3 with an unobtrusive front-end written with Flask.

## Launcher
A CLI based throwing framework written in python for automating the scheduled throwing of exploits and network chaff for distraction.

## Persistence
An experimental script for maintaining persistence on a box in a way that is hard to observe in network traffic. Communications between the host and victim change ports regularly, almost like frequency-hopping radio communications.

## Grapefuzz
Starter scripts for common fuzzing frameworks

#### Neat-O One Liners
| Command            | Purpose |
| -------------      | ------------- |
| netstat -tulpn     | see what programs listen on what ports |
| fuser -k 31337/tcp | kill process binding on tcp port 31337 |
| for i in {x..y}; do kill -9 $i; done | kill range of processes (like if fuzzing gone badddd) |

#### NGINX URL Filtering 
http://www.cyberciti.biz/faq/nginx-block-url-access-all-except-one-ip-address/
