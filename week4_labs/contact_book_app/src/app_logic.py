import flet as ft
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db

# -------------------------------
# Display Contacts
# -------------------------------
def display_contacts(page, contacts_list_view, db_conn, search_term=""):
    """Fetches and displays all contacts in the ListView."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn, search_term)

    for contact in contacts:
        contact_id, name, phone, email = contact

        # Each contact inside a Card with icons
        card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(name, size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([ft.Icon(ft.Icons.PHONE), ft.Text(phone or "N/A")]),
                    ft.Row([ft.Icon(ft.Icons.EMAIL), ft.Text(email or "N/A")]),
                    ft.Row([
                        ft.IconButton(ft.Icons.EDIT, tooltip="Edit",
                                      on_click=lambda e, c=contact: open_edit_dialog(page, c, db_conn, contacts_list_view)),
                        ft.IconButton(ft.Icons.DELETE, tooltip="Delete",
                                      on_click=lambda e, cid=contact_id: confirm_delete(page, cid, db_conn, contacts_list_view)),
                    ])
                ]),
                padding=10
            )
        )
        contacts_list_view.controls.append(card)

    page.update()

# -------------------------------
# Add Contact
# -------------------------------
def add_contact(page, inputs, contacts_list_view, db_conn):
    """Adds a new contact with validation and refreshes the list."""
    name_input, phone_input, email_input = inputs

    # Validation: prevent empty name
    if not name_input.value.strip():
        name_input.error_text = "Name cannot be empty"
        page.update()
        return
    name_input.error_text = None

    # Save contact
    add_contact_db(db_conn, name_input.value.strip(), phone_input.value.strip(), email_input.value.strip())

    # Clear inputs
    for field in inputs:
        field.value = ""

    display_contacts(page, contacts_list_view, db_conn)
    page.update()

# -------------------------------
# Delete Contact (with confirmation)
# -------------------------------
def confirm_delete(page, contact_id, db_conn, contacts_list_view):
    """Shows confirmation dialog before deleting a contact."""

    def on_yes(e):
        delete_contact_db(db_conn, contact_id)
        display_contacts(page, contacts_list_view, db_conn)
        page.dialog.open = False
        page.update()

    def on_no(e):
        page.dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("Yes", on_click=on_yes),
            ft.TextButton("No", on_click=on_no),
        ]
    )
    page.dialog = dialog
    dialog.open = True
    page.update()

# -------------------------------
# Edit Contact
# -------------------------------
def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    """Opens a dialog to edit a contact's details."""
    contact_id, name, phone, email = contact
    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)

    def save_and_close(e):
        if not edit_name.value.strip():
            edit_name.error_text = "Name cannot be empty"
            page.update()
            return
        update_contact_db(db_conn, contact_id, edit_name.value.strip(), edit_phone.value.strip(), edit_email.value.strip())
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
    page.dialog = dialog
    dialog.open = True
    page.update()
