import datetime
import flet as ft
from flet_navigator import PageData
import requests
from src.utils.global_state import GlobalState
from src.utils.route_guard import BASE_URL


def subject_detail_screen(page_data: PageData) -> ft.Control:
    page = page_data.page
    subject_id = page_data.parameters.get("id")
    token = GlobalState.get_user().get("token")
    headers = {"x-access-token": token}

    # ---------------------------
    # State Variables
    # ---------------------------
    # This variable will store the selected class id from the dropdown.
    selected_class_id = None
    # A list to store checkboxes for each enrolled student.
    student_checkboxes = []

    # ---------------------------
    # Helper Functions
    # ---------------------------
    def show_snackbar(message, success):
        page.snack_bar = ft.SnackBar(
            ft.Text(message, color=ft.colors.GREEN if success else ft.colors.RED)
        )
        page.snack_bar.open = True
        page.update()

    def open_dialog(dialog):
        page.dialog = dialog
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    # ---------------------------
    # Data Fetching Functions
    # ---------------------------
    def fetch_subject_details():
        try:
            response = requests.get(
                f"{BASE_URL}/subject/{subject_id}/students", headers=headers
            )
            return response.json() if response.status_code == 200 else {}
        except Exception as e:
            show_snackbar(f"Error fetching subject: {str(e)}", False)
            return {}

    def fetch_available_students():
        try:
            response = requests.get(f"{BASE_URL}/students", headers=headers)
            if response.status_code == 200:
                all_students = response.json().get("students", [])
                # Filter out students already enrolled in the subject
                current_students = [s["id"] for s in subject_data.get("students", [])]
                return [s for s in all_students if s["id"] not in current_students]
            return []
        except Exception as e:
            show_snackbar(f"Error fetching students: {str(e)}", False)
            return []

    def fetch_classes():
        """
        Fetch all classes for this subject.
        (Requires that your backend implements GET /subject/<subject_id>/classes)
        """
        try:
            response = requests.get(
                f"{BASE_URL}/subject/{subject_id}/classes", headers=headers
            )
            if response.status_code == 200:
                return response.json().get("classes", [])
            else:
                return []
        except Exception as ex:
            show_snackbar(f"Error fetching classes: {str(ex)}", False)
            return []

    # ---------------------------
    # Dialog Functions (for Assign & Create)
    # ---------------------------
    def show_assign_student_dialog(e):
        students = fetch_available_students()
        if not students:
            show_snackbar("No available students to assign!", False)
            return

        student_dropdown = ft.Dropdown(
            label="Select Student",
            options=[
                ft.dropdown.Option(
                    key=str(s["id"]),
                    text=f"{s['first_name']} {s['last_name']}"
                )
                for s in students
            ],
            autofocus=True
        )

        def assign_student(e):
            if not student_dropdown.value:
                return

            data = {
                "student_id": int(student_dropdown.value),
                "subject_id": int(subject_id)
            }

            try:
                response = requests.post(
                    f"{BASE_URL}/assign_student", json=data, headers=headers
                )
                if response.status_code == 201:
                    show_snackbar("Student assigned successfully!", True)
                    refresh_data()
                else:
                    show_snackbar(response.json().get("message", "Assignment failed"), False)
                close_dialog(dialog)
            except Exception as e:
                show_snackbar(f"Error: {str(e)}", False)

        dialog = ft.AlertDialog(
            title=ft.Text("Assign Student"),
            content=student_dropdown,
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog(dialog)),
                ft.TextButton("Assign", on_click=assign_student),
            ],
        )
        open_dialog(dialog)

    def show_create_class_dialog(e):
        today = datetime.date.today().isoformat()

        def create_class(e):
            data = {"subject_id": int(subject_id)}
            try:
                response = requests.post(
                    f"{BASE_URL}/classes", json=data, headers=headers
                )
                if response.status_code == 201:
                    show_snackbar("Class created successfully!", True)
                    # Optionally refresh the classes dropdown
                    refresh_classes()
                else:
                    show_snackbar(response.json().get("message", "Class creation failed"), False)
                close_dialog(dialog)
            except Exception as e:
                show_snackbar(f"Error: {str(e)}", False)

        dialog = ft.AlertDialog(
            title=ft.Text("Create New Class"),
            content=ft.Text(f"Create class for today's date ({today})?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog(dialog)),
                ft.TextButton("Create", on_click=create_class),
            ],
        )
        open_dialog(dialog)

    # ---------------------------
    # Refresh Functions
    # ---------------------------
    def refresh_data():
        nonlocal subject_data
        subject_data = fetch_subject_details()
        load_students()

    def refresh_classes():
        # Refresh the classes dropdown by re-fetching classes.
        classes = fetch_classes()
        class_dropdown.options = [
            ft.dropdown.Option(
                key=str(cls["id"]),
                text=f"Class on {cls['date']}"
            )
            for cls in classes
        ]
        page.update()

    # ---------------------------
    # UI Loading Functions
    # ---------------------------
    student_list = ft.Column()

    def load_students():
        nonlocal student_checkboxes
        student_list.controls.clear()
        student_checkboxes.clear()
        if "students" in subject_data:
            for student in subject_data["students"]:
                # Create a checkbox for each student.
                cb = ft.Checkbox(
                    label=f"{student['first_name']} {student['last_name']}",
                    value=False
                )
                # Save the student id in the control's data attribute
                cb.data = student["id"]
                student_checkboxes.append(cb)
                # Instead of a ListTile, simply add the checkbox.
                student_list.controls.append(cb)
        else:
            student_list.controls.append(ft.Text("No enrolled students", italic=True))
        page.update()

    # ---------------------------
    # Attendance Submission
    # ---------------------------
    def save_attendance(e):
        if not class_dropdown.value:
            show_snackbar("Please select a class first.", False)
            return

        selected_class = int(class_dropdown.value)
        # Build a list of attendance entries based on checked checkboxes.
        selected_attendance = []
        for cb in student_checkboxes:
            if cb.value:  # if the checkbox is checked
                selected_attendance.append({
                    "student_id": cb.data,
                    "status": "present"
                })

        if not selected_attendance:
            show_snackbar("No students selected!", False)
            return

        try:
            all_success = True
            # Iterate over each attendance record and POST it.
            for entry in selected_attendance:
                response = requests.post(
                    f"{BASE_URL}/classes/{selected_class}/attendance",
                    json={"student_id": entry["student_id"], "status": entry["status"]},
                    headers=headers
                )
                if response.status_code != 201:
                    all_success = False
            if all_success:
                show_snackbar("Attendance marked successfully!", True)
            else:
                show_snackbar("Failed to mark attendance for some students", False)
        except Exception as ex:
            show_snackbar(f"Error: {str(ex)}", False)

    # ---------------------------
    # Initial Data Load
    # ---------------------------
    subject_data = fetch_subject_details()
    load_students()

    # Create a persistent dropdown for classes.
    classes = fetch_classes()
    class_dropdown = ft.Dropdown(
        label="Select Class",
        options=[
            ft.dropdown.Option(
                key=str(cls["id"]),
                text=f"Class on {cls['date']}"
            )
            for cls in classes
        ],
        autofocus=True,
    )
    # When the dropdown value changes, update the selected class id.
    def on_class_change(e):
        nonlocal selected_class_id
        selected_class_id = class_dropdown.value
        page.update()

    class_dropdown.on_change = on_class_change

    # ---------------------------
    # AppBar with actions
    # ---------------------------
    page.appbar = ft.AppBar(
        title=ft.Text(subject_data.get("name", "Subject Detail")),
        leading=ft.IconButton(
            ft.icons.ARROW_BACK, on_click=lambda e: page_data.navigate("subjects")
        ),
        actions=[
            ft.IconButton(ft.icons.GROUP_ADD, on_click=show_assign_student_dialog),
            ft.IconButton(ft.icons.CALENDAR_TODAY, on_click=show_create_class_dialog),
            # New button to view report; pass along the subject id.
            ft.IconButton(
                ft.icons.ASSIGNMENT,
                on_click=lambda e: page_data.navigate("subject_report", parameters={"id": subject_id})
            ),
        ]
    )

    # ---------------------------
    # Main UI
    # ---------------------------
    # The UI now includes:
    # - A dropdown at the top for class selection.
    # - A list of enrolled students with checkboxes.
    # - A button to save the attendance.
    return ft.Container(
        content=ft.Column([
            ft.ListTile(
                title=ft.Text("Subject Information", weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(f"ID: {subject_id}"),
            ),
            ft.Divider(),
            # Persistent Class Selection
            ft.Column([
                ft.Text("Mark Attendance:", weight=ft.FontWeight.BOLD),
                class_dropdown,
            ]),
            ft.Divider(),
            ft.Column([
                ft.Text("Enrolled Students:", weight=ft.FontWeight.BOLD),
                student_list,
            ]),
            ft.Divider(),
            ft.ElevatedButton("Save Attendance", on_click=save_attendance)
        ]),
        expand=True
    )
