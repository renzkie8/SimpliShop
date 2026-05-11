"""Pharmacist dashboard overview with real database integration."""

import flet as ft
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader
from datetime import datetime

def PharmacistDashboard():
    """Main pharmacist dashboard with statistics and quick actions."""
    
    user = AppState.get_user()
    user_name = user['full_name'] if user else "Pharmacist"
    
    # Fetch dashboard statistics
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Metric: Pending Prescriptions
    cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Pending'")
    result = cursor.fetchone()
    pending_rx = result[0] if result else 0
    
    # Metric: Today's Approved Prescriptions
    cursor.execute("""
        SELECT COUNT(*) FROM prescriptions 
        WHERE status = 'Approved' 
        AND DATE(reviewed_date) = DATE('now')
    """)
    result = cursor.fetchone()
    approved_rx = result[0] if result else 0
    
    # Metric: Total Patient Count
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Patient'")
    result = cursor.fetchone()
    total_patients = result[0] if result else 0
    
    # Metric: Valid Inventory Items
    cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock > 0")
    result = cursor.fetchone()
    medicines_available = result[0] if result else 0
    
    # Fetch pending prescription details
    cursor.execute("""
        SELECT p.id, p.created_at, p.status,
               u.full_name as patient_name,
               m.name as medicine_name
        FROM prescriptions p
        LEFT JOIN users u ON p.patient_id = u.id
        LEFT JOIN medicines m ON p.medicine_id = m.id
        WHERE p.status = 'Pending'
        ORDER BY p.created_at DESC
        LIMIT 5
    """)
    pending_prescriptions = cursor.fetchall()
    
    # Fetch recent activity history
    cursor.execute("""
        SELECT action, details, timestamp
        FROM activity_log
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 5
    """, (user['id'],))
    recent_activities = cursor.fetchall()
    
    # Fetch inventory shortage alerts
    cursor.execute("""
        SELECT name, stock
        FROM medicines
        WHERE stock < 10  
        ORDER BY stock ASC
        LIMIT 15
    """)
    low_stock_medicines = cursor.fetchall()
    
    conn.close()
    
    # UI Component: Statistics Card
    def create_stat_card(title, value, icon, color, subtitle=""):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=40),
                    ft.Column([
                        ft.Text(title, size=14, color="outline"),
                        ft.Text(
                            str(value),
                            size=32,
                            weight="bold",
                            color=color,
                        ),
                        ft.Text(subtitle, size=11, color="outline") if subtitle else ft.Container(height=16),
                    ], spacing=2, expand=True),
                ], spacing=15),
            ]),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
            height=140,
        )
    
    # UI Component: Quick Action Button
    def create_action_button(text, icon, route, color):
        return ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(icon, color="onPrimary"),
                ft.Text(text, color="onPrimary"),
            ], spacing=10),
            bgcolor=color,
            on_click=lambda e: e.page.go(route),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=15,
            ),
        )
    
    # Utility: Relative Time Formatter
    def time_ago(timestamp_str):
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()
            delta = now - timestamp
            
            if delta.days > 0:
                return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
            elif delta.seconds >= 3600:
                hours = delta.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif delta.seconds >= 60:
                minutes = delta.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
        except:
            return timestamp_str
    
    # UI Component: Prescription Queue Item
    def create_prescription_item(rx):
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"Prescription #{rx[0]}", weight="bold", size=14),
                    ft.Text(f"Customer: {rx[3]}", size=12, color="outline"),
                    ft.Text(f"Medicine: {rx[4]}", size=12),
                    ft.Text(f"Submitted: {time_ago(rx[1])}", size=11, color="outline", italic=True),
                ], spacing=3, expand=True),
                ft.Container(
                    content=ft.Text("Pending", size=12, weight="bold", color="onTertiaryContainer"),
                    bgcolor=ft.colors.with_opacity(0.2, "tertiary"),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=15,
                ),
                ft.IconButton(
                    icon=ft.icons.ARROW_FORWARD,
                    icon_color="primary",
                    tooltip="Review Prescription",
                    on_click=lambda e, rx_id=rx[0]: e.page.go(f"/pharmacist/prescription/{rx_id}"),
                ),
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
        )
    
    # UI Component: Alert Notification Item
    def create_alert_item(message, icon, color):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color, size=24),
                ft.Text(message, size=13, expand=True),
            ], spacing=10),
            padding=12,
            border=ft.border.all(1, color),
            border_radius=8,
            bgcolor=ft.colors.with_opacity(0.05, color),
        )
    
    # UI Component: Activity Log Item
    def create_activity_item(action, details, timestamp):
        action_icons = {
            'prescription_approved': '✓',
            'prescription_rejected': '✗',
            'prescription_dispensed': '📦',
            'medicine_updated': '💊',
        }
        icon = action_icons.get(action, '•')
        
        return ft.Text(
            f"{icon} {details}",
            size=12,
            color="outline",
        )
    
    # Render pending prescriptions queue
    pending_rx_widgets = []
    if pending_prescriptions:
        for rx in pending_prescriptions:
            pending_rx_widgets.append(create_prescription_item(rx))
    else:
        pending_rx_widgets.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, size=60, color="primary"),
                    ft.Text("No pending prescriptions!", size=16, color="outline"),
                    ft.Text("Great job! All prescriptions have been reviewed.", size=12, color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=30,
            )
        )
    
    # Render activity timeline
    activity_widgets = []
    if recent_activities:
        for activity in recent_activities:
            activity_widgets.append(create_activity_item(activity[0], activity[1], activity[2]))
    else:
        activity_widgets.append(
            ft.Text("No recent activity", size=12, color="outline", italic=True)
        )
    
    # Render system alerts panel
    alert_widgets = []
    
    # Inventory shortage warnings
    low_stock_count = len(low_stock_medicines)
    if low_stock_count > 0:
        # Display aggregate count
        alert_widgets.append(
            create_alert_item(
                f"{low_stock_count} medicine(s) are low in stock",
                ft.icons.WARNING,
                "error"
            )
        )
        
        # Display specific items
        for med in low_stock_medicines[:5]:  # Show top 5
            alert_widgets.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.MEDICATION, size=16, color="error"),
                        ft.Text(f"{med[0]}: {med[1]} units left", size=12, expand=True),
                    ], spacing=5),
                    padding=8,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=5,
                )
            )
    
    # Prescription backlog warnings
    if pending_rx > 5:
        alert_widgets.append(
            create_alert_item(
                f"{pending_rx} prescriptions need review",
                ft.icons.PRIORITY_HIGH,
                "tertiary"
            )
        )
    elif pending_rx > 0:
        alert_widgets.append(
            create_alert_item(
                f"{pending_rx} prescription(s) waiting for review",
                ft.icons.INFO,
                "primary"
            )
        )
    
    # Empty state mapping
    if not alert_widgets:
        alert_widgets.append(
            create_alert_item(
                "All systems normal - No critical alerts",
                ft.icons.CHECK_CIRCLE,
                "primary"
            )
        )
    
    return ft.Column([
        # Primary Navigation Header
        NavigationHeader(
            f"Welcome, {user_name}",
            "Pharmacist Dashboard - Review and validate prescriptions",
            show_back=False,  # Dashboard is the starting point
            show_forward=False,
        ),
        
        # KPI metrics section
        ft.Row([
            create_stat_card(
                "Pending Reviews",
                pending_rx,
                ft.icons.PENDING_ACTIONS,
                "tertiary",
                "Requires action"
            ),
            create_stat_card(
                "Approved Today",
                approved_rx,
                ft.icons.CHECK_CIRCLE,
                "primary",
                "This shift"
            ),
            create_stat_card(
                "Total Customers",
                total_patients,
                ft.icons.PEOPLE,
                "secondary",
            ),
            create_stat_card(
                "Medicines Available",
                medicines_available,
                ft.icons.MEDICATION,
                "primary",
            ),
        ], spacing=15),
        
        ft.Container(height=20),
        
        # Fast navigation shortcuts
        ft.Container(
            content=ft.Column([
                ft.Text("Quick Actions", size=20, weight="bold"),
                ft.Row([
                    create_action_button(
                        "Review Prescriptions",
                        ft.icons.ASSIGNMENT,
                        "/pharmacist/prescriptions",
                        "primary",
                    ),
                    create_action_button(
                        "Search Medicines",
                        ft.icons.SEARCH,
                        "/pharmacist/medicines",
                        "secondary",
                    ),
                    create_action_button(
                        "Generate Report",
                        ft.icons.ANALYTICS,
                        "/pharmacist/reports",
                        "tertiary",
                    ),
                    create_action_button(
                        "Verify Orders",
                        ft.icons.VERIFIED,
                        "/staff/orders",
                        "primary",
                    ),
                ], spacing=15, wrap=True),
            ], spacing=15),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        # Main dashboard grid
        ft.Row([
            # Prescriptions queue panel
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.PRIORITY_HIGH, color="tertiary", size=24),
                        ft.Text("Prescriptions Requiring Review", size=20, weight="bold"),
                    ], spacing=10),
                    ft.Divider(),
                    
                    *pending_rx_widgets,
                    
                    ft.Container(height=10),
                    ft.TextButton(
                        "View All Prescriptions →",
                        on_click=lambda e: e.page.go("/pharmacist/prescriptions"),
                    ),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=2,
            ),
            
            # System alerts panel
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.NOTIFICATIONS_ACTIVE, color="error", size=24),
                        ft.Text("Alerts & Notifications", size=20, weight="bold"),
                    ], spacing=10),
                    ft.Divider(),
                    
                    *alert_widgets,
                    
                    ft.Container(height=15),
                    
                    ft.Text("Recent Activity", size=16, weight="bold"),
                    ft.Divider(height=10),
                    
                    ft.Container(
                        content=ft.Column(
                            activity_widgets,
                            spacing=8,
                        ),
                        padding=10,
                        border=ft.border.all(1, "outlineVariant"),
                        border_radius=8,
                    ),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=1,
            ),
        ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
    ], scroll=ft.ScrollMode.AUTO, spacing=0, expand=True)




