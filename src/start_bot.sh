#!/bin/bash

while true; do

    scrapy crawl get_correio24horas && 
echo "" &&
scrapy crawl get_correiobraziliense && 
echo "" &&
scrapy crawl get_estadao &&
echo "" &&
scrapy crawl get_folhasp &&
echo "" &&
scrapy crawl get_oglobo2 &&
echo "" &&
scrapy crawl get_g1 && wait

done



