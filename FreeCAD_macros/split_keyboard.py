"""
This macro creates a 3D model of a split keyboard case.
(The case is supposed to be laser-cut from 3 mm wood sheet.)
FreeCAD version 1.0.0.
Python version 3.11.
"""

import configparser
import os.path


SCRIPT_FILE = __file__
CONFIG_FILE_NAME = "split_keyboard.ini"


def main():
    prints(f"Hello. Executing file: '{SCRIPT_FILE}'")
    
    (success, config) = read_configuration(SCRIPT_FILE, CONFIG_FILE_NAME)
    if success:
        (success, doc) = create_document(config.get("General", "DOCUMENT_NAME"))
    if success:
        prints("    TODO: Create top plate.")
        prints("    TODO: Create bottom plate.")
        prints("    TODO: Create thumb plates.")
        prints("    TODO: Create side walls.")
        prints("    TODO: Create wrist support.")
        prints("    TODO: Create enclosure that connects the halves.")
        prints("    TODO: Create and connect the right side.")
    
    prints("Exiting.")


def prints(message, indent=0):
    total_indent = 2 * indent
    # Print to Report view:
    print(f"{'':<{total_indent}}{message}")
    # Print to Python console:
    Gui.doCommand(f"#> {'':<{total_indent}}{message}")


"""
Reads a configuration file.
Uses the directory the script_file is in and the file name in config_file_name.
"""
def read_configuration(script_file, config_file_name):
    prints("Reading configuration file...", 1)
    directory = os.path.dirname(script_file)
    directory = os.path.abspath(directory) # Fix / vs. \.
    config_file = os.path.join(directory, config_file_name)
    prints(f"TEST: config file: '{config_file}'", 2)
    
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        prints("Success.", 2)
        return (True, config)
    else:
        prints(f"Error: configuration file doesn't exist: '{config_file}'", 2)
        return (False, None)


def create_document(document_name):
    prints("Creating document in FreeCAD...", 1)
    if App.activeDocument() and (App.activeDocument().Label == document_name):
        prints("Closing existing document of same name.", 2)
        App.closeDocument(document_name)

    new_document = FreeCAD.newDocument(document_name)
    prints(f"Success: created document '{document_name}'.", 2)
    return (True, new_document)


main()
