import flet as ft, asyncio
import requests
# from components.button import form_button
from flet_navigator import PageData

from src.components.loader import Loader
from src.components.responsive_card import ResponsiveForm
from src.components.snack_bar import SnackBar
from src.utils.global_state import GlobalState
from src.utils.route_guard import BASE_URL


def login_screen(page_data: PageData) -> None:
    page = page_data.page
    page.navigation_bar = None

    async def on_submit():
        email = email_tf.value
        password = password_tf.value

        try:
            # Send login request to the backend
            response = requests.post(f"{BASE_URL}/login", json={"email": email, "password": password})

            if response.status_code == 200:
                data = response.json()
                token = data.get('token')  # Extract the token from the response

                # Save the logged-in user in global state
                GlobalState.set_user({"email": email, "token": token})

                # Show success message and navigate to the subjects screen
                page.overlay.append(SnackBar('Uspešna prijava!', duration=2500))
                page_data.navigate('subjects')
            else:
                page.overlay.append(SnackBar('Prijava nije uspela! Pokušaj ponovo.', duration=2500, snackbar_type='ERROR'))
        except Exception as e:
            page.overlay.append(SnackBar(f'Greška: {e}', duration=2500, snackbar_type='ERROR'))

        page.update()

    email_tf = ft.TextField(
        label='E-adresa',
        prefix_icon=ft.Icons.EMAIL,
        keyboard_type=ft.KeyboardType.EMAIL,
        autofill_hints=ft.AutofillHint.EMAIL
    )
    password_tf = ft.TextField(
        label='Lozinka',
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
        autofill_hints=ft.AutofillHint.PASSWORD
    )

    container = ResponsiveForm(
        controls=[
            ft.Row(
                [ft.Text("Prijava", theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Column(
                [
                    email_tf,
                    password_tf,
                ]
            ),
            ft.Row(
                [
                    ft.ElevatedButton(
                        'Prijavi se',
                        expand=True,
                        height=50,
                        on_click=lambda _: asyncio.run(on_submit()),
                    )
                ]
            ),
            ft.Row(
                [
                    ft.TextButton(
                        'Nemaš nalog? Registruj se',
                        on_click=lambda _: page_data.navigate('register'),
                    )
                ]
            )
        ]
    )

    return ft.SafeArea(container)
