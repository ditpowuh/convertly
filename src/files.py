from PIL import Image, ImageSequence
from fontTools.ttLib import TTFont
from moviepy import VideoFileClip
from pydub import AudioSegment
import numpy as np
import pillow_heif
import pdf2image
import cv2

import zipfile
import tempfile
import os

AudioSegment.converter = os.path.join(os.path.dirname(__file__), "assets", "ffmpeg.exe")
pillow_heif.register_heif_opener()

fileTypes = {
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
              "wmv",
              "flv",
              "webm",
              "mkv",
              "3gp",
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
              "alac",
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

def getPossibleExtensions(inputExtension: str):
    possibleExtensions = []
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

def getFinalPath(name: str, outputPath: str):
    fileName = name.split(".")
    finalPath = os.path.join(outputPath, name)
    counter = 1
    while os.path.exists(finalPath):
        counter += 1
        finalPath = os.path.join(outputPath, f"{fileName[0]} ({counter}).{fileName[1]}")
    return finalPath

def convertImage(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    with Image.open(inputPath) as img:
        if targetExtension in ["jpg", "jpeg"] and img.mode in ["RGBA", "P"]:
            img = img.convert("RGB")
        img.save(getFinalPath(f"{fileName.split(".")[0]}.{targetExtension}", outputPath))

def convertGifToVideo(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    with Image.open(inputPath) as img:
        width, height = img.size
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(getFinalPath(f"{fileName.split(".")[0]}.{targetExtension}", outputPath), fourcc, 30, (width, height))

        for frame in ImageSequence.Iterator(img):
            frame = frame.convert("RGB")
            frameNp = np.array(frame)
            frameBgr = cv2.cvtColor(frameNp, cv2.COLOR_RGB2BGR)
            duration = frame.info.get("duration", 100)
            frameCount = max(1, int(round((duration / 1000) * 30)))
            for _ in range(frameCount):
                video.write(frameBgr)
        video.release()

def convertVideoToGif(fileName: str, inputPath: str, outputPath: str):
    clip = VideoFileClip(inputPath)
    clip.write_gif(getFinalPath(f"{fileName.split(".")[0]}.gif", outputPath))

def convertVideo(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    video = VideoFileClip(inputPath)
    video.write_videofile(getFinalPath(f"{fileName.split(".")[0]}.{targetExtension}", outputPath))

def convertImageToPdf(fileName: str, inputPath: str, outputPath: str):
    with Image.open(inputPath) as img:
        if img.mode in ["RGBA", "P"]:
            img = img.convert("RGB")
        img.save(getFinalPath(f"{fileName.split(".")[0]}.pdf", outputPath), "PDF")

def convertPdfToImage(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    images = pdf2image.convert_from_path(inputPath, poppler_path = os.path.join(os.path.dirname(__file__), "assets", "poppler", "Library", "bin"))
    if len(images) == 1:
        images[0].save(getFinalPath(f"{fileName.split(".")[0]}.{targetExtension}", outputPath))
    else:
        with zipfile.ZipFile(getFinalPath(f"{fileName.split(".")[0]}.zip", outputPath), "w") as zipf:
            for i, image in enumerate(images):
                with tempfile.NamedTemporaryFile(suffix = f".{targetExtension}", delete_on_close = False) as temp:
                    image.save(temp.name)
                    zipf.write(temp.name, arcname = f"{fileName.split(".")[0]}_{i + 1}.{targetExtension}")

def convertAudio(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    audio = AudioSegment.from_file(inputPath)
    desiredFormat = "ipod" if targetExtension == "m4a" else targetExtension
    audio.export(getFinalPath(f"{fileName.split(".")[0]}.{targetExtension}", outputPath), format = desiredFormat)

def convertVideoToAudio(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    with tempfile.NamedTemporaryFile(suffix = ".wav", delete_on_close = False) as temp:
        with VideoFileClip(inputPath) as video:
            video.audio.write_audiofile(temp.name)

        audio = AudioSegment.from_file(temp.name, format = "wav")
        desiredFormat = "ipod" if targetExtension == "m4a" else targetExtension
        audio.export(getFinalPath(f"{fileName.split(".")[0]}.{targetExtension}", outputPath), format = desiredFormat)

def convertFont(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    font = TTFont(inputPath)
    if targetExtension == "ttf" or targetExtension == "otf":
        font.flavor = None
    else:
        font.flavor = targetExtension
    font.save(getFinalPath(f"{fileName.split(".")[0]}.{targetExtension}", outputPath))
