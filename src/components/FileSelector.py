import flet as ft

@ft.component
def FileSelector(state):
    return ft.Column(
        controls = [
            ft.Container(
                content = ft.Row(
                    [ft.Text("No file selected" if state.file == None else state.file.path, size = 16, weight = ft.FontWeight.BOLD)],
                    alignment = ft.MainAxisAlignment.CENTER,
                ),
                padding = ft.Padding.only(top = 25, bottom = 5)
            ),
            ft.Container(
                content = ft.Row(
                    [ft.Button("Select File", icon = ft.Icons.FILE_OPEN_ROUNDED, on_click = state.pickFile)],
                    alignment = ft.MainAxisAlignment.CENTER
                ),
                padding = ft.Padding.only(bottom = 25)
            )
        ]
    )
