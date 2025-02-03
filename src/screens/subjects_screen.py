import flet as ft
from flet_navigator import PageData
import requests

from src.utils.global_state import GlobalState
from src.utils.route_guard import BASE_URL


def subjects_screen(page_data: PageData) -> ft.Control:
    page = page_data.page

    # Fetch subjects
    def fetch_subjects():
        token = GlobalState.get_user().get("token")
        headers = {"x-access-token": token}
        try:
            response = requests.get(f"{BASE_URL}/subjects", headers=headers)
            if response.status_code == 200:
                subjects = response.json().get("subjects", [])
                return subjects if subjects else []
            else:
                show_snackbar("Failed to fetch subjects!", success=False)
                return []
        except Exception as e:
            show_snackbar(f"Error fetching subjects: {str(e)}", success=False)
            return []

    # Add new subject dialog
    def show_add_subject_dialog(e):
        # TextField for subject name
        subject_name_field = ft.TextField(label="Subject Name", autofocus=True)

        # Error message label
        error_label = ft.Text("", color=ft.colors.RED, size=12)

        # Submit button handler
        def submit_subject(e):
            token = GlobalState.get_user().get("token")
            headers = {"x-access-token": token}
            subject_name = subject_name_field.value.strip()

            if not subject_name:
                error_label.value = "Subject name is required!"
                error_label.update()
                return

            data = {"name": subject_name}
            try:
                response = requests.post(f"{BASE_URL}/subjects", json=data, headers=headers)
                if response.status_code == 201:
                    show_snackbar("Subject added successfully!", success=True)
                    add_subject_dialog.open = False
                    load_subjects()  # Reload subjects
                else:
                    show_snackbar(response.json().get("message", "Failed to add subject."), success=False)
            except Exception as e:
                show_snackbar(f"Error adding subject: {str(e)}", success=False)

            add_subject_dialog.open = False
            page.update()

        # Define and show the Add Subject dialog
        add_subject_dialog = ft.AlertDialog(
            title=ft.Text("Add Subject"),
            content=ft.Column([
                subject_name_field,
                error_label
            ]),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                ft.TextButton("Add", on_click=submit_subject),
            ],
        )

        def open_dialog():
            page.dialog = add_subject_dialog
            add_subject_dialog.open = True
            page.update()

        def close_dialog():
            add_subject_dialog.open = False
            page.update()

        open_dialog()

    # Load subjects into list
    subjects_list = ft.Column(spacing=10, expand=True)

    def load_subjects():
        subjects_list.controls.clear()
        subjects = fetch_subjects()
        if subjects:
            for subject in subjects:
                subjects_list.controls.append(
                    ft.ListTile(
                        title=ft.Text(subject["name"]),
                        leading=ft.Icon(ft.icons.BOOK),
                        on_click=lambda e, s_id=subject["id"]: page_data.navigate(
                            "subject_detail", parameters={"id": s_id}
                        ),
                    )
                )
        else:
            subjects_list.controls.append(
                ft.Text("No subjects available.", size=20, text_align=ft.TextAlign.CENTER)
            )
        page.update()

    # Helper to show snack bars
    def show_snackbar(message, success=True):
        page.snack_bar = ft.SnackBar(
            ft.Text(message, color=ft.colors.GREEN if success else ft.colors.RED)
        )
        page.snack_bar.open = True
        page.update()

    # Initial load
    load_subjects()

    # AppBar with Add Subject button
    page.appbar = ft.AppBar(
        title=ft.Text("Subjects"),
        actions=[ft.IconButton(ft.icons.ADD, on_click=show_add_subject_dialog)],
    )

    # Main Container
    container = ft.Container(
        expand=True,
        content=ft.SafeArea(
            ft.ListView(controls=[subjects_list], expand=True)
        ),
    )

    return container
