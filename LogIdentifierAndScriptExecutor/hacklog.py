"""
                            LOG ENHANCER
                            === ========
DESCRIPTION
===========
Objective is to parse a set of log files for a keyword and execute a script or command post that.

ARGUMENTS
=========
--config (or) -c : Config file with absolute path
--help (or) -h : Provide help information

CONFIG PARAMETERS
=================

TargetFile = "Specify the log file which should be scanned"
TargetStatement =  "Specify the Keyword you are looking for"
CommandsToBeExecuted = "Specify the Commands to be executed after keyword is found"
*Duration = "Specify the total runtime of this script"
*Frequency = "Specify the frequency in minutes in which the script re-scans the log file"

* - These parameters are not mandatory

"""
import json
import os
import sys
import shutil
from collections import OrderedDict
from time import sleep
import subprocess
import datetime
import signal


class Intelogger:
    def __init__(self, arg):
        self.target_directory = arg[0]
        self.target_file = arg[1]
        self.target_statement = arg[2]
        self.commands_to_be_executed = arg[3]
        self.script_to_executed = arg[4]
        self.script_env = arg[5]
        self.duration = int(arg[6])
        self.frequency = int(arg[7])
        print("Parsed config file values", self.target_directory, self.target_file, self.target_statement,
              self.commands_to_be_executed, self.script_to_executed, self.script_env,  self.duration, self.frequency)

    def command_executor(self):
        try:
            for command in self.commands_to_be_executed:
                command = command.strip()
                print("Going to execute command: " + command)
                #output_file_name = command.replace(" ",'_') + '_output.log'
                output_file_name = 'output.log'
                now = datetime.datetime.now()
                with open(output_file_name, 'a+') as out:
                    out.write(now.strftime("%Y-%m-%d %H:%M:%S") + " Executing command " + command + "\n")
                    out.flush()
                    return_code = subprocess.call(command, stdout=out, shell=True)

        except Exception as e:
            raise Exception(e)

    def script_executor(self):
        try:
            if self.script_to_executed:
                print("Going to execute script: " + self.script_to_executed)
                file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.script_to_executed)
                # output_file_name = command.replace(" ",'_') + '_output.log'
                output_file_name = 'output.log'
                now = datetime.datetime.now()
                with open(output_file_name, 'a+') as out:
                    out.write(now.strftime("%Y-%m-%d %H:%M:%S") + " Executing script " + self.script_to_executed + "\n")
                    out.flush()
                    return_code = subprocess.call(self.script_env + ' ' + file_path, stdout=out, shell=True)
        except Exception as e:
            raise Exception(e)

    def copy_log_files(self):
        try:
            if not os.path.isdir('log_files'):
                os.system("mkdir log_files")
            src_files = os.listdir(self.target_directory)

            for file_name in src_files:
                if not file_name.startswith(self.target_file.split('.')[0]) or \
                        "tar.gz" in file_name:
                    continue
                shutil.copy(self.target_directory + "/" + file_name, "./log_files/")
        except Exception as e:
            raise Exception(e)

    def search_and_execute(self):
        found = False
        try:
            src_files = os.listdir('log_files')
            print(src_files)

            for file in src_files:
                with open(('log_files/' + file), 'r') as log_file:
                    for line in log_file:
                        if self.target_statement in line:
                            print("Debug: Found string - {0}".format(self.target_statement))
                            found = True
                            Intelogger.command_executor(self)
                            Intelogger.script_executor(self)
                            break

            if not found:
                print("Debug: Not Found string - {0}".format(self.target_statement))
                return False
            else:
                return True
        except IOError:
            raise IOError("Log File " + self.target_file + " does not exist")
        except Exception as e:
            raise Exception("Oops! " + str(e) + " occurred.")
        finally:
            print("Deleting files")
            os.system("rm -rf ./log_files/*")

    def initiator(self):
        try:
            now = datetime.datetime.now()
            print("Going to Execute the script now at " + now.strftime("%Y-%m-%d %H:%M:%S"))
            time = 0
            while time < self.duration:
                self.copy_log_files()
                if self.search_and_execute():
                    break
                print("Sleep initiated for " + str(self.frequency) + " minutes")
                sleep(60 * self.frequency)
                time += self.frequency

        except Exception as e:
            raise Exception(e)
        finally:
            print("Script execution completed at " + now.strftime("%Y-%m-%d %H:%M:%S"))


class ConfigParser:
    def __init__(self):
        try:
            arg_dict = {}
            self.config_file_path = ''
            position = 1
            if not (len(sys.argv) - 1) > 0:
                print(__doc__)
                raise ValueError("Error: No arguments provided. Please provide arguments to proceed.")

            while position <= len(sys.argv) - 1:
                if sys.argv[position] in ("--help" or "-h"):
                    arg_dict['help'] = ""
                    raise Warning(__doc__)
                elif sys.argv[position] in ("--config" or "-c"):
                    arg_dict['config'] = sys.argv[position + 1]
                    break
                else:
                    raise IOError("Error: Wrong command line attribute received. Please use --help for more details.")

            if not os.path.isfile(arg_dict['config']):
                raise IOError("Error: Config File does not exist")

            print("\nUsing the config file: " + arg_dict['config'])
            self.config_file_path = arg_dict['config']

            if self.config_file_path.__contains__(".config"):
                self.config_params = self.parse_config_file_type_dot_config()
            elif self.config_file_path.__contains__(".json"):
                self.config_params = self.parse_config_file_type_json()

        except IndexError:
            raise IndexError("Error: Config file value not mentioned")
        except Exception as e:
            raise Exception(e)

    def parse_config_file_type_dot_config(self):
        """
        Parse the config file or the input arguments
        :returns List object
        """

        try:
            target_directory = ''
            target_file = ''
            target_statement = ''
            commands_to_be_executed = []
            script_to_be_executed = ''
            script_env = ''
            duration = 5
            frequency = 1

            f = open(self.config_file_path, 'r')

            for item in f.readlines():
                item = item.replace('\n', '')
                if 'TargetDirectory' in item:
                    target_directory = item.split('=')[1]
                if 'TargetFile' in item:
                    target_file = item.split('=')[1]
                if 'TargetStatement' in item:
                    target_statement = item.split('=')[1]
                if 'CommandsToBeExecuted' in item:
                    commands_to_be_executed = item.split('=')[1].split(',')
                if 'ScriptToBeExecuted' in item:
                    script_to_be_executed = item.split('=')[1]
                if 'ScriptEnv' in item:
                    script_env = item.split('=')[1]
                if 'Duration' in item:
                    duration = item.split('=')[1]
                if 'Frequency' in item:
                    frequency = item.split('=')[1]

            f.close()

            return [target_directory, target_file, target_statement, commands_to_be_executed, script_to_be_executed, script_env, duration, frequency]
        except IOError as e:
            raise Exception(e)

    def parse_config_file_type_json(self):
        """
        :return: List
        """
        try:
            with open(self.config_file_path) as f:
                data = f.read()
            data = json.loads(data, object_pairs_hook=OrderedDict)

            params = []
            for config_param, value in data.items():
                if config_param == "scriptToBeExecuted":
                    params.append(value['name'])
                    params.append(value['env'])
                elif config_param == "commandsToBeExecuted":
                    params.append(value.split(','))
                else:
                    params.append(value)

            f.close()

            return params
        except IOError as e:
            raise Exception(e)


try:
    config_parser = ConfigParser()
    intel_logger = Intelogger(config_parser.config_params)
    intel_logger.initiator()
except Exception as e:
    print(e)
