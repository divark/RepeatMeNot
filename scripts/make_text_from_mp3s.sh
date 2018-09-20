#!/bin/bash

autosub_call() {
    echo "Working on $1"
    autosub "$1"
}

for i in *.mp3; do
	SRTCHECK=`echo "$i" | cut -f 1 -d '.'`
    if [[ ! -f $i ]] ; then break ; fi
    if [[ -f $i.srt ]] ; then break; fi
    autosub_call "$i" &
	sleep 5
done

wait
if [[ ! -d textfiles/ ]]; then mkdir textfiles; fi

for j in *.srt; do
    if [[ ! -f $j ]] ; then break; fi

    mv $i textfiles/
done
