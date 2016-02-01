#!/bin/sh

ROUND=$1
FILE=$2

_pushround = $(which pushround.py)

cd staging
tcpflow -o conversations/$ROUND -T %T_%C_%a-%b_%A-%B -l *.pcap*

cd ../conversations/$ROUND
$_pushround report.xml
