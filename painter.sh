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
GRAPH_DIR=$BASE_DIR/graph

# Establish directories if not found
[ -d $VPC_DIR ] && rm -rf $VPC_DIR/* || mkdir -p $VPC_DIR
[ -d $JSON_DIR ] && rm -rf $JSON_DIR/* || mkdir -p $JSON_DIR
[ -d $GRAPH_DIR ] && rm -rf $GRAPH_DIR/* || mkdir -p $GRAPH_DIR

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
        png_file=`echo $svg_file | sed 's/\.svg/\.png/'`
        inkscape -zT -e "$png_file" -f "$svg_file" > /dev/null
    done
fi

echo "Step 3:Generating dot documents from feed items, please wait..."
python $BASE_DIR/json2dot.py "$*"

sleep 1

printf "\nNow, some folders were created when painting the vpc. \n\n"
printf "vpc/ : the json-formatted files contain info about AWS VPC which fetched AWS through the AWS command line interface.\n"
printf "json/ : the json-formatted files contain processed info from the vpc folder.\n"
printf "graph/ : the png-formatted photoes generated by pydot through gotted data about AWS VPC.\n\n"


read -p "Do you want to clean up history files? [y/n]:" cln
if [[ $cln == 'y' || $cln == 'Y' || $cln == 'yes' || $cln == "YES" ]]; then
    rm -rf $VPC_DIR
    rm -rf $JSON_DIR
    rm -rf $GRAPH_DIR
fi
echo "Finished!"
