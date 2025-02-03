import flet as ft
from flet_navigator import PageData

from src.components.navbar import navbar


def home_screen(page_data: PageData):
    page = page_data.page
    navbar(page_data)

    page.update()

    return ft.Text('Hello')
