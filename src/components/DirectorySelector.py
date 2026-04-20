import flet as ft

@ft.component
def DirectorySelector(state):
    return ft.Column(
        controls = [
            ft.Container(
                content = ft.Row(
                    [ft.Text("No output directory selected" if state.directory == None else state.directory + "\\", size = 16, weight = ft.FontWeight.BOLD)],
                    alignment = ft.MainAxisAlignment.CENTER,
                ),
                padding = ft.Padding.only(top = 25, bottom = 5)
            ),
            ft.Row(
                [ft.Button("Select Directory", icon = ft.Icons.FOLDER_OUTLINED, on_click = state.pickFolder)],
                alignment = ft.MainAxisAlignment.CENTER
            )
        ]
    )
