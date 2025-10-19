# Tiny FreeCAD Macro How-To

- Install FreeCAD. Assumed installation directory (for Windows): `<programs directory>/FreeCAD1.0`.
- Python console is nice to have: choose from the menu: "View" → "Panels" → "Python console".
- Report view too: choose from the menu: "View" → "Panels" → "Report view". (Python console doesn't show problems in the macro's code, but Report view does.)
- Choose from the menu: "Macro" → "Macros..."
- Note the "User macros location". It's probably (for Windows) `<user path>/AppData/Roaming/FreeCAD/Macro`.
- Choose "Create" or select a macro file from the list and choose "Edit".
- Write code.
- To execute the macro, press Ctrl+F6 or choose from the menu: "Macro" → "Execute macro".

## Good to Know

- FreeCAD automatically imports its features and functions, so things like these work: `FreeCAD.ActiveDocument` or `Gui.doCommand`.
- `os.getcwd()` is `<programs directory>/FreeCAD1.0/bin`.
- `sys.argv[0]` is `<programs directory>/FreeCAD1.0/bin/freecad.exe`.
- `__file__` is `<user path>/AppData/Roaming/FreeCAD/Macro/<macro's filename>`.
- To print stuff to the Report view, use `print` as usual:
  - `print("Hello.")`
  - `print(f"Hello, {name}.")`
  - Make sure that Report view is set to show normal messages (secondary click on the view to get the options).
- To print stuff to the Python console, use `Gui.doCommand`.
  - Use `#` in the beginning of the line so that the console treats it as a comment: `Gui.doCommand("# Hello.")`
  - `Gui.doCommand(f"# Hello, {name}.")`
- Recomputing the document needs to be done every now and then. How often exactly? Don't know. I'll do it at least after any major additions.

## About the Split Keyboard Project

That is, `split_keyboard.py`.

- There are a lot of simple comments since this is a First Project.
- I haven't personally tested it, but the laser cutter I'll use apparently has a kerf of 0.1 mm. Simplified, kerf is the width of the hole that is created when the laser burns away material.

### The Shape

Top plate switch places, 37 pieces (with corners H, I, J, K, L, M, N, O):
```
       H              I
5       [] [] [] [] []
1   O                  []
7    [] [] [] [] [] []    []   J
2                      []    []
7    [] [] [] [] [] []    []
2                      []    []
7    [] [] [] [] [] []    []   K
1   N                  []
5       [] [] [] [] []
       M              L
```

Top plate, rotated conveniently (switches are marked with `o`; A–F are corners; sides a, b, c, d, e, f are all supposed to be straight):
```
 A              a              B
    __________________________
   |               o  o  o  o \
   |            o              |  b
   |         o      o  o  o  o \
   |      o      o             / C
   |   o      o      o  o  o  /
   |       o      o          /
f  |    o      o      o  o  /  c
   | o      o      o       /
   |     o      o      o _/
   |  o      o      o __/  D
   |      o      o __/
   |   o      o __/
   |       o __/     d
   |________/
 F           E
       e
```
