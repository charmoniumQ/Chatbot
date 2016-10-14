#!/bin/bash

if [[ ! -e data/marx_cut.txt ]]
then
	curl http://www.gutenberg.org/files/46423/46423-0.txt -o data/marx.txt
	head -n 6910 data/marx.txt | tail -n +44 > data/marx_cut.txt
fi

python3 simple_markov.py data/marx_cut.txt
