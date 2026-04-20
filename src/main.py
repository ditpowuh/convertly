import flet as ft

from components import TitleBar, FileSelector, FileTypeSelector, DirectorySelector

from state import AppState
import converter

@ft.component
def App():
    page = ft.context.page

    state, _ = ft.use_state(AppState)

    def convertFile():
        nonlocal state
        if state.processing:
            return page.show_dialog(ft.SnackBar(ft.Text("A conversion is still in progress.", weight = ft.FontWeight.BOLD), duration = 2000))
        if state.file == None:
            return page.show_dialog(ft.SnackBar(ft.Text("Please select a file.", weight = ft.FontWeight.BOLD), duration = 2000))
        if state.directory == None:
            return page.show_dialog(ft.SnackBar(ft.Text("Please select an output directory.", weight = ft.FontWeight.BOLD), duration = 2000))
        if len(state.possibleExtensions) == 0:
            return page.show_dialog(ft.SnackBar(ft.Text("Given file does not have any available conversions.", weight = ft.FontWeight.BOLD), duration = 2000))

        state.processing = True

        extension = state.file.name.split(".")[-1].lower()
        selectedFormat = state.desiredExtension

        if extension in converter.fileTypes["group"]["images"]["content"]:
            if selectedFormat in converter.fileTypes["group"]["images"]["content"] or selectedFormat == "gif":
                converter.convertImage(state.file.name, state.file.path, state.directory, selectedFormat)
            elif selectedFormat == "pdf":
                converter.convertImageToPdf(state.file.name, state.file.path, state.directory)

        if extension in converter.fileTypes["group"]["audio"]["content"] and selectedFormat in converter.fileTypes["group"]["audio"]["content"]:
            converter.convertAudio(state.file.name, state.file.path, state.directory, selectedFormat)

        if extension in converter.fileTypes["group"]["videos"]["content"]:
            if selectedFormat in converter.fileTypes["group"]["videos"]["content"]:
                converter.convertVideo(state.file.name, state.file.path, state.directory, selectedFormat)
            elif selectedFormat in converter.fileTypes["group"]["audio"]["content"]:
                converter.convertVideoToAudio(state.file.name, state.file.path, state.directory, selectedFormat)
            elif selectedFormat == "gif":
                converter.convertVideoToGif(state.file.name, state.file.path, state.directory)

        if extension in converter.fileTypes["group"]["fonts"]["content"] and selectedFormat in converter.fileTypes["group"]["fonts"]["content"]:
            converter.convertFont(state.file.name, state.file.path, state.directory, selectedFormat)

        if extension == "gif":
            if selectedFormat in converter.fileTypes["group"]["images"]["content"]:
                converter.convertImage(state.file.name, state.file.path, state.directory, selectedFormat)
            if selectedFormat in converter.fileTypes["group"]["videos"]["content"]:
                converter.convertGifToVideo(state.file.name, state.file.path, state.directory, selectedFormat)

        if extension == "pdf" and selectedFormat in converter.fileTypes["group"]["images"]["content"]:
            converter.convertPdfToImage(state.file.name, state.file.path, state.directory, selectedFormat)

        state.processing = False
        page.show_dialog(ft.SnackBar(ft.Text("Successfully converted and save!", weight = ft.FontWeight.BOLD), duration = 2000))

    return [
        TitleBar(),
        FileSelector(state),
        FileTypeSelector(state),
        DirectorySelector(state),
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
    ]

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

    page.render(App)

if __name__ == "__main__":
    ft.run(main, assets_dir = "assets")
