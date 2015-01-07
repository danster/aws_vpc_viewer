#!/usr/bin/python
# -*- coding: utf-8 -*-

#   Generating dot documents from json file
#   Author: Huangmaofeng
#   Date: 2015-01-07

import copy
import glob
import json
import os
import sys

BASE_DIR = os.path.split(os.path.realpath(__file__))[0]
VPC_DIR = os.path.join(BASE_DIR, "vpc")
JSON_DIR = os.path.join(BASE_DIR, "json")

REGIONS = ['ap-southeast-1','ap-northeast-1']

def fileCheck(_file):
    try:
        f = open(_file)
        return f
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)
        sys.exit()

def getInstances():
    print 'generating instance list data from json files fetched by aws api'
    instances = list()
    for region in REGIONS :
        _jsons = glob.glob(VPC_DIR+os.sep+"instances*"+region+"*")
        for js in _jsons:
            _file = fileCheck(js)
            _dict = json.load(_file)
            for info in _dict["Reservations"] :
                for instance in info["Instances"]:
                    it = copy.deepcopy(instance)
                    it['ReservationId'] = info['ReservationId']
                    it['Region'] = region
                    instances.append(it)
            _file.close()

    # print 'dumping instance to json file ... '
    # with open(JSON_DIR+os.sep+'instances','w') as _file:
    #     json.dump(instances, _file, indent = 4, separators=(',', ': '))
    # print 'dumping instance to json file end. '

    return instances


def getNetworks():
    print 'generating subnets, vpcs and zones data from json files fetched by aws api '
    subnets = list()
    vpcs = list()
    zones = list()
    for region in REGIONS :
        _jsons = glob.glob(VPC_DIR+os.sep+"subnets*"+region+"*")
        for js in _jsons:
            _file = fileCheck(js)
            _dict = json.load(_file)
            for subnet in _dict["Subnets"] :
                subnet['Region'] = region
                subnets.append(copy.deepcopy(subnet))
            _file.close()

        _jsons = glob.glob(VPC_DIR+os.sep+"vpcs*"+region+"*")
        for js in _jsons:
            _file = fileCheck(js)
            _dict = json.load( fileCheck(js) )
            for vpc in _dict["Vpcs"] :
                vpc['Region'] = region
                vpcs.append(copy.deepcopy(vpc))
            _file.close()

        _jsons = glob.glob(VPC_DIR+os.sep+"availablity_zones*"+region+"*")
        for js in _jsons:
            _file = fileCheck(js)
            _dict = json.load( fileCheck(js) )
            for zone in _dict["AvailabilityZones"] :
                zone['Region'] = region
                zones.append(copy.deepcopy(zone))
            _file.close()

    # print 'dumping datum of subnets, vpcs, zones to json file ... '
    # with open(JSON_DIR+os.sep+'subnets','w') as _file:
    #     json.dump(subnets, _file, indent = 4, separators=(',', ': '))
    # with open(JSON_DIR+os.sep+'vpcs','w') as _file:
    #     json.dump(vpcs, _file, indent = 4, separators=(',', ': '))
    # with open(JSON_DIR+os.sep+'zones','w') as _file:
    #     json.dump(zones, _file, indent = 4, separators=(',', ': '))
    # print 'dumping is end. '

    return subnets, vpcs, zones