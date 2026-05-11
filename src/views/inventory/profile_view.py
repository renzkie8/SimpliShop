"""Inventory Manager profile and settings view."""

import flet as ft
from state.app_state import AppState
from services.database import get_db_connection
from utils.notifications import show_success, show_error

def InventoryProfileView():
    """Inventory Manager profile and account settings."""
    
    user = AppState.get_user()
    
    # Fetch user profile data
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user['id'],))
    row = cursor.fetchone()
    user_data = dict(row) 
    conn.close()
    
    # Utility Functions
    def get_display_name():
        fname = user_data.get('full_name', '') or ""
        return fname.strip()

    # Initialize display components
    txt_name_header = ft.Text(get_display_name(), size=24, weight="bold")
    txt_username_header = ft.Text(f"@{user_data['username']}", size=14, color="outline")
    
    txt_email = ft.Text(user_data['email'] or "Not provided", size=14, weight="bold")
    txt_phone = ft.Text(user_data['phone'] or "Not provided", size=14, weight="bold")
    txt_dob = ft.Text(user_data.get('dob') or "Not provided", size=14, weight="bold")
    txt_address = ft.Text(user_data.get('address') or "Not provided", size=14, weight="bold")

    def create_info_row(label, text_control, icon):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color="primary", size=24),
                ft.Column([
                    ft.Text(label, size=12, color="outline"),
                    text_control,
                ], spacing=2, expand=True),
            ], spacing=15),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
        )
    
    # Profile Editing Logic
    def edit_profile(e):
        
        def create_input(label, val, icon,multiline=True):
            return ft.TextField(
                label=label,
                value=val if val and val != "Not provided" else "",
                prefix_icon=icon,
                width=None,
                expand=True,
                border_color="primary",
                text_size=14,
            )

        full_name_field = create_input("Full Name", user_data.get('full_name'), ft.icons.PERSON)
        email_field = create_input("Email", user_data.get('email'), ft.icons.EMAIL)
        phone_field = create_input("Phone", user_data.get('phone'), ft.icons.PHONE)
        dob_field = create_input("Date of Birth (YYYY-MM-DD)", user_data.get('dob'), ft.icons.CAKE)
        address_field = create_input("Address", user_data.get('address'), ft.icons.HOME, multiline=True)
        
        def save_changes(dialog_e):
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE users 
                    SET full_name = ?, email = ?, phone = ?, dob = ?, address = ?
                    WHERE id = ?
                """, (
                    full_name_field.value,
                    email_field.value,
                    phone_field.value,
                    dob_field.value,
                    address_field.value,
                    user_data['id']
                ))
                conn.commit()
                
                user_data['full_name'] = full_name_field.value
                user_data['email'] = email_field.value
                user_data['phone'] = phone_field.value
                user_data['dob'] = dob_field.value
                user_data['address'] = address_field.value
                
                txt_name_header.value = get_display_name()
                txt_email.value = email_field.value or "Not provided"
                txt_phone.value = phone_field.value or "Not provided"
                txt_dob.value = dob_field.value or "Not provided"
                txt_address.value = address_field.value or "Not provided"

                user['full_name'] = full_name_field.value
                AppState.set_user(user)

                dialog_e.page.close(edit_dialog)
                show_success(dialog_e.page, "Profile updated successfully!")
                dialog_e.page.update()

            except Exception as ex:
                show_error(dialog_e.page, f"Error updating profile")
                dialog_e.page.update()
            finally:
                conn.close()
        
        edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([ft.Icon(ft.icons.EDIT, color="primary"), ft.Text("Edit Profile")]),
            bgcolor="surface",
            shape=ft.RoundedRectangleBorder(radius=12),
            content=ft.Container(
                width=500,
                padding=10,
                content=ft.Column([
                    full_name_field,
                    email_field,
                    phone_field,
                ], spacing=15, scroll=ft.ScrollMode.AUTO, tight=True)
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: e.page.close(edit_dialog)),
                ft.ElevatedButton("Save Changes", bgcolor="primary", color="white", on_click=save_changes),
            ],
            actions_padding=20,
        )
        e.page.open(edit_dialog)
    
    # Password Modification Logic
    def change_password(e):
        def create_pass_input(label, icon):
            return ft.TextField(
                label=label,
                password=True,
                can_reveal_password=True,
                prefix_icon=icon,
                width=float("inf"), 
                border_color="primary"
            )

        current_password = create_pass_input("Current Password", ft.icons.LOCK_OUTLINE)
        new_password = create_pass_input("New Password", ft.icons.LOCK)
        confirm_password = create_pass_input("Confirm New Password", ft.icons.LOCK_RESET)
        error_text = ft.Text("", color="error", size=12)
        
        def save_password(dialog_e):
            error_text.value = ""
            if not all([current_password.value, new_password.value, confirm_password.value]):
                error_text.value = "All fields are required"
                dialog_e.page.update()
                return
            
            if new_password.value != confirm_password.value:
                error_text.value = "New passwords do not match"
                dialog_e.page.update()
                return
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE id = ?", (user_data['id'],))
            stored_password = cursor.fetchone()['password']
            
            if current_password.value != stored_password:
                error_text.value = "Current password is incorrect"
                conn.close()
                dialog_e.page.update()
                return
            
            cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password.value, user_data['id']))
            conn.commit()
            conn.close()

            dialog_e.page.close(pwd_dialog)
            show_success(dialog_e.page, "Password changed successfully!")
            dialog_e.page.update()
        
        pwd_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([ft.Icon(ft.icons.LOCK_RESET, color="primary"), ft.Text("Change Password")]),
            bgcolor="surface",
            shape=ft.RoundedRectangleBorder(radius=12),
            content=ft.Container(
                width=500,
                padding=10,
                content=ft.Column([
                    current_password,
                    new_password,
                    confirm_password,
                    error_text,
                ], spacing=20, tight=True)
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: e.page.close(pwd_dialog)),
                ft.ElevatedButton("Change Password", bgcolor="primary", color="white", on_click=save_password),
            ],
            actions_padding=20,
        )
        e.page.open(pwd_dialog)
    
    # Navigation Handlers
    def logout(e):
        def confirm_logout(dialog_e):
            show_success(dialog_e.page, "Logged out successfully!", duration=2)
            AppState.set_user(None)
            dialog_e.page.go("/")
        
        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.icons.LOGOUT, color="error"),
                ft.Text("Confirm Logout")
            ]),
            content=ft.Text("Are you sure you want to logout?", size=14),
            actions=[
                ft.TextButton("Cancel", on_click=lambda x: e.page.close(confirm_dialog)),
                ft.ElevatedButton(
                    "Logout",
                    bgcolor="error",
                    color="white",
                    on_click=confirm_logout
                ),
            ],
        )
        e.page.open(confirm_dialog)
    
    # Main View Implementation
    return ft.Column([
        # Profile header section
        ft.Container(
            content=ft.Row([
                ft.Container(
                    width=100,
                    height=100,
                    bgcolor="primaryContainer",
                    border_radius=50,
                    content=ft.Icon(ft.icons.INVENTORY_2, size=50, color="onPrimaryContainer"),
                    alignment=ft.alignment.CENTER,
                ),
                ft.Column([
                    txt_name_header,
                    txt_username_header,
                    ft.Container(
                        content=ft.Text("Inventory Manager", size=12, weight="bold", color="onPrimaryContainer"),
                        bgcolor="primaryContainer",
                        padding=ft.padding.symmetric(horizontal=12, vertical=4),
                        border_radius=15,
                    ),
                ], spacing=5, expand=True),
                
                ft.ElevatedButton(
                    "Logout",
                    icon=ft.icons.LOGOUT,
                    bgcolor="error",
                    color="onError",
                    on_click=logout,
                ),
            ], spacing=20),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        ft.Text("Contact Information", size=20, weight="bold"),
        ft.Container(height=10),
        
        # Contact information grid
        ft.Row([
            ft.Column([
                create_info_row("Email", txt_email, ft.icons.EMAIL),
            ], spacing=10, expand=True),
            
            ft.Column([
                create_info_row("Phone", txt_phone, ft.icons.PHONE),
            ], spacing=10, expand=True),
        ], spacing=15),

        ft.Container(height=10),

        ft.Row([
            ft.Column([
                create_info_row("Date of Birth", txt_dob, ft.icons.CAKE),
            ], spacing=10, expand=True),
            
            ft.Column([
                create_info_row("Address", txt_address, ft.icons.HOME),
            ], spacing=10, expand=True),
        ], spacing=15),
        
        ft.Container(height=20),
        ft.Divider(),
        ft.Container(height=10),
        
        # Account management actions
        ft.Text("Account Actions", size=20, weight="bold"),
        ft.Container(height=10),
        
        ft.Column([
            # Edit Profile
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.EDIT, color="primary", size=24),
                    ft.Column([
                        ft.Text("Edit Profile", size=14, weight="bold"),
                        ft.Text("Update your personal information", size=12, color="outline"),
                    ], spacing=2, expand=True),
                    ft.Icon(ft.icons.CHEVRON_RIGHT, color="outline"),
                ], spacing=15),
                padding=15,
                border=ft.border.all(1, "outlineVariant"),
                border_radius=8,
                ink=True,
                on_click=edit_profile,
            ),
            
            # Change Password
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.LOCK, color="secondary", size=24),
                    ft.Column([
                        ft.Text("Change Password", size=14, weight="bold"),
                        ft.Text("Update your account password", size=12, color="outline"),
                    ], spacing=2, expand=True),
                    ft.Icon(ft.icons.CHEVRON_RIGHT, color="outline"),
                ], spacing=15),
                padding=15,
                border=ft.border.all(1, "outlineVariant"),
                border_radius=8,
                ink=True,
                on_click=change_password,
            ),
            
        ], spacing=10),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)


