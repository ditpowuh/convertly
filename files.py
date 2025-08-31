from PIL import Image
import os

fileTypes = {
    "imageExtensions": sorted([
        "png",
        "jpg",
        "jpeg",
        "gif",
        "webp",
        "bmp"
    ])
}

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
