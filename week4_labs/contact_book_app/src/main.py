import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact

def main(page: ft.Page):
    page.title = "Contact Book"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_width = 400
    page.window_height = 650
    page.theme_mode = ft.ThemeMode.LIGHT  # default theme

    db_conn = init_db()

    # Input fields
    name_input = ft.TextField(label="Name", width=350)
    phone_input = ft.TextField(label="Phone", width=350)
    email_input = ft.TextField(label="Email", width=350)
    inputs = (name_input, phone_input, email_input)

    # Contact list view
    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)

    # Add button
    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn)
    )

    # Search bar
    search_input = ft.TextField(
        label="Search Contacts",
        width=350,
        on_change=lambda e: display_contacts(page, contacts_list_view, db_conn, e.control.value)
    )

    # Dark mode toggle
    theme_switch = ft.Switch(
        label="Dark Mode",
        value=False,
        on_change=lambda e: setattr(
            page,
            "theme_mode",
            ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        ) or page.update()
    )

    # Layout
    page.add(
        ft.Column(
            [
                ft.Row([ft.Text("Contact Book", size=24, weight=ft.FontWeight.BOLD), theme_switch]),
                ft.Divider(),
                ft.Text("Enter Contact Details:", size=18, weight=ft.FontWeight.BOLD),
                name_input,
                phone_input,
                email_input,
                add_button,
                ft.Divider(),
                search_input,
                ft.Text("Contacts:", size=18, weight=ft.FontWeight.BOLD),
                contacts_list_view,
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
    )

    # Initial load of contacts
    display_contacts(page, contacts_list_view, db_conn)

if __name__ == "__main__":
    ft.app(target=main)
