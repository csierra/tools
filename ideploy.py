#!/usr/local/bin/python3

import os
import readline
import sys

from pip._vendor.distlib.compat import raw_input, ChainMap

portal_home = <path_to_liferay_portal_home>

module_paths = {
    'apps': {'path': '/modules/apps', 'includeSublevels': True},
    'frontend': {'path': '/modules/frontend', 'includeSublevels': False}
    }

portal_paths = {
    'portal-impl': {'path': '/portal-impl', 'command': 'ant deploy'},
    'portal-service': {'path': '/portal-service', 'command': 'ant deploy'},
    'portal-web': {'path': '/portal-web', 'command': 'ant deploy-fast'},
    'util-taglib': {'path': '/util-taglib', 'command': 'ant deploy'},
    }

# Simple completer: https://pymotw.com/2/readline/
class SimpleCompleter(object):

    def __init__(self, options):
        self.options = sorted(options)
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s
                                for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None

        return response

def searchDirForModules(path, includeSublevels):

    modules = {}

    for entry in os.listdir(path):
        path_entry = os.path.join(path, entry)
        if os.path.isdir(path_entry):
            modules[entry] = path_entry
            if includeSublevels:
                subModules = searchDirForModules(path_entry, False)
                modules = ChainMap({}, modules, subModules)

    return modules

# Adds all modules in apps
def getModules():

    allModules = {}

    for key, value in module_paths.items():
        modules = searchDirForModules(portal_home + value['path'], value['includeSublevels'])
        allModules = ChainMap({}, allModules, modules)

    return allModules

def input_loop(modules):
    
    selectedModule = ''

    while selectedModule != 'exit':
        selectedModule = raw_input('Please specify a module to deploy ("exit" to exit): ')
        if selectedModule in modules:
            readline.add_history(selectedModule)
            os.chdir(modules.get(selectedModule))
            os.system("gradlew deploy")
        elif selectedModule in portal_paths:
            readline.add_history(selectedModule)
            os.chdir(portal_home + portal_paths[selectedModule].get('path'))
            os.system(portal_paths[selectedModule].get('command'))
        elif selectedModule != 'exit':
            print("Nothing to deploy, go along")

def initialize():

    modules = getModules()

    ### Add autocompletion
    readline.set_completer(SimpleCompleter(ChainMap({}, portal_paths, modules).keys()).complete)

    ### Mac issues with binding when using tabs for autocompletion
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind -e")
        readline.parse_and_bind("bind '\t' rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    input_loop(modules)

initialize()
