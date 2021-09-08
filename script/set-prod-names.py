"""
    Go through glyphs in a UFO font source and apply AGL (Adobe Glyph List) names, based on Unicode values.

    Current assumptions:
    - Fonts do not have glyphs that are ligated (which would need names like 'uni20AC0308', mapped to the string U+20AC U+0308)
    
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

            # if hex is above the range 0000–FFFF, it must be named differently, with a u000000 format
            if glyph.unicodes[0] > 65535:
                uniNames[glyph.name] = f'u{glyph.unicodes[0]:0>6X}'

            # TODO: check for ligated glyphs? These should have an underscore before the first period, e.g. f_l.ss01

            # TODO: add "uni____" style name to actual glyph

    else:
        skippedGlyphs.append(glyph.name)
    
    # TODO: update groups, kerning, features(?)
    # TODO? if glyph has a name change, probably check for suffixed alts with previous name, then update those as well. print list

    # TODO? Should this copy UFOs to new UFOs, to leave working names? Saga doesn’t need that.

    # TODO: save changes to a txt file, next to UFO (and maybe give option of saving this in another dir)

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
