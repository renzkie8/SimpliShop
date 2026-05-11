"""Staff dashboard with quick access and statistics."""

import flet as ft
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def StaffDashboard():
    """Staff member dashboard with overview."""
    
    # Contextual user awareness
    user = AppState.get_user()
    user_name = user['full_name'] if user else "Staff Member"
    
    # Metrics Aggregation
    # Retrieve KPIs from database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Aggregate patient total
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Patient'")
    total_patients = cursor.fetchone()[0]
    
    # Retrieve current day new user metrics
    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE role = 'Patient' AND DATE(created_at) = DATE('now')
    """)
    new_today = cursor.fetchone()[0]
    
    # Calculate pending prescription volume
    cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Pending'")
    active_prescriptions = cursor.fetchone()[0]
    
    # Retrieve most recent user records
    cursor.execute("""
        SELECT id, full_name, phone, email, created_at
        FROM users
        WHERE role = 'Patient'
        ORDER BY created_at DESC
        LIMIT 5
    """)
    recent_patients = cursor.fetchall()
    
    # Terminate DB Connection
    conn.close()
    
    # Interface Component Helpers
    
    # Metric card component factory
    def create_stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=40),
                ft.Text(str(value), size=32, weight="bold", color=color),
                ft.Text(title, size=12, color="outline", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            padding=20,
            bgcolor="surface", # This ensures it looks good in dark mode (greyish)
            border_radius=12,
            border=ft.border.all(1, "outlineVariant"),
            expand=True, # This makes all 3 cards the same width
        )
    
    # Navigation action button generator
    def create_action_button(text, icon, route, color):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icon, color="onPrimary"),
                ft.Text(text, color="onPrimary", size=15, weight="bold"),
            ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=color,
            on_click=lambda e: e.page.go(route), # Go to the page when clicked
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=20, # Big padding makes it look modern
            ),
            width=1000, # Force it to stretch
        )
    
    # List element factory for recent patients
    def create_patient_item(patient):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.PERSON, color="primary", size=24),
                ft.Column([
                    ft.Text(patient[1], size=14, weight="bold"),
                    # Truncate timestamp to date format
                    ft.Text(f"Reg: {patient[4][:10]}", size=11, color="outline"),
                ], spacing=2, expand=True),
                # Transition trigger to detailed view
                ft.IconButton(
                    icon=ft.icons.ARROW_FORWARD_IOS,
                    icon_size=16,
                    icon_color="primary",
                    tooltip="View Details",
                    on_click=lambda e, pid=patient[0]: e.page.go(f"/staff/patient/{pid}"),
                ),
            ], spacing=10),
            padding=12,
            border=ft.border.only(bottom=ft.border.BorderSide(1, "outlineVariant")),
        )
    
    # --- MAIN LAYOUT ---
    return ft.Column([
        # Dashboard Header (No back button because this is the home page)
        NavigationHeader(
            f"Welcome, {user_name}",
            "Staff Portal - Assist with customer records and inquiries",
            show_back=False,
        ),
        
        # The main content area
        ft.Container(
            padding=ft.padding.all(20),
            content=ft.Column([
                
                # 1. The Stats Row (The 3 boxes)
                ft.Row([
                    create_stat_card("Total Customers", total_patients, ft.icons.GROUPS, "primary"),
                    create_stat_card("New Today", new_today, ft.icons.PERSON_ADD, "secondary"),
                    create_stat_card("Active Rx", active_prescriptions, ft.icons.MEDICATION, "tertiary"),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # 2. Split View (Actions on Left, Guidelines on Right)
                ft.Row([
                    # LEFT COLUMN: Buttons and Recent List
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Quick Actions", size=18, weight="bold"),
                            create_action_button("📦 Order Tracking", ft.icons.LOCAL_SHIPPING, "/staff/orders", "tertiary"),
                            create_action_button("Search Customers", ft.icons.SEARCH, "/staff/search", "primary"),
                            create_action_button("View All Customers", ft.icons.LIST, "/staff/patients", "secondary"),
                            create_action_button("Help Desk", ft.icons.HELP, "/staff/help", "tertiary"),
                            
                            ft.Container(height=20),
                            
                            # Recent Registrations Box
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Recent Registrations", size=16, weight="bold"),
                                    ft.Divider(),
                                    # Comprehension-based list rendering
                                    *([create_patient_item(p) for p in recent_patients] if recent_patients else [ft.Text("No new customers today", italic=True)]),
                                ], spacing=10),
                                padding=20,
                                bgcolor="surface",
                                border_radius=12,
                                border=ft.border.all(1, "outlineVariant"),
                            ),
                        ]),
                        expand=2, # Takes up 2/3 of the width
                    ),
                    
                    # RIGHT COLUMN: Static Guidelines info
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Staff Guidelines", size=18, weight="bold"),
                            ft.Container(
                                content=ft.Column([
                                    ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, size=16, color="primary"), ft.Text("Verify ID before sharing info", size=13)], spacing=10),
                                    ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, size=16, color="primary"), ft.Text("Keep customer data confidential", size=13)], spacing=10),
                                    ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, size=16, color="primary"), ft.Text("Report errors to Admin", size=13)], spacing=10),
                                    ft.Row([ft.Icon(ft.icons.CHECK_CIRCLE, size=16, color="primary"), ft.Text("Be polite and professional", size=13)], spacing=10),
                                ], spacing=15),
                                padding=20,
                                bgcolor="surface",
                                border_radius=12,
                                border=ft.border.all(1, "outlineVariant"),
                            ),
                            
                            ft.Container(height=20),
                            
                            # Read-only warning box
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.icons.LOCK, color="tertiary"),
                                    ft.Text("You have Read-Only access to customers.", size=12, expand=True)
                                ], spacing=10),
                                padding=15,
                                bgcolor=ft.colors.with_opacity(0.1, "tertiary"),
                                border_radius=10,
                            )
                        ]),
                        expand=1, # Takes up 1/3 of the width
                    )
                ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.START, expand=True)
                
            ])
        )
    ], scroll=ft.ScrollMode.AUTO, spacing=0, expand=True)


