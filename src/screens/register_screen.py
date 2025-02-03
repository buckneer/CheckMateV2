import flet as ft
import asyncio
import requests
from flet_navigator import PageData

from src.components.loader import Loader
from src.components.responsive_card import ResponsiveForm
from src.components.snack_bar import SnackBar, SnackBarTypes  # Custom SnackBar
from src.utils.route_guard import BASE_URL


def register_screen(page_data: PageData):
    page = page_data.page

    async def on_submit():
        loader = Loader(page)
        asyncio.create_task(loader.create_loader())

        # Gather form data
        name = name_tf.value
        email = email_tf.value
        password = password_tf.value

        try:
            # Send a POST request to register the user
            response = requests.post(
                f'{BASE_URL}/register',
                json={
                    "name": name,
                    "email": email,
                    "password": password
                }
            )

            if response.status_code == 200:
                # Registration successful
                page.overlay.append(SnackBar(
                    title='Uspešna registracija!',
                    subtitle='Premeštam te na stranicu za prijavu...',
                    snackbar_type=SnackBarTypes.SUCCESS,
                    duration=2500
                ))
                page_data.navigate('/')  # Redirect to login screen

            else:
                # Handle errors from the backend
                error_data = response.json()
                error_snack = SnackBar(
                    title='Greška prilikom registracije',
                    snackbar_type=SnackBarTypes.ERROR
                )

                # Highlight fields with errors if provided
                field_controls = {
                    "email": email_tf,
                    "name": name_tf,
                    "password": password_tf,
                }

                for error in error_data.get("errors", []):
                    if error["field"] in field_controls:
                        field_controls[error["field"]].border_color = ft.Colors.RED_300

                    error_snack.append_error(error["message"])

                page.overlay.append(error_snack)

        except Exception as e:
            # Handle unexpected errors
            page.overlay.append(SnackBar(
                title='Greška',
                subtitle=str(e),
                snackbar_type=SnackBarTypes.ERROR
            ))

        finally:
            loader.delete_loader()
            page.update()

    email_tf = ft.TextField(
        prefix_icon=ft.Icons.EMAIL,
        label='E-adresa',
        autofill_hints=ft.AutofillHint.EMAIL,
        keyboard_type=ft.KeyboardType.EMAIL
    )

    name_tf = ft.TextField(
        prefix_icon=ft.Icons.PERSON,
        label='Ime i prezime'
    )

    password_tf = ft.TextField(
        prefix_icon=ft.Icons.LOCK,
        label='Lozinka',
        password=True,
        can_reveal_password=True,
        autofill_hints=ft.AutofillHint.NEW_PASSWORD
    )

    container = ft.SafeArea(
        ResponsiveForm(
            [
                ft.Row(
                    [ft.Text('Registracija', theme_style=ft.TextThemeStyle.HEADLINE_MEDIUM)],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Column(
                    [email_tf, password_tf, name_tf]
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            'Registruj se',
                            on_click=lambda _: asyncio.run(on_submit()),
                            height=50,
                            expand=True
                        )
                    ],
                ),
                ft.Row(
                    [ft.TextButton('Imaš nalog? Prijavi se', on_click=lambda _: page_data.navigate('/'))]
                )
            ]
        )
    )

    return container
