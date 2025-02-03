import flet as ft


class SnackBarTypes:
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    INFO = 'INFO'


bgcolors = {
    'SUCCESS': ft.Colors.GREEN_100,
    'ERROR': ft.Colors.RED_100,
    'INFO': ft.Colors.WHITE60,
}


class SnackBar(ft.SnackBar):
    def __init__(self, title: str, subtitle: str | None = None, duration=4000,
                 snackbar_type: SnackBarTypes | str = SnackBarTypes.SUCCESS, open=True):
        self.column = ft.Column([
            ft.Text(title, weight=ft.FontWeight.BOLD),
        ])
        super().__init__(self.column)
        self.snackbar_type = snackbar_type

        self.open = open
        self.duration = duration
        self.bgcolor = bgcolors[snackbar_type]
        self.content = self.column

        if subtitle is not None:
            self.column.controls.append(ft.Text(subtitle))

    def append_error(self, error: str):
        if self.snackbar_type == SnackBarTypes.ERROR:
            self.column.controls.append(ft.Text(f'• {error}'))



