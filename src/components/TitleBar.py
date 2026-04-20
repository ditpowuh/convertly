import flet as ft

@ft.component
def TitleBar():
    page = ft.context.page

    def resizeWindow():
        page.window.maximized = not page.window.maximized
        page.update()

    def minimiseWindow():
        page.window.minimized = True
        page.update()

    async def closeWindow(e):
        await page.window.close()

    return ft.ResponsiveRow([
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
