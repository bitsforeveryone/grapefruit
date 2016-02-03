#!/bin/bash

FILE=$1
DB='db.db'

if [ -z $FILE ]; then
	FILE="data/*.pcap*"
fi

mkdir -p $(pwd)"/data/conversations/"$ROUND
mkdir -p $(pwd)"/data/done"

for file in $FILE
do
	sqlite3 $DB "INSERT INTO rounds VALUES (NULL);"
	ROUND=$(sqlite3 $DB "SELECT MAX(num) FROM rounds;")
	echo "[+] Processing $file as round $ROUND"
	tcpflow -o data/conversations/$ROUND -T %T_%C_%a-%b_%A-%B -r $file
	echo "[+] $file processed"
	python pushround.py data/conversations/$ROUND/report.xml
	mv $file "data/done/."
	echo "[+] Round $ROUND databased"
done
