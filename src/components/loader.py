import flet as ft, asyncio


class Loader:

    def __init__(self, page: ft.Page):
        self.page = page
        self.stack = ft.Stack(
            controls=[
                ft.Container(expand=True, bgcolor=ft.Colors.BLACK, opacity=0.8),
                ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[ft.ProgressBar()]
                )
            ]
        )

    async def create_loader(self):
        await asyncio.sleep(0.5)
        self.page.overlay.append(self.stack)
        self.page.update()

    def delete_loader(self):
        self.page.overlay.clear()
        self.page.update()
