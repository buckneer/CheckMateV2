import flet as ft
from flet_navigator import PageData

pages = ['subjects', 'students', 'profile']


def navbar(page_data: PageData, current_page=1):
    global previous_index
    page = page_data.page
    current_route = page_data.current_route()

    if current_route in pages:
        i = pages.index(current_route)
        previous_index = i
    else:
        i = current_page

    page.navigation_bar = ft.NavigationBar(
        selected_index=i,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.EXPLORE, label='Predmeti'),
            ft.NavigationBarDestination(icon=ft.Icons.COMMUTE, label='Studenti'),
            ft.NavigationBarDestination(
                selected_icon=ft.Icons.PERSON,
                icon=ft.Icons.PERSON_OUTLINE,
                label='Profil',
            ),
        ],
        on_change=lambda e: handle_change(e)
    )

    def handle_change(e):
        page_data.navigate(pages[int(e.data)])
