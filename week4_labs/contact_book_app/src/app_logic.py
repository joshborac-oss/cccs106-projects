import flet as ft
import re
from database import update_contact_db, delete_contact_db, add_contact_db, get_all_contacts_db


# --- Validation helpers ---
def validate_name(name: str) -> str | None:
    if not name.strip():
        return "Name cannot be empty!"
    return None


def validate_phone(phone: str) -> str | None:
    if phone.strip() and not phone.isdigit():
        return "Phone must contain only numbers!"
    return None


def validate_email(email: str) -> str | None:
    if email.strip() and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Invalid email format!"
    return None


# --- Display contacts ---
def display_contacts(page, contacts_list_view, db_conn):
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn)
    for contact in contacts:
        add_contact_tile(page, contacts_list_view, db_conn, contact)
    page.update()


def search_contacts(page, contacts_list_view, db_conn, query: str):
    """Filter contacts by name, phone, or email."""
    contacts_list_view.controls.clear()
    contacts = get_all_contacts_db(db_conn)
    for contact in contacts:
        if query.lower() in " ".join(map(str, contact[1:])).lower():
            add_contact_tile(page, contacts_list_view, db_conn, contact)
    page.update()


# --- Add contact ---
def add_contact(page, inputs, contacts_list_view, db_conn):
    name_input, phone_input, email_input = inputs

    # Reset old errors
    name_input.error_text = None
    phone_input.error_text = None
    email_input.error_text = None

    # Collect validation errors
    errors = {
        "name": validate_name(name_input.value),
        "phone": validate_phone(phone_input.value),
        "email": validate_email(email_input.value),
    }

    # Assign error_text if needed
    if errors["name"]:
        name_input.error_text = errors["name"]
    if errors["phone"]:
        phone_input.error_text = errors["phone"]
    if errors["email"]:
        email_input.error_text = errors["email"]

    # If any errors, stop
    if any(errors.values()):
        page.update()
        return

    # Save to DB
    add_contact_db(db_conn, name_input.value, phone_input.value, email_input.value)

    # Reset inputs
    for field in inputs:
        field.value = ""
        field.error_text = None

    display_contacts(page, contacts_list_view, db_conn)
    page.update()


# --- Contact Card ---
def add_contact_tile(page, contacts_list_view, db_conn, contact):
    contact_id, name, phone, email = contact

    contacts_list_view.controls.append(
        ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(name, size=16, weight=ft.FontWeight.BOLD),
                                ft.PopupMenuButton(
                                    icon=ft.Icons.MORE_VERT,
                                    items=[
                                        ft.PopupMenuItem(
                                            text="Edit",
                                            icon=ft.Icons.EDIT,
                                            on_click=lambda e, c=contact: open_edit_dialog(
                                                page, c, db_conn, contacts_list_view
                                            ),
                                        ),
                                        ft.PopupMenuItem(),
                                        ft.PopupMenuItem(
                                            text="Delete",
                                            icon=ft.Icons.DELETE,
                                            on_click=lambda e, cid=contact_id: confirm_delete(
                                                page, cid, db_conn, contacts_list_view
                                            ),
                                        ),
                                    ],
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Text(f"📞 {phone}"),
                        ft.Text(f"✉ {email}"),
                    ]
                ),
                padding=10,
            ),
            elevation=2,
        )
    )


# --- Delete contact with confirmation ---
def confirm_delete(page, contact_id, db_conn, contacts_list_view):
    def yes_delete(e):
        delete_contact_db(db_conn, contact_id)
        dialog.open = False
        display_contacts(page, contacts_list_view, db_conn)
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Confirm Delete"),
        content=ft.Text("Are you sure you want to delete this contact?"),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, "open", False) or page.update()),
            ft.TextButton("Delete", on_click=yes_delete),
        ],
    )
    page.open(dialog)


# --- Edit contact ---
def open_edit_dialog(page, contact, db_conn, contacts_list_view):
    contact_id, name, phone, email = contact
    edit_name = ft.TextField(label="Name", value=name)
    edit_phone = ft.TextField(label="Phone", value=phone)
    edit_email = ft.TextField(label="Email", value=email)

    def save_and_close(e):
        # Reset errors
        edit_name.error_text = None
        edit_phone.error_text = None
        edit_email.error_text = None

        # Validate all
        errors = {
            "name": validate_name(edit_name.value),
            "phone": validate_phone(edit_phone.value),
            "email": validate_email(edit_email.value),
        }

        if errors["name"]:
            edit_name.error_text = errors["name"]
        if errors["phone"]:
            edit_phone.error_text = errors["phone"]
        if errors["email"]:
            edit_email.error_text = errors["email"]

        if any(errors.values()):
            page.update()
            return

        update_contact_db(db_conn, contact_id, edit_name.value, edit_phone.value, edit_email.value)
        dialog.open = False
        display_contacts(page, contacts_list_view, db_conn)
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Edit Contact"),
        content=ft.Column([edit_name, edit_phone, edit_email]),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, "open", False) or page.update()),
            ft.TextButton("Save", on_click=save_and_close),
        ],
    )
    page.open(dialog)
