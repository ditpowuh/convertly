from ffmpeg import FFmpeg
import subprocess

def runFFMPEG(instance: FFmpeg) -> None:
    startupInfo = subprocess.STARTUPINFO()
    startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupInfo.wShowWindow = 0
    subprocess.run(instance.arguments, startupinfo = startupInfo, creationflags = subprocess.CREATE_NO_WINDOW, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
