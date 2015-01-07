#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'danster'


def usage():
    print '''Usage:

    bash painter.sh <subcommand> [options]

Subcommands:
    routes             Paint the topology about network route tables of aws vpc
    subnets            Paint the topology about subnets of aws vpc
    instances          paint the topology about all instances in aws vpc

Options:
    -t, --tree         Output the result as a tree photo
    -m, --map          Output the result as a map photo,
                       -m and -t cannot appear at the same time

    -o file, --outfile=file  Write output to 'file'
    -h, --help         Show this message
    -v, --version      Print the name and version
    '''

