#!/bin/sh

ROUND=$1
FILE=$2
DIR=$(pwd)
_pushround=$DIR/pushround.py

if [ -z $ROUND ]; then
	ROUND='0'
fi

if [ -z $FILE ]; then
	FILE=$DIR/"staging/*.pcap*"
fi

tcpflow -o $DIR/conversations/$ROUND -T %T_%C_%a-%b_%A-%B -l $FILE

$_pushround $DIR/conversations/$ROUND/"report.xml"
