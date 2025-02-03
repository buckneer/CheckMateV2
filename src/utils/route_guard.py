from flet_navigator import PageData, ROUTE_404

from src.components.navbar import navbar
from src.utils.global_state import GlobalState


def guests_guard(page_data: PageData, title: str, target_screen, to: str = '/'):
    if not GlobalState.get_user():
        page_data.page.title = title
        page_data.page.add(target_screen(page_data))

    else:
        page_data.navigate(to)


def auth_guard(page_data: PageData, title: str, target_screen):
    if GlobalState.get_user():
        navbar(page_data)
        page_data.page.title = title
        page_data.page.add(target_screen(page_data))

    else:
        page_data.navigate_homepage()


BASE_URL = "http://127.0.0.1:5000"
