#!/bin/bash

#install afl, build qemu mode, export AFL_PATH=...

if [ $# -eq 0 ]; then
    echo "Usage: $0 [path to dir of bins] [input corpus dir] [timeout (s)]"
    echo "Use absolute paths"
else
    bins=$1
    indir=$2
    tout=$3
    cd $bins
    mkdir -p out

    for f in *; do
        #echo $f
        if [[ -x $f ]] && [[ -f $f ]]; then
            oStdin=out/$f/out_stdin
            oFile=out/$f/out_file
            
            cd out
            mkdir -p $f
            cd $f
            mkdir -p out_stdin
            mkdir -p out_file
	    cd $bins
	    timeout $tout afl-fuzz -Q -d -i $indir -o $oStdin ./$f @@
            timeout $tout afl-fuzz -Q -d -i $indir -o $oFile ./$f
        fi
    done
fi
