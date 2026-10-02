# Third-Party Notices

Video Downloader uses and/or distributes third-party software. The licenses
of these components remain separate from the license of the Video Downloader
source code.

The MIT License in the repository root applies to the original Video Downloader
source code only and does not replace or modify the licenses of third-party
components.

## 1. PySide6 / Qt for Python

**Component:** PySide6 / Qt for Python  
**Version used for development:** 6.11.2  
**License:** LGPLv3 / GPLv3 and Qt Commercial License options

PySide6 is the official Python binding for Qt. The Community Edition is
available under LGPLv3/GPLv3. This project uses the Community Edition Python
package.

Official licensing information:
https://doc.qt.io/qtforpython-6/licensing.html

Additional Qt licensing information:
https://www.qt.io/licensing/

## 2. yt-dlp

**Component:** yt-dlp  
**Version used for development:** 2026.8.19  
**License:** The Unlicense

yt-dlp's source code and Python package are distributed under the Unlicense.
Some yt-dlp release artifacts can contain third-party code under additional
licenses; this project uses yt-dlp through its Python package and packages
its own application separately.

Official project:
https://github.com/yt-dlp/yt-dlp

License:
https://github.com/yt-dlp/yt-dlp/blob/master/LICENSE

Third-party licensing information:
https://github.com/yt-dlp/yt-dlp/blob/master/THIRD_PARTY_LICENSES.txt

## 3. yt-dlp-ejs

**Component:** yt-dlp-ejs  
**License:** Unlicense, with bundled components under MIT and ISC

The yt-dlp-ejs project states that its code is licensed under the Unlicense,
while its prebuilt wheels contain `meriyah` under ISC and `astring` under MIT.

Official project:
https://github.com/yt-dlp/ejs

License information:
https://github.com/yt-dlp/ejs#licensing

## 4. FFmpeg

**Component:** FFmpeg  
**Version currently used by the project:** FFmpeg 9.0.2 / n9.0.2-22 build family

This project uses FFmpeg as a separate command-line executable for media
processing.

FFmpeg licensing depends on the build configuration. FFmpeg states that most
files are licensed under LGPL v2.1 or later, while optional GPL components are
licensed under GPL v2 or later and are enabled when a build is configured with
`--enable-gpl`.

The FFmpeg binary currently used by this project is a GPL static build from
the BtbN Windows build family (`win64-gpl`). Verify the exact binary and its
included licensing/source materials before each public release.

Official FFmpeg license information:
https://ffmpeg.org/legal.html
https://ffmpeg.org/doxygen/trunk/md_LICENSE.html

BtbN FFmpeg Builds:
https://github.com/BtbN/FFmpeg-Builds

Important:
The FFmpeg license applies to FFmpeg itself, not to the original Video
Downloader source code. When redistributing an FFmpeg binary, retain the
applicable license and source-code compliance materials required by that
binary's license.

## 5. Deno

**Component:** Deno  
**Runtime:** Deno 2.x (project-bundled executable)

**License:** MIT

Deno's main workspace is licensed under the MIT License. Deno is included as
a separate runtime used by yt-dlp's JavaScript support.

Official project:
https://github.com/denoland/deno

License:
https://github.com/denoland/deno/blob/main/LICENSE.md

## 6. Trademark / Project Ownership

The names and trademarks of PySide6, Qt, yt-dlp, FFmpeg, Deno, and their
respective contributors or organizations belong to their respective owners.

This project is not affiliated with, endorsed by, or sponsored by those
projects unless explicitly stated.

## 7. Release Distribution

For a Windows release, the distributor should keep the applicable third-party
license notices and other required licensing materials together with the
distributed application or otherwise make them available as required by the
respective licenses.

Before publishing a release, verify:

- The exact FFmpeg build and license variant.
- The exact Deno version.
- The third-party notices included by the installed package versions.
- Any additional libraries bundled into the final PyInstaller application.

This file is a project notice, not legal advice.
