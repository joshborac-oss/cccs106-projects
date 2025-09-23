import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact


def main(page: ft.Page):
    page.title = "Contact Book"
    page.theme_mode = "dark"   # default theme
    page.horizontal_alignment = "center"
    page.scroll = "auto"

    # Toggle Dark / Light mode
    def toggle_theme(e):
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        tooltip="Toggle Theme",
        on_click=toggle_theme,
    )

    # Database connection
    db_conn = init_db()

    # Inputs
    name_input = ft.TextField(label="Name", width=300)
    phone_input = ft.TextField(label="Phone", width=300)
    email_input = ft.TextField(label="Email", width=300)

    contacts_list_view = ft.ListView(expand=True, spacing=10, padding=10)

    # Add button
    add_btn = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(
            page,
            (name_input, phone_input, email_input),
            contacts_list_view,
            db_conn,
        ),
    )

    # Layout
    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("📒 My Contact Book", size=22, weight="bold", expand=True),
                        theme_btn,
                    ],
                    alignment="spaceBetween",
                ),
                name_input,
                phone_input,
                email_input,
                add_btn,
                ft.Divider(),
                ft.Text("Saved Contacts:", size=18, weight="w500"),
                contacts_list_view,
            ],
            expand=True,
            horizontal_alignment="center",
        )
    )

    # Initial load
    display_contacts(page, contacts_list_view, db_conn)


ft.app(target=main)
