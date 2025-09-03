import flet as ft

import files

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed = ft.Colors.INDIGO)
    page.window.title_bar_hidden = True
    page.window.min_width = 854
    page.window.min_height = 576
    page.bgcolor = "#dddddd"
    page.spacing = 15
    page.padding = 0

    page.title = "Convertly"

    processing = False
    file = None
    directory = None

    page.add(
        ft.ResponsiveRow([
            ft.WindowDragArea(
                ft.Container(
                    width = page.window.width,
                    bgcolor = "#eeeeee",
                    padding = 20,
                    content = ft.Row([
                        ft.Container(
                            content = ft.Text("Convertly", size = 20, color = "#000000", weight = ft.FontWeight.BOLD),
                            padding = ft.padding.only(left = 10)
                        ),
                        ft.Container(
                            content = ft.Row([
                                ft.IconButton(ft.Icons.MINIMIZE_ROUNDED, icon_color = "#000000", on_click = lambda _ : minimiseWindow()),
                                ft.IconButton(ft.Icons.CHECK_BOX_OUTLINE_BLANK_ROUNDED, icon_color = "#000000", on_click = lambda _ : resizeWindow()),
                                ft.IconButton(ft.Icons.CLOSE_ROUNDED, icon_color = "#000000", on_click = lambda _ : page.window.close())
                            ])
                        )
                    ], alignment = "spaceBetween"),
                    border_radius = ft.border_radius.only(bottom_left = 8, bottom_right = 8)
                )
            )
        ])
    )

    def resizeWindow():
        page.window.maximized = not page.window.maximized
        page.update()

    def minimiseWindow():
        page.window.minimized = True
        page.update()

    def fileResult(event: ft.FilePickerResultEvent):
        nonlocal file
        if event.files:
            file = event.files[0]
            fileText.value = file.path
            updateDropdown(file.name)
            page.update()

    def directoryResult(event: ft.FilePickerResultEvent):
        nonlocal directory
        if event.path:
            directory = event.path
            directoryText.value = event.path + "\\"
            page.update()

    def updateDropdown(fileName: str):
        givenExtension = fileName.split(".")[1].lower()
        extensions = files.getPossibleExtensions(givenExtension)
        if len(extensions) != 0:
            conversionDropdown.options = [ft.DropdownOption(key = extension, content = ft.Text(extension)) for extension in extensions if extension != givenExtension]
            conversionDropdown.disabled = False
            conversionDropdown.value = conversionDropdown.options[0].key
        else:
            conversionDropdown.options = []
            conversionDropdown.disabled = True
            conversionDropdown.key = "None"
            conversionDropdown.value = ""
        page.update()

    def convertFile():
        nonlocal processing
        if processing:
            return page.open(ft.SnackBar(ft.Text("A conversion is still in progress.", weight = ft.FontWeight.BOLD), duration = 2000))
        if file == None:
            return page.open(ft.SnackBar(ft.Text("Please select a file.", weight = ft.FontWeight.BOLD), duration = 2000))
        if directory == None:
            return page.open(ft.SnackBar(ft.Text("Please select an output directory.", weight = ft.FontWeight.BOLD), duration = 2000))
        if conversionDropdown.value == None or conversionDropdown.value == "":
            return page.open(ft.SnackBar(ft.Text("Given file does not have any available conversions.", weight = ft.FontWeight.BOLD), duration = 2000))

        processing = True

        extension = file.name.split(".")[1].lower()
        selectedFormat = conversionDropdown.value

        if extension in files.fileTypes["group"]["images"]["content"]:
            if selectedFormat in files.fileTypes["group"]["images"]["content"] or selectedFormat == "gif":
                files.convertImage(file.name, file.path, directory, selectedFormat)
            elif selectedFormat == "pdf":
                files.convertImageToPdf(file.name, file.path, directory)

        if extension in files.fileTypes["group"]["audio"]["content"] and selectedFormat in files.fileTypes["group"]["audio"]["content"]:
            files.convertAudio(file.name, file.path, directory, selectedFormat)

        if extension in files.fileTypes["group"]["videos"]["content"]:
            if selectedFormat in files.fileTypes["group"]["videos"]["content"]:
                files.convertVideo(file.name, file.path, directory, selectedFormat)
            elif selectedFormat in files.fileTypes["group"]["audio"]["content"]:
                files.convertVideoToAudio(file.name, file.path, directory, selectedFormat)
            elif selectedFormat == "gif":
                files.convertVideoToGif(file.name, file.path, directory)

        if extension in files.fileTypes["group"]["fonts"]["content"] and selectedFormat in files.fileTypes["group"]["fonts"]["content"]:
            files.convertFont(file.name, file.path, directory, selectedFormat)

        if extension == "gif":
            if selectedFormat in files.fileTypes["group"]["images"]["content"]:
                files.convertImage(file.name, file.path, directory, selectedFormat)
            if selectedFormat in files.fileTypes["group"]["videos"]["content"]:
                files.convertGifToVideo(file.name, file.path, directory, selectedFormat)

        if extension == "pdf" and selectedFormat in files.fileTypes["group"]["images"]["content"]:
            files.convertPdfToImage(file.name, file.path, directory, selectedFormat)

        processing = False
        page.open(ft.SnackBar(ft.Text("Successfully converted and save!", weight = ft.FontWeight.BOLD), duration = 2000))

    filePicker = ft.FilePicker(on_result = fileResult)
    page.overlay.append(filePicker)
    directoryPicker = ft.FilePicker(on_result = directoryResult)
    page.overlay.append(directoryPicker)

    fileText = ft.Text("No file selected", size = 16, weight = ft.FontWeight.BOLD)
    conversionDropdown = ft.Dropdown(
        filled = True,
        fill_color = "#eeeeee",
        border_width = 0,
        options = [],
        disabled = True,
        text_style = ft.TextStyle(weight = ft.FontWeight.BOLD)
    )
    directoryText = ft.Text("No output directory selected", size = 16, weight = ft.FontWeight.BOLD)

    statusText = ft.Text("", weight = ft.FontWeight.BOLD)

    page.add(
        ft.Container(
            content = ft.Row(
                [fileText],
                alignment = ft.MainAxisAlignment.CENTER,
            ),
            padding = ft.padding.only(top = 25)
        ),
        ft.Row(
            [ft.ElevatedButton("Select File", icon = ft.Icons.FILE_OPEN_ROUNDED, on_click = lambda _ : filePicker.pick_files())],
            alignment = ft.MainAxisAlignment.CENTER
        ),
        ft.Container(
            content = ft.Row(
                [
                    ft.Text("Convert to:", size = 14, weight = ft.FontWeight.BOLD),
                    conversionDropdown
                ],
                alignment = ft.MainAxisAlignment.CENTER
            ),
            padding = ft.padding.only(top = 25)
        ),
        ft.Container(
            content = ft.Row(
                [directoryText],
                alignment = ft.MainAxisAlignment.CENTER,
            ),
            padding = ft.padding.only(top = 25)
        ),
        ft.Row(
            [ft.ElevatedButton("Select Directory", icon = ft.Icons.FOLDER_OUTLINED, on_click = lambda _ : directoryPicker.get_directory_path())],
            alignment = ft.MainAxisAlignment.CENTER
        ),
        ft.Container(
            content = ft.Row(
                [
                    ft.OutlinedButton("Convert", style = ft.ButtonStyle(
                        padding = ft.Padding(40, 20, 40, 20),
                        text_style = ft.TextStyle(size = 16, weight = ft.FontWeight.BOLD)
                    ),
                    on_click = lambda _ : convertFile())
                ],
                alignment = ft.MainAxisAlignment.CENTER
            ),
            padding = ft.padding.only(top = 25)
        )
    )

    page.window.center()
    page.update()

if __name__ == "__main__":
    ft.app(main)
