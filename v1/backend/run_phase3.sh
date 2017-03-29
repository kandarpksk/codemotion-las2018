#!/bin/bash
for i in $(eval echo {$1..$2}); do
	echo
	echo processing ${i}
	time python phase3.py $i 2>../public/other/video${i}.json >>temp/temp
	echo -- $i >> temp/temp
done