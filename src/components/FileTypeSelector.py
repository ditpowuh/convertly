import flet as ft

@ft.component
def FileTypeSelector(state):
    givenExtension = state.file.name.split(".")[-1].lower() if state.file != None else None

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
                            value = "" if len(state.possibleExtensions) == 0 else state.possibleExtensions[0],
                            on_select = state.changeTargetExtension
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
