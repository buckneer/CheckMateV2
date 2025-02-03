import flet as ft
from flet_navigator import PageData
import requests

from src.components.navbar import navbar
from src.utils.global_state import GlobalState
from src.utils.route_guard import BASE_URL


def profile_screen(page_data: PageData) -> ft.Control:
    page = page_data.page

    # Retrieve the user email from GlobalState
    user_data = GlobalState.get_user()
    user_email = user_data.get("email", "Unknown Email") if user_data else "Not Logged In"
    token = GlobalState.get_user().get("token")
    headers = {"x-access-token": token}

    # Fetch data for dropdown
    def fetch_students():
        try:
            response = requests.get(f"{BASE_URL}/students", headers=headers)
            if response.status_code == 200:
                return response.json().get("students", [])
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

    def fetch_subjects():
        try:
            response = requests.get(f"{BASE_URL}/subjects", headers=headers)
            if response.status_code == 200:
                return response.json().get("subjects", [])
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Failed to fetch subjects!"))
                page.snack_bar.open = True
                page.update()
                return []
        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error fetching subjects: {str(e)}"))
            page.snack_bar.open = True
            page.update()
            return []

    # Open assign student to subject dialog
    def show_assign_student_dialog(e):
        students = fetch_students()
        subjects = fetch_subjects()

        if not students or not subjects:
            page.snack_bar = ft.SnackBar(ft.Text("Students or subjects data is missing!"))
            page.snack_bar.open = True
            page.update()
            return

        student_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(key=str(s["id"]), text=f"{s['first_name']} {s['last_name']}")
                for s in students
            ],
            label="Select Student",
            width=400,
        )

        subject_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(key=str(s["id"]), text=s["name"]) for s in subjects
            ],
            label="Select Subject",
            width=400,
        )

        def submit_assignment(e):
            student_id = student_dropdown.value
            subject_id = subject_dropdown.value

            if not student_id or not subject_id:
                page.snack_bar = ft.SnackBar(ft.Text("Please select a student and a subject."))
                page.snack_bar.open = True
                page.update()
                return

            data = {"student_id": student_id, "subject_id": subject_id}
            try:
                response = requests.post(f"{BASE_URL}/assign_student", json=data, headers=headers)
                if response.status_code == 200:
                    page.snack_bar = ft.SnackBar(ft.Text("Student assigned to subject successfully!"))
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Failed to assign student to subject."))
                page.snack_bar.open = True
            except Exception as e:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error assigning student: {str(e)}"))
                page.snack_bar.open = True

            assign_dialog.open = False
            page.update()

        assign_dialog = ft.AlertDialog(
            title=ft.Text("Assign Student to Subject"),
            content=ft.Column([student_dropdown, subject_dropdown], spacing=20),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: set_dialog_open(False)),
                ft.TextButton("Assign", on_click=submit_assignment),
            ],
        )

        def set_dialog_open(value):
            assign_dialog.open = value
            page.update()

        assign_dialog.open = True
        page.dialog = assign_dialog
        page.update()

    # Logout function
    def logout_user(_):
        GlobalState.clear_token()
        page_data.navigate("main")

    # Screen content
    container = ft.Column(
        controls=[
            ft.Text("Profile Screen", size=40, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(f"Email: {user_email}", size=20, text_align=ft.TextAlign.CENTER),
            ft.ElevatedButton(
                text="Assign Student to Subject",
                on_click=show_assign_student_dialog,
                bgcolor=ft.colors.BLUE,
                color=ft.colors.WHITE,
            ),
            ft.ElevatedButton(
                text="Logout",
                on_click=logout_user,
                bgcolor=ft.colors.RED,
                color=ft.colors.WHITE,
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )

    navbar(page_data)

    return ft.SafeArea(container)
