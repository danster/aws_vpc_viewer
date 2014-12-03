#!/bin/bash

# @Filename: script.sh
# @Version: 1.0
# @Created_at: 2014-10-29
# @Description: This script can help you generate Excel-Formatted reports and
#               then upload to S3(s3://tmap-cassowary/reports/) automatically.
#

# Environment Variables
BASE_DIR=$(pwd)
EC2_DIR=$BASE_DIR/ec2
ELB_DIR=$BASE_DIR/elb
RDS_DIR=$BASE_DIR/rds
S3_DIR=$BASE_DIR/s3

# Establish directories if not found
[ -d $EC2_DIR ] && rm -rf $EC2_DIR/* || mkdir -p $EC2_DIR
[ -d $ELB_DIR ] && rm -rf $ELB_DIR/* || mkdir -p $ELB_DIR
[ -d $RDS_DIR ] && rm -rf $RDS_DIR/* || mkdir -p $RDS_DIR
[ -d $S3_DIR ] && rm -rf $S3_DIR/* || mkdir -p $S3_DIR

echo "Step 1: Generating feed items for Amazon Resources, please wait..."

for region in 'ap-northeast-1' 'ap-southeast-1'; do
    # get describes about all EC2 instances
    aws ec2 describe-instances --region $region > ${EC2_DIR}/ec2_${region}.json
    aws ec2 describe-volumes --region $region > ${EC2_DIR}/vol_${region}.json

    # get describes about all Load Balancers
    LoadBalancers=$(aws elb describe-load-balancers --region $region)
    echo "$LoadBalancers" > ${ELB_DIR}/elb_${region}.json

    aws elb describe-tags --load-balancer-names $(echo "$LoadBalancers" |grep LoadBalancerName| awk -F\" '{print $4}'| xargs)  --region $region > ${ELB_DIR}/tags_${region}.json

    # get describes about all rds Instances
    RDSInstances=$(aws rds describe-db-instances --region $region)
    echo "$RDSInstances" > ${RDS_DIR}/rds_${region}.json

    DBInstanceIdentifiers=$(echo "$RDSInstances" |grep "\"DBInstanceIdentifier\"" |awk -F\" '{print $4}' |xargs)

    for DBInstance in $DBInstanceIdentifiers; do
        aws rds list-tags-for-resource --resource-name arn:aws:rds:$region:889515947644:db:$DBInstance --region $region > ${RDS_DIR}/tags_${region}_${DBInstance}.json
    done

    # get s3 lists
    S3Buckets=$(aws s3api list-buckets)
    echo "$S3Buckets" > ${S3_DIR}/buckets.json

    BucketsName=$(echo "$S3Buckets" |grep "\"Name\"" |awk -F\" '{print $4}')

    for bucket in $BucketsName; do
        aws s3api get-bucket-tagging --bucket $bucket > ${S3_DIR}/tags_${bucket}.json
        aws s3api get-bucket-location --bucket $bucket > ${S3_DIR}/loc_${bucket}.json
        aws s3api get-bucket-logging --bucket $bucket > ${S3_DIR}/log_${bucket}.json
        aws s3api get-bucket-versioning --bucket $bucket > ${S3_DIR}/ver_${bucket}.json
    done
done

echo "Step 2:Exporting items to Excel, please wait..."
python $BASE_DIR/json2xlsx.py

sleep 1

# read -p "Do you want to upload reports to S3 right now? [y/n]:" res
# if [[ $res == 'y' || $res == 'Y' || $res == 'yes' || $res == "YES" ]]; then
#     echo "Step 3: Uploading... ..."
#     aws s3 sync $BASE_DIR s3://tmap-cassowary/reports/ --exclude "*" --include "*.xlsx"
# fi

read -p "Do you want to clean up history files? [y/n]:" cln
if [[ $cln == 'y' || $cln == 'Y' || $cln == 'yes' || $cln == "YES" ]]; then
    rm -rf $EC2_DIR
    rm -rf $ELB_DIR
    rm -rf $RDS_DIR
    rm -rf $S3_DIR
fi
echo "Finished!"

