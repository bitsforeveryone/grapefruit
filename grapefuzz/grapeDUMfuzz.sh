#!/bin/bash

if [ $# -eq 0 ]; then
	echo "so many A's to stdin and command line"
	echo "Usage: $0 [bin dir]"
	echo "Use absolute paths"
else

	cd $1
	
	for f in *; do
		echo $f
		python -c "print 'A'*4097" | timeout 1 ./$f &>/dev/null
		timeout 1 ./$f $(python -c "print 'A'*4097") &>/dev/null
	done
fi
