"""
This macro creates a 3D model of a split keyboard case.
(The case is supposed to be laser-cut from 3 mm wood sheet.)
------------------------------------------------------------------------
FreeCAD version 1.0.0.
Python version 3.11.
"""

import configparser
import os.path


SCRIPT_FILE = __file__
CONFIG_FILE_NAME = "split_keyboard.ini"

# Visual and positional layout of the left side of the split keyboard.
# Each coordinate denotes one switch's place (in unit lengths, not in
# mm). Numbers chosen just to keep it definitely positive even when
# rotating.
LAYOUT_LEFT = [
              (11, 14), (12, 14), (13, 14), (14, 14), (15, 14),
                                                                (16, 13.5),
    (10, 13), (11, 13), (12, 13), (13, 13), (14, 13), (15, 13),             (17, 13),
                                                                (16, 12.5),           (18, 12.5),
    (10, 12), (11, 12), (12, 12), (13, 12), (14, 12), (15, 12),             (17, 12),
                                                                (16, 11.5),           (18, 11.5),
    (10, 11), (11, 11), (12, 11), (13, 11), (14, 11), (15, 11),             (17, 11),
                                                                (16, 10.5),
              (11, 10), (12, 10), (13, 10), (14, 10), (15, 10)
]


def main():
    prints(f"Hello. Executing file: '{SCRIPT_FILE}'")

    config = read_configuration(SCRIPT_FILE, CONFIG_FILE_NAME)
    doc = create_document(config.get("General", "DOCUMENT_NAME"))
    switch_hole_list = create_switch_holes(doc, LAYOUT_LEFT, config, "SwitchHole")

    # Now that there are objects, adjust the view:
    Gui.activeDocument().activeView().viewIsometric()
    Gui.ActiveDocument.ActiveView.setAxisCross(True)
    Gui.SendMsgToActiveView("ViewFit")

    prints("    TODO: Create top plate.")
    prints("    TODO: Create bottom plate.")
    prints("    TODO: Create thumb plates.")
    prints("    TODO: Create side walls.")
    prints("    TODO: Create wrist support.")
    prints("    TODO: Create enclosure that connects the halves.")
    prints("    TODO: Create and connect the right side.")

    prints("Exiting.")


#--------------------------------------------------------------------------------------------------
# Utility functions.


def prints(message, indent=0):
    total_indent = 2 * int(indent)
    # Print to Report view:
    print(f"{'':<{total_indent}}{message}")
    # Print to Python console:
    Gui.doCommand(f"#> {'':<{total_indent}}{message}")


"""
Object dimensions need to be made slightly bigger to account for
laser kerf. If the shape is supposed to be a hole, the dimensions
need to be made smaller.
"""
def account_for_kerf(number, kerf, hole=False):
    sign = 1.0
    if hole:
        sign = -1.0
    kerfed = float(number) + sign*float(kerf)
    return kerfed


#--------------------------------------------------------------------------------------------------
# Other functions.


"""
Reads a configuration file.
Uses the directory the script_file is in and the file name in config_file_name.
"""
def read_configuration(script_file, config_file_name):
    prints("Reading configuration file...", 1)
    directory = os.path.dirname(script_file)
    directory = os.path.abspath(directory) # Fix / vs. \.
    config_file = os.path.join(directory, config_file_name)
    #prints(f"TEST: config file: '{config_file}'", 2)

    config = configparser.ConfigParser()
    config.read(config_file)
    prints("Success.", 2)
    return config


def create_document(document_name):
    prints("Creating document in FreeCAD...", 1)
    if App.activeDocument() and (App.activeDocument().Label == document_name):
        prints("Closing existing document of same name.", 2)
        App.closeDocument(document_name)

    new_document = FreeCAD.newDocument(document_name)
    prints(f"Success: created document '{document_name}'.", 2)
    return new_document


def create_switch_holes(doc, layout, config, object_name):
    prints("Creating switch holes...", 1)
    switch_hole_list = []
    i = 0

    for coordinate in layout:
        switch_name = f"{object_name}{'%03d'%i}"
        # Make an empty object with a name:
        switch_object = doc.addObject("Part::Feature", switch_name)

        kerf = config.get("General", "LASER_KERF_MM")
        # Create a switch shape for the object:
        switch_object.Shape = Part.makeBox(
            account_for_kerf(config.get("Keyboard", "SWITCH_LENGTH_X_MM"), kerf, hole=True),
            account_for_kerf(config.get("Keyboard", "SWITCH_LENGTH_Y_MM"), kerf, hole=True),
            account_for_kerf(config.get("Keyboard", "CASE_THICKNESS_MM"), kerf, hole=True))

        # Calculate switch's place:
        (placement_x, placement_y) = coordinate
        place_x = float(placement_x) * float(config.get("Keyboard", "SWITCH_DISTANCE_X_MM"))
        place_y = float(placement_y) * float(config.get("Keyboard", "SWITCH_DISTANCE_Y_MM"))
        # Assign the place:
        switch_object.Placement.Base = FreeCAD.Vector(place_x, place_y)

        switch_hole_list.append(switch_object)
        i = i + 1

    prints(f"Success: created {i} switch holes.", 2)

    # Recomputing the document needs to be done every now and then.
    doc.recompute()

    return switch_hole_list


#--------------------------------------------------------------------------------------------------


main()
