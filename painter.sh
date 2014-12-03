#!/bin/bash

# @Filename: fetcher.sh
# @Version: 1.0
# @Created_at: 2014-11-26
# @Description: This script can help you check the vpc network topology on AWS
#
# Environment Variables
BASE_DIR=$(pwd)
VPC_DIR=$BASE_DIR/vpc
JSON_DIR=$BASE_DIR/json
ICON_DIR=$BASE_DIR/icons

# Establish directories if not found
[ -d $VPC_DIR ] && rm -rf $VPC_DIR/* || mkdir -p $VPC_DIR
[ -d $JSON_DIR ] && rm -rf $JSON_DIR/* || mkdir -p $JSON_DIR

echo "Step 1: Generating feed items for Amazon Resources, please wait..."

for region in 'ap-northeast-1' 'ap-southeast-1'; do
    # get describes about all EC2 instances
    aws ec2 describe-instances --region $region > ${VPC_DIR}/instances_${region}.json
    aws ec2 describe-vpcs --region $region > ${VPC_DIR}/vpcs_${region}.json
    aws ec2 describe-subnets --region $region > ${VPC_DIR}/subnets_${region}.json
    aws ec2 describe-availability-zones --region $region > ${VPC_DIR}/availablity_zones_${region}.json
done

echo "Step 2:Transforming svg files into png files, please wait..."
if [[ -d $ICON_DIR ]]; then
    /bin/ls $ICON_DIR/*.svg | while read svg_file
    do
        png_file = `echo $svg_file | sed 's/\.svg/\.png/'`
        inkspace -zT -e "$png_file" -f "$svg_file"
    done
fi

echo "Step 3:Generating dot documents from feed items, please wait..."
python $BASE_DIR/json2dot.py

sleep 1

read -p "Do you want to describe the dot document by a graph now ? [y/n]:" res
if [[ $res == 'y' || $res == 'Y' || $res == 'yes' || $res == "YES" ]]; then
    dot -Tpng -o vpc.png vpc.dot
fi

read -p "Do you want to clean up history files? [y/n]:" cln
if [[ $cln == 'y' || $cln == 'Y' || $cln == 'yes' || $cln == "YES" ]]; then
    rm -rf $VPC_DIR
    rm -rf $JSON_DIR
fi
echo "Finished!"
