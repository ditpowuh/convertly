import flet as ft

@ft.component
def FileTypeSelector(state):
    def changeFileType(event):
        state.changeTargetExtension(event.data)

    return ft.Row(
        [
            ft.Container(
                content = ft.Row(
                    [
                        ft.Text("Convert to:", size = 14, weight = ft.FontWeight.BOLD),
                        ft.Dropdown(
                            filled = True,
                            fill_color = "#f5f2fa",
                            border_width = 0,
                            options = [ft.DropdownOption(key = extension, content = ft.Text(extension)) for extension in state.possibleExtensions],
                            disabled = len(state.possibleExtensions) == 0,
                            text_style = ft.TextStyle(weight = ft.FontWeight.BOLD),
                            value = "" if len(state.possibleExtensions) == 0 else state.desiredExtension,
                            on_select = changeFileType
                        )
                    ],
                    alignment = ft.MainAxisAlignment.CENTER,
                    wrap = True
                ),
                padding = ft.Padding.all(25),
                bgcolor = "#d8d8eb",
                border_radius = 15
            )
        ],
        alignment = ft.MainAxisAlignment.CENTER
    )
