#!/bin/bash

#apt-get install bfbtester

if [ $# -eq 0 ]; then
	echo "Usage: $0 [bin dir]"
	echo "Use absolute paths"
else
	cd $1

	for f in *; do
		bfbtester -a $f
	done
fi
