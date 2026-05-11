import flet as ft
import threading
import time
import sqlite3
import threading
import time
from services.database import authenticate_user, get_db_connection
from state.app_state import AppState
from utils.notifications import show_success, show_error, show_warning, LOGIN_SUCCESS, LOGIN_FAILED, SIGNUP_SUCCESS, REQUIRED_FIELDS, PASSWORD_MISMATCH, DUPLICATE_USERNAME
from services.google_auth import get_auth_url, get_auth_result, clear_auth_result

def LandingPage(page: ft.Page):

    # Initialize theme toggle
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        e.control.icon = ft.icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE
        page.update()

    theme_icon_name = ft.icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.icons.DARK_MODE
    theme_toggle_btn = ft.IconButton(
        icon=theme_icon_name, 
        on_click=toggle_theme, 
        tooltip="Toggle Theme",
        style=ft.ButtonStyle(
            shape=ft.CircleBorder(),
            side=ft.BorderSide(1, "outlineVariant"),
        )
    )

    # Initialize input factory
    
    def create_input(label, password=False, icon=None):
        return ft.TextField(
            label=label,
            password=password,
            can_reveal_password=password,
            prefix_icon=icon,
            border_radius=8,
            border_color="outlineVariant",
            focused_border_color="primary",
            content_padding=16,
            text_size=14,
            height=50,
        )

    # Render authentication form
    login_user = create_input("Username or Email", icon=ft.icons.PERSON)
    login_pass = create_input("Password", password=True, icon=ft.icons.LOCK)
    
    login_role = ft.Dropdown(
        label="Select Role",
        border_radius=8,
        border_color="outlineVariant",
        focused_border_color="primary",
        content_padding=10,
        options=[
            ft.dropdown.Option("Patient", text="Customer"),
            ft.dropdown.Option("Admin", text="Administrator"),
            ft.dropdown.Option("Pharmacist"),
            ft.dropdown.Option("Inventory", text="Inventory Manager"),
            ft.dropdown.Option("Billing", text="Billing Clerk"),
            ft.dropdown.Option("Staff", text="Staff Member"),
        ],
    )
    
    login_error = ft.Text(color="error", size=12, text_align="center")

    # Render registration form
    su_f_name = create_input("First Name", icon=ft.icons.BADGE)
    su_l_name = create_input("Last Name", icon=ft.icons.BADGE)
    su_user = create_input("Username", icon=ft.icons.PERSON)
    su_email = create_input("Email Address", icon=ft.icons.EMAIL)
    su_pass = create_input("Create Password", password=True, icon=ft.icons.LOCK)
    su_phone = create_input("Phone Number", icon=ft.icons.PHONE)
    su_address = create_input("Address", icon=ft.icons.LOCATION_ON)

    su_role = ft.Dropdown(
        label="Register As",
        border_radius=8,
        border_color="outlineVariant",
        focused_border_color="primary",
        content_padding=10,
        options=[
            ft.dropdown.Option("Patient", text="Customer"),
            ft.dropdown.Option("Staff", text="Staff Member"),
            ft.dropdown.Option("Pharmacist"),
            ft.dropdown.Option("Inventory", text="Inventory Manager"),
            ft.dropdown.Option("Billing", text="Billing Clerk"),
        ]
    )
    su_error = ft.Text(color="error", size=12, text_align="center")

    # Authentication callbacks

    def handle_login(e):
        if not login_user.value or not login_pass.value or not login_role.value:
            login_error.value = "Please fill all fields."
            show_error(e.page, "Please fill all fields.")
            page.update()
            return
            
        user = authenticate_user(login_user.value, login_pass.value)
        if user:
            # Verify role authorization
            if user['role'] != login_role.value and user['role'] != 'Admin':
                login_error.value = f"Access Denied. You are not a {login_role.value}."
                show_error(e.page, f"Access Denied. You are not a {login_role.value}.")
                page.update()
                return

            # Verify account status
            if dict(user).get('status') == 'Pending':
                login_error.value = "Account pending Admin approval."
                show_error(e.page, "Account pending Admin approval.")
                page.update()
                return
            
            # Establish session context
            AppState.set_user(user)
            show_success(e.page, f"{LOGIN_SUCCESS} {user['full_name']} as {user['role']}")
            page.go("/dashboard")
        else:
            login_error.value = "Invalid Username or Password"
            show_error(e.page, "Invalid Username or Password")
            page.update()

    def handle_signup(e):
        if not su_f_name.value or not su_l_name.value or not su_user.value or not su_email.value or not su_pass.value or not su_phone.value or not su_address.value or not su_role.value:
            su_error.value = "Please fill all fields."
            show_error(e.page, "Please fill all fields.")
            page.update()
            return
            
        first = su_f_name.value
        last = su_l_name.value
        username = su_user.value
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Validate unique username
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                conn.close()
                su_error.value = "Username is already taken."
                show_error(e.page, "Username is already taken.")
                page.update()
                return
                
            # Validate unique email
            if su_email.value:
                cursor.execute("SELECT id FROM users WHERE email = ?", (su_email.value,))
                if cursor.fetchone():
                    conn.close()
                    su_error.value = "An account with this email already exists."
                    show_error(e.page, "An account with this email already exists.")
                    page.update()
                    return

            # Validate unique full name
            full_name_combined = f"{first} {last}".strip()
            cursor.execute(
                "SELECT id FROM users WHERE (full_name || ' ' || last_name) = ? OR full_name = ?", 
                (full_name_combined, first)
            )
            if cursor.fetchone():
                conn.close()
                su_error.value = "An account with this name already exists."
                show_error(e.page, "An account with this name already exists.")
                page.update()
                return

            # Persist user record
            cursor.execute(
                "INSERT INTO users (username, password, role, full_name, last_name, email, phone, address, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (username, su_pass.value, su_role.value, first, last, su_email.value, su_phone.value, su_address.value, 'Pending')
            )
            conn.commit()
            conn.close()
            su_error.value = ""
            show_success(e.page, "Account created! Pending Admin approval.")
            # Navigate to authentication tab
            switch_tab(None, "login")
            login_user.value = username
            page.update()
        except sqlite3.IntegrityError:
            su_error.value = "Account creation failed (username might exist)."
            show_error(e.page, "Account creation failed (username might exist).")
            page.update()
        except Exception as ex:
            su_error.value = "An unexpected error occurred during signup."
            show_error(e.page, "An unexpected error occurred during signup.")
            page.update()

    # Google OAuth implementation
    _polling = {"active": False}  # Prevent concurrent polling threads

    def handle_google_signup(e):
        """Initialize Google OAuth registration flow."""
        clear_auth_result()
        url = get_auth_url(mode="signup")
        page.launch_url(url, web_popup_window=True, window_width=500, window_height=600)
        _start_polling()

    def handle_google_login(e):
        """Initialize Google OAuth authentication flow."""
        clear_auth_result()
        url = get_auth_url(mode="login")
        page.launch_url(url, web_popup_window=True, window_width=500, window_height=600)
        _start_polling()

    def _start_polling():
        """Background daemon to poll for OAuth authentication payload."""
        if _polling["active"]:
            return
        _polling["active"] = True

        def _poll():
            try:
                for _ in range(60):  # Maximum polling duration: 120 seconds
                    time.sleep(2)
                    result = get_auth_result()
                    if result:
                        clear_auth_result()
                        _polling["active"] = False
                        try:
                            _process_google_result(result)
                        except Exception as process_ex:
                            login_error.value = str(process_ex)
                            page.update()
                        return
                _polling["active"] = False
            except Exception as e:
                _polling["active"] = False
                login_error.value = str(e)
                page.update()

        t = threading.Thread(target=_poll, daemon=True)
        t.START()

    def _process_google_result(result):
        """Process OAuth payload for authentication or registration."""
        email = result.get("email", "")
        given_name = result.get("given_name", "")
        family_name = result.get("family_name", "")
        full_name = result.get("name", "Google User")
        username = email.split("@")[0] if email else "google_user"
        mode = result.get("mode", "login")

        if mode == "login":
            # Authenticate user via Google identity
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND email != ''", (email,))
            existing_user = cursor.fetchone()
            conn.close()
            
            if existing_user:
                if dict(existing_user).get('status') == 'Pending':
                    login_error.value = "Account pending Admin approval."
                    show_error(page, "Account pending Admin approval.")
                    page.update()
                    return
                AppState.set_user(existing_user)
                show_success(page, f"Welcome back, {given_name or full_name}!")
                page.go("/dashboard")
            else:
                login_error.value = "No account found. Please sign up first."
                show_error(page, "No account found with this Google email. Please sign up first.")
                page.update()
        else:
            # Pre-fill registration fields with Google identity details
            su_f_name.value = given_name or full_name.split(" ")[0]
            su_l_name.value = family_name or (full_name.split(" ", 1)[1] if " " in full_name else "")
            su_user.value = username
            su_email.value = email
            # Transition to role selection view
            switch_tab(None, "signup")
            show_success(page, f"Welcome {given_name or full_name}! Please select a role and fill remaining fields.")
            page.update()

    def handle_forgot_password(e):
        show_error(e.page, "Please contact the Administrator to reset your password.")
        page.update()

    # Primary layout construction

    def create_social_btn(text, on_click):
        # OAuth Single Sign-On Button Component
        return ft.Container(
            content=ft.Row([
                ft.Image(src="https://upload.wikimedia.org/wikipedia/commons/c/c1/Google_%22G%22_logo.svg", width=18, height=18),
                ft.Text(text, weight="w500", color="onSurface")
            ], alignment=ft.MainAxisAlignment.CENTER),
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            padding=12,
            ink=True,
            on_click=on_click
        )

    divider = ft.Row([
        ft.Container(expand=True, content=ft.Divider(height=1, thickness=1, color="outlineVariant")),
        ft.Text("OR", size=11, color="outline"),
        ft.Container(expand=True, content=ft.Divider(height=1, thickness=1, color="outlineVariant")),
    ], spacing=15)

    # Assemble authentication view
    login_form = ft.Column([
        create_social_btn("Continue with Google", handle_google_login),
        ft.Container(height=10),
        divider,
        ft.Container(height=10),
        login_user,
        login_pass,
        login_role,
        ft.Container(height=5),
        ft.ElevatedButton("Login", width=float("inf"), height=48, 
                          style=ft.ButtonStyle(
                              shape=ft.RoundedRectangleBorder(radius=8),
                              bgcolor="#00897b",
                              color=ft.colors.WHITE
                          ), on_click=handle_login),
        login_error,
        ft.Container(height=10),
        ft.Row([ft.TextButton("Forgot Password?", style=ft.ButtonStyle(color="#00897b"), on_click=handle_forgot_password)], alignment=ft.MainAxisAlignment.CENTER),
    ], spacing=15)

    # Assemble registration view
    signup_form = ft.Column([
        create_social_btn("Sign up with Google", handle_google_signup),
        ft.Container(height=10),
        divider,
        ft.Container(height=10),
        ft.Row([ft.Container(su_f_name, expand=True), ft.Container(su_l_name, expand=True)], spacing=10),
        su_user,
        su_email,
        su_pass,
        su_phone,
        su_address,
        su_role,
        ft.Container(height=5),
        ft.ElevatedButton("Create Account", width=float("inf"), height=48, 
                          style=ft.ButtonStyle(
                              shape=ft.RoundedRectangleBorder(radius=8),
                              bgcolor="#00897b",
                              color=ft.colors.WHITE
                          ), on_click=handle_signup),
        su_error,
    ], spacing=15, visible=False)

    # Render navigation tabs
    tab_login = ft.Container(
        content=ft.Text("Login", size=16, weight="w600", color="#00897b"),
        padding=ft.padding.only(bottom=10, left=20, right=20),
        border=ft.border.only(bottom=ft.BorderSide(2, "#00897b")),
        on_click=lambda e: switch_tab(e, "login"),
        ink=True
    )
    
    tab_signup = ft.Container(
        content=ft.Text("Sign Up", size=16, weight="w600", color="outline"),
        padding=ft.padding.only(bottom=10, left=20, right=20),
        border=ft.border.only(bottom=ft.BorderSide(2, ft.colors.TRANSPARENT)),
        on_click=lambda e: switch_tab(e, "signup"),
        ink=True
    )

    def switch_tab(e, tab_name):
        if tab_name == "login":
            tab_login.content.color = "#00897b"
            tab_login.border = ft.border.only(bottom=ft.BorderSide(2, "#00897b"))
            tab_signup.content.color = "outline"
            tab_signup.border = ft.border.only(bottom=ft.BorderSide(2, ft.colors.TRANSPARENT))
            login_form.visible = True
            signup_form.visible = False
        else:
            tab_signup.content.color = "#00897b"
            tab_signup.border = ft.border.only(bottom=ft.BorderSide(2, "#00897b"))
            tab_login.content.color = "outline"
            tab_login.border = ft.border.only(bottom=ft.BorderSide(2, ft.colors.TRANSPARENT))
            signup_form.visible = True
            login_form.visible = False
        page.update()

    tabs_row = ft.Row([tab_login, tab_signup], alignment=ft.MainAxisAlignment.CENTER, spacing=0)

    right_panel = ft.Container(
        expand=1,
        bgcolor="surface",
        padding=40,
        alignment=ft.alignment.CENTER,
        content=ft.Column([
            ft.Row([ft.Container(expand=True), theme_toggle_btn]),
            ft.Container(expand=True),
            ft.Container(
                width=420,
                content=ft.Column([
                    tabs_row,
                    ft.Container(height=20),
                    login_form,
                    signup_form
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ),
            ft.Container(expand=True),
            ft.Text("Group 5: Colico | David | Nonato", size=12, color="outline", text_align="center")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.CENTER)
    )

    # Render branding section
    left_panel = ft.Container(
        expand=1,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=["#00564d", "#00897b"]
        ),
        padding=40,
        alignment=ft.alignment.CENTER,
        content=ft.Column([
            ft.Text("PharmaOps", size=48, weight="bold", color=ft.colors.WHITE, style=ft.TextStyle(shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK26))),
            ft.Text("Pharmacy Management System", size=18, color=ft.colors.WHITE70),
            ft.Container(height=30),
            ft.Container(
                content=ft.Text("\u201cEfficient Pharmacy Management\nfor Better Healthcare.\u201d", 
                                size=16, color=ft.colors.WHITE, text_align="center", italic=True),
                border=ft.border.only(top=ft.BorderSide(1, ft.colors.WHITE30)),
                padding=ft.padding.only(top=20)
            ),
            ft.Container(height=40),
            ft.Icon(ft.icons.MONITOR_HEART, size=60, color=ft.colors.WHITE30)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER)
    )

    view = ft.Row(
        expand=True,
        spacing=0,
        controls=[left_panel, right_panel]
    )

    return view


