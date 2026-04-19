import pytest

import wave
import tempfile

from PIL import Image
import numpy as np

from convertly import converter

def getConversionPairs(fileTypes):
    pairs = []
    for inputExtension in fileTypes:
        outputExtensions = converter.getPossibleExtensions(inputExtension)
        for outputExtension in outputExtensions:
            if not (inputExtension, outputExtension) in pairs:
                pairs.append((inputExtension, outputExtension))

    return pairs

@pytest.mark.parametrize("inputExtension, outputExtension", getConversionPairs(converter.fileTypes["group"]["images"]["content"]))
def testImageConversions(tmp_path, inputExtension, outputExtension):
    outputDirectory = tmp_path / "output"
    outputDirectory.mkdir()

    inputFile = tmp_path / f"test.{inputExtension}"

    img = Image.new("RGB", (16, 16))

    try:
        img.save(inputFile)
    except Exception:
        pytest.skip(f"Cannot generate test file for {outputExtension}")

    try:
        if inputExtension in converter.fileTypes["group"]["images"]["content"]:
            if outputExtension in converter.fileTypes["group"]["images"]["content"] or outputExtension == "gif":
                converter.convertImage(inputFile.name, str(inputFile), str(outputDirectory), outputExtension)
            elif outputExtension == "pdf":
                converter.convertImageToPdf(inputFile.name, str(inputFile), str(outputDirectory))

        if inputExtension == "gif":
            if outputExtension in converter.fileTypes["group"]["images"]["content"]:
                converter.convertImage(inputFile.name, str(inputFile), str(outputDirectory), outputExtension)
            if outputExtension in converter.fileTypes["group"]["videos"]["content"]:
                converter.convertGifToVideo(inputFile.name, str(inputFile), str(outputDirectory), outputExtension)

        if inputExtension == "pdf" and outputExtension in converter.fileTypes["group"]["images"]["content"]:
            converter.convertPdfToImage(inputFile.name, str(inputFile), str(outputDirectory), outputExtension)
    except Exception:
        pytest.fail(f"Conversion failed: {inputExtension} -> {outputExtension}")

    outputFile = outputDirectory / f"test.{outputExtension}"
    assert outputFile.exists()

@pytest.mark.parametrize("inputExtension, outputExtension", getConversionPairs(converter.fileTypes["group"]["audio"]["content"]))
def testAudioConversions(tmp_path, inputExtension, outputExtension):
    outputDirectory = tmp_path / "output"
    outputDirectory.mkdir()

    inputFile = tmp_path / f"test.{inputExtension}"

    sampleRate = 44100
    samples = (np.zeros(sampleRate)).astype(np.int16)

    try:
        with wave.open(str(inputFile), "w") as file:
            file.setnchannels(1)
            file.setsampwidth(2)
            file.setframerate(sampleRate)
            file.writeframes(samples.tobytes())
    except Exception:
        pytest.skip(f"Cannot generate test file for {inputExtension}")

    try:
        if inputExtension in converter.fileTypes["group"]["audio"]["content"] and outputExtension in converter.fileTypes["group"]["audio"]["content"]:
            converter.convertAudio(inputFile.name, str(inputFile), str(outputDirectory), outputExtension)
    except Exception:
        pytest.fail(f"Conversion failed: {inputExtension} -> {outputExtension}")

    outputFile = outputDirectory / f"test.{outputExtension}"
    assert outputFile.exists()

@pytest.mark.parametrize("inputExtension, outputExtension", getConversionPairs(list(converter.fileTypes["individual"].keys())))
def testIndividualConversions(tmp_path, inputExtension, outputExtension):
    outputDirectory = tmp_path / "output"
    outputDirectory.mkdir()

    inputFile = tmp_path / f"test.{inputExtension}"

    img = Image.new("RGB", (16, 16))

    try:
        if inputExtension == "gif":
            img.save(inputFile)
        if inputExtension == "pdf":
            img.save(inputFile, "PDF")
    except Exception:
        pytest.skip(f"Cannot generate test file for {inputExtension}")

    try:
        if inputExtension == "gif":
            if outputExtension in converter.fileTypes["group"]["images"]["content"]:
                converter.convertImage(inputFile.name, str(inputFile), str(outputDirectory), outputExtension)
            if outputExtension in converter.fileTypes["group"]["videos"]["content"]:
                converter.convertGifToVideo(inputFile.name, str(inputFile), str(outputDirectory), outputExtension)

        if inputExtension == "pdf" and outputExtension in converter.fileTypes["group"]["images"]["content"]:
            converter.convertPdfToImage(inputFile.name, str(inputFile), str(outputDirectory), outputExtension)
    except Exception:
        pytest.fail(f"Conversion failed: {inputExtension} -> {outputExtension}")

    outputFile = outputDirectory / f"test.{outputExtension}"
    assert outputFile.exists()
