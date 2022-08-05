#!/bin/ksh

f1=${1}.sortednumbers
cat $1 | cut -d',' -f1 | sort > $f1

f2=${2}.sortednumbers
cat $2 | cut -d',' -f1 | sort > $f2

comm=${1}_${2}.comm
comm -12 $f1 $f2 > $comm

remove=`cat $comm`
grep -v "$remove" $1 > ${1}.withoutcommon
grep -v "$remove" $2 > ${2}.withoutcommon

grep -f $comm $1 
grep -f $comm $1 | wc -l

echo "Remove one of the files ${1}.withoutcommon or ${2}.withoutcommon as per your contact strategy"
wc -l $1 ${1}.withoutcommon $2 ${2}.withoutcommon

rm $f1 $f2 $comm
