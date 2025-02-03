import flet as ft


class ResponsiveForm(ft.Container):
    def __init__(self, controls, col={'md': 6, 'lg': 5, 'xl': 4}, alignment=ft.MainAxisAlignment.CENTER):
        super().__init__()

        self.content = ft.ResponsiveRow(
            [
                ft.Column(
                    col=col,
                    controls=controls,
                )
            ],
            alignment=alignment
        )

