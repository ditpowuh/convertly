import flet as ft

import converter

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(color_scheme_seed = ft.Colors.INDIGO)
    page.window.alignment = ft.Alignment.CENTER
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

    def resizeWindow():
        page.window.maximized = not page.window.maximized
        page.update()

    def minimiseWindow():
        page.window.minimized = True
        page.update()

    async def closeWindow(e):
        await page.window.close()

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
                            padding = ft.Padding.only(left = 10)
                        ),
                        ft.Container(
                            content = ft.Row([
                                ft.IconButton(ft.Icons.MINIMIZE_ROUNDED, icon_color = "#000000", on_click = lambda _ : minimiseWindow()),
                                ft.IconButton(ft.Icons.CHECK_BOX_OUTLINE_BLANK_ROUNDED, icon_color = "#000000", on_click = lambda _ : resizeWindow()),
                                ft.IconButton(ft.Icons.CLOSE_ROUNDED, icon_color = "#000000", on_click = closeWindow)
                            ])
                        )
                    ], alignment = "spaceBetween"),
                    border_radius = ft.BorderRadius.only(bottom_left = 8, bottom_right = 8)
                )
            )
        ])
    )

    def updateDropdown(fileName: str):
        givenExtension = fileName.split(".")[-1].lower()
        extensions = converter.getPossibleExtensions(givenExtension)
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
            return page.show_dialog(ft.SnackBar(ft.Text("A conversion is still in progress.", weight = ft.FontWeight.BOLD), duration = 2000))
        if file == None:
            return page.show_dialog(ft.SnackBar(ft.Text("Please select a file.", weight = ft.FontWeight.BOLD), duration = 2000))
        if directory == None:
            return page.show_dialog(ft.SnackBar(ft.Text("Please select an output directory.", weight = ft.FontWeight.BOLD), duration = 2000))
        if conversionDropdown.value == None or conversionDropdown.value == "":
            return page.show_dialog(ft.SnackBar(ft.Text("Given file does not have any available conversions.", weight = ft.FontWeight.BOLD), duration = 2000))

        processing = True

        extension = file.name.split(".")[-1].lower()
        selectedFormat = conversionDropdown.value

        if extension in converter.fileTypes["group"]["images"]["content"]:
            if selectedFormat in converter.fileTypes["group"]["images"]["content"] or selectedFormat == "gif":
                converter.convertImage(file.name, file.path, directory, selectedFormat)
            elif selectedFormat == "pdf":
                converter.convertImageToPdf(file.name, file.path, directory)

        if extension in converter.fileTypes["group"]["audio"]["content"] and selectedFormat in converter.fileTypes["group"]["audio"]["content"]:
            converter.convertAudio(file.name, file.path, directory, selectedFormat)

        if extension in converter.fileTypes["group"]["videos"]["content"]:
            if selectedFormat in converter.fileTypes["group"]["videos"]["content"]:
                converter.convertVideo(file.name, file.path, directory, selectedFormat)
            elif selectedFormat in converter.fileTypes["group"]["audio"]["content"]:
                converter.convertVideoToAudio(file.name, file.path, directory, selectedFormat)
            elif selectedFormat == "gif":
                converter.convertVideoToGif(file.name, file.path, directory)

        if extension in converter.fileTypes["group"]["fonts"]["content"] and selectedFormat in converter.fileTypes["group"]["fonts"]["content"]:
            converter.convertFont(file.name, file.path, directory, selectedFormat)

        if extension == "gif":
            if selectedFormat in converter.fileTypes["group"]["images"]["content"]:
                converter.convertImage(file.name, file.path, directory, selectedFormat)
            if selectedFormat in converter.fileTypes["group"]["videos"]["content"]:
                converter.convertGifToVideo(file.name, file.path, directory, selectedFormat)

        if extension == "pdf" and selectedFormat in converter.fileTypes["group"]["images"]["content"]:
            converter.convertPdfToImage(file.name, file.path, directory, selectedFormat)

        processing = False
        page.show_dialog(ft.SnackBar(ft.Text("Successfully converted and save!", weight = ft.FontWeight.BOLD), duration = 2000))

    async def pickFile():
        nonlocal file
        files = await ft.FilePicker().pick_files()
        if files:
            file = files[0]
            fileText.value = file.path
            updateDropdown(file.name)
            page.update()

    async def pickFolder():
        nonlocal directory
        path = await ft.FilePicker().get_directory_path()
        if path:
            directory = path
            directoryText.value = directory + "\\"
            page.update()

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
            padding = ft.Padding.only(top = 25)
        ),
        ft.Row(
            [ft.Button("Select File", icon = ft.Icons.FILE_OPEN_ROUNDED, on_click = pickFile)],
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
            padding = ft.Padding.only(top = 25)
        ),
        ft.Container(
            content = ft.Row(
                [directoryText],
                alignment = ft.MainAxisAlignment.CENTER,
            ),
            padding = ft.Padding.only(top = 25)
        ),
        ft.Row(
            [ft.Button("Select Directory", icon = ft.Icons.FOLDER_OUTLINED, on_click = pickFolder)],
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
            padding = ft.Padding.only(top = 25)
        )
    )

    page.update()

if __name__ == "__main__":
    ft.run(main, assets_dir = "assets")
