import os
import docker
import argparse
import sys
import json

CONFIG_FILE = None
DOCKERFILE = None
CLIENT = None

def createParser():
    parser = argparse.ArgumentParser(prog='docker-builder',description='Helps to build and push docker images')
    parser.add_argument('--file',help='Path to docker file',required=True)
    parser.add_argument('--config',help='Path to configuration file',required=True)
    return parser


def createDockerClient():
    '''
        Returns docker client object.
    '''
    try:
        return docker.from_env()
    except Exception:
        raise RuntimeError

def checkValidConfig(config):
    '''
        Checks if the config file is valid.
    '''
    if 'imageName' not in config:
        print("'imageName' is a required key in configuration")
        raise AttributeError
    if 'repoName' not in config:
        print("'repoName' is a required key in configuration")
        raise AttributeError
    if 'tag' not in config:
        print("'tag' is a required key in configuration")
        raise AttributeError
    if 'deploy' in config:
        if not isinstance(config['deploy'],list):
            print("'deploy' key musg be a list")
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
        imageName = config['imageName']
        repoName = config['repoName']
        tag = config['tag']
        if 'deploy' in config:
            deploy = config['deploy']
        else:
            deploy = None
        if 'build_args' in config and len(config['build_args'])!=0:
            buildArgs = config['build_args']
        else:
            buildArgs = None
        return repoName,imageName,tag,deploy,buildArgs
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
            sys.exit(1)
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
    except Exception:
        print("Failed to write logs to file")


def buildImage(repoName,imageName,tagName):
    '''
        Helps to build the image.
    '''
    try:
        with open(DOCKERFILE,'rb') as f:
            try:
                result = CLIENT.images.build(
                    fileobj = f,
                    tag = f'{repoName}/{imageName}:{tagName}',
                    forcerm=True
                )
                writeLogstoFile(result[1],f'{repoName}-{imageName}-{tagName}')
                print(f"Successfully built image with ID: {result[0].id} and tags: {result[0].attrs['RepoTags']}") 
            except Exception as e:
                print('Failed to build image.')
                sys.exit(1)
    except Exception as e:
        print(f"Failed to not open dockerfile: {DOCKERFILE}")
        sys.exit(1)

def buildImageWithArgs(repoName,imageName,tagName,buildArgs):
    '''
        Helps to build the image with arguments.
    '''
    try:
        with open(DOCKERFILE,'rb') as f:
            try:
                result = CLIENT.images.build(
                    fileobj = f,
                    tag = f'{repoName}/{imageName}:{tagName}',
                    buildargs = buildArgs,
                    forcerm=True
                )
                writeLogstoFile(result[1],f'{repoName}-{imageName}-{tagName}')
                print(f"Successfully built image with ID: {result[0].id} and tags: {result[0].attrs['RepoTags']}") 
            except Exception as e:
                print('Failed to build image.')
                sys.exit(1)
    except Exception as e:
        print(f"Failed to open dockerfile: {DOCKERFILE}")
        sys.exit(1)

def deployToDockerHub(repoName,imageName,tagName):
    '''Function to deploy image to docker hub'''
    try:
        dockerHubLogin()
    except AttributeError:
        print("'HUB_USERNAME' or 'HUB_PASSWORD' not set")
        sys.exit()
    try:
        CLIENT.images.push(f"{os.environ['HUB_USERNAME']}/{repoName}/{imageName}",tag=tagName)
    except Exception as e:
        print(e.__cause__)

def deployImage(deploys,repoName,imageName,tagName):
    '''Helps to deploy code to specified repository'''
    if deploys != None:
        if len(deploys) !=0:
            for deploy in deploys:
                if deploy == 'docker-hub':
                    deployToDockerHub(repoName,imageName,tagName)
        else:
            print("deploy key contains empty list.")
    else:
        print("deploy key not set")
    
def main():
    '''
        Program starts here.
    '''
    global CLIENT,DOCKERFILE,CONFIG_FILE
    parser = createParser()
    arguments = parser.parse_args(sys.argv[1:])
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
    repoName,imageName,tag,deploy,buildArgs = readConfig(CONFIG_FILE)
    if(buildArgs==None):
        buildImage(repoName,imageName,tag)
    else:
        buildImage(repoName,imageName,tag,buildArgs)
    
    deployImage(deploy,)
    

if __name__ == "__main__":
    main()