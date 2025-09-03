# convertly

#### python packages
- flet (tested with 0.28.3)
- pillow (tested with 10.4.0)
- pydub (tested with 0.25.1)
- moviepy (tested with 2.1.2)
- fonttools (tested with 4.57.0)
- pdf2image (tested with 1.17.0)
- opencv-python (tested with 4.12.0)
- numpy (tested with 2.2.6)

#### additional prerequisites
- ffmpeg
  - Store `ffmpeg.exe` in `src/assets`
- poppler
  - Store folder in `src/assets` under the name of `poppler`

> A Flet application used to convert a number of different formats between each other.

### How to use
#### Using Python
1. Install necessary requirements via `pip install`
2. Download and install additional assets
    1. Go to the [FFmpeg Download](https://ffmpeg.org/download.html) page to install and extract `ffmpeg.exe` from zip file.<br>Move that file to the `assets` folder (`src/assets`).
    2.  Go to the [Releases Page](http://github.com/oschwartz10612/poppler-windows/releases) from `poppler-windows` to install the latest verison of poppler.<br>Extract the contents into `assets` and rename to `poppler`.
3. Run the command `flet run`
#### Using Releases
1. Download the application from `Releases`
2. Extract the contents of the zip file
3. Run the executable file