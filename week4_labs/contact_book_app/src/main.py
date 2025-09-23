import flet as ft
from database import init_db
from app_logic import display_contacts, add_contact, search_contacts


def main(page: ft.Page):
    page.title = "Contact Book"
    page.window_width = 420
    page.window_height = 650
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    db_conn = init_db()

    # --- Inputs ---
    name_input = ft.TextField(label="Name", width=350)
    phone_input = ft.TextField(label="Phone", width=350)
    email_input = ft.TextField(label="Email", width=350)
    inputs = (name_input, phone_input, email_input)

    # --- Contact list ---
    contacts_list_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)

    # --- Search bar ---
    search_input = ft.TextField(
        label="Search",
        width=350,
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: search_contacts(
            page, contacts_list_view, db_conn, search_input.value
        ),
    )

    # --- Add button ---
    add_button = ft.ElevatedButton(
        text="Add Contact",
        on_click=lambda e: add_contact(page, inputs, contacts_list_view, db_conn),
        width=200,
    )

    # --- Theme toggle (your provided code) ---
    page.theme_mode = ft.ThemeMode.LIGHT  # Set initial theme

    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.LIGHT:
            page.theme_mode = ft.ThemeMode.DARK
            theme_btn.icon = ft.Icons.LIGHT_MODE  # 🌞 show sun when in dark mode
        else:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_btn.icon = ft.Icons.DARK_MODE  # 🌙 show moon when in light mode
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE,  # Start with moon (since we begin in LIGHT mode)
        tooltip="Switch Theme",
        on_click=toggle_theme,
    )

    # --- Layout ---
    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Text("📒 Contact Book", size=22, weight=ft.FontWeight.BOLD),
                        theme_btn,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                name_input,
                phone_input,
                email_input,
                add_button,
                ft.Divider(),
                search_input,
                ft.Text("Contacts:", size=18, weight=ft.FontWeight.BOLD),
                contacts_list_view,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
    )

    # Load contacts
    display_contacts(page, contacts_list_view, db_conn)


if __name__ == "__main__":
    ft.app(target=main)
