import flet as ft
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db


def display_contacts(page, contacts_list_view, db_conn):
    """Fetches and displays all contacts in the ListView."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn)

    for contact in contacts:
        contact_id, name, phone, email = contact

        contacts_list_view.controls.append(
            ft.ListTile(
                title=ft.Text(name, size=16, weight="bold"),
                subtitle=ft.Text(f"📞 {phone} | ✉️ {email}"),
                trailing=ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT,
                    items=[
                        ft.PopupMenuItem(
                            text="Edit",
                            icon=ft.Icons.EDIT,
                            on_click=lambda e, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view),
                        ),
                        ft.PopupMenuItem(),  # Divider
                        ft.PopupMenuItem(
                            text="Delete",
                            icon=ft.Icons.DELETE,
                            on_click=lambda e, cid=contact_id: confirm_delete(page, cid, db_conn, contacts_list_view),
                        ),
                    ],
                ),
            )
        )
    page.update()


def add_contact(page, inputs, contacts_list_view, db_conn):
    """Adds a new contact and refreshes the list."""
    name_input, phone_input, email_input = inputs

    if not name_input.value.strip():
        page.snack_bar = ft.SnackBar(ft.Text("⚠️ Name is required!"), bgcolor="red")
        page.snack_bar.open = True
        page.update()
        return

    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)

    for field in inputs:
        field.value = ""

    display_contacts(page, contacts_list_view, db_conn)
    page.update()


def confirm_delete(page, contact_id, db_conn, contacts_list_view):
    """Show confirmation before deleting contact."""

    def delete_and_close(e):
        delete_contact_db(db_conn, contact_id)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Delete Contact"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Delete", on_click=delete_and_close),
        ],
    )
    page.open(dialog)


def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit a contact's details."""
    contact_id, name, phone, email = contact
    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)

    def save_and_close(e):
        if not edit_name.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Name cannot be empty!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return

        update_contact_db(db_conn, contact_id, edit_name.value, edit_phone.value, edit_email.value)
        dialog.open = False
        page.update()
        display_contacts(page, contacts_list_view, db_conn)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email]),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False) or page.update()),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )
    page.open(dialog)
