import flet as ft

class TodoApp:
    """Main Task Tracker application built with Flet v0.28."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.new_task_input = ft.TextField(
            hint_text="Borac Grade Calculator",
            bgcolor=ft.Colors.PURPLE_50,
            expand=True,
            on_submit=self.add_task_from_event,
        )
        self.tasks_list = ft.Column()
        self.progress_text = ft.Text("No tasks yet", color=ft.Colors.GREY)
        self.progress_bar = ft.ProgressBar(width=600, value=0)

        self.view = ft.Column(
            width=450,
            spacing=20,
            controls=[
                ft.Row(
                    controls=[
                        self.new_task_input,
                        ft.FloatingActionButton(
                            icon=ft.Icons.ADD_TASK, 
                            bgcolor=ft.Colors.GREEN,
                            on_click=self.add_clicked),
                    ],
                ),
                ft.Column(
                    spacing=6,
                    controls=[self.progress_text, self.progress_bar],
                ),
                self.tasks_list,
            ],
        )

    def add_task_from_event(self, e: ft.ControlEvent):
        self.add_task(self.new_task_input.value)

    def add_clicked(self, e: ft.ControlEvent):
        self.add_task(self.new_task_input.value)

    def add_task(self, task_name: str):
        task_name = (task_name or "").strip()
        if not task_name:
            return

        task_row = self.create_task_row(task_name)
        self.tasks_list.controls.append(task_row)
        self.new_task_input.value = ""
        self.new_task_input.focus()
        self.update_progress()
        self.page.update()

    def create_task_row(self, task_name: str) -> ft.Row:
        task_label = ft.Text(task_name)
        task_container = ft.Container(
            content=task_label,
            bgcolor=ft.Colors.YELLOW_100,
            padding=ft.padding.symmetric(horizontal=6, vertical=4),
            border_radius=ft.border_radius.all(4),
        )
        checkbox = ft.Checkbox(value=False, label=None)
        delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED,
            bgcolor=ft.Colors.RED_100, 
            tooltip="Delete Task")

        def status_changed(_: ft.ControlEvent):
            if checkbox.value:
                task_label.style = ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH)
                task_container.bgcolor = ft.Colors.LIGHT_GREEN_100
            else:
                task_container.bgcolor = ft.Colors.YELLOW_100
                task_label.style = None
 
            task_label.update()
            task_container.update()
            self.update_progress()

        def delete_clicked(_: ft.ControlEvent):
            def confirm_delete(_):
                self.page.close(delete_dialog)
                if task_row in self.tasks_list.controls:
                    self.tasks_list.controls.remove(task_row)
                    self.tasks_list.update()
                    self.update_progress()

            def cancel_delete(_):
                self.page.close(delete_dialog)

            delete_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm Deletion"),
                content=ft.Text(f"Are you sure you want to delete this task?\n\n\"{task_name}\""),
                actions=[
                    ft.TextButton("Cancel", on_click=cancel_delete),
                    ft.TextButton("Delete", on_click=confirm_delete),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.open(delete_dialog)

        checkbox.on_change = status_changed
        delete_button.on_click = delete_clicked

        task_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[checkbox, task_container],
                ),
                ft.Row(
                    spacing=0,
                    controls=[delete_button],
                ),
            ],
        )
        task_row.data = checkbox

        return task_row

    def update_progress(self):
        total_tasks = len(self.tasks_list.controls)
        if total_tasks == 0:
            self.progress_bar.value = 0
            self.progress_text.value = "No tasks yet"
        else:
            completed_tasks = sum(
                1 for row in self.tasks_list.controls if getattr(row.data, "value", False)
            )
            self.progress_bar.value = completed_tasks / total_tasks
            self.progress_text.value = f"{completed_tasks} of {total_tasks} tasks completed"

        self.progress_bar.update()
        self.progress_text.update()


def main(page: ft.Page):
    page.title = "Lastname Task Tracker"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.bgcolor = ft.Colors.LIGHT_BLUE_50
    page.window.width = 400
    page.window.height = 700
    page.window.center()
    page.window.resizable = False
    page.scroll = "auto"

    app = TodoApp(page)
    page.add(app.view)


if __name__ == "__main__":
    ft.app(target=main)
