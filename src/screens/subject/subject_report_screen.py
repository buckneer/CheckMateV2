import flet as ft
from flet_navigator import PageData
import requests
from src.utils.global_state import GlobalState
from src.utils.route_guard import BASE_URL


def subject_report_screen(page_data: PageData) -> ft.Control:
    page = page_data.page
    # Retrieve the subject id from the page parameters.
    subject_id = page_data.parameters.get("id")
    token = GlobalState.get_user().get("token")
    headers = {"x-access-token": token}

    # UI components: a dropdown for selecting a class, plus two columns for present and absent students.
    report_class_dropdown = ft.Dropdown(label="Select Class")
    present_students_column = ft.Column()
    absent_students_column = ft.Column()

    def show_snackbar(message, success):
        page.snack_bar = ft.SnackBar(
            ft.Text(message, color=ft.colors.GREEN if success else ft.colors.RED)
        )
        page.snack_bar.open = True
        page.update()

    # Fetch all classes for the subject.
    def fetch_classes():
        try:
            response = requests.get(f"{BASE_URL}/subject/{subject_id}/classes", headers=headers)
            if response.status_code == 200:
                return response.json().get("classes", [])
            return []
        except Exception as e:
            show_snackbar(f"Error fetching classes: {str(e)}", False)
            return []

    # Populate the dropdown with class options.
    def load_class_options():
        classes = fetch_classes()
        report_class_dropdown.options = [
            ft.dropdown.Option(
                key=str(cls["id"]),
                text=f"Class on {cls['date']}"
            ) for cls in classes
        ]
        page.update()

    # When a class is selected, fetch its attendance details.
    def on_class_change(e):
        selected_class_id = report_class_dropdown.value
        if not selected_class_id:
            return
        try:
            response = requests.get(f"{BASE_URL}/classes/{selected_class_id}", headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Use the flat structure returned by your backend.
                attendance = data.get("attendance", [])
                # Filter attendance records to get those with status "present".
                present_students = [record for record in attendance if record.get("status") == "present"]
                # Build a set of present student IDs.
                present_ids = {record["student_id"] for record in present_students}

                # Fetch the full list of enrolled students for the subject.
                subject_response = requests.get(f"{BASE_URL}/subject/{subject_id}/students", headers=headers)
                if subject_response.status_code == 200:
                    subject_data = subject_response.json()
                    all_students = subject_data.get("students", [])
                    # Absent students are those not in the present_ids set.
                    absent_students = [s for s in all_students if s["id"] not in present_ids]
                else:
                    absent_students = []

                # Update the UI lists.
                present_students_column.controls.clear()
                absent_students_column.controls.clear()

                if present_students:
                    for record in present_students:
                        name = f"{record.get('first_name', '')} {record.get('last_name', '')}"
                        present_students_column.controls.append(ft.Text(name))
                else:
                    present_students_column.controls.append(ft.Text("No students present"))

                if absent_students:
                    for student in absent_students:
                        name = f"{student.get('first_name', '')} {student.get('last_name', '')}"
                        absent_students_column.controls.append(ft.Text(name))
                else:
                    absent_students_column.controls.append(ft.Text("No students absent"))
                page.update()
            else:
                show_snackbar("Failed to load class report", False)
        except Exception as ex:
            show_snackbar(f"Error: {str(ex)}", False)

    # Bind the on_change event of the dropdown.
    report_class_dropdown.on_change = on_class_change
    load_class_options()

    # Set up the AppBar with a back button.
    page.appbar = ft.AppBar(
        title=ft.Text("Subject Report"),
        leading=ft.IconButton(
            ft.icons.ARROW_BACK,
            on_click=lambda e: page_data.navigate("subject_detail", parameters={"id": subject_id})
        )
    )

    # Build and return the screen layout.
    return ft.Container(
        content=ft.Column([
            ft.Text("Report for Subject", weight=ft.FontWeight.BOLD),
            report_class_dropdown,
            ft.Divider(),
            ft.Row([
                ft.Column(
                    [ft.Text("Present Students", weight=ft.FontWeight.BOLD), present_students_column],
                    expand=True
                ),
                ft.VerticalDivider(),
                ft.Column(
                    [ft.Text("Absent Students", weight=ft.FontWeight.BOLD), absent_students_column],
                    expand=True
                )
            ])
        ]),
        expand=True
    )
