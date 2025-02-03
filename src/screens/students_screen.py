import flet as ft
from flet_navigator import PageData
from src.components.navbar import navbar
import requests

from src.utils.global_state import GlobalState
from src.utils.route_guard import BASE_URL


def students_screen(page_data: PageData) -> ft.Control:
    page = page_data.page

    # Fetch students
    def fetch_students():
        token = GlobalState.get_user().get("token")
        headers = {"x-access-token": token}
        try:
            response = requests.get(f"{BASE_URL}/students", headers=headers)
            if response.status_code == 200:
                students = response.json().get("students", [])
                return students if students else []
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Failed to fetch students!"))
                page.snack_bar.open = True
                page.update()
                return []
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error fetching students: {str(e)}"))
            page.snack_bar.open = True
            page.update()
            return []

    # Add new student dialog
    def show_add_student_dialog(e):
        first_name_field = ft.TextField(label="First Name", autofocus=True)
        last_name_field = ft.TextField(label="Last Name")
        email_field = ft.TextField(label="Email")

        def submit_student(e):
            token = GlobalState.get_user().get("token")
            headers = {"x-access-token": token}
            data = {
                "first_name": first_name_field.value,
                "last_name": last_name_field.value,
                "email": email_field.value,
            }

            try:
                response = requests.post(f"{BASE_URL}/students", json=data, headers=headers)
                if response.status_code == 201:
                    page.snack_bar = ft.SnackBar(ft.Text("Student added successfully!"))
                    load_students()
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Failed to add student."))
                page.snack_bar.open = True
            except Exception as e:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error adding student: {str(e)}"))
                page.snack_bar.open = True

            page.dialog.open = False
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Add Student"),
            content=ft.Column([first_name_field, last_name_field, email_field], spacing=10),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.dialog.close()),
                ft.TextButton("Add", on_click=submit_student),
            ],
        )
        page.dialog.open = True
        page.update()

    # Load students
    students_list = ft.Column()

    def load_students():
        students_list.controls.clear()
        students = fetch_students()
        if students:
            for student in students:
                students_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(f"{student['first_name']} {student['last_name']}"),
                        subtitle=ft.Text(student['email']),
                        leading=ft.Icon(ft.icons.PERSON),
                    )
                )
        else:
            students_list.controls.append(
                ft.Text("No students available.", size=20, text_align=ft.TextAlign.CENTER)
            )
        page.update()

    load_students()

    # Assign the AppBar to the page
    page.appbar = ft.AppBar(
        title=ft.Text("Students"),
        actions=[
            ft.IconButton(ft.icons.ADD, on_click=show_add_student_dialog)
        ],
    )

    # Layout
    container = ft.Container(
        expand=True,
        content=ft.SafeArea(
            ft.ListView(
                controls=[students_list],
            )
        )
    )

    return container
