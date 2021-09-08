# Set Production Names

A script to run through UFOs and apply production names to glyphs, in order to ensure they work well in PDFs, PostScript printing, etc.

The AGL (Adobe Glyph List) Specification provides a list of acceptable names for glyphs, which are needed for some contexts. This includes: 
- Easy-to-read names for Latin
- `uni0000` names for things with Unicode hex values from `0000` to `FFFF`, then allows "
- `u000000` names for Unicodes above `FFFF`.
- Ligatures outside of the main Latin naming should use a format like `uniXXXXYYYY` (e.g. `uni20AC0308` for the string `U+20AC U+0308`). This script currently does not do this, as it may or may not be needed, but this could be added if needed.

See https://silnrsi.github.io/FDBP/en-US/Glyph_Naming.html for details on working vs production glyph names.

See https://github.com/adobe-type-tools/agl-specification for the AGL spec.


## Usage

### Set up virtual environment

The first time you build, you will need to set up a virtual environment and install dependencies.

<details>
<summary><b><!-------->Setting up the build environment<!--------></b> (Click to expand)</summary>

(Prerequisite: download and install Python from python.org if you haven’t already done so.)

First, navigate to the base of the project in a terminal. Then, use the following steps to set up the project.

To build, create a virtual environment:

```bash
python3 -m venv venv
```

Then activate it:

```bash
source venv/bin/activate
```

Then install requirements:

```bash
pip install -r requirements.freeze.txt
```

</details>

### Running the script

Once you are in this project directory in a terminal and the project requirements are set up (see above), you can run the script in a single step:

```bash
python3 script/set-prod-names.py -u sources
```

...where `sources` points to a directory which includes `.ufo`s (at the top level) in which you want to set production glyph names.

This will update the glyph names in the UFOs – including in `groups.plist` and `kerning.plist`, but not in `features.fea`.

## Project support

If you run into blockers, please file an issue and/or reach out to Stephen Nixon at `stephen@arrowtype.com` with any questions.
