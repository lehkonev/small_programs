"""
This macro creates a 3D model of a split keyboard case.
(The case is supposed to be laser-cut from 3 mm wood sheet.)
------------------------------------------------------------------------
FreeCAD version 1.0.0.
Python version 3.11.
"""

from draftgeoutils import geometry
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
LAYOUT_LEFT_THUMB = [
    (0, 2),  (1, 2),  (2, 2),
    (0, 1),  (1, 1),  (2, 1),
    (0, 0),  (1, 0),  (2, 0),
]

VECTOR_ZERO = FreeCAD.Vector(0.0, 0.0, 0.0)
VECTOR_ONE_X = FreeCAD.Vector(1.0, 0.0, 0.0)
VECTOR_ONE_Y = FreeCAD.Vector(0.0, 1.0, 0.0)
VECTOR_ONE_Z = FreeCAD.Vector(0.0, 0.0, 1.0)

# If START_AT_STEP is 0, create a new document. If it is not, try to
# find a file with a number one less than it from the macro directory.
# If not found, start at step 0.
START_AT_STEP = 8
# If STOP_AT_STEP is equal to or greater than the existing maximum step,
# all steps are performed. If it is below, only steps up to that
# step are performed.
STOP_AT_STEP = 8
STEPS = {
    0: "Creating document...",
    1: "Creating top plate switch holes...",
    2: "Creating top plate...",
    3: "Creating bottom plate...",
    4: "Creating side walls...",
    5: "Creating top thumb plate...",
    6: "Creating bottom thumb plate...",
    7: "Creating wrist support...",
    8: "Creating support structures...",
    9: "Creating enclosure that connects the halves...",
    10: "Creating and connecting right side...",
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
    while step < stop_before_step:
        prints(f"Step {step}: {STEPS[step]}", 1)

        match step:
            case 0:
                doc = create_document(base_document_name)
            case 1:
                switch_hole_list = create_switch_holes(doc, LAYOUT_LEFT, config, "SwitchHole")
                # Well, for various reasons, this did NOT work:
                #create_switch_hole_faces(config, LAYOUT_LEFT, None, VECTOR_ONE_X, VECTOR_ONE_Y)

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
                (left_wall, top_wall, bottom_left_wall, bottom_right_wall) = create_side_walls(
                    doc, config, objects["TopPlate"], objects["BottomPlate"], "SideWall")
                objects["LeftSideWall"] = left_wall
                objects["TopSideWall"] = top_wall
                objects["BottomLeftSideWall"] = bottom_left_wall
                objects["BottomRightSideWall"] = bottom_right_wall
            case 5:
                top_thumb_plate = create_top_thumb_plate(doc, config, objects["TopPlate"],
                    objects["BottomPlate"], "TopThumbPlate")
                objects["TopThumbPlate"] = top_thumb_plate
            case 6:
                bottom_thumb_plate = create_bottom_plate(doc, config, objects["TopThumbPlate"],
                    "BottomThumbPlate")
                objects["BottomThumbPlate"] = bottom_thumb_plate
            case 7:
                (connect, top, short, medium, long) = create_wrist_support(doc, config,
                    objects["BottomPlate"], "WristSupport")
                objects["WristSupportConnectBottom"] = connect
                objects["WristSupportTop"] = top
                objects["WristSupportShortSideWall"] = short
                objects["WristSupportMediumSideWall"] = medium
                objects["WristSupportLongSideWall"] = long
            case 8:
                (lower, upper) = create_top_plate_supports(doc, config,
                    objects["BottomLeftSideWall"], "TopPlateSupport")
                objects["TopPlateSupportLower"] = lower
                objects["TopPlateSupportUpper"] = upper
                (lower_support, upper_support) = create_thumb_plate_supports(doc, config,
                    objects["TopThumbPlate"], objects["BottomThumbPlate"], objects["TopPlate"],
                    "ThumbPlateSupport")
                objects["ThumbPlateSupportLower"] = lower_support
                objects["ThumbPlateSupportUpper"] = upper_support
            case bigger if bigger < len(STEPS):
                prints("TODO", 2)
            case _:
                break

        step = step + 1

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


def is_same_vector_vertex(v_1, v_2):
    if (v_1 is None) and (v_2 is None):
        return True
    elif (v_1 is None) or (v_2 is None):
        return False

    v_1_x = None
    v_1_y = None
    v_1_z = None
    v_2_x = None
    v_2_y = None
    v_2_z = None
    try:
        # Vector:
        v_1_x = v_1.x
        v_1_y = v_1.y
        v_1_z = v_1.z
    except:
        # Vertex:
        v_1_x = v_1.X
        v_1_y = v_1.Y
        v_1_z = v_1.Z
    try:
        v_2_x = v_2.x
        v_2_y = v_2.y
        v_2_z = v_2.z
    except:
        v_2_x = v_2.X
        v_2_y = v_2.Y
        v_2_z = v_2.Z

    if ((v_1_x is None) or (v_2_x is None) or (v_1_y is None)
            or (v_2_y is None) or (v_1_z is None) or (v_2_z is None)):
        raise Exception("Error: Could not compare vectors/vertices.")

    return isclose(v_1_x, v_2_x) and isclose(v_1_y, v_2_y) and isclose(v_1_z, v_2_z)


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


def get_long_edge_vertices(config, object):
    longer_than = get_longer_than(config)
    long_edges = get_long_edges(object, longer_than)
    #prints(f"TEST: found {len(long_edges)}.", 4)
    long_edge_vertices = get_rim_vertices(long_edges)
    return long_edge_vertices


def get_long_edges(object, longer_than):
    if (longer_than < 0) or isclose(longer_than, 0.0):
        raise Exception("Error: edge length comparison value has to be greater than 0.")

    edges = []
    try:
        edges = object.Shape.Edges
    except:
        edges = object.Edges
    long_edges = []
    i = 1
    for edge in edges:
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
# Keyboard creation utility functions.


def create_switch_hole_faces(config, layout, edge_corner, tangent_x, tangent_y):
    #kerf = config.get("General", "LASER_KERF_MM")
    (switch_x, switch_y, distance_x, distance_y) = get_switch_data(config)

    corner = VECTOR_ZERO
    if edge_corner is not None:
        edge_buffer = get_edge_buffer(config)
        corner = edge_corner + edge_buffer*(tangent_x+tangent_y)

    switch_holes = None
    i = 0
    for coordinate in layout:
        (placement_x, placement_y) = coordinate
        start_x = float(placement_x) * distance_x
        start_y = float(placement_y) * distance_y
        end_x = start_x + switch_x
        end_y = start_x + switch_y

        corners = []
        c1 = start_x*tangent_x + start_y*tangent_y
        c2 = (start_x+switch_x)*tangent_x + start_y*tangent_y
        c3 = (start_x+switch_x)*tangent_x + (start_y+switch_y)*tangent_y
        c4 = start_x*tangent_x + (start_y+switch_y)*tangent_y
        corners.append(corner + c1)
        corners.append(corner + c2)
        corners.append(corner + c3)
        corners.append(corner + c4)
        face = make_face_from_corners(corners)

        if switch_holes is None:
            switch_holes = face
        else:
            switch_holes = switch_holes.fuse(face)

        i = i + 1

    prints(f"Success: created {i} switch hole faces.", 2)
    return switch_holes


def get_bottom_face_attributes(plate):
    bottom_face = None
    bottom_normal = None
    bottom_tangent_1 = None
    bottom_tangent_2 = None
    longest_edge = 0.0
    # Get the normal and tangents of the bottom face of the plate.
    # Also the length of the longest edge of that face.
    for face in sorted(plate.Shape.Faces, key=lambda f: f.Area, reverse=True):
        face_normal = face.normalAt(0, 0)
        if face_normal.z < 0:
            bottom_face = face
            bottom_normal = face_normal
            (bottom_tangent_1, bottom_tangent_2) = face.tangentAt(0, 0)
            longest_edge = sorted(face.Edges, key=lambda f: f.Length, reverse=True)[0]
            break
    #prints(f"TEST: bottom_normal: {format_vector(bottom_normal)}", 3)
    #prints(f"TEST: bottom_tangent_1: {format_vector(bottom_tangent_1)}", 3)
    #prints(f"TEST: bottom_tangent_2: {format_vector(bottom_tangent_2)}", 3)
    #prints(f"TEST: longest_edge: {longest_edge.Length:.2f}", 3)
    return (bottom_face, bottom_normal, bottom_tangent_1, bottom_tangent_2, longest_edge)


def get_edge_buffer(config):
    # Edge buffer should be:
    #   1) at least the length from the edge of the switch to the
    #      edge of the key cap,
    #   2) plus the thickness of the case material because a wall
    #      will most likely be right under the edge and
    #   3) maybe some extra.
    (switch_x, switch_y, distance_x, distance_y) = get_switch_data(config)
    min_distance_x = (distance_x-switch_x) / 2.0
    min_distance_y = (distance_y-switch_y) / 2.0
    min_distance = max(min_distance_x, min_distance_y)
    thickness = float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    extra = float(config.get("Keyboard", "PLATE_EXTRA_MM"))
    return min_distance + thickness + extra


def get_longer_than(config):
    longer_than = max(
        float(config.get("Keyboard", "SWITCH_LENGTH_X_MM")),
        float(config.get("Keyboard", "SWITCH_LENGTH_Y_MM")))
    return longer_than


def get_switch_data(config):
    switch_x = float(config.get("Keyboard", "SWITCH_LENGTH_X_MM"))
    switch_y = float(config.get("Keyboard", "SWITCH_LENGTH_Y_MM"))
    distance_x = float(config.get("Keyboard", "SWITCH_DISTANCE_X_MM"))
    distance_y = float(config.get("Keyboard", "SWITCH_DISTANCE_Y_MM"))
    return (switch_x, switch_y, distance_x, distance_y)


def get_wrist_support_dimensions(config):
    length_x = float(config.get("Keyboard", "WRIST_SUPPORT_LENGTH_X_MM"))
    length_y = float(config.get("Keyboard", "WRIST_SUPPORT_LENGTH_Y_MM"))
    corner_cut_x = float(config.get("Keyboard", "WRIST_SUPPORT_CORNER_CUT_X_MM"))
    corner_cut_y = float(config.get("Keyboard", "WRIST_SUPPORT_CORNER_CUT_Y_MM"))
    return (length_x, length_y, corner_cut_x, corner_cut_y)


def get_wrist_support_height(config):
    return (float(config.get("Keyboard", "WRIST_SUPPORT_WALL_HEIGHT_MM"))
        + float(config.get("Keyboard", "CASE_THICKNESS_MM")))


"""
Finds the bottom edge of an object. Assumes that there is only one and
that both of the edge's vertices have the same min z value.
"""
def find_min_z_edge_of_plate(long, plate):
    long_edges = get_long_edges(plate, long)
    bottom_edge = None
    min_z = None
    for edge in long_edges:
        edge_z = edge.Vertexes[0].Z
        if min_z is None:
            min_z = edge_z
        else:
            min_z = min(min_z, edge_z)

        if isclose(edge.Vertexes[0].Z, min_z) and isclose(edge.Vertexes[1].Z, min_z):
            bottom_edge = edge

    if bottom_edge is None:
        raise Exception("Error: could not find bottom edge of top thumb plate.")

    #prints(f"TEST: bottom_edge: {format_vertices(bottom_edge.Vertexes)}", 3)
    return bottom_edge


def find_second_to_max_x_of_switches(config, switch_plate):
    thickness = float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    longer_edges = get_long_edges(switch_plate, thickness)
    not_longer = get_longer_than(config)
    edges = list(filter(
        lambda e: isclose(e.Length, not_longer) or (e.Length < not_longer),
        longer_edges))
    max_x_vertex = Part.Vertex(0.0, 0.0, 0.0)
    second_to_max_x_vertex = None
    for edge in edges:
        for vertex in edge.Vertexes:
            if vertex.X > max_x_vertex.X:
                second_to_max_x_vertex = max_x_vertex
                max_x_vertex = vertex
    #prints(f"TEST: second_to_max_x_vertex: {format_vertex(second_to_max_x_vertex)}", 3)
    #prints(f"TEST: max_x_vertex: {format_vertex(max_x_vertex)}", 3)
    return second_to_max_x_vertex


#----------------------------------------------------------------------x---------------------------
# The functions that create the top plate.


def create_switch_holes(doc, layout, config, object_name):
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
    expand_by = switch_hypotenuse/2.0 + get_edge_buffer(config)
    #prints(f"TEST: expand_by: {expand_by:.2f}.", 2)
    return expand_by


def make_switch_holes(doc, base_object, switch_holes, object_name):
    # Group/fuse the switch holes.
    switches_name = f"{object_name}SwitchHoles"
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

    if "Thumb" in top_plate.Name:
        return select_bottom_thumb_plate_vertices(rim_vertices, max_z, min_z, min_y)
    else:
        return select_bottom_plate_vertices(rim_vertices, min_x)


"""
Gets the correct top plate outer rim vertices for creating
the bottom thumb plate.
"""
def select_bottom_thumb_plate_vertices(rim_vertices, max_z, min_z, min_y):
    rim_vertices.sort(key=lambda v: v.Y)
    rim_vertices.sort(key=lambda v: v.Z)

    # Discard the min_z vertex that is near min_y and the
    # max_z vertex, so the first and last ones in the list.
    vertices = rim_vertices[1:-1]
    #prints(f"TEST: {len(vertices)} vertices: {format_vertices(vertices)}", 4)

    # Switch the places of the last and third last vertices
    # to order the rim correctly.
    vertices.sort(key=lambda v: v.Y)
    should_be_last = vertices[len(vertices) - 3]
    vertices[len(vertices) - 3] = vertices[len(vertices) - 1]
    vertices[len(vertices) - 1] = should_be_last
    #prints(f"TEST: {len(vertices)} vertices: {format_vertices(vertices)}", 4)

    return vertices


"""
Gets the correct top plate outer rim vertices for creating
the bottom plate.
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

    # Switch the places of the last two vertices to order the rim
    # correctly.
    should_be_last = vertices[len(vertices) - 2]
    vertices[len(vertices) - 2] = vertices[len(vertices) - 1]
    vertices[len(vertices) - 1] = should_be_last
    #prints(f"TEST: {len(vertices)} vertices: {format_vertices(vertices)}", 4)

    return vertices


#----------------------------------------------------------------------x---------------------------
# The functions that create the four side walls between the top and
# bottom plates.


def create_side_walls(doc, config, top_plate, bottom_plate, object_name):
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

    bottom_right_wall_object = create_bottom_right_side_wall(doc, config, top_plate,
        bottom_left_wall_object, f"BottomRight{object_name}")
    prints("Created bottom right side wall.", 2)

    prints("Success.", 2)
    return (left_wall_object, top_wall_object, bottom_left_wall_object, bottom_right_wall_object)


"""
Creates a rectangular side wall at minimum x, between the top and
bottom plates. The top plate's smallest z edge will rest on this wall.
"""
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

    top_plate_rim_vertices = get_long_edge_vertices(config, top_plate)
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


def create_bottom_right_side_wall(doc, config, top_plate, bottom_left_wall, object_name):
    # From the top plate, first take the six vertices with smallest y.
    top_plate_rim_vertices = get_long_edge_vertices(config, top_plate)
    wall_vertices_1 = (sorted(top_plate_rim_vertices, key=lambda v: v.Y))[:6]
    # Then take two with largest x.
    wall_vertices_1 = (sorted(wall_vertices_1, key=lambda v: v.X))[-2:]
    # Finally, take the one with smaller z.
    wall_vertices_1 = (sorted(wall_vertices_1, key=lambda v: v.Z))[:1]
    # Append the lower z vertex.
    wall_vertices_1.append(Part.Vertex(wall_vertices_1[0].X, wall_vertices_1[0].Y, 3.0))

    # From bottom_left_wall_vertices, take two vertices with largest x and smallest y.
    wall_vertices_2 = (sorted(bottom_left_wall.Shape.Vertexes, key=lambda v: v.X))[-4:]
    wall_vertices_2 = (sorted(wall_vertices_2, key=lambda v: v.Y))[:2]
    wall_vertices_2.sort(key=lambda v: v.Z)

    wall_vertices = wall_vertices_1 + wall_vertices_2
    #prints(f"TEST: wall_vertices: {format_vertices(wall_vertices)}", 3)

    bottom_right_wall_face = make_face_from_corners(vertices_to_vectors(wall_vertices))
    # The extrude direction is either the face's normal or its negation.
    direction = bottom_right_wall_face.normalAt(0, 0)
    if direction.x > 0:
        direction = -direction
    extrude_vector = direction * float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    bottom_right_wall_object = make_solid_from_face(doc, bottom_right_wall_face,
        extrude_vector, f"{object_name}Untrimmed")
    doc.recompute()

    # The bottom right side wall's larger z and smaller x sides cut
    # into the top plate and bottom left side wall respectively,
    # so it needs to be trimmed.
    bottom_right_wall_object = trim_bottom_right_side_wall(doc, config,
        bottom_right_wall_object, top_plate, bottom_left_wall, object_name)

    return bottom_right_wall_object


def trim_bottom_right_side_wall(doc, config, bottom_right_wall, top_plate, bottom_left_wall,
        object_name):
    remove_name = bottom_right_wall.Name
    thickness = float(config.get("Keyboard", "CASE_THICKNESS_MM"))

    # First, make crude trims.
    # This leaves the larger z side face slightly slanted:
    bottom_right_wall_new_shape = bottom_right_wall.Shape.cut(top_plate.Shape)
    # This leaves a corner in the smaller x side face:
    bottom_right_wall_new_shape = bottom_right_wall_new_shape.cut(bottom_left_wall.Shape)
    #half_trimmed_TEST = doc.addObject("Part::Feature", f"{object_name}HalfTrimmedTEST")
    #half_trimmed_TEST.Shape = bottom_right_wall_new_shape

    # Make a box that can be used to fully trim the smaller x side.
    cut_shape = make_bottom_right_side_wall_cut_shape(doc, bottom_right_wall_new_shape,
        thickness, object_name)
    bottom_right_wall_new_shape = bottom_right_wall_new_shape.cut(cut_shape)
    #trimmed_TEST = doc.addObject("Part::Feature", f"{object_name}TrimmedTEST")
    #trimmed_TEST.Shape = bottom_right_wall_new_shape

    # Then take the second to largest face and extrude that into the negative of its normal.
    face = sorted(bottom_right_wall_new_shape.Faces, key=lambda f: f.Area, reverse=True)[1]
    direction = -(face.normalAt(0, 0))
    extrude_vector = direction * float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    bottom_right_wall_object = make_solid_from_face(doc, face, extrude_vector, object_name)

    # Finally, delete the original bottom right wall.
    doc.removeObject(remove_name)
    doc.recompute()

    return bottom_right_wall_object


def make_bottom_right_side_wall_cut_shape(doc, shape, thickness, object_name):
    # The two shortest edges have the vertices that can be used to
    # create the cutoff shape.
    edges = sorted(shape.Edges, key=lambda e: e.Length)
    #for edge_TEST in edges:
        #prints(f"TEST: edge length: {edge_TEST.Length:.2f}", 3)
    short_edges = edges[:2]

    # The correct vertices are the ones with larger x.
    vectors = []
    for edge in short_edges:
        vertex = edge.Vertexes[0]
        if edge.Vertexes[1].X > vertex.X:
            vertex = edge.Vertexes[1]
        vector = vertex_to_vector(vertex)

        # The larger z needs to be made a little larger (exact size
        # is not necessary).
        if not isclose(vector.z, thickness):
            vector.z = vector.z + thickness
        vectors.append(vector)
    #prints(f"TEST: short edge vectors: {format_vectors(vectors)}", 3)
    if len(vectors) != 2:
        raise Exception(f"Error: got {len(vectors)} short edge vectors (should be two).")

    # Use the normal of the largest face to calculate corners for the
    # face that can be used to make a trimming shape.
    faces = sorted(shape.Faces, key=lambda f: f.Area, reverse=True)
    direction = faces[0].normalAt(0, 0) * thickness
    corners = []
    for vector in vectors:
        corners.append(vector + direction)
        corners.append(vector - direction)
        direction = -direction
    #prints(f"TEST: cut-block vectors: {format_vectors(corners)}", 3)

    cut_face = make_face_from_corners(corners)
    #face_TEST = doc.addObject("Part::Feature", f"{object_name}FaceTEST")
    #face_TEST.Shape = cut_face
    direction = cut_face.normalAt(0, 0)
    if direction.x > 0:
        direction = -direction
    extrude_vector = direction * thickness
    cut_shape = cut_face.extrude(extrude_vector)
    #cut_TEST = make_solid_from_face(doc, cut_face, extrude_vector, f"{object_name}CutShapeTEST")

    return cut_shape


#----------------------------------------------------------------------x---------------------------
# The functions that create the top plate for thumb switches.


def create_top_thumb_plate(doc, config, top_plate, bottom_plate, object_name):
    # Create the base thumb plate.
    prints("Making the face of the thumb plate base...", 2)
    thumb_base_face = make_thumb_plate_base_face(doc, config, top_plate)
    #thumb_base_face_TEST = doc.addObject("Part::Feature", f"{object_name}BaseTEST")
    #thumb_base_face_TEST.Shape = thumb_base_face
    prints("Success.", 3)

    # The origin corner for the switch holes is the one with smallest x.
    edge_corner = sorted(thumb_base_face.Vertexes, key=lambda v: v.X)[0]
    (tangent_1, tangent_2) = thumb_base_face.tangentAt(0, 0)
    # Is there a better way to get suitable tangents than just knowing?
    tangent_x = -tangent_2
    tangent_y = -tangent_1
    #prints(f"TEST: tangent_x: {format_vector(tangent_x)}, tangent_y: {format_vector(tangent_y)}.", 2)

    # Nudge the origin corner a little to the "y" direction to give
    # more space for the switches.
    edge_corner = (vertex_to_vector(edge_corner)
        + float(config.get("Keyboard", "THUMB_PLATE_EXTRA_Y_MM"))*tangent_y)

    switch_hole_faces = create_switch_hole_faces(config, LAYOUT_LEFT_THUMB,
        edge_corner, tangent_x, tangent_y)
    #thumb_switches_TEST = doc.addObject("Part::Feature", f"{object_name}SwitchesTEST")
    #thumb_switches_TEST.Shape = switch_hole_faces

    thumb_plate_face = thumb_base_face.cut(switch_hole_faces)
    type = thumb_plate_face.ShapeType
    if type != "Face":
        prints(f"Resulting thumb_plate_face is a '{type}'; extract a face.", 2)
        thumb_plate_face = thumb_plate_face.Faces[0]
    #thumb_plate_TEST = doc.addObject("Part::Feature", f"{object_name}TEST")
    #thumb_plate_TEST.Shape = thumb_plate_face
    prints("Made switch holes into thumb plate base.", 2)

    normal = thumb_plate_face.normalAt(0, 0)
    if normal.x < 0:
        normal = -normal
    extrude_vector = float(config.get("Keyboard", "CASE_THICKNESS_MM")) * normal
    thumb_plate = make_solid_from_face(doc, thumb_plate_face, extrude_vector, object_name)
    prints("Success.", 2)

    return thumb_plate


def make_thumb_plate_base_face(doc, config, top_plate):
    (thumb_edge, max_z) = find_thumb_edge(config, top_plate)
    prints("Found thumb edge.", 3)

    # Find the normal of the bottom face of the top plate.
    bottom_face_normal = None
    faces = sorted(top_plate.Shape.Faces, key=lambda f: f.Area, reverse=True)
    for f in faces:
        normal = f.normalAt(0, 0)
        # The wanted normal points "down" (negative z).
        if normal.z < 0:
            bottom_face_normal = normal
            break
    if bottom_face_normal is None:
        raise Exception("Error: could not find the normal of the bottom side of the top plate.")
    #prints(f"TEST: normal of top plate bottom: {format_vector(bottom_face_normal)}", 3)

    # Make a crude estimate of how far down the edge should be extruded.
    extrude_distance = 2 * max_z

    # Extrude the edge into the same direction as the top plate's
    # bottom face normal to get a starting 90 degree angle between
    # the top plate and the thumb plate.
    thumb_face_shape = thumb_edge.extrude(extrude_distance * bottom_face_normal)
    prints("Made the face of thumb plate base.", 3)

    # Use one of the edge's vertices as a base point.
    base_point = vertex_to_vector(thumb_edge.Vertexes[0])
    # Rotate the face around the edge (edge's tangent is an axis).
    degrees = float(config.get("Keyboard", "THUMB_PLATE_TILT_ANGLE_DEG"))
    thumb_face_shape.rotate(base_point, thumb_edge.tangentAt(0), degrees)
    prints(f"Tilted thumb plate base {degrees:.2f} degrees.", 3)

    thumb_face = trim_thumb_plate_base_face(config, thumb_face_shape)
    prints(f"Trimmed thumb plate base.", 3)

    # The face is a shell after the cut? Return the first (and only)
    # face in its shape then.
    if thumb_face.ShapeType != "Face":
        prints(f"Resulting thumb_face is a '{thumb_face.ShapeType}'; extract a face.", 3)
        thumb_face = thumb_face.Faces[0]
    return thumb_face


"""
Finds the edge of the top plate where the thumb plate should attach.
The edge has a maximum x vertex but no maximum y vertex.
"""
def find_thumb_edge(config, top_plate):
    longer_than = get_longer_than(config)
    long_edges = get_long_edges(top_plate, longer_than)
    rim_vertices = get_rim_vertices(long_edges)
    (min_x, min_y, min_z, max_x, max_y, max_z) = get_mins_maxes_from_vertices(rim_vertices)

    thumb_edge = None
    for e in long_edges:
        # The edge is attached to maximum x.
        if isclose(e.Vertexes[0].X, max_x) or isclose(e.Vertexes[1].X, max_x):
            # The right one is not attached to maximum y.
            if not (isclose(e.Vertexes[0].Y, max_y) or isclose(e.Vertexes[1].Y, max_y)):
                thumb_edge = e
                break

    if thumb_edge is None:
        raise Exception("Error: could not find thumb edge on top plate.")

    #prints(f"TEST: thumb_edge: {format_vertices(thumb_edge.Vertexes)}", 3)
    return (thumb_edge, max_z)


"""
Trims off the part of the face that goes below CASE_THICKNESS_MM
on the z-axis.
"""
def trim_thumb_plate_base_face(config, thumb_face_shape):
    thickness = float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    bound_box = thumb_face_shape.BoundBox

    corners = []
    corners.append(FreeCAD.Vector(bound_box.XMin, bound_box.YMin, thickness))
    corners.append(FreeCAD.Vector(bound_box.XMax, bound_box.YMin, thickness))
    corners.append(FreeCAD.Vector(bound_box.XMax, bound_box.YMax, thickness))
    corners.append(FreeCAD.Vector(bound_box.XMin, bound_box.YMax, thickness))
    trim_box_face = make_face_from_corners(corners)

    trim_box = trim_box_face.extrude((bound_box.ZMin-thickness) * VECTOR_ONE_Z)
    thumb_face = thumb_face_shape.cut(trim_box)

    return thumb_face


#----------------------------------------------------------------------x---------------------------
# The functions that create the wrist support piece.


def create_wrist_support(doc, config, bottom_plate, object_name):
    prints("Creating the connecting piece...", 2)
    connect_object = create_wrist_support_connect(doc, config, bottom_plate,
        f"{object_name}Connect")

    prints("Creating the bottom piece...", 2)
    (support_bottom_object, short_wall_corners, medium_wall_corners, long_wall_corners) \
        = create_wrist_support_bottom(doc, config, connect_object, f"{object_name}Bottom")

    prints("Creating the top piece...", 2)
    support_top_object = create_wrist_support_top(doc, config, support_bottom_object,
        f"{object_name}Top")

    prints("Creating side walls...", 2)
    centre = support_bottom_object.Shape.CenterOfGravity
    short_side_wall_object = create_wrist_support_side_wall(doc, config,
        short_wall_corners, centre, f"{object_name}ShortSideWall")
    medium_side_wall_object = create_wrist_support_side_wall(doc, config,
        medium_wall_corners, centre, f"{object_name}MediumSideWall")
    long_side_wall_object = create_wrist_support_side_wall(doc, config,
        long_wall_corners, centre, f"{object_name}LongSideWall")

    # TODO: This conserves the edges/vertices inside the shape, how to remove?
    prints(f"Fusing connection and bottom pieces...", 2)
    fused = connect_object.Shape.fuse(support_bottom_object.Shape)
    connect_bottom_object = doc.addObject("Part::Feature", f"{object_name}ConnectBottom")
    connect_bottom_object.Shape = fused
    doc.removeObject(f"{object_name}Bottom")
    doc.removeObject(f"{object_name}Connect")
    prints(f"Success: created {object_name}ConnectBottom.", 3)

    return (connect_bottom_object, support_top_object, short_side_wall_object,
        medium_side_wall_object, long_side_wall_object)


def create_wrist_support_connect(doc, config, bottom_plate, object_name):
    # Find the vertices where the support will mainly attach.
    smaller_y_vertices = (sorted(bottom_plate.Shape.Vertexes, key=lambda v: v.Y))[:6]
    larger_x_vertices = (sorted(smaller_y_vertices, key=lambda v: v.X, reverse=True))[:4]
    starting_vertices = (sorted(larger_x_vertices, key=lambda v: v.Z))[:2]
    #prints(f"TEST: starting_vertices: {format_vertices(starting_vertices)}", 3)
    if len(starting_vertices) != 2:
        raise Exception(f"Error: got {len(starting_vertices)} starting vertices (should be two).")

    # Find the corresponding side face of the bottom plate.
    starting_face = None
    f = 0
    for face in bottom_plate.Shape.Faces:
        #prints(f"TEST: face {f}:", 3)
        f = f + 1
        sames = 0
        v = 0
        for vertex in face.Vertexes:
            if (is_same_vector_vertex(starting_vertices[0], vertex)
                    or is_same_vector_vertex(starting_vertices[1], vertex)):
                sames = sames + 1
            #prints(f"TEST: vertex {v}, sames: {sames}", 4)
            v = v + 1
        if sames == 2:
            starting_face = face
            break

    if starting_face is None:
        raise Exception("Error: could not find starting face on bottom plate.")

    normal = starting_face.normalAt(0, 0)
    if normal.x < 0:
        normal = -normal
    size = (float(config.get("Keyboard", "WRIST_CONNECT_LENGTH_Y_MM"))
        + float(config.get("Keyboard", "WRIST_SUPPORT_LENGTH_Y_MM")))
    connect_object = make_solid_from_face(doc, starting_face, (size * normal),
        f"{object_name}")

    prints(f"Success.", 3)
    return connect_object


def create_wrist_support_bottom(doc, config, connect_object, object_name):
    # Find the directions where to create the corners.
    direction_x = None
    direction_y = None
    for face in connect_object.Shape.Faces:
        normal = face.normalAt(0, 0)
        if (normal.x < 0) and (normal.y < 0):
            direction_x = normal
        elif (normal.x < 0) and (normal.y > 0):
            direction_y = normal

    if (direction_x is None) or (direction_y is None):
        raise Exception("Error: could not find direction x or y from the faces.")

    # Find the origin corner.
    max_x_vertex = (sorted(connect_object.Shape.Vertexes, key=lambda v: v.X, reverse=True))[0]

    # The starting corner has a displacement.
    displacement = float(config.get("Keyboard", "WRIST_SUPPORT_DISPLACE_X_MM")) * direction_x
    max_x_corner = vertex_to_vector(max_x_vertex) + displacement
    max_x_corner.z = 0.0 # Just in case.

    (length_x, length_y, corner_cut_x, corner_cut_y) = get_wrist_support_dimensions(config)
    corners = []
    min_y_corner = max_x_corner + length_x*direction_x
    min_x_corner = max_x_corner + length_x*direction_x + length_y*direction_y
    max_y_corner = max_x_corner + corner_cut_x*direction_x + length_y*direction_y
    cut_x_corner = max_x_corner + corner_cut_y*direction_y
    corners = [max_x_corner, min_y_corner, min_x_corner, max_y_corner, cut_x_corner]
    support_bottom_face = make_face_from_corners(corners)
    thickness = float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    extrude_vector = thickness * VECTOR_ONE_Z
    support_bottom_object = make_solid_from_face(doc, support_bottom_face, extrude_vector,
        f"{object_name}")

    # Save the corners for side walls.
    short_wall_corners = [min_y_corner, min_x_corner]
    medium_wall_corners = [min_x_corner - thickness*direction_x, max_y_corner]
    long_wall_corners = [min_y_corner - thickness*direction_x, max_x_corner]

    prints(f"Success.", 3)
    return (support_bottom_object, short_wall_corners, medium_wall_corners, long_wall_corners)


def create_wrist_support_top(doc, config, support_bottom_object, object_name):
    support_top_shape = support_bottom_object.Shape.copy()
    support_top_object = doc.addObject("Part::Feature", f"{object_name}")
    support_top_object.Shape = support_top_shape
    top_place = get_wrist_support_height(config)
    top_place = top_place + float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    support_top_object.Placement.Base = support_top_object.Placement.Base + top_place*VECTOR_ONE_Z
    prints(f"Success: created {object_name}.", 3)
    return support_top_object


def create_wrist_support_side_wall(doc, config, wall_corners, centre, object_name):
    thickness = float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    height = get_wrist_support_height(config)
    for c in wall_corners:
        c.z = thickness

    corners = [
        wall_corners[0] + height*VECTOR_ONE_Z,
        wall_corners[0],
        wall_corners[1],
        wall_corners[1] + height*VECTOR_ONE_Z,
        ]
    side_wall_face = make_face_from_corners(corners)

    normal = side_wall_face.normalAt(0, 0)
    #prints(f"TEST: {object_name} normal: {format_vector(normal)}", 3)
    face_centre_minus = side_wall_face.CenterOfGravity - normal
    face_centre_plus = side_wall_face.CenterOfGravity + normal
    distance_minus = centre.distanceToPoint(face_centre_minus)
    distance_plus = centre.distanceToPoint(face_centre_plus)
    #prints(f"TEST: distance_minus: {distance_minus:.2f}; distance_plus: {distance_plus:.2f}", 3)
    if distance_minus < distance_plus:
        normal = -normal
    extrude_vector = thickness * normal
    side_wall_object = make_solid_from_face(doc, side_wall_face, extrude_vector, object_name)

    prints(f"Success: created {object_name}.", 3)
    return side_wall_object


#----------------------------------------------------------------------x---------------------------
# The functions that create support structures.


def create_top_plate_supports(doc, config, bottom_left_wall, object_name):
    prints("Creating top plate supports...", 2)
    # Create the support structures; they're copies of the bottom
    # left side wall but not as long in the positive x direction.
    support_lower_y_shape = bottom_left_wall.Shape.copy()
    support_upper_y_shape = bottom_left_wall.Shape.copy()

    # To calculate the minimum x coordinate of the shape that trims the
    # supports, take the minimum x vertex of the original shape and add
    # the wanted length to it.
    min_vertex = (sorted(bottom_left_wall.Shape.Vertexes, key=lambda v: v.X))[0]
    min_x = min_vertex.X
    trim_start_lower = min_x + float(config.get("Keyboard", "TOP_PLATE_LOWER_SUPPORT_LENGTH_X_MM"))
    trim_start_upper = min_x + float(config.get("Keyboard", "TOP_PLATE_UPPER_SUPPORT_LENGTH_X_MM"))
    # The rest of the shape can just be a big box; just take the
    # biggest length of the original structure.
    sorted_edges = sorted(bottom_left_wall.Shape.Edges, key=lambda e: e.Length, reverse=True)
    dimension = sorted_edges[0].Length
    # Create the corners for the trim boxes.
    corners_lower = [
        FreeCAD.Vector(trim_start_lower, min_vertex.Y - dimension, min_vertex.Z + dimension),
        FreeCAD.Vector(trim_start_lower, min_vertex.Y - dimension, min_vertex.Z - dimension),
        FreeCAD.Vector(trim_start_lower, min_vertex.Y + dimension, min_vertex.Z - dimension),
        FreeCAD.Vector(trim_start_lower, min_vertex.Y + dimension, min_vertex.Z + dimension),
        ]
    corners_upper = []
    for corner in corners_lower:
        vector = FreeCAD.Vector(trim_start_upper, corner.y, corner.z)
        corners_upper.append(vector)
    lower_face = make_face_from_corners(corners_lower)
    upper_face = make_face_from_corners(corners_upper)
    lower_trim_box = lower_face.extrude(dimension * VECTOR_ONE_X)
    upper_trim_box = upper_face.extrude(dimension * VECTOR_ONE_X)
    # Perform the trim.
    support_lower_y_shape = support_lower_y_shape.cut(lower_trim_box)
    support_upper_y_shape = support_upper_y_shape.cut(upper_trim_box)

    # Create the objects.
    support_lower_y = doc.addObject("Part::Feature", f"{object_name}Lower")
    support_upper_y = doc.addObject("Part::Feature", f"{object_name}Upper")
    support_lower_y.Shape = support_lower_y_shape
    support_upper_y.Shape = support_upper_y_shape

    # Move them to the correct place.
    lower_place = float(config.get("Keyboard", "TOP_PLATE_LOWER_SUPPORT_DISTANCE_Y_MM"))
    upper_place = float(config.get("Keyboard", "TOP_PLATE_UPPER_SUPPORT_DISTANCE_Y_MM"))
    support_lower_y.Placement.Base = support_lower_y.Placement.Base + lower_place*VECTOR_ONE_Y
    support_upper_y.Placement.Base = support_upper_y.Placement.Base + upper_place*VECTOR_ONE_Y

    prints(f"Success: created {object_name}s.", 3)
    return (support_lower_y, support_upper_y)


def create_thumb_plate_supports(doc, config, top_thumb_plate, bottom_thumb_plate, top_plate, object_name):
    prints("Creating top thumb plate supports...", 2)
    lower_support = create_lower_edge_thumb_plate_support(doc, config, top_thumb_plate,
        f"{object_name}Lower")
    upper_support = create_upper_edge_thumb_plate_support(doc, config, top_thumb_plate,
        bottom_thumb_plate, f"{object_name}Upper")

    # If the top thumb plate doesn't have switch holes in the upper y
    # area, the upper support might cut into the top plate. Check if
    # this is the case and then trim the upper support. If it is
    # trimmed, one vertex of the upper support touches the top plate
    # (but not in reality because the corner is so sharp that enough
    # of it will be lost due to kerf.)
    upper_support = trim_upper_support(doc, config, top_plate, upper_support,
        f"{object_name}Upper")

    (lower_stopper, upper_stopper) = create_thumb_plate_stoppers(doc, config, top_thumb_plate, bottom_thumb_plate, upper_support, f"{object_name}Stopper")

    return (lower_support, upper_support)


def create_lower_edge_thumb_plate_support(doc, config, top_plate, object_name):
    # The lower (smaller y) support will be under the shorter, more
    # vertical edge of the bottom of the top thumb plate.
    min_x_vertex = sorted(top_plate.Shape.Vertexes, key=lambda v: v.X)[0]
    min_z_vertices = sorted(top_plate.Shape.Vertexes, key=lambda v: v.Z)[:2]
    min_y_vertex = sorted(min_z_vertices, key=lambda v: v.Y)[0]
    z_vertex = Part.Vertex(min_x_vertex.X, min_x_vertex.Y, min_y_vertex.Z)
    corners = [
        min_x_vertex,
        min_y_vertex,
        z_vertex,
        ]
    lower_support_face = make_face_from_corners(vertices_to_vectors(corners))
    #lower_support_TEST = doc.addObject("Part::Feature", f"{object_name}TEST")
    #lower_support_TEST.Shape = lower_support_face
    normal = lower_support_face.normalAt(0, 0)
    thickness = float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    lower_support_shape_1 = lower_support_face.extrude(thickness/2.0 * normal)
    lower_support_shape_2 = lower_support_face.extrude(thickness/2.0 * -normal)
    # TODO: This fusion also retains the original edges...
    lower_support_shape = lower_support_shape_1.fuse(lower_support_shape_2)
    lower_support = doc.addObject("Part::Feature", f"{object_name}")
    lower_support.Shape = lower_support_shape

    prints(f"Success: created {object_name}.", 3)
    return lower_support


def create_upper_edge_thumb_plate_support(doc, config, top_plate, bottom_plate, object_name):
    # The upper (bigger y) support will have an upper face that is
    # parallel to be bottom face of the top thumb plate, so it will
    # be at an angle compared to the lower edge support.

    # First, find the vertex of the switch holes with maximum x
    # and the one just before it; the support needs to be some
    # distance away from it so it doesn't disturb the switch.
    second_to_max_x_vertex = find_second_to_max_x_of_switches(config, top_plate)

    (bottom_face, bottom_normal, bottom_tangent_1, bottom_tangent_2, longest_edge) \
        = get_bottom_face_attributes(top_plate)


    # Displace the (non-)starting point.
    thickness = float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    displacement = get_edge_buffer(config) + thickness
    non_starting_point = second_to_max_x_vertex
    # TODO: Any way to find out which way to point the tangents?
    non_starting_point.Placement.Base = (non_starting_point.Placement.Base
        + (displacement*(-bottom_tangent_1-bottom_tangent_2).normalize()))

    # Find the lowest edge of the top thumb plate;
    # the support will be perpendicular to it.
    long = get_longer_than(config)
    bottom_edge = find_min_z_edge_of_plate(long, top_plate)

    # Get a vector that is parallel to the bottom face of the top
    # thumb plate and tells the distance from the (non-)starting
    # point to the bottom edge.
    (top_face_vector, number) = geometry.findPerpendicular(
        vertex_to_vector(second_to_max_x_vertex), [bottom_edge])
    if top_face_vector.z < 0:
        top_face_vector = -top_face_vector
    #prints(f"TEST: top_face_vector: {format_vector(top_face_vector)}", 3)
    # Make a copy to prevent top_face_vector from being altered.
    top_face_direction = FreeCAD.Vector(top_face_vector)
    top_face_direction.normalize()

    # The edge from the (non-)starting point to the bottom edge
    # contains one corner point of the support structure.
    edge_to_bottom_edge = non_starting_point.extrude(-top_face_vector)
    # Make the edge from the (non-)starting point up along the
    # bottom face of the top thumb plate long enough so that the
    # actual max z point can be found.
    edge_to_top_edge = non_starting_point.extrude(longest_edge.Length * top_face_direction)
    #edge_TEST = edge_to_bottom_edge.fuse(edge_to_top_edge)
    #face_edge_TEST = doc.addObject("Part::Feature", f"{object_name}EdgeTEST")
    #face_edge_TEST.Shape = edge_TEST

    # edge_to_top_edge is too long; find the the intersection
    # between it and the top thumb plate bottom face's edge.
    max_z_vertex = get_max_z_vertex_for_upper_thumb_support(edge_to_top_edge, bottom_face, long)

    (upper_support_face, normal) = make_upper_edge_thumb_plate_support_face(edge_to_bottom_edge, max_z_vertex)
    #face_TEST = doc.addObject("Part::Feature", f"{object_name}FaceTEST")
    #face_TEST.Shape = upper_support_face
    extrude_vector = thickness * normal
    upper_support = make_solid_from_face(doc, upper_support_face, extrude_vector, object_name)

    prints(f"Success: created {object_name}.", 3)
    return upper_support


"""
Finds the intersection point of edge_to_top_edge ("edge") and one edge
of the bottom face of the top thumb plate ("face_edge"). Should also
work for a more generalised case.
There seems to be no simple way to get such a simple intersection,
so the edges are made into lines (infinite in length?). Of course,
then all "face_lines" intersect with the "line". Therefore, to find
the real intersecting point, check if the intersection points have a
vertex in common with or are "inside" both "edge" and "face_edge"
because THAT can be done.
"""
def get_max_z_vertex_for_upper_thumb_support(edge, bottom_face, long):
    max_z_vertex = None
    line_to_top_edge = Part.Line(vertex_to_vector(edge.Vertexes[0]),
        vertex_to_vector(edge.Vertexes[1]))
    for face_edge in get_long_edges(bottom_face, long):
        line = Part.Line(vertex_to_vector(face_edge.Vertexes[0]),
            vertex_to_vector(face_edge.Vertexes[1]))
        point_list = line.intersect(line_to_top_edge)
        #prints(f"TEST: intersect point: {format_vertices(point_list)}", 3)
        points = len(point_list)
        if points > 1:
            raise Exception(f"Error: initial intersect list has {points} points (should be one).")
        elif points == 0:
            # This shouldn't happen, but if it does, check the next one.
            continue

        point = point_list[0]

        # isInside requires defining the tolerance and whether
        # to count a point on a face as being "inside".
        #is_in_top = edge.isInside(vertex_to_vector(point), 0.0001, True)
        #is_in_face = face_edge.isInside(vertex_to_vector(point), 0.0001, True)

        common_with_edge = edge.common(point)
        common_with_face_edge = face_edge.common(point)
        top_edge_commons = len(common_with_edge.Vertexes)
        face_edge_commons = len(common_with_face_edge.Vertexes)
        #prints(f"TEST: vertex of top: {format_vertices(common_with_edge.Vertexes)}", 4)
        #prints(f"TEST: vertex of face: {format_vertices(common_with_face_edge.Vertexes)}", 4)
        #prints(f"TEST: common_with_edge: {top_edge_commons}, is_in_top: is_in_top", 4)
        #prints(f"TEST: common_with_face_edge: {face_edge_commons}, is_in_face: is_in_face", 4)

        max_z_vertex = None
        if (top_edge_commons > 0) and (face_edge_commons > 0):
            max_z_vertex = common_with_edge.Vertexes[0]
            if is_same_vector_vertex(max_z_vertex, common_with_face_edge.Vertexes[0]):
                break

    if max_z_vertex is None:
        raise Exception("Error: couldn't find an intersection point between"
            + " edge_to_top_edge and any edge of the bottom of the top thumb plate.")

    return max_z_vertex


def make_upper_edge_thumb_plate_support_face(edge_to_bottom_edge, max_z_vertex):
    corner_1 = edge_to_bottom_edge.Vertexes[0]
    if corner_1.Z > edge_to_bottom_edge.Vertexes[1].Z:
        corner_1 = edge_to_bottom_edge.Vertexes[1]
    corner_2 = max_z_vertex
    corner_3 = Part.Vertex(corner_2.X, corner_2.Y, corner_1.Z)
    corners = vertices_to_vectors([corner_1, corner_2, corner_3])
    upper_support_face = make_face_from_corners(corners)

    normal = upper_support_face.normalAt(0, 0)
    if normal.x > 0:
        normal = -normal

    return (upper_support_face, normal)


def trim_upper_support(doc, config, top_plate, upper_support, object_name):
    top_plate_common_shape = upper_support.Shape.common(top_plate.Shape)
    vertices = top_plate_common_shape.Vertexes
    if len(vertices) > 0:
        #top_plate_common_TEST = doc.addObject("Part::Feature", f"{object_name}CommonTEST")
        #top_plate_common_TEST.Shape = top_plate_common_shape
        #prints(f"TEST: common shape vertices: {format_vertices(vertices)}", 4)
        bound_box = top_plate_common_shape.BoundBox
        # The trimming shape needs to be made a little larger.
        less = float(config.get("Keyboard", "CASE_THICKNESS_MM"))
        more = 2.0 * less
        x_len = bound_box.XLength + more
        y_len = bound_box.YLength + more
        z_len = bound_box.ZLength + more
        trim_shape = Part.makeBox(x_len, y_len, z_len)
        trim_shape.Placement.Base = FreeCAD.Vector(bound_box.XMin - less, bound_box.YMin - less, bound_box.ZMin)
        #trim_TEST = doc.addObject("Part::Feature", f"{object_name}TrimTEST")
        #trim_TEST.Shape = trim_shape
        upper_support.Shape = upper_support.Shape.cut(trim_shape)
        prints(f"Trimmed {object_name}.", 4)
    return upper_support


#----------------------------------------------------------------------x---------------------------
# The functions that create support structures (thumb plate stoppers).


def create_thumb_plate_stoppers(doc, config, top_plate, bottom_plate, upper_support, object_name):
    prints("Creating thumb plate stoppers...", 2)
    extend_bottom_thumb_plate_for_stoppers(doc, config, bottom_plate)
    # Trim off the high end of the upper support triangle to create
    # the stopper and make an extension to support the top thumb plate.
    stopper_shape = create_stopper_shape(doc, config, upper_support)
    stopper_TEST = doc.addObject("Part::Feature", f"{object_name}TEST")
    stopper_TEST.Shape = stopper_shape
    # TODO:
    #create_and_move_stoppers(doc, stopper_shape)

    return (None, None)
    #return (lower_stopper, upper_stopper)


def extend_bottom_thumb_plate_for_stoppers(doc, config, bottom_plate):
    (min_x, min_y, min_z, max_x, max_y, max_z) \
        = get_mins_maxes_from_vertices(bottom_plate.Shape.Vertexes)

    extend_face = None
    normal = None
    for face in bottom_plate.Shape.Faces:
        found_max_x = False
        found_min_y = False
        for vertex in face.Vertexes:
            if isclose(vertex.X, max_x):
                found_max_x = True
            elif isclose(vertex.Y, min_y):
                found_min_y = True

        if found_max_x and found_min_y:
            extend_face = face
            normal = face.normalAt(0, 0)
            if normal.x < 0:
                normal = -normal
            break

    if extend_face is None:
        raise Exception("Error: couldn't find the extend face on the bottom thumb plate.")

    extrude_vector = float(config.get("Keyboard", "THUMB_PLATE_EXTEND_MM")) * normal
    #name_TEST = f"{bottom_plate.Name}Extension"
    #thumb_plate_extension_TEST = make_solid_from_face(doc, extend_face, extrude_vector, name_TEST)
    extend_shape = extend_face.extrude(extrude_vector)
    bottom_plate.Shape = bottom_plate.Shape.fuse(extend_shape)

    prints(f"Success: extended {bottom_plate.Name}.", 3)


def create_stopper_shape(doc, config, upper_support):
    (base_shape, direction) = create_base_stopper_shape(doc, config, upper_support)
    other_half_shape = create_stopper_half(doc, config, base_shape, direction)
    stopper_shape = base_shape.fuse(other_half_shape)

    thickness = float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    bottom_shapes = []
    # Since the fusing seems to preserve the originals as subshapes,
    # there are two bottoms, so both need to be extruded.
    for face in stopper_shape.Faces:
        normal = face.normalAt(0, 0)
        if isclose(normal.x, 0.0) and isclose(normal.y, 0.0):
            if normal.z > 0:
                normal = -normal
            bottom_shapes.append(face.extrude(thickness * normal))

    for shape in bottom_shapes:
        stopper_shape = stopper_shape.fuse(shape)

    return stopper_shape


def create_base_stopper_shape(doc, config, upper_support):
    # Get the trimming direction from the face of the vertical side.
    normal = None
    trim_face = None
    for face in upper_support.Shape.Faces:
        normal = face.normalAt(0, 0)
        if isclose(normal.z, 0.0):
            trim_face = face
            if normal.x > 0:
                normal = -normal
            break

    if normal is None:
        raise Exception("Error: couldn't find the right normal of the upper support structure.")

    min_x_vertices = sorted(upper_support.Shape.Vertexes, key=lambda v: v.X)[0:1]
    end_point = sorted(min_x_vertices, key=lambda v: v.Z)[0]
    non_starting_point = sorted(upper_support.Shape.Vertexes, key=lambda v: v.Y)[0]
    stopper_length = float(config.get("Keyboard", "THUMB_PLATE_STOPPER_LENGTH_MM"))
    starting_vector = vertex_to_vector(non_starting_point) + stopper_length*normal
    trim_vector = starting_vector - vertex_to_vector(end_point)
    trim_shape = trim_face.extrude(trim_vector)
    #trim_TEST = doc.addObject("Part::Feature", "TrimTEST")
    #trim_TEST.Shape = trim_shape

    stopper_shape = upper_support.Shape.copy()
    stopper_shape = stopper_shape.cut(trim_shape)
    #trimmed_stopper_TEST = doc.addObject("Part::Feature", "TrimmedStopperTEST")
    #trimmed_stopper_TEST.Shape = stopper_shape

    direction = FreeCAD.Vector(trim_vector)
    direction.normalize()
    return (stopper_shape, direction)


def create_stopper_half(doc, config, base_shape, direction):
    other_shape = base_shape.copy()
    short_edges = sorted(other_shape.Edges, key=lambda e: e.Length)[:3]
    rotation_edge = None
    for edge in short_edges:
        for vertex in edge.Vertexes:
            if isclose(vertex.Y, other_shape.BoundBox.YMin):
                rotation_edge = edge
                break

    base_point = vertex_to_vector(rotation_edge.Vertexes[0])
    other_shape.rotate(base_point, rotation_edge.tangentAt(0), -90.0)
    other_shape.rotate(other_shape.BoundBox.Center, VECTOR_ONE_Z, 180.0)
    other_shape.rotate(other_shape.BoundBox.Center, direction, 180.0)
    other_shape = trim_other_stopper_shape(doc, config, other_shape, base_shape)
    stopper_TEST = doc.addObject("Part::Feature", "TrimmedStopperShapeTEST")
    stopper_TEST.Shape = other_shape

    return other_shape


def trim_other_stopper_shape(doc, config, other_shape, base_shape):
    # The trim direction is the angled side of the base stopper shape.
    normal = None
    trim_face = None
    max_length = None
    for face in base_shape.Faces:
        normal = face.normalAt(0, 0)
        if (not isclose(normal.x, 0.0)) and (not isclose(normal.y, 0.0)) and (not isclose(normal.z, 0.0)):
            trim_face = face
            max_length = sorted(face.Edges, key=lambda e: e.Length, reverse=True)[0].Length
            if normal.z < 0:
                normal = -normal
            break

    thickness = float(config.get("Keyboard", "CASE_THICKNESS_MM"))
    trim_face = trim_face.copy()
    trim_face.Placement.Base = trim_face.Placement.Base + thickness*normal
    enough = max_length * thickness
    trim_face_expanded = expand_face(trim_face, enough)
    trim_shape = trim_face_expanded.extrude(enough * normal)
    other_shape = other_shape.cut(trim_shape)

    return other_shape


#----------------------------------------------------------------------x---------------------------


main()
