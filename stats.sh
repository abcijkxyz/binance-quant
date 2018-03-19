#!/bin/bash
date
netstat -apn|grep 9443
sellamount=`grep "FILLED SELL $2" $1 |wc -l`
echo "SELL Orders:" $sellamount
buyamount=`grep "FILLED BUY $2" $1 |wc -l`
echo "BUY Orders:" $buyamount

echo "price drift:" `expr $sellamount - $buyamount`
