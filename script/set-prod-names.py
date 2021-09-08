"""
    Goes through glyphs in a UFO font source and applies AGL (Adobe Glyph List) names, based on Unicode values.

    Run on the command line, pointing to a folder containing UFOs. See README for details.

        python3 script/set-prod-names.py -u sources

    Current assumptions:
    - Fonts do not have glyphs that are ligated (which would need names like 'uni20AC0308', mapped to the string U+20AC U+0308)
    
"""

from fontParts.fontshell import RFont as Font
from fontTools import agl
import argparse
import os


def findProdNames(font):
    """
        Sets glyph names according to AGL spec.
    """

    # setting up report to store changes
    report = {}
    report["Production names to set"] = {}
    report["Glyphs with already-correct naming"] = []
    report["Glyphs with no Unicode value"] = []

    for glyph in font:

        # if glyph has Unicode value
        if glyph.unicodes != ():
            try:
                # check if existing name matches the AGL name
                if glyph.name == agl.UV2AGL[glyph.unicodes[0]]:
                    report["Glyphs with already-correct naming"].append(glyph.name)

                # if not, add it to a dict to correct below
                else:
                    report["Production names to set"][glyph.name] = agl.UV2AGL[glyph.unicodes[0]]

            # catch if name doesn’t match a name in AGL, then give a "uni____" name
            # formatting help: https://gist.github.com/arrowtype/713dad14fe9a574d58d1aab61ba9b2f0#gistcomment-3234771
            except KeyError:
                # add it to a dict to correct below
                report["Production names to set"][glyph.name] = f'uni{glyph.unicodes[0]:0>4X}'

                # if hex is above the range 0000–FFFF, it must be named differently, with a u000000 format
                if glyph.unicodes[0] > 65535:
                    report["Production names to set"][glyph.name] = f'u{glyph.unicodes[0]:0>6X}'

                # TODO: check for ligated glyphs? These should have an underscore before the first period, e.g. f_l.ss01

                # TODO: add "uni____" style name to actual glyph

        # if glyph has no Unicode value
        if glyph.unicodes == ():
            report["Glyphs with no Unicode value"].append(glyph.name)
        
        # TODO: update groups, kerning, features(?)
        # TODO? if glyph has a name change, probably check for suffixed alts with previous name, then update those as well. print list

        # TODO? Should this copy UFOs to new UFOs, to leave working names? Saga doesn’t need that.

        # TODO: save changes to a txt file, next to UFO (and maybe give option of saving this in another dir)

    return report


# def setProdnames(font,report):

    ## this may be all that is needed??? FontMake may look for this and use it...
    # font.lib["public.postscriptNames"] = mapping

    # if not, look up how to change a glyph name, including name, groups, kerning


def saveReport(path, report):
    """
    Writes out the report text file from the report dictionary to
    the given *path*.

    *path* is a `string` of the path to write to
    """

    seperator = "\n_________________________"

    final_report = [f"{path.split('.')[0]}.ufo", seperator, "Production names set:"]
    if report["Production names to set"]:
        for oldName, newName in report["Production names to set"].items():
            final_report.append(f"\t{oldName.ljust(31)}→ {newName}")
    else:
        final_report.append("No names needed setting!")

    final_report.append(seperator)
    final_report.append("Glyphs with already-correct naming:")
    if report["Glyphs with already-correct naming"]:
        for name in report["Glyphs with already-correct naming"]:
            final_report.append(f"\t{name}")
    else:
        final_report.append("No glyphs had already-correct names.")

    final_report.append(seperator)
    final_report.append("Glyphs with no Unicode value:")
    if report["Glyphs with no Unicode value"]:
        for name in report["Glyphs with no Unicode value"]:
            final_report.append(f"\t{name}")
    else:
        final_report.append("No glyphs had no unicode values.")

    with open(path, "w") as reportDoc:
        reportDoc.write("\n".join(final_report))


if __name__ == "__main__":


    description = """
        Goes through glyphs in a UFO font source and applies AGL (Adobe Glyph List) names, based on Unicode values.
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("-u","--ufoDir",
                    default="sources",
                    help="Relative path in which you have UFOs you want to edit.")

    args = parser.parse_args()
    
    
    # fontPaths = [get UFOs in dir]

    # open each UFO, then manipulate it
    for fileName in os.listdir(args.ufoDir):
        if fileName.endswith(".ufo"):
            ufoPath = os.path.join(args.ufoDir, fileName)
            font = Font(ufoPath, showInterface=False)

            # a place to store changes made, then report these later
            report = findProdNames(font)

            # TODO: set prod names
            # setProdNames(font, report)

            # write report of changes applied to UFO
            reportPath = ufoPath.replace(".ufo",".prod_names.txt")
            saveReport(reportPath, report)





# print("\n\n")
# print("--------------------------------------------------")
# print("FONT:", font.info.familyName, font.info.styleName)

# print("\nGlyph Names already set correctly:")
# print("\t", end="")
# for name in alreadyGood:
#     print(f"/{name}", end=" ")

# print("\n\nIn AGL:")
# for name, newName in toAdjust.items():
#     print(f"\t{name.ljust(31,'_')} {newName}")

# print("\nNot in AGL:")
# for name, newName in uniNames.items():
#     print(f"\t{name.ljust(31,'_')} {newName}")


# print("\nSkipped glyphs (no Unicode value set):")
# print("\t", end="")
# for name in skippedGlyphs:
#     print(f"/{name}", end=" ")

# print("\n\n")
