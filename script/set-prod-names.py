"""
    Goes through glyphs in a UFO font source and applies AGL (Adobe Glyph List) names, based on Unicode values.

    Run on the command line, pointing to a folder containing UFOs. See README for details.

        python3 script/set-prod-names.py -u sources

    Current assumptions:
    - Glyphs have only one Unicode value each (it is possible, but rare, for glyphs to have multiple Unicodes pointing to them)
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
    report["Prod Names with Codepoints"] = {}
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
                    report["Prod Names with Codepoints"][glyph.unicodes[0]] = (glyph.name, agl.UV2AGL[glyph.unicodes[0]])

            # catch if name doesn’t match a name in AGL, then give a "uni0000" name
            # formatting help: https://gist.github.com/arrowtype/713dad14fe9a574d58d1aab61ba9b2f0#gistcomment-3234771
            except KeyError:
                # add it to a dict to correct below
                report["Production names to set"][glyph.name] = f'uni{glyph.unicodes[0]:0>4X}'
                report["Prod Names with Codepoints"][glyph.unicodes[0]] = (glyph.name, f'uni{glyph.unicodes[0]:0>4X}')

                # if hex is above the range 0000–FFFF, it must be named differently, with a u000000 format
                if glyph.unicodes[0] > 65535:
                    report["Production names to set"][glyph.name] = f'u{glyph.unicodes[0]:0>6X}'
                    report["Prod Names with Codepoints"][glyph.unicodes[0]] = (glyph.name, f'u{glyph.unicodes[0]:0>6X}')

                # TODO? maybe check for ligated glyphs? In working glyphs, these should have an underscore before the first period, and then should turn into a format like 'uni20AC0308', mapped to the string U+20AC U+0308

        # if glyph has no Unicode value
        if glyph.unicodes == ():
            report["Glyphs with no Unicode value"].append(glyph.name)

        # just to catch the possibility of glyphs with more than one Unicode (rare, but possible)
        if len(glyph.unicodes) > 1:
            raise Exception(f"Glyph /{glyph.name} has multiple Unicodes. This is not supported by this script. You should either upgrade the script, or else break up the glyph into one glyph per Unicode.")

    return report


def addProdNamesToFontLib(font,report):

    ## this may be all that is needed??? FontMake may look for this and use it...

    mapping = report["Production names to set"]
    font.lib["public.postscriptNames"] = mapping

    font.save()

    # if not, look up how to change a glyph name, including name, groups, kerning


def saveReport(path, report):
    """
    Writes out the report text file from the report dictionary to
    the given *path*.

    *path* is a `string` of the path to write to
    """

    seperator = "\n---------------------------------------------------"

    final_report = ["PRODUCTION NAMING REPORT\n", f"{path.split('.')[0]}.ufo", seperator, "Production names set:\n"]
    final_report.append(f"    {'PROD NAME'.rjust(16)} : {'UNICODE'.ljust(7)} • {'WORKING NAME'.ljust(31)}\n")
    if report["Prod Names with Codepoints"]:
        for codepoint, oldNameNewName in sorted(report["Prod Names with Codepoints"].items()):
            if codepoint > 65535:
                hexUnicode = f'{codepoint:0>6X}'
            else:
                hexUnicode = f'{codepoint:0>4X}'
            # final_report.append(f"    {hexUnicode.rjust(9)} : {oldNameNewName[0].ljust(31)} → {oldNameNewName[1]}")
            final_report.append(f"    {oldNameNewName[1].rjust(16)} : {hexUnicode.ljust(7)} • {oldNameNewName[0].ljust(31)}")
    else:
        final_report.append("No names needed setting!")

    final_report.append(seperator)
    final_report.append("Glyphs with already-correct naming:")
    if report["Glyphs with already-correct naming"]:
        final_report.append("    " + " ".join([name for name in sorted(report["Glyphs with already-correct naming"])]))
    else:
        final_report.append("No glyphs had already-correct names.")

    final_report.append(seperator)
    final_report.append("Glyphs with no Unicode value:")
    if report["Glyphs with no Unicode value"]:
        final_report.append("    " + " ".join([name for name in sorted(report["Glyphs with no Unicode value"])]))
    else:
        final_report.append("No glyphs had no unicode values.")

    with open(path, "w") as reportDoc:
        reportDoc.write("\n".join(final_report))
        print(f"DONE! Results recorded to {path}")


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

            # open the font in memory
            font = Font(ufoPath)

            # a place to store changes made, then report these later
            report = findProdNames(font)

            # 
            addProdNamesToFontLib(font, report)

            # write report of changes applied to UFO
            reportPath = ufoPath.replace(".ufo",".prod_names.txt")
            saveReport(reportPath, report)

