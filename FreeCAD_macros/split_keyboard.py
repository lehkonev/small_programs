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
FREECAD_EXT = ".FCStd" # Expected name format: "SplitKeyboard001.FCStd".

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

VECTOR_ONE_X = FreeCAD.Vector(1.0, 0.0, 0.0)
VECTOR_ONE_Y = FreeCAD.Vector(0.0, 1.0, 0.0)
VECTOR_ONE_Z = FreeCAD.Vector(0.0, 0.0, 1.0)

# If START_AT_STEP is 0, create a new document. If it is not, try to
# find a file with a number one less than it from the macro directory.
# If not found, start at step 0.
START_AT_STEP = 4
# If STOP_AT_STEP is equal to or greater than the existing maximum step,
# all steps are performed. If it is below, only steps up to that
# step are performed.
STOP_AT_STEP = 9
STEPS = {
    0: "Creating document...",
    1: "Creating switch holes...",
    2: "Creating top plate...",
    3: "Creating bottom plate...",
    4: "Creating side walls...",
    5: "Creating thumb plates...",
    6: "Creating wrist support...",
    7: "Creating enclosure that connects the halves...",
    8: "Creating and connecting right side...",
}

def main():
    prints(f"Hello. Executing file: '{SCRIPT_FILE}'")

    # Read files from the macro directory.
    directory = os.path.dirname(SCRIPT_FILE)
    directory = os.path.abspath(directory) # Fix / vs. \.

    config = read_configuration_file(directory, CONFIG_FILE_NAME)
    base_document_name = config.get("General", "DOCUMENT_NAME")

    document_number = START_AT_STEP - 1
    (doc, start_at_step) = open_document(directory, base_document_name, document_number)

    if STOP_AT_STEP < start_at_step:
        prints(f"Warning: Stopping step ({STOP_AT_STEP}) is less than"
            + f" starting step ({start_at_step}). Nothing is done.")
    stop_before_step = min(STOP_AT_STEP + 1, len(STEPS))

    (objects, switch_hole_list) = get_objects(doc)

    step = start_at_step
    stop_step = step - 1
    while step < stop_before_step:
        prints(f"Step {step}: {STEPS[step]}", 1)

        match step:
            case 0:
                doc = create_document(base_document_name)
            case 1:
                switch_hole_list = create_switch_holes(doc, LAYOUT_LEFT, config, "SwitchHole")
                # Now that there are objects, adjust the view:
                Gui.activeDocument().activeView().viewIsometric()
                Gui.ActiveDocument.ActiveView.setAxisCross(True)
                Gui.SendMsgToActiveView("ViewFit")
            case 2:
                top_plate = create_top_plate(doc, config, switch_hole_list, "TopPlate")
                objects["TopPlate"] = top_plate
            case 3:
                bottom_plate = create_bottom_plate(doc, config, objects["TopPlate"],
                    "BottomPlate")
                objects["BottomPlate"] = bottom_plate
            case 4:
                create_side_walls(doc, config, objects["TopPlate"], objects["BottomPlate"],
                    "SideWall")
            case bigger if bigger < len(STEPS):
                prints("TODO", 2)
                stop_step = stop_step - 1
            case _:
                break

        step = step + 1
        stop_step = stop_step + 1

    new_doc_name = f"{base_document_name}{'%03d'%stop_step}"
    if (doc is not None) and (doc.Label != new_doc_name):
        prints(f"Rename the document to '{new_doc_name}' (last actual step: {stop_step}).")
        doc.Label = f"{new_doc_name}"

    prints("Exiting.")


#----------------------------------------------------------------------x---------------------------
# File and document utility functions.


def read_configuration_file(directory, config_file_name):
    prints("Reading configuration file...", 1)
    config_file = os.path.join(directory, config_file_name)
    #prints(f"TEST: config file: '{config_file}'", 2)

    config = configparser.ConfigParser()
    config.read(config_file)
    prints("Success.", 2)
    return config


def open_document(directory, base_document_name, number):
    if number <= 0:
        return (None, 0)

    document_name = f"{base_document_name}{'%03d'%number}"
    file_name = f"{document_name}{FREECAD_EXT}"
    full_file_name = f"{directory}/{file_name}"
    prints(f"Trying to open document '{document_name}'...", 1)
    close_document(document_name)

    try:
        #prints(f"TEST: Opening: '{full_file_name}'...", 2)
        FreeCAD.openDocument(full_file_name)
        App.setActiveDocument(document_name)
        App.ActiveDocument=App.getDocument(document_name)
        Gui.ActiveDocument=Gui.getDocument(document_name)
        prints(f"Success: opened '{file_name}'.", 2)
        return (App.ActiveDocument, number + 1)
    except:
        prints(f"Warning: Could not find '{file_name}' or something went wrong."
            + " Starting at step 0.", 2)

    return (None, 0)


def close_document(document_name):
    try:
        App.setActiveDocument(document_name)
    except:
        # There is no document with that name; nothing needs to be done.
        return

    prints(f"Closing existing '{document_name}' document.", 2)
    App.closeDocument(document_name)


def get_objects(doc):
    objects = {}
    switch_hole_list = []
    if doc is not None:
        for obj in doc.Objects:
            if obj.ViewObject.isVisible():
                if obj.Name.startswith("SwitchHole"):
                    switch_hole_list.append(obj)
                else:
                    objects[obj.Name] = obj
    return (objects, switch_hole_list)


def create_document(document_name):
    prints("Creating new document in FreeCAD...", 1)
    close_document(document_name)

    new_document = FreeCAD.newDocument(document_name)
    prints(f"Success: created document '{document_name}'.", 2)
    return new_document


#----------------------------------------------------------------------x---------------------------
# Printing and formatting utility functions.


def prints(message, indent=0):
    total_indent = 2 * int(indent)
    # Print to Report view:
    print(f"{'':<{total_indent}}{message}")
    # Print to Python console:
    Gui.doCommand(f"#> {'':<{total_indent}}{message}")


"""
Formats a vector to be printed (two decimals).
"""
def format_vector(vector):
    return f"x: {vector.x:.2f}; y: {vector.y:.2f}; z: {vector.z:.2f}"


def format_vectors(vectors):
    str_vectors = []
    for v in vectors:
        str_vectors.append(f"({v.x:.2f}, {v.y:.2f}, {v.z:.2f})")
    return str_vectors


"""
Formats a vertex to be printed (two decimals).
"""
def format_vertex(vertex):
    return f"x: {vertex.X:.2f}; y: {vertex.Y:.2f}; z: {vertex.Z:.2f}"


def format_vertices(vertices):
    str_vertices = []
    for v in vertices:
        str_vertices.append(f"({v.X:.2f}, {v.Y:.2f}, {v.Z:.2f})")
    return str_vertices


#----------------------------------------------------------------------x---------------------------
# Conversion and calculation utility functions.


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


def vector_to_vertex(vector):
    return Part.Vertex(vector.x, vector.y, vector.z)


def vertex_to_vector(vertex):
    return FreeCAD.Vector(vertex.X, vertex.Y, vertex.Z)


def vertices_to_vectors(vertices):
    vectors = []
    for vertex in vertices:
        vectors.append(vertex_to_vector(vertex))
    return vectors


#----------------------------------------------------------------------x---------------------------
# FreeCAD utility functions.


"""
Expands a face sideways (parallel to the face).
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


def get_long_edges(object, longer_than):
    if (longer_than < 0) or isclose(longer_than, 0.0):
        raise Exception("Error: edge length comparison value has to be greater than 0.")

    long_edges = []
    i = 1
    for edge in object.Shape.Edges:
        if (edge.Length < 0) or isclose(edge.Length, 0.0):
            raise Exception("Error: invalid edge length: {edge.Length}.")

        if (edge.Length > longer_than) and (not isclose(edge.Length, longer_than)):
            #prints(f"TEST: edge {i} p0: {format_vertex(edge.Vertexes[0])}", 4)
            #prints(f"TEST: edge {i} p1: {format_vertex(edge.Vertexes[1])}", 4)
            i = i + 1
            long_edges.append(edge)

    return long_edges


def get_mins_maxes_from_vertices(vertices):
    min_x = None
    min_y = None
    min_z = None
    max_x = None
    max_y = None
    max_z = None

    for vertex in vertices:
        if min_x is None:
            min_x = vertex.X
            min_y = vertex.Y
            min_z = vertex.Z
            max_x = vertex.X
            max_y = vertex.Y
            max_z = vertex.Z
        else:
            min_x = min(min_x, vertex.X)
            min_y = min(min_y, vertex.Y)
            min_z = min(min_z, vertex.Z)
            max_x = max(max_x, vertex.X)
            max_y = max(max_y, vertex.Y)
            max_z = max(max_z, vertex.Z)

    return (min_x, min_y, min_z, max_x, max_y, max_z)


def get_rim_vertices(rim_edges):
    rim_vertices = []
    for edge in rim_edges:
        for vertex in edge.Vertexes:
            # Find unique vertices of the rim of object.
            found_same = False
            for v in rim_vertices:
                if isclose(vertex.X, v.X) and isclose(vertex.Y, v.Y) and isclose(vertex.Z, v.Z):
                    found_same = True
                    break
            if not found_same:
                rim_vertices.append(vertex)
                #prints(f"TEST: new rim vertex: {format_vertex(vertex)}", 4)

    return rim_vertices


def hide_children(object):
    for child in object.ViewObject.Proxy.claimChildren():
        child.ViewObject.hide()


def make_face_from_corners(corners):
    if len(corners) < 3:
        raise Exception("Error: need at least three corners to make a face.")

    # Create lines and then edges from the corners.
    edges = []
    # An edge between the last and first corner is also needed,
    # so start with the last corner.
    previous_corner = corners[len(corners) - 1]
    for corner in corners:
        #prints(f"TEST: edge from {format_vector(previous_corner)} to {format_vector(corner)}.", 3)
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


def make_solid_from_face(doc, face, extrude_vector, object_name):
    new_part = face.extrude(extrude_vector)
    new_object = doc.addObject("Part::Feature", object_name)
    new_object.Shape = new_part
    return new_object


#----------------------------------------------------------------------x---------------------------
# The functions that create the top plate.


def create_switch_holes(doc, layout, config, object_name):
    prints("Creating switch holes...", 1)
    switch_hole_list = []
    i = 0

    for coordinate in layout:
        switch_name = f"{object_name}{'%03d'%i}"
        # Make an empty object with a name:
        switch_object = doc.addObject("Part::Feature", switch_name)

        #kerf = config.get("General", "LASER_KERF_MM")
        # Create a switch shape for the object:
        switch_object.Shape = Part.makeBox(
            float(config.get("Keyboard", "SWITCH_LENGTH_X_MM")),
            float(config.get("Keyboard", "SWITCH_LENGTH_Y_MM")),
            float(config.get("Keyboard", "CASE_THICKNESS_MM")))

        # Calculate switch's place:
        (placement_x, placement_y) = coordinate
        place_x = float(placement_x) * float(config.get("Keyboard", "SWITCH_DISTANCE_X_MM"))
        place_y = float(placement_y) * float(config.get("Keyboard", "SWITCH_DISTANCE_Y_MM"))
        # Assign the place:
        switch_object.Placement.Base = FreeCAD.Vector(place_x, place_y)

        switch_hole_list.append(switch_object)
        i = i + 1

    # Recomputing the document needs to be done every now and then.
    doc.recompute()

    prints(f"Success: created {i} switch holes.", 2)
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
    extrude_vector = VECTOR_ONE_Z * float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    top_plate_object = make_solid_from_face(doc, top_plate_face, extrude_vector,
        f"{object_name}Switchless")
    prints("Created top plate solid from face.", 2)
    doc.recompute()

    top_plate_object = make_switch_holes(doc, top_plate_object, switch_hole_list,
        f"{object_name}Unextended")
    prints("Made switch holes into the top plate.", 2)
    layout_angle = rotate_top_plate(top_plate_object, config)
    prints(f"Rotated top plate {layout_angle:.2f} degrees.", 2)
    doc.recompute()

    top_plate_object = make_left_side_rectangular(doc, top_plate_object, config, object_name)
    prints("Made left side rectangular.", 2)
    doc.recompute()

    tilt_angle = tilt_top_plate(top_plate_object, config)
    prints(f"Tilted top plate {tilt_angle} degrees.", 2)
    prints("Success.", 2)
    return top_plate_object


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


def make_switch_holes(doc, base_object, switch_holes, object_name):
    # Group/fuse the switch holes.
    switches_name = "LeftSwitchHoles"
    left_switches = doc.addObject("Part::MultiFuse", switches_name)
    left_switches.Shapes = switch_holes

    doc.recompute()

    # Create a top plate with switch holes by using the old top
    # plate as a base and the switch holes as a tool for makeCutOut.
    new_top_plate = BOPTools.JoinFeatures.makeCutout(name=object_name)
    new_top_plate.Base = base_object
    new_top_plate.Tool = left_switches
    new_top_plate.Proxy.execute(new_top_plate)
    new_top_plate.purgeTouched()

    # Hide the boxes that were switch holes and the old top plate.
    hide_children(new_top_plate)

    return new_top_plate


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


"""
Makes the left side of the top plate rectangular by creating filler
solids. Or, stretches the corners with smallest x coordinates to the
minimum x coordinate.
"""
def make_left_side_rectangular(doc, top_plate_object, config, object_name):
    vertices = get_vertices_of_rectangular_extension(top_plate_object, config)
    left_rectangle_face = make_face_from_corners(vertices_to_vectors(vertices))
    extrude_vector = VECTOR_ONE_Z * float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    left_rectangle_name = f"{object_name}Extension"
    left_rectangle_object = make_solid_from_face(
        doc, left_rectangle_face, extrude_vector, left_rectangle_name)
    doc.recompute()
    # NOTE: left_rectangle_object seems to have a missing part,
    # but when fused below, the problem disappears.

    # Combine the left side with the existing top plate.
    new_top_plate_object = BOPTools.JoinFeatures.makeConnect(name=object_name)
    new_top_plate_object.Objects = [top_plate_object, left_rectangle_object]
    new_top_plate_object.Proxy.execute(new_top_plate_object)
    new_top_plate_object.purgeTouched()
    hide_children(new_top_plate_object)

    return new_top_plate_object


def get_vertices_of_rectangular_extension(top_plate_object, config):
    # Find the long edges of the top plate.
    longer_than = max(
        float(config.get("Keyboard", "SWITCH_LENGTH_X_MM")),
        float(config.get("Keyboard", "SWITCH_LENGTH_Y_MM")))
    long_edges = get_long_edges(top_plate_object, longer_than)
    #prints(f"TEST: found {len(long_edges)} long edges.", 3)

    # Half of the edges are from the bottom of the top plate and half
    # from the top (z coordinate is 0.0 or 3.0 and otherwise they're
    # the same). Filter out the ones with larger z.
    long_edges = list(filter(lambda e: isclose(e.Vertexes[0].Z, 0.0), long_edges))
    #prints(f"TEST: long edge zs: {[float('%.02f' % e.Vertexes[0].Z) for e in long_edges]}", 3)

    rim_vertices = get_rim_vertices(long_edges)
    #prints(f"TEST: rim vertices: {format_vertices(rim_vertices)}", 3)

    (min_x, min_y, min_z, max_x, max_y, max_z) = get_mins_maxes_from_vertices(rim_vertices)
    #prints(f"TEST: min_x: {min_x:.2f}; min_y: {min_y:.2f}; min_z: {min_z:.2f}")
    #prints(f"TEST: max_x: {max_x:.2f}; max_y: {max_y:.2f}; max_z: {max_z:.2f}")

    # There are two vertices with max_y, and the one with the
    # smaller x is the rightmost vertex that is needed.
    vertices_y_max = list(filter(lambda r: isclose(r.Y, max_y), rim_vertices))
    #prints(f"TEST: vertices with y_max: {format_vertices(vertices_y_max)}", 3)
    if len(vertices_y_max) != 2:
        raise Exception(f"Error: found {len(vertices_y_max)} max y vertices (should be two).")

    top_right_corner = vertices_y_max[0]
    if vertices_y_max[1].X < top_right_corner.X:
        top_right_corner = vertices_y_max[1]
    #prints(f"TEST: top right corner: {format_vertex(top_right_corner)}", 3)

    # The top right corner and all vertices to the left of it (so
    # with smaller x) are needed to remodel the top plate.
    corner_x = top_right_corner.X
    vertices = list(filter(lambda v: (v.X < corner_x) or isclose(v.X, corner_x), rim_vertices))
    #prints(f"TEST: vertices: {format_vertices(vertices)}", 3)
    vertices.sort(key=lambda v: v.Y)
    #prints(f"TEST: vertices sorted: {format_vertices(vertices)}", 3)

    # Add the corners that make the left side rectangular:
    vertices.append(Part.Vertex(min_x, max_y, min_z))
    vertices.append(Part.Vertex(min_x, min_y, min_z))
    #prints(f"TEST: vertices complete: {format_vertices(vertices)}", 3)

    if len(vertices) != 7:
        raise Exception(f"Error: got {len(vertices)} vertices (should be seven).")

    return vertices


"""
Tilts top plate so that the right side is higher than the left.
The angle needs to be negative to tilt it in the right direction.
"""
def tilt_top_plate(top_plate_object, config):
    tilt_angle = -float(config.get("Keyboard", "TOP_PLATE_TILT_ANGLE_DEG"))
    position = top_plate_object.Placement.Base
    # Rotate along y-axis (pitch).
    rotation = FreeCAD.Rotation(0.0, tilt_angle, 0.0) # Yaw, pitch, roll.
    # Rotate through lower leftmost edge. Getting the corner of
    # minimums works for this purpose.
    bound_box = top_plate_object.Shape.BoundBox
    centre = FreeCAD.Vector(bound_box.XMin, bound_box.YMin, bound_box.ZMin)
    top_plate_object.Placement = FreeCAD.Placement(
        position,
        rotation,
        centre)
    return tilt_angle


#----------------------------------------------------------------------x---------------------------
# The functions that create the bottom plate.


"""
The bottom plate is essentially a projection of the top plate's
outer rim onto the xy-plane.
"""
def create_bottom_plate(doc, config, top_plate, object_name):
    prints("Creating bottom plate...", 1)

    rim_vertices = get_rim_vertices_from_top_plate(top_plate, config)

    # Project the rim corners onto the xy-plane. First convert them
    # into vectors, because vertices can't be edited.
    corners = vertices_to_vectors(rim_vertices)
    for vector in corners:
        vector.z = 0.0
    #prints(f"TEST: {len(corners)} corners: {format_vectors(corners)}", 2)

    bottom_plate_face = make_face_from_corners(corners)
    extrude_vector = VECTOR_ONE_Z * float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    bottom_plate_object = make_solid_from_face(doc, bottom_plate_face, extrude_vector, object_name)
    doc.recompute()

    prints("Success.", 2)
    return bottom_plate_object


def get_rim_vertices_from_top_plate(top_plate, config):
    longer_than = max(
        float(config.get("Keyboard", "SWITCH_LENGTH_X_MM")),
        float(config.get("Keyboard", "SWITCH_LENGTH_Y_MM")))
    long_edges = get_long_edges(top_plate, longer_than)
    #prints(f"TEST: found {len(long_edges)} long edges.", 3)

    rim_vertices = get_rim_vertices(long_edges)
    #prints(f"TEST: {len(rim_vertices)} rim vertices: {format_vertices(rim_vertices)}", 3)

    (min_x, min_y, min_z, max_x, max_y, max_z) = get_mins_maxes_from_vertices(rim_vertices)
    #prints(f"TEST: min_x: {min_x:.2f}; min_y: {min_y:.2f}; min_z: {min_z:.2f}", 3)
    #prints(f"TEST: max_x: {max_x:.2f}; max_y: {max_y:.2f}; max_z: {max_z:.2f}", 3)

    vertices = select_bottom_plate_vertices(rim_vertices, min_x)

    # Switch the places of the last two vertices to order the rim
    # correctly.
    should_be_last = vertices[len(vertices) - 2]
    vertices[len(vertices) - 2] = vertices[len(vertices) - 1]
    vertices[len(vertices) - 1] = should_be_last
    #prints(f"TEST: {len(vertices)} vertices: {format_vertices(vertices)}", 3)

    return vertices


"""
Gets the correct top plate outer rim vertices for creating
the bottom plate.
(This could also be done by projecting each vertex of a pair up and
down along the z-axis and seeing if the resulting line intersects
with both the top and bottom face of the top plate; the wanted
vertex only intersects with one.)
"""
def select_bottom_plate_vertices(rim_vertices, min_x):
    # The vertices are sorted (first by y, then by x) into pairs.
    rim_vertices.sort(key=lambda v: v.X)
    rim_vertices.sort(key=lambda v: v.Y)

    # From one pair, the one with the larger x should be kept,
    # except for the two smallest x (min_x) pairs, where the
    # minimum x vertex should be kept.
    vertices = []
    i = 0
    while i < len(rim_vertices):
        vertex_0 = rim_vertices[i]
        vertex_1 = rim_vertices[i + 1]
        if isclose(vertex_0.X, min_x):
            vertices.append(vertex_0)
        elif isclose(vertex_1.X, min_x):
            vertices.append(vertex_1)
        elif vertex_0.X > vertex_1.X:
            vertices.append(vertex_0)
        else:
            vertices.append(vertex_1)
        i = i + 2
    #prints(f"TEST: {len(vertices)} vertices: {format_vertices(vertices)}", 4)
    return vertices


#----------------------------------------------------------------------x---------------------------
# The functions that create the four side walls between the top and
# bottom plates.


def create_side_walls(doc, config, top_plate, bottom_plate, object_name):
    prints("Creating side walls...", 1)

    bottom_plate_vertices = list(filter(
        lambda v: not isclose(v.Z, 0.0), bottom_plate.Shape.Vertexes))
    (min_x, min_y, min_z, max_x, max_y, max_z) = get_mins_maxes_from_vertices(
        bottom_plate_vertices)
    #prints(f"TEST: min_x: {min_x:.2f}; min_y: {min_y:.2f}; min_z: {min_z:.2f}", 2)
    #prints(f"TEST: max_x: {max_x:.2f}; max_y: {max_y:.2f}; max_z: {max_z:.2f}", 2)

    # For creating the long side wall at min_x (left), just the two
    # min_x vertices are needed.
    left_wall_vertices = list(filter(
        lambda v: isclose(v.X, min_x), bottom_plate_vertices))
    no_of_vs = len(left_wall_vertices)
    if no_of_vs != 2:
        raise Exception(f"Error: found {no_of_vs} min x vertices (should be two).")
    left_wall_object = create_left_side_wall(doc, config, left_wall_vertices, f"Left{object_name}")
    left_wall_vertices = left_wall_object.Shape.Vertexes
    prints("Created left side wall.", 2)

    new_top_plate_placement_vector = top_plate.Placement.Base
    raise_by = (float(config.get("Keyboard", "CASE_THICKNESS_MM"))
        + float(config.get("Keyboard", "LEFT_WALL_HEIGHT_MM")))
    new_top_plate_placement_vector.z = new_top_plate_placement_vector.z + raise_by
    top_plate.Placement.Base = new_top_plate_placement_vector
    doc.recompute()
    prints(f"Raised top plate by {raise_by:.2f} mm.", 2)

    top_wall_object = create_side_wall(doc, config, bottom_plate_vertices,
        left_wall_vertices, top_plate, max_y, f"Top{object_name}")
    prints("Created top side wall.", 2)

    bottom_left_wall_object = create_side_wall(doc, config, bottom_plate_vertices,
        left_wall_vertices, top_plate, min_y, f"BottomLeft{object_name}")
    prints("Created bottom left side wall.", 2)

    prints("TODO: create bottom right side wall.", 2)


def create_left_side_wall(doc, config, vertices, object_name):
    vertices.sort(key=lambda v: v.Y)
    height = float(config.get("Keyboard", "LEFT_WALL_HEIGHT_MM"))
    #half_kerf = float(config.get("General", "LASER_KERF_MM"))/2.0
    corners = []
    corners.append(FreeCAD.Vector(vertices[0].X, vertices[0].Y, vertices[0].Z + height))
    corners.append(FreeCAD.Vector(vertices[0].X, vertices[0].Y, vertices[0].Z))
    corners.append(FreeCAD.Vector(vertices[1].X, vertices[1].Y, vertices[1].Z))
    corners.append(FreeCAD.Vector(vertices[1].X, vertices[1].Y, vertices[1].Z + height))

    left_wall_face = make_face_from_corners(corners)
    extrude_vector = VECTOR_ONE_X * float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    left_wall_object = make_solid_from_face(doc, left_wall_face, extrude_vector, object_name)
    doc.recompute()
    return left_wall_object


"""
Creates a side wall at minimum/maximum y between the bottom plate, left side
wall and top plate.
Needed:
  1) From bottom plate: a min/max y vertex (the one with bigger x).
  2) From left wall: two top right (min/max y, bigger x) vertices.
  3) From top plate: two vertices with min/max y from the lower z edge.
"""
def create_side_wall(doc, config, bottom_plate_vertices, left_wall_vertices, top_plate,
        the_y, object_name):
    wall_vertices_1 = list(filter(
        lambda v: isclose(v.Y, the_y), bottom_plate_vertices))
    no_of_vs = len(wall_vertices_1)
    if no_of_vs != 2:
        raise Exception(f"Error: found {no_of_vs} y vertices (should be two).")
    wall_vertices_1.sort(key=lambda v: v.X)
    wall_vertices_1 = wall_vertices_1[1:]
    #prints(f"TEST: wall_vertices_1: {format_vertices(wall_vertices_1)}", 3)

    direction = 1
    start = 0
    end = 4
    if the_y > top_plate.Shape.CenterOfGravity.y:
        direction = -1
        start = len(left_wall_vertices) - 4
        end = len(left_wall_vertices)

    wall_vertices_2 = sorted(left_wall_vertices, key=lambda v: v.Y)[start:end]
    #prints(f"TEST: wall_vertices_2, 1: {format_vertices(wall_vertices_2)}", 3)
    wall_vertices_2 = sorted(wall_vertices_2, key=lambda v: v.X)[-2:]
    #prints(f"TEST: wall_vertices_2, 2: {format_vertices(wall_vertices_2)}", 3)
    wall_vertices_2.sort(key=lambda v: v.Z)

    longer_than = max(
        float(config.get("Keyboard", "SWITCH_LENGTH_X_MM")),
        float(config.get("Keyboard", "SWITCH_LENGTH_Y_MM")))
    top_plate_long_edges = get_long_edges(top_plate, longer_than)
    #prints(f"TEST: found {len(top_plate_long_edges)} long edges in top plate.", 3)
    top_plate_rim_vertices = get_rim_vertices(top_plate_long_edges)
    #prints(f"TEST: top_plate_rim_vertices: {format_vertices(top_plate_rim_vertices)}", 3)
    wall_vertices_3 = list(filter(
        lambda v: isclose(v.Y, the_y), top_plate_rim_vertices))
    no_of_vs = len(wall_vertices_3)
    if no_of_vs != 4:
        raise Exception(f"Error: found {no_of_vs} max y vertices (should be four).")
    wall_vertices_3.sort(key=lambda v: v.Z)
    # There are four vertices, sorted by z -> get first and third.
    wall_vertices_3 = [wall_vertices_3[0], wall_vertices_3[2]]

    wall_vertices = wall_vertices_1 + wall_vertices_2 + wall_vertices_3
    #prints(f"TEST: wall_vertices: {format_vertices(wall_vertices)}", 3)
    wall_face = make_face_from_corners(vertices_to_vectors(wall_vertices))
    extrude_vector = direction*VECTOR_ONE_Y * float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    wall_object = make_solid_from_face(doc, wall_face, extrude_vector, object_name)
    doc.recompute()

    return wall_object


#----------------------------------------------------------------------x---------------------------


main()
