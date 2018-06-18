#!/bin/bash
date
netstat -apn|grep 9443

function stats()
{
    sellamount=`grep "FILLED SELL $2" $1 |wc -l`
    echo "SELL Orders:" $sellamount
    buyamount=`grep "FILLED BUY $2" $1 |wc -l`
    echo "BUY Orders:" $buyamount
    echo "price drift:" `expr $sellamount - $buyamount`
}

FILE=$1
shift
while [ $# -gt  0 ]
do
    echo $1
    stats $FILE $1
    shift
done
