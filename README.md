# convertly

> A Flet application used to convert a number of different formats between each other.

This app was originally made for my own personal use, where I needed some files to be in other formats without the hassle of online converters or privacy concerns. It is intended to be used on `Windows` devices.

### How to use
#### Using Python (Poetry)
1. Ensure you have [Poetry](https://python-poetry.org/) installed
1. Install necessary dependencies/requirements via `poetry install`
3. Run the command `poetry run flet run -r`
#### Using Releases
1. Download the application from `Releases`
2. Extract the contents of the zip file
3. Run the executable file

### Supported Files
- Images (png, jpg, jpeg, webp, bmp, heic, gif)
- Videos (mp4, m4v, mov, avi, webm, mkv, mpg, vob)
- Audio (mp3, wav, aac, ogg, m4a, flac, wma, aiff, amr, opus)
- Fonts (otf, ttf, woff, woff2)
- PDF file

Conversion between different categories is possible for some of them. For example:
<br/>
- A gif can be converted to a video and vice versa.
- A video file can be converted to an audio file.
- PDF files can be converted to images and vice versa.

### Building
#### Windows
The application can be built via the following command (after dependencies are installed):
```
poetry run flet build windows
```

### Issues
If any problems or bugs arise, or if you need a file conversion that is not available in Convertly, open a issue in GitHub - I'll be happy to support it in this app.
<br/>
The eventual goal of this app is to be free of needing online converters.
