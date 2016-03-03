#!/bin/bash

#This is a simple example of how to harness a fuzzer to fuzz a large number of binaries. 

if [ $# -eq 0 ]; then
	echo "Usage: $0 [bin dir]"
	echo "Use absolute paths"
else

	cd $1
	
	for f in *; do
		echo $f
		python -c "print 'A'*4097" | timeout .5 ./$f &>/dev/null
		timeout .5 ./$f $(python -c "print 'A'*4097") &>/dev/null
	done
fi
