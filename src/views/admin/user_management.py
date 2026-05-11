"""User management - Add, Edit, Delete users with real database."""

import flet as ft
from services.database import get_db_connection
from datetime import datetime
from utils.notifications import show_success, show_error, show_warning, show_info, DELETE_SUCCESS, UPDATE_SUCCESS, CREATE_SUCCESS, REQUIRED_FIELDS, DELETE_CONFIRM

def UserManagement():
    """User management interface with full CRUD operations."""
    
    users_container = ft.Column(spacing=10)
    
    search_field = ft.TextField(
        label="Search Users",
        hint_text="Search by username or name...",
        prefix_icon=ft.icons.SEARCH,
        border_color="primary", 
        width=300,
    )
   
    role_filter = ft.Dropdown(
        label="Filter by Role",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Patient", text="Customer"),
            ft.dropdown.Option("Pharmacist"),
            ft.dropdown.Option("Inventory"),
            ft.dropdown.Option("Billing"),
            ft.dropdown.Option("Staff"),
            ft.dropdown.Option("Admin"),
        ],
        value="All",
        width=200,
        border_color="primary", 
    )

    status_filter = ft.Dropdown(
        label="Filter by Status",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Pending"),
            ft.dropdown.Option("Approved"),
            ft.dropdown.Option("Rejected"),
        ],
        value="All",
        width=200,
        border_color="primary",
    )
    
    def load_users(e=None):
        try:
            query = search_field.value.lower() if search_field.value else ""
            role = role_filter.value

            conn = get_db_connection()
            cursor = conn.cursor()

            # Calculate user distribution per role to enforce minimum role constraints
            cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
            counts_result = cursor.fetchall()
            role_counts = {row[0]: row[1] for row in counts_result}

            # Fetch filtered user records
            sql = "SELECT * FROM users WHERE 1=1"
            params = []

            if query:
                sql += " AND (LOWER(username) LIKE ? OR LOWER(full_name) LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])

            if role != "All":
                sql += " AND role = ?"
                params.append(role)

            status = status_filter.value
            if status != "All":
                sql += " AND status = ?"
                params.append(status)

            sql += " ORDER BY CASE WHEN status = 'Pending' THEN 0 ELSE 1 END, created_at DESC"

            cursor.execute(sql, params)
            users = cursor.fetchall()
            conn.close()

            users_container.controls.clear()

            if users:
                # Render DataGrid Header
                users_container.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Username", size=13, weight="bold", expand=1),
                            ft.Text("Full Name", size=13, weight="bold", expand=2),
                            ft.Text("Role", size=13, weight="bold", expand=1),
                            ft.Text("Status", size=13, weight="bold", expand=1),
                            ft.Text("Email", size=13, weight="bold", expand=2),
                            ft.Text("Actions", size=13, weight="bold", expand=2),
                        ]),
                        bgcolor="surfaceVariant",
                        padding=15,
                        border_radius=8,
                    )
                )

                # Render DataGrid Rows
                for user in users:
                    # Verify minimum role requirement constraint
                    user_role = user['role']
                    total_in_role = role_counts.get(user_role, 0)
                    is_last_user = (total_in_role <= 1)

                    users_container.controls.append(
                        create_user_row(user, load_users, is_last_user)
                    )
                if e:
                    pass  # Suppress notifications during internal refresh
            else:
                users_container.controls.append(
                    ft.Container(
                        content=ft.Text("No users found", size=16, color="outline"),
                        padding=50,
                        alignment=ft.alignment.center,
                    )
                )
                if e:
                    show_warning(e.page, "No users found matching your criteria.", duration=2)

            if e:
                e.page.update()

        except Exception as ex:
            if e:
                show_error(e.page, "Error loading users.")
    
    # UI Component: DataGrid Row
    def create_user_row(user, refresh_callback, is_delete_disabled):
        
        def delete_user(e):
            def confirm_delete(dialog_e):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users WHERE id = ?", (user['id'],))
                    conn.commit()
                    conn.close()

                    dialog_e.page.close(dialog)
                    show_success(dialog_e.page, DELETE_SUCCESS.format(user['username']))
                    dialog_e.page.update()
                    refresh_callback(dialog_e)
                except Exception as ex:
                    show_error(dialog_e.page, "Failed to delete user.")

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirm Delete"),
                content=ft.Text(f"Delete user '{user['username']}'?\nThis cannot be undone."),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: e.page.close(dialog)),
                    ft.TextButton("Delete", on_click=confirm_delete),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            e.page.open(dialog)
        
        def edit_user(e):
            username_field = ft.TextField(label="Username", value=user['username'], disabled=True, border_color="primary")
            fullname_field = ft.TextField(label="Full Name", value=user['full_name'] or "", border_color="primary")
            lastname_field = ft.TextField(label="Last Name", value=user['last_name'] or "", border_color="primary")
            email_field = ft.TextField(label="Email", value=user['email'] or "", border_color="primary")
            phone_field = ft.TextField(label="Phone", value=user['phone'] or "", border_color="primary")
            
            role_field = ft.Dropdown(
                label="Role",
                options=[
                    ft.dropdown.Option("Patient", text="Customer"),
                    ft.dropdown.Option("Pharmacist"),
                    ft.dropdown.Option("Inventory"),
                    ft.dropdown.Option("Billing"),
                    ft.dropdown.Option("Staff"),
                    ft.dropdown.Option("Admin"),
                ],
                value=user['role'],
                border_color="primary"
            )
            
            password_field = ft.TextField(
                label="New Password (optional)",
                password=True,
                can_reveal_password=True,
                border_color="primary"
            )
            
            def save_changes(dialog_e):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()

                    # Validate email uniqueness
                    if email_field.value and email_field.value != user['email']:
                        cursor.execute("SELECT id FROM users WHERE email = ? AND id != ?", (email_field.value, user['id']))
                        if cursor.fetchone():
                            conn.close()
                            show_error(dialog_e.page, "This email is already used by another account!")
                            dialog_e.page.update()
                            return

                    if password_field.value:
                        cursor.execute("""
                            UPDATE users
                            SET full_name=?, last_name=?, email=?, phone=?, role=?, password=?
                            WHERE id=?
                        """, (fullname_field.value, lastname_field.value, email_field.value,
                              phone_field.value, role_field.value, password_field.value, user['id']))
                    else:
                        cursor.execute("""
                            UPDATE users
                            SET full_name=?, last_name=?, email=?, phone=?, role=?
                            WHERE id=?
                        """, (fullname_field.value, lastname_field.value, email_field.value,
                              phone_field.value, role_field.value, user['id']))

                    conn.commit()
                    conn.close()

                    dialog_e.page.close(edit_dialog)
                    show_success(dialog_e.page, UPDATE_SUCCESS.format(user['username']))
                    dialog_e.page.update()
                    refresh_callback(dialog_e)
                except Exception as ex:
                    show_error(dialog_e.page, "Failed to update user.")

            edit_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Edit User: {user['username']}"),
                content=ft.Container(
                    content=ft.Column([
                        username_field,
                        fullname_field,
                        lastname_field,
                        email_field,
                        phone_field,
                        role_field,
                        password_field,
                    ], tight=True, scroll=ft.ScrollMode.AUTO),
                    width=400,
                    height=400,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: e.page.close(edit_dialog)),
                    ft.TextButton("Save", on_click=save_changes),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            
            e.page.open(edit_dialog)
        
        user_status = dict(user).get('status', 'Approved')
        status_colors = {'Pending': '#FFA000', 'Approved': '#4CAF50', 'Rejected': '#F44336'}
        status_color = status_colors.get(user_status, '#9E9E9E')

        def approve_user(e):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET status = 'Approved' WHERE id = ?", (user['id'],))
                conn.commit()
                conn.close()
                show_success(e.page, f"User '{user['username']}' has been approved!")
                refresh_callback(e)
            except Exception as ex:
                show_error(e.page, "Failed to approve user.")

        def reject_user(e):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET status = 'Rejected' WHERE id = ?", (user['id'],))
                conn.commit()
                conn.close()
                show_error(e.page, f"User '{user['username']}' has been rejected.")
                refresh_callback(e)
            except Exception as ex:
                show_error(e.page, "Failed to reject user.")

        # Configure record action controls
        action_buttons = [
            ft.IconButton(
                icon=ft.icons.EDIT,
                icon_color="primary",
                tooltip="Edit User",
                on_click=edit_user,
            ),
        ]

        if user_status == 'Pending':
            action_buttons.insert(0, ft.IconButton(
                icon=ft.icons.CHECK_CIRCLE,
                icon_color="#4CAF50",
                tooltip="Approve User",
                on_click=approve_user,
            ))
            action_buttons.insert(1, ft.IconButton(
                icon=ft.icons.CANCEL,
                icon_color="#F44336",
                tooltip="Reject User",
                on_click=reject_user,
            ))

        action_buttons.append(
            ft.IconButton(
                icon=ft.icons.DELETE,
                icon_color="grey" if is_delete_disabled else "error",
                disabled=is_delete_disabled,
                tooltip="Cannot delete the last user of this role" if is_delete_disabled else "Delete User",
                on_click=delete_user,
            )
        )

        return ft.Container(
            content=ft.Row([
                ft.Text(user['username'], size=13, expand=1),
                ft.Text(user['full_name'] or "N/A", size=13, expand=2),
                ft.Container(
                    content=ft.Text("Customer" if user['role'] == "Patient" else user['role'], size=11, weight="bold", color="onPrimaryContainer"),
                    bgcolor="primaryContainer",
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=5,
                    expand=1,
                ),
                ft.Container(
                    content=ft.Text(user_status, size=11, weight="bold", color="white"),
                    bgcolor=status_color,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=5,
                    expand=1,
                ),
                ft.Text(user['email'] or "N/A", size=13, expand=2),
                ft.Row(action_buttons, spacing=2, expand=2),
            ]),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
        )
    
    def add_user(e):
        username_field = ft.TextField(label="Username *", hint_text="Unique username", border_color="primary")
        password_field = ft.TextField(label="Password *", password=True, can_reveal_password=True, border_color="primary")
        fullname_field = ft.TextField(label="Full Name", hint_text="First name", border_color="primary")
        lastname_field = ft.TextField(label="Last Name", border_color="primary")
        email_field = ft.TextField(label="Email", hint_text="user@example.com", border_color="primary")
        phone_field = ft.TextField(label="Phone", hint_text="09171234567", border_color="primary")
        
        role_field = ft.Dropdown(
            label="Role *",
            options=[
                ft.dropdown.Option("Patient", text="Customer"),
                ft.dropdown.Option("Pharmacist"),
                ft.dropdown.Option("Inventory"),
                ft.dropdown.Option("Billing"),
                ft.dropdown.Option("Staff"),
                ft.dropdown.Option("Admin"),
            ],
            value="Patient",
            border_color="primary"
        )
        
        def save_new_user(dialog_e):
            try:
                if not username_field.value or not password_field.value:
                    show_error(dialog_e.page, REQUIRED_FIELDS)
                    dialog_e.page.update()
                    return

                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("SELECT id FROM users WHERE username = ?", (username_field.value,))
                if cursor.fetchone():
                    conn.close()
                    show_error(dialog_e.page, "Username already exists!")
                    dialog_e.page.update()
                    return

                if email_field.value:
                    cursor.execute("SELECT id FROM users WHERE email = ?", (email_field.value,))
                    if cursor.fetchone():
                        conn.close()
                        show_error(dialog_e.page, "An account with this email already exists!")
                        dialog_e.page.update()
                        return

                cursor.execute("""
                    INSERT INTO users (username, password, role, full_name, last_name, email, phone, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (username_field.value, password_field.value, role_field.value,
                      fullname_field.value, lastname_field.value, email_field.value,
                      phone_field.value, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                conn.commit()
                conn.close()

                dialog_e.page.close(add_dialog)
                show_success(dialog_e.page, CREATE_SUCCESS.format(f"User '{username_field.value}'"))
                dialog_e.page.update()
                load_users(dialog_e)
            except Exception as ex:
                show_error(dialog_e.page, "Failed to create user.")
        
        add_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Add New User"),
            content=ft.Container(
                content=ft.Column([
                    username_field,
                    password_field,
                    fullname_field,
                    lastname_field,
                    email_field,
                    phone_field,
                    role_field,
                ], tight=True, scroll=ft.ScrollMode.AUTO),
                width=400,
                height=400,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: e.page.close(add_dialog)),
                ft.TextButton("Create", on_click=save_new_user),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        e.page.open(add_dialog)
    
    load_users(None)
    
    return ft.Column([
        ft.Row([
            ft.Text("User Management", size=28, weight="bold"),
        ]),
        ft.Text("Add, edit, and manage system users", size=14, color="grey"),
        
        ft.Container(height=20),
        
        ft.Row([
            search_field,
            role_filter,
            status_filter,
            ft.ElevatedButton(
                "Search",
                icon=ft.icons.SEARCH,
                bgcolor="primary",
                color="white",
                on_click=load_users,
            ),
            ft.ElevatedButton(
                "Add User",
                icon=ft.icons.ADD,
                bgcolor="secondary",
                color="white",
                on_click=add_user,
            ),
        ], spacing=10, run_spacing=10, wrap=True),
        
        ft.Container(height=20),
        
        users_container,
    ], scroll=ft.ScrollMode.AUTO, spacing=0)




