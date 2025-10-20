"""
This macro creates a 3D model of a split keyboard case.
(The case is supposed to be laser-cut from 3 mm wood sheet.)
------------------------------------------------------------------------
FreeCAD version 1.0.0.
Python version 3.11.
"""

from math import atan, degrees, isclose, sqrt
import BOPTools.JoinFeatures
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

VECTOR_ONE_Z = FreeCAD.Vector(0.0, 0.0, 1.0)


def main():
    prints(f"Hello. Executing file: '{SCRIPT_FILE}'")

    config = read_configuration(SCRIPT_FILE, CONFIG_FILE_NAME)
    doc = create_document(config.get("General", "DOCUMENT_NAME"))
    switch_hole_list = create_switch_holes(doc, LAYOUT_LEFT, config, "SwitchHole")

    # Now that there are objects, adjust the view:
    Gui.activeDocument().activeView().viewIsometric()
    Gui.ActiveDocument.ActiveView.setAxisCross(True)
    Gui.SendMsgToActiveView("ViewFit")

    create_top_plate(doc, config, switch_hole_list, "TopPlate")
    prints("TODO: Create bottom plate.", 1)
    prints("TODO: Create thumb plates.", 1)
    prints("TODO: Create side walls.", 1)
    prints("TODO: Create wrist support.", 1)
    prints("TODO: Create enclosure that connects the halves.", 1)
    prints("TODO: Create and connect the right side.", 1)

    prints("Exiting.")


#----------------------------------------------------------------------x---------------------------
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


"""
Formats a vector to be printed (two decimals).
"""
def format_vector(vector):
    return f"x: {vector.x:.2f}; y: {vector.y:.2f}; z: {vector.z:.2f}"


#----------------------------------------------------------------------x---------------------------
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
            float(config.get("Keyboard", "CASE_THICKNESS_MM")))

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


def create_top_plate(doc, config, switch_hole_list, object_name):
    prints("Creating top plate...", 1)

    corners = find_corners(switch_hole_list)
    prints(f"Found {len(corners)} corners.", 2)
    top_plate_face = make_face_from_corners(corners)
    prints("Created top plate face from the corners.", 2)
    expand_by = get_top_plate_expansion(config)
    top_plate_face = expand_face(top_plate_face, expand_by)
    prints(f"Expanded top plate face by {expand_by:.2f} mm.", 2)
    top_plate_part = top_plate_face.extrude(VECTOR_ONE_Z
        * float(config.get("Keyboard", "CASE_THICKNESS_MM")))
    top_plate_object = doc.addObject("Part::Feature", object_name)
    top_plate_object.Shape = top_plate_part
    doc.recompute()
    prints("Created top plate solid from face.", 2)

    top_plate_object = make_switch_holes(doc, top_plate_object, switch_hole_list)
    prints("Made switch holes into the top plate.", 2)

    layout_angle = rotate_top_plate(top_plate_object, config)
    prints(f"Rotated top plate {layout_angle:.2f} degrees.", 2)
    doc.recompute()

    #top_plate_template_3 = make_left_side_rectangular(top_plate_template_2)
    prints("TODO: Make left side rectangular.", 2)
    #tilt_raise_top_plate()
    prints("TODO: Tilt and raise top plate.", 2)
    #prints("Success.", 2)


def make_switch_holes(doc, base_object, switch_holes):
    # Group/fuse the switch holes.
    switches_name = "LeftSwitchHoles"
    left_switches = doc.addObject("Part::MultiFuse", switches_name)
    left_switches.Shapes = switch_holes

    doc.recompute()

    # Create a top plate with switch holes by using the old top
    # plate as a base and the switch holes as a tool for makeCutOut.
    new_top_plate = BOPTools.JoinFeatures.makeCutout(name=base_object.Name)
    new_top_plate.Base = base_object
    new_top_plate.Tool = left_switches
    new_top_plate.Proxy.execute(new_top_plate)
    new_top_plate.purgeTouched()

    # Hide the boxes that were switch holes and the old top plate.
    for obj in new_top_plate.ViewObject.Proxy.claimChildren():
        obj.ViewObject.hide()

    return new_top_plate


"""
This "finds" the corners from the list of switch holes. It relies on
the fact that it is known that there are three switches on the left,
two on the right, five at the bottom and five at the top.
The corners aren't the exact corners of the individual switch holes
but their centres of gravity. Since the face made from the corners
needs to be expanded anyway, the necessary extra offset is included
when expanding.
"""
def find_corners(switch_hole_list):
    # First, make a list of the switch holes sorted by the x coordinate
    # of their centres of gravity and then the y coordinate.
    switch_holes_sorted_y = sorted(switch_hole_list,
        key=lambda switch: switch.Shape.CenterOfGravity.y)
    switch_holes_sorted_x_y = sorted(switch_holes_sorted_y,
        key=lambda switch: switch.Shape.CenterOfGravity.x)
    #prints(f"TEST: Sorted by x, then y:", 3)
    #for switch_hole in switch_holes_sorted_x_y:
        #prints(f"TEST: {switch_hole.Name}: {format_vector(switch_hole.Shape.CenterOfGravity)}", 4)

    # The three first switch holes in the list are the leftmost ones
    # and the two last ones are the rightmost ones.
    left_bottom_corner = switch_holes_sorted_x_y[0]
    left_top_corner = switch_holes_sorted_x_y[2]
    right_bottom_corner = switch_holes_sorted_x_y[35]
    right_top_corner = switch_holes_sorted_x_y[36]

    # Sort by y again to get list sorted by y and then x.
    switch_holes_sorted_y_x = sorted(switch_holes_sorted_x_y,
        key=lambda switch: switch.Shape.CenterOfGravity.y)
    #prints(f"TEST: Sorted by y, then x:", 3)
    #for switch_hole in switch_holes_sorted_y_x:
        #prints(f"TEST: {switch_hole.Name}: {format_vector(switch_hole.Shape.CenterOfGravity)}", 4)

    # The first five switch holes are the bottom ones and the five
    # last ones are the top ones.
    bottom_left_corner = switch_holes_sorted_y_x[0]
    bottom_right_corner = switch_holes_sorted_y_x[4]
    top_left_corner = switch_holes_sorted_y_x[32]
    top_right_corner = switch_holes_sorted_y_x[36]

    # Put the corner switch holes in order, same as
    # corners H, I, J, K, L, M, N, O in README.md.
    corner_switch_holes = [top_left_corner, top_right_corner, right_top_corner, right_bottom_corner,
        bottom_right_corner, bottom_left_corner, left_bottom_corner, left_top_corner]

    corners = []
    for switch_hole in corner_switch_holes:
        corner_coord = switch_hole.Shape.CenterOfGravity
        # Z should be 0 here.
        corner_coord.z = 0.0
        corners.append(corner_coord)
        #prints(f"TEST: corner: {switch_hole.Name}: {format_vector(corner_coord)}", 3)
    return corners


def make_face_from_corners(corners):
    # Create lines and then edges from the corners.
    edges = []
    # An edge between the last and first corner is also needed,
    # so start with the last corner.
    previous_corner = corners[len(corners) - 1]
    for corner in corners:
        line = Part.LineSegment(previous_corner, corner)
        edge = Part.Edge(line)
        edges.append(edge)
        previous_corner = corner
    #prints(f"TEST: Created {len(edges)} edges.", 3)

    # Make the edges into a (closed) wire.
    wire = Part.Wire(edges)
    if not wire.isClosed():
        # FreeCAD sometimes fails to close the wire.
        raise Exception("Error: wire is not closed. Retry?")

    # Make the wire into a face.
    face = Part.Face(wire)

    return face


"""
Since the top plate's corners are the centres of gravity of the
switch holes, the top plate face needs to be expanded by:
  1) half the hypotenuse of a switch face,
  2) at least the thickness of the material for integrity,
  3) at least the thickness of the material again to account
     for finger joining the laser-cut parts,
  4) any wanted extra and
  5) half the kerf.
"""
def get_top_plate_expansion(config):
    switch_len_x = float(config.get("Keyboard", "SWITCH_LENGTH_X_MM"))
    switch_len_y = float(config.get("Keyboard", "SWITCH_LENGTH_Y_MM"))
    switch_hypotenuse = sqrt(switch_len_x**2 + switch_len_y**2)
    #prints(f"TEST: switch hypotenuse: {switch_hypotenuse:.2f}.", 2)
    expand_by = (switch_hypotenuse/2.0
        + 2.0*float(config.get("Keyboard", "CASE_THICKNESS_MM"))
        + float(config.get("Keyboard", "CASE_THICKNESS_MM"))
        + float(config.get("Keyboard", "PLATE_EXTRA_MM")))
    #prints(f"TEST: expand_by: {expand_by:.2f}.", 2)
    return expand_by


"""
Expands a face sideways.
"""
def expand_face(face, expand_by):
    # From official docs:
    #   join: method of offsetting non-tangent joints. 0 = arcs,
    #     1 = tangent, 2 = intersection.
    #   fill: if true, the output is a face filling the space covered
    #     by offset. If false, the output is a wire.
    #   openResult: affects the way open wires are processed. If False,
    #     an open wire is made. If True, a closed wire is made from a
    #     double-sided offset, with rounds around open vertices.
    #   intersection: affects the way compounds are processed. If
    #     False, all children are offset independently. If True, and
    #     children are edges/wires, the children are offset in a
    #     collective manner. If compounding is nested, collectiveness
    #     does not spread across compounds (only direct children of a
    #     compound are taken collectively).
    offset_wire = face.makeOffset2D(offset=expand_by, join=2, fill=False,
        openResult = True, intersection = True)
    offset_face = Part.Face(offset_wire)
    return offset_face


def rotate_top_plate(top_plate_object, config):
    # Rotate top plate so that the side between top right corner and
    # right top corner (side b in README.md) is horizontal and at top.
    layout_angle = degrees(atan(
        float(config.get("Keyboard", "SWITCH_DISTANCE_Y_MM"))
        / (2.0*float(config.get("Keyboard", "SWITCH_DISTANCE_X_MM")))
        ))
    position = top_plate_object.Placement.Base
    # Rotate along z-axis (yaw).
    rotation = FreeCAD.Rotation(layout_angle, 0.0, 0.0) # Yaw, pitch, roll.
    # Rotate through centre so the object isn't too displaced.
    centre = top_plate_object.Shape.CenterOfGravity
    top_plate_object.Placement = FreeCAD.Placement(
        position,
        rotation,
        centre)
    return layout_angle


#----------------------------------------------------------------------x---------------------------


main()
