# snapshot-analyzer
Demo project to analyze AWS EC2 snapshots

## About

This project is a demo, and uses boto3 to manage AWS EC2 instance snapshots.

## Configuring

shotty uses the configuration file creaetd by the AWS cli. e.g.

`aws configure --profile shotty`

## Running

`pipenv run "python shotty/shotty.py <command> <--project=PROJECT>"`

*command* is list, start, or stop
*project* is optional
