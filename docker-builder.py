import os
import docker
import argparse
import sys
import json

CONFIG_FILE = None
DOCKERFILE = None

parser = argparse.ArgumentParser(prog='docker-builder',description='Helps to build and push docker images')
parser.add_argument('--file',help='Path to docker file',required=True)
parser.add_argument('--config',help='Path to configuration file',required=True)


def readConfig(configFile):
    '''
        Reads the configuration file to build image.
    '''
    return None


def checkFileExists(file):
    '''
        Checks if the file passed exists on the system or not.
    '''
    if not os.path.exists(file):
        raise FileNotFoundError
    else:
        return file


def main():
    '''
        Program starts here.
    '''
    arguments = parser.parse_args()
    try:
        CONFIG_FILE = checkFileExists(arguments.file)
    except FileNotFoundError:
        print(f'Dockerfile not found at {arguments.file}')
        sys.exit(1)
    try:
        DOCKERFILE =  checkFileExists(arguments.config)
    except FileNotFoundError:
        print(f'Dockerfile not found at {arguments.config}')
        sys.exit(1)


if __name__ == "__main__":
    main()