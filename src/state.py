import flet as ft
from dataclasses import dataclass

import converter

@dataclass
@ft.observable
class AppState:
    processing = False
    file = None
    directory = None

    possibleExtensions = []
    desiredExtension = None

    async def pickFile(self):
        files = await ft.FilePicker().pick_files()
        if files:
            self.file = files[0]
            givenExtension = self.file.name.split(".")[-1].lower()
            if givenExtension == None:
                self.possibleExtensions = []
            else:
                self.possibleExtensions = [extension for extension in converter.getPossibleExtensions(givenExtension) if extension != givenExtension]
            if len(self.possibleExtensions) > 0:
                self.desiredExtension = self.possibleExtensions[0]
            else:
                self.desiredExtension = None

    async def pickFolder(self):
        path = await ft.FilePicker().get_directory_path()
        if path:
            self.directory = path

    def changeTargetExtension(self, event):
        self.desiredExtension = event.data
