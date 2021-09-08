import os
import docker
import argparse
import sys
import json

CONFIG_FILE = None
DOCKERFILE = None
CLIENT = None

parser = argparse.ArgumentParser(prog='docker-builder',description='Helps to build and push docker images')
parser.add_argument('--file',help='Path to docker file',required=True)
parser.add_argument('--config',help='Path to configuration file',required=True)


def createDockerClient():
    '''
        Returns docker client object.
    '''
    try:
        return docker.from_env()
    except Exception as e:
        raise RuntimeError

def checkValidConfig(config):
    '''
        Checks if the config file is valid.
    '''
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
            deploy = None
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
        return os.path.abspath(file)


def dockerHubLogin():
    '''
        Helps to authenticate to docker hub.
    '''
    if 'HUB_USERNAME' in os.environ and 'HUB_PASS' in os.environ:
        try:
            CLIENT.login(username=os.environ['HUB_USERNAME'],password=os.environ['HUB_PASS'])
        except Exception as e:
            print(e.__cause__)
    else:
        raise AttributeError


def dockerCheck():
    '''
        Checks if docker is present in the environment.
    '''
    return None


def writeLogstoFile(logs,createdImage):
    '''
        Helps to write build logs to file.
    '''
    try:
        home_dir = os.path.expanduser("~")
        logs_dir = os.path.join(home_dir,".docker_builder_logs")
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        with open(f"{logs_dir}{os.path.sep}{createdImage}-logs",'w') as f:
            for line in logs:
                if 'stream' in line:
                    f.write(line['stream'])
        print(f"Successfully wrote build logs to {logs_dir}{os.path.sep}{createdImage}-logs")
    except Exception as e:
        print("Failed to write logs to file")


def buildImage(imageName,tagName):
    '''
        Helps to build the image.
    '''
    try:
        with open(DOCKERFILE,'rb') as f:
            try:
                result = CLIENT.images.build(
                    fileobj = f,
                    tag = f'{imageName}:{tagName}',
                    forcerm=True
                )
                writeLogstoFile(result[1],f'{imageName}-{tagName}')
                print(f"Successfully built image with ID: {result[0].id} and tags: {result[0].attrs['RepoTags']}") 
            except Exception as e:
                print('Failed to build image.')
                sys.exit(1)
    except Exception as e:
        print(f"Failed to not open dockerfile: {DOCKERFILE}")
        sys.exit(1)


def main():
    '''
        Program starts here.
    '''
    global CLIENT,DOCKERFILE,CONFIG_FILE
    arguments = parser.parse_args()
    try:
        CLIENT = createDockerClient()
    except RuntimeError:
        print('Docker is not running or not installed')
        sys.exit(1)
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
    buildImage(imageName,tag)
    

if __name__ == "__main__":
    main()