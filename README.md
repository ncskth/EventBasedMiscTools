This repository provides tools to parse, convert and analyze recordings from event-based cameras by IniVation, Prophesee and Celepixel.

## Pre-requisites

```sh
$ sudo add-apt-repository ppa:inivation-ppa/inivation
$ sudo apt-get update
$ sudo apt-get install dv-runtime-dev
```
## Tools

### Parsing

The [parser](https://github.com/ncskth/EventBasedMiscTools/blob/main/parsing/parser.py) is a generator that decodes data from files using one of the following formats:  *.raw, *.aedat4 or *.bin (mipi) files. It can be used in a loop, like in [parse_n.py](https://github.com/ncskth/EventBasedMiscTools/blob/main/parsing/parse_n.py):

```sh
$ python3 parse_n.py -i <filename>.<format> -n <nb_of_events>
```
### Conversion

The converters generate a *.csv file from files in one of the following formats: *.raw, *.aedat4 or *.bin (mipi) files.

```sh
$ python3 <format>2csv.py -i <filename>.<format> -o <filename>.csv
```
### Analysis

So far, the analysis consists on counting events in 100ms bins and generating a histogram with the occurrences.

```sh
$ python3 analyze_csv.py -i <filename>.csv
``` 
