#!/bin/sh

$ROUND=$1

cd staging
tcpflow -o conversations/$ROUND -T %T_%C_%a-%b_%A-%B -l *.pcap*

cd ../conversations/$ROUND
xml2json --input report.xml --output report.json
