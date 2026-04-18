from PIL import Image, ImageSequence
from fontTools.ttLib import TTFont
import numpy as np
import pillow_heif
import fitz
import cv2
import av

import zipfile
import tempfile
import os

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
        finalPath = os.path.join(outputPath, f"{fileName[0]} ({counter}).{fileName[-1]}")
    return finalPath

def getOnlyName(fileName: str):
    return ".".join(fileName.split(".")[:-1])

def convertImage(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    with Image.open(inputPath) as img:
        if targetExtension in ["jpg", "jpeg"] and img.mode in ["RGBA", "P"]:
            img = img.convert("RGB")
        img.save(getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath))

def convertGifToVideo(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    with Image.open(inputPath) as img:
        width, height = img.size
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
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

def convertVideoToGif(fileName: str, inputPath: str, outputPath: str):
    output = getFinalPath(f"{getOnlyName(fileName)}.gif", outputPath)

    container = av.open(inputPath)

    frames = []
    for frame in container.decode(video=0):
        img = frame.to_image()
        frames.append(img)

    frames[0].save(output, save_all = True, append_images = frames[1:], duration = 100, loop = 0)

def convertVideo(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    output = getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath)

    containerMap = {
        "mp4": "mp4",
        "mkv": "matroska",
        "webm": "webm",
        "avi": "avi"
    }

    codecMap = {
        "mp4": "libx264",
        "mkv": "libx264",
        "avi": "mpeg4",
        "webm": "libvpx"
    }

    containerFormat = containerMap.get(targetExtension)
    codec = codecMap.get(targetExtension)

    if not containerFormat or not codec:
        raise ValueError(f"Unsupported format: {targetExtension}")

    inputContainer = av.open(inputPath)
    outputContainer = av.open(output, mode = "w", format = containerFormat)

    video_stream = next((s for s in inputContainer.streams if s.type == "video"), None)
    if not video_stream:
        raise ValueError("No video stream found")

    outStream = outputContainer.add_stream(codec)
    outStream.width = video_stream.width
    outStream.height = video_stream.height
    outStream.pix_fmt = "yuv420p"

    for frame in inputContainer.decode(video_stream):
        packet = outStream.encode(frame)
        if packet:
            outputContainer.mux(packet)

    packet = outStream.encode(None)
    if packet:
        outputContainer.mux(packet)

    outputContainer.close()

def convertImageToPdf(fileName: str, inputPath: str, outputPath: str):
    with Image.open(inputPath) as img:
        if img.mode in ["RGBA", "P"]:
            img = img.convert("RGB")
        img.save(getFinalPath(f"{getOnlyName(fileName)}.pdf", outputPath), "PDF")

def convertPdfToImage(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    doc = fitz.open(inputPath)

    images = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi = 200)
        images.append((i, pix))

    if len(images) == 1:
        i, pix = images[0]
        pix.save(getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath))

    else:
        with zipfile.ZipFile(getFinalPath(f"{getOnlyName(fileName)}.zip", outputPath), "w") as zipf:
            for i, pix in images:
                with tempfile.NamedTemporaryFile(suffix = f".{targetExtension}", delete = False) as temp:
                    tempPath = temp.name

                pix.save(tempPath)
                zipf.write(tempPath, arcname = f"{getOnlyName(fileName)}_{i + 1}.{targetExtension}")

                os.remove(tempPath)

def convertAudio(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    output = getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath)

    inputContainer = av.open(inputPath)

    audioStream = next((s for s in inputContainer.streams if s.type == "audio"), None)
    if audioStream is None:
        raise ValueError("No audio stream found in input file")

    outputContainer = av.open(output, mode="w")

    codecMap = {
        "mp3": "libmp3lame",
        "wav": "pcm_s16le",
        "aac": "aac",
        "m4a": "aac",
        "flac": "flac",
        "ogg": "libvorbis"
    }

    codec = codecMap.get(targetExtension, None)
    if codec is None:
        raise ValueError(f"Unsupported target audio format: {targetExtension}")

    outStream = outputContainer.add_stream(codec)

    outStream.rate = audioStream.rate
    outStream.channels = audioStream.channels

    for packet in inputContainer.demux(audioStream):
        for frame in packet.decode():
            packet = outStream.encode(frame)
            if packet:
                outputContainer.mux(packet)

    packet = outStream.encode(None)
    if packet:
        outputContainer.mux(packet)

    outputContainer.close()

def convertVideoToAudio(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    output = getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath)

    inputContainer = av.open(inputPath)

    audioStream = next((s for s in inputContainer.streams if s.type == "audio"), None)
    if not audioStream:
        raise ValueError("No audio stream found")

    codecMap = {
        "mp3": "libmp3lame",
        "wav": "pcm_s16le",
        "aac": "aac",
        "m4a": "aac",
        "flac": "flac",
        "ogg": "libvorbis"
    }

    containerMap = {
        "mp3": "mp3",
        "wav": "wav",
        "aac": "adts",
        "m4a": "ipod",
        "flac": "flac",
        "ogg": "ogg"
    }

    codec = codecMap.get(targetExtension)
    container = containerMap.get(targetExtension)

    if not codec or not container:
        raise ValueError(f"Unsupported format: {targetExtension}")

    outputContainer = av.open(output, mode="w", format=container)

    outStream = outputContainer.add_stream(codec)

    for packet in inputContainer.demux(audioStream):
        for frame in packet.decode():
            packet = outStream.encode(frame)
            if packet:
                outputContainer.mux(packet)

    packet = outStream.encode(None)
    if packet:
        outputContainer.mux(packet)

    outputContainer.close()

def convertFont(fileName: str, inputPath: str, outputPath: str, targetExtension: str):
    font = TTFont(inputPath)
    if targetExtension == "ttf" or targetExtension == "otf":
        font.flavor = None
    else:
        font.flavor = targetExtension
    font.save(getFinalPath(f"{getOnlyName(fileName)}.{targetExtension}", outputPath))
