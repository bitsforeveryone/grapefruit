#!/bin/bash

#apt-get install bfbtester

if [$# == 0]; then
	echo "Usage: $0 [bin dir]"
	echo "Use absolute paths"
fi

cd $1

for f in *; do
	bfbtester -a $f
done
