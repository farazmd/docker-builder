import sys
import os
import pytest
sys.path.append(os.path.pathsep.join(__file__.split()[:-2]))
import docker_builder

''' Testing parser functionality'''

def test_valid_parser_arguments():
    parser = docker_builder.createParser()
    arguments = parser.parse_args(['--file','./files/Dockerfile.test','--config','./files/test_config.json'])
    assert len(vars(arguments)) == 2

def test_no_config_passed(capsys):
    parser = docker_builder.createParser()
    with pytest.raises(SystemExit):
        parser.parse_args(['--file','./files/Dockerfile.test'])
    captured = capsys.readouterr()
    assert 'error: the following arguments are required: --config' in captured.err

def test_no_file_passed(capsys):
    parser = docker_builder.createParser()
    with pytest.raises(SystemExit):
        parser.parse_args(['--config','./files/test_config.json'])
    captured = capsys.readouterr()
    assert 'error: the following arguments are required: --file' in captured.err

def test_no_arguments_passed(capsys):
    parser = docker_builder.createParser()
    with pytest.raises(SystemExit):
        parser.parse_args([])
    captured = capsys.readouterr()
    assert 'error: the following arguments are required: --file, --config' in captured.err
