import ffmpeg_binaries as ffmpeg
from ffmpeg import FFmpeg

from PIL import Image, ImageFile, ImageSequence
from fontTools.ttLib import TTFont
import numpy as np
import pillow_heif
import pymupdf
import cv2

from typing import TypedDict

import zipfile
import tempfile
import os

ffmpeg.init()
pillow_heif.register_heif_opener()

class OtherTypes(TypedDict, total = False):
    individual: list[str]
    group: list[str]

class GroupType(TypedDict, total = False):
    content: list[str]
    other: OtherTypes

class IndividualType(TypedDict, total = False):
    individual: list[str]
    group: list[str]

class FileTypes(TypedDict):
    group: dict[str, GroupType]
    individual: dict[str, IndividualType]

fileTypes: FileTypes = {
    "group": {
        "images": {
            "content": [
                "png",
                "jpg",
                "jpeg",
                "webp",
                "bmp",
                "heic"
            ],
            "other": {
                "individual": ["gif", "pdf"]
            }
        },
        "videos": {
            "content": [
              "mp4",
              "m4v",
              "mov",
              "avi",
              "webm",
              "mkv",
              "mpeg",
              "mpg",
              "vob"
            ],
            "other": {
                "individual": ["gif"],
                "group": ["audio"]
            }
        },
        "audio": {
            "content": [
                "mp3",
                "wav",
                "aac",
                "ogg",
                "m4a",
                "flac",
                "wma",
                "aiff",
                "amr",
                "opus"
            ]
        },
        "fonts": {
            "content": [
                "otf",
                "ttf",
                "woff",
                "woff2"
            ]
        }
    },
    "individual": {
        "gif": {
            "group": ["images", "videos"]
        },
        "pdf": {
            "group": ["images"]
        }
    }
}

def getPossibleExtensions(inputExtension: str) -> list[str]:
    possibleExtensions: list[str] = []
    if inputExtension in fileTypes["individual"]:
        if "individual" in fileTypes["individual"][inputExtension]:
            possibleExtensions = possibleExtensions + fileTypes["individual"][inputExtension]["individual"]
        if "group" in fileTypes["individual"][inputExtension]:
            for group in fileTypes["individual"][inputExtension]["group"]:
                possibleExtensions = possibleExtensions + fileTypes["group"][group]["content"]
        return sorted(possibleExtensions)
    for category in fileTypes["group"].keys():
        if inputExtension in fileTypes["group"][category]["content"]:
            possibleExtensions = possibleExtensions + fileTypes["group"][category]["content"]
            if "other" in fileTypes["group"][category]:
                if "individual" in fileTypes["group"][category]["other"]:
                    possibleExtensions = possibleExtensions + fileTypes["group"][category]["other"]["individual"]
                if "group" in fileTypes["group"][category]["other"]:
                    for group in fileTypes["group"][category]["other"]["group"]:
                        possibleExtensions = possibleExtensions + fileTypes["group"][group]["content"]
            return sorted(possibleExtensions)
    return sorted(possibleExtensions)

def getFinalPath(name: str, outputPath: str) -> str:
    fileName = name.split(".")
    finalPath = os.path.join(outputPath, name)
    counter = 1
    while os.path.exists(finalPath):
        counter += 1
        finalPath = os.path.join(outputPath, f"{fileName[0]} ({counter}).{fileName[-1]}")
    return finalPath

def getOnlyName(fileName: str) -> str:
    return ".".join(fileName.split(".")[:-1])

def convertImage(fileName: str, inputPath: str, outputPath: str, targetExtension: str) -> None:
    with Image.open(inputPath) as img:
        output: Image.Image | ImageFile.ImageFile = img
        if targetExtension in ["jpg", "jpeg"] and output.mode in ["RGBA", "P"]:
            output = output.convert("RGB")
        output.save(getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath))

def convertGifToVideo(fileName: str, inputPath: str, outputPath: str, targetExtension: str) -> None:
    with Image.open(inputPath) as img:
        width, height = img.size
        fourcc = cv2.VideoWriter.fourcc(*"mp4v")
        video = cv2.VideoWriter(getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath), fourcc, 30, (width, height))

        for frame in ImageSequence.Iterator(img):
            frame = frame.convert("RGB")
            frameNp = np.array(frame)
            frameBgr = cv2.cvtColor(frameNp, cv2.COLOR_RGB2BGR)
            duration = frame.info.get("duration", 100)
            frameCount = max(1, int(round((duration / 1000) * 30)))
            for _ in range(frameCount):
                video.write(frameBgr)
        video.release()

def convertVideoToGif(fileName: str, inputPath: str, outputPath: str) -> None:
    filter = "split[s0][s1];[s0]palettegen=stats_mode=full[p];[s1][p]paletteuse=dither=sierra2_4a"
    ffmpegInstance = (FFmpeg().option("y").input(inputPath).output(getFinalPath(f"{getOnlyName(fileName)}.gif", outputPath), {"filter_complex": filter, "loop": "0"}))
    ffmpegInstance.execute()

def convertVideo(fileName: str, inputPath: str, outputPath: str, targetExtension: str) -> None:
    options = {
        "vcodec": "libx264",
        "acodec": "aac",
        "pix_fmt": "yuv420p",
        "crf": "23"
    }

    if targetExtension == "webm":
        options["vcodec"] = "libvpx-vp9"
        options["acodec"] = "libopus"
    elif targetExtension in ["mpeg", "mpg", "vob"]:
        options["vcodec"] = "mpeg2video"
        options["acodec"] = "mp2"
        options.pop("pix_fmt", None)
        options.pop("crf", None)
        options["q:v"] = "2"

    ffmpegInstance = (FFmpeg().option("y").input(inputPath).output(getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath), options))
    ffmpegInstance.execute()

def convertImageToPdf(fileName: str, inputPath: str, outputPath: str) -> None:
    with Image.open(inputPath) as img:
        output: Image.Image | ImageFile.ImageFile = img
        if output.mode in ["RGBA", "P"]:
            output = output.convert("RGB")
        output.save(getFinalPath(f"{getOnlyName(fileName)}.pdf", outputPath), "PDF")

def convertPdfToImage(fileName: str, inputPath: str, outputPath: str, targetExtension: str) -> None:
    doc = pymupdf.open(inputPath)

    images: list[tuple[int, pymupdf.Pixmap]] = []
    for i in range(len(doc)):
        page: pymupdf.Page = doc[i]
        pix = page.get_pixmap(dpi = 200)
        images.append((i, pix))

    if len(images) == 1:
        i, pix = images[0]
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        img.save(getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath))
    else:
        with zipfile.ZipFile(getFinalPath(f"{getOnlyName(fileName)}.zip", outputPath), "w") as zipf:
            for i, pix in images:
                with tempfile.NamedTemporaryFile(suffix = f".{targetExtension}", delete = False) as temp:
                    tempPath = temp.name

                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                img.save(tempPath)
                zipf.write(tempPath, arcname = f"{getOnlyName(fileName)}_{i + 1}.{targetExtension}")

                os.remove(tempPath)

def convertAudio(fileName: str, inputPath: str, outputPath: str, targetExtension: str) -> None:
    ffmpegInstance = (FFmpeg().option("y").input(inputPath).output(getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath)))
    ffmpegInstance.execute()

def convertVideoToAudio(fileName: str, inputPath: str, outputPath: str, targetExtension: str) -> None:
    with tempfile.NamedTemporaryFile(suffix = ".wav", delete_on_close = False) as temp:
        ffmpegInstance = (FFmpeg().option("y").input(inputPath).output(temp.name, {"vn": None, "acodec": "pcm_s16le"}))
        ffmpegInstance.execute()

        convertAudio(fileName, temp.name, outputPath, targetExtension)

def convertFont(fileName: str, inputPath: str, outputPath: str, targetExtension: str) -> None:
    font = TTFont(inputPath)
    if targetExtension == "ttf" or targetExtension == "otf":
        font.flavor = None
    else:
        font.flavor = targetExtension
    font.save(getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath))
