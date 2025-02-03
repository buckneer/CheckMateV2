import flet as ft

def form_button(text: str, on_submit):
  return ft.ElevatedButton(text, on_click=on_submit)