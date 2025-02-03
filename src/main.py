import flet as ft
import requests
from flet_navigator import PublicFletNavigator, PageData, route

from src.screens.profile_screen import profile_screen
from src.screens.students_screen import students_screen
from src.screens.subject.subject_detail_screen import subject_detail_screen
from src.screens.subject.subject_report_screen import subject_report_screen
from src.screens.subjects_screen import subjects_screen
from src.screens.login_screen import login_screen
from src.screens.register_screen import register_screen
from src.utils.route_guard import auth_guard, guests_guard


# Backend URL


@route('/')
def main(page_data: PageData) -> None:
    guests_guard(page_data, 'CheckMate | Prijava', login_screen)


@route
def register(page_data: PageData) -> None:
    guests_guard(page_data, 'CheckMate | Registracija', register_screen)


@route
def subjects(page_data: PageData) -> None:
    auth_guard(page_data, "CheckMate | Predmeti", subjects_screen)


@route
def students(page_data: PageData) -> None:
    auth_guard(page_data, "CheckMate | Studenti", students_screen)


@route
def profile(page_data: PageData) -> None:
    auth_guard(page_data, "CheckMate | Profil", profile_screen)


@route
def subject_detail(page_data: PageData) -> None:
    auth_guard(page_data, "CheckMate | Subject Detail", subject_detail_screen)


@route
def subject_report(page_data: PageData) -> None:
    auth_guard(page_data, "CheckMate | Subject Detail", subject_report_screen)


ft.app(lambda page: PublicFletNavigator(page).render(page))
