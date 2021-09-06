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


def checkValidConfig(config):
    if 'name' not in config:
        raise AttributeError
    elif 'tag' not in config:
        raise AttributeError

def readConfig(configFile):
    '''
        Reads the configuration file to build image.
    '''
    try:
        with open(configFile) as f:
            config = f.read()
            config = json.loads(config)
        try:
            checkValidConfig(config)
        except AttributeError:
            print("Invalid configuration.\nPlease check documentation.")
            sys.exit(1)
        imageName = config['name']
        tag = config['tag']
        if 'deploy' in config:
            deploy = config['deploy']
        else:
            deploy = False
        return imageName,tag,deploy
    except Exception as e:
        print("Error")
        sys.exit(1)


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
        DOCKERFILE = checkFileExists(arguments.file)
    except FileNotFoundError:
        print(f'Dockerfile not found at {arguments.file}')
        sys.exit(1)
    try:
        CONFIG_FILE =  checkFileExists(arguments.config)
    except FileNotFoundError:
        print(f'Configuration not found at {arguments.config}')
        sys.exit(1)
    imageName,tag,deploy = readConfig(CONFIG_FILE)
    print(imageName,tag,deploy)

if __name__ == "__main__":
    main()