"""
    Go through glyphs in a UFO font source and apply AGL (Adobe Glyph List) names, based on Unicode values.
"""

from fontTools import agl

font = CurrentFont()

alreadyGood = []
toAdjust = {}
uniNames = {}
skippedGlyphs = []

for glyph in font:
    if glyph.unicodes != ():
        try:
            # check if existing name matches the AGL name
            if glyph.name == agl.UV2AGL[glyph.unicodes[0]]:
                alreadyGood.append(glyph.name)

            # if not, add it to a dict to correct below
            else:
                toAdjust[glyph.name] = agl.UV2AGL[glyph.unicodes[0]]

        # catch if name doesn’t match a name in AGL, then give a "uni____" name
        # formatting help: https://gist.github.com/arrowtype/713dad14fe9a574d58d1aab61ba9b2f0#gistcomment-3234771
        except KeyError:
            # add it to a dict to correct below
            uniNames[glyph.name] = f'uni{glyph.unicodes[0]:0>4X}'


            # TODO: add "uni____" style name

    else:
        skippedGlyphs.append(glyph.name)
    
    # TODO: update groups, kerning, features(?)
    # TODO? if glyph has a name change, probably check for suffixed alts with previous name, then update those as well. print list

    # TODO? Should this copy UFOs to new UFOs, to leave working names?

print("\n\n")
print("--------------------------------------------------")
print("FONT:", font.info.familyName, font.info.styleName)

print("\nGlyph Names already set correctly:")
print("\t", end="")
for name in alreadyGood:
    print(f"/{name}", end=" ")

print("\n\nIn AGL:")
for name, newName in toAdjust.items():
    print(f"\t{name.ljust(31,'_')} {newName}")

print("\nNot in AGL:")
for name, newName in uniNames.items():
    print(f"\t{name.ljust(31,'_')} {newName}")


print("\nSkipped glyphs (no Unicode value set):")
print("\t", end="")
for name in skippedGlyphs:
    print(f"/{name}", end=" ")

print("\n\n")
