#!/bin/ksh

f1=${1}.sortednumbers
cat $1 | cut -d',' -f1 | sort > $f1

f2=${2}.sortednumbers
cat $2 | cut -d',' -f1 | sort > $f2

comm=${1}_${2}.comm
comm -12 $f1 $f2 > $comm

rm $f1 $f2

grep -f $comm $1