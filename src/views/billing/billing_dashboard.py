"""Billing dashboard with comprehensive billing features."""

import flet as ft
from datetime import datetime, timedelta
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def BillingDashboard():
    """Main billing dashboard with statistics and quick actions."""
    
    user = AppState.get_user()
    user_name = user['full_name'] if user else "Billing Clerk"
    
    # Initialize default metric values
    pending_invoices = 0
    paid_today = 0
    revenue_today = 0.0
    pending_amount = 0.0
    recent_invoices = []
    recent_activities = []

    # Data Retrieval and Aggregation
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query pending invoice totals
        cursor.execute("SELECT COUNT(*) FROM invoices WHERE status = 'Unpaid'")
        pending_invoices = cursor.fetchone()[0] or 0
        
        # Query daily completed transactions count
        cursor.execute("SELECT COUNT(*) FROM invoices WHERE status = 'Paid' AND DATE(payment_date) = DATE('now')")
        paid_today = cursor.fetchone()[0] or 0
        
        # Query daily realized revenue
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE status = 'Paid' AND DATE(payment_date) = DATE('now')")
        revenue_today = cursor.fetchone()[0] or 0.0
        
        # Query total outstanding receivables
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM invoices WHERE status = 'Unpaid'")
        pending_amount = cursor.fetchone()[0] or 0.0
        
        # Query recent invoice records
        cursor.execute("""
            SELECT i.id, i.invoice_number, i.total_amount, i.status, i.created_at, u.full_name as patient_name
            FROM invoices i
            LEFT JOIN users u ON i.patient_id = u.id
            ORDER BY i.id ASC LIMIT 5
        """)
        recent_invoices = cursor.fetchall()
        
        # Query recent user activity
        try:
            cursor.execute("""
                SELECT action, details, timestamp FROM activity_log
                WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5
            """, (user['id'],))
            recent_activities = cursor.fetchall()
        except: 
            recent_activities = []
        
        conn.close()
    except Exception as e:
        pass
    
    # UI Component Definitions
    
    # UI Component: Statistics Card (Fixed Dimension)
    def create_stat_card(title, value, icon, color, subtitle="", is_currency=False):
        display_value = f"₱{value:,.2f}" if is_currency else str(value)
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=40),
                    ft.Column([
                        ft.Text(title, size=14, color="outline"),
                        ft.Text(
                            display_value,
                            size=28 if is_currency else 32,
                            weight="bold",
                            color=color,
                        ),
                        # Vertical alignment spacer
                        ft.Text(subtitle, size=11, color="outline") if subtitle else ft.Container(height=16),
                    ], spacing=2, expand=True),
                ], spacing=15),
            ]),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
            height=140, # Apply constrained height
        )
    
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
    
    def create_invoice_item(inv):
        status_colors = {"Paid": "primary", "Unpaid": "error", "Partial": "tertiary", "Cancelled": "outline"}
        status_color = status_colors.get(inv[3], "outline")
        
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"Invoice #{inv[1]}", weight="bold", size=14),
                    ft.Text(f"Customer: {inv[5]}", size=12, color="outline"),
                    ft.Text(f"Amount: ₱{inv[2]:,.2f}", size=13, weight="bold", color="primary"),
                    ft.Text(f"Date: {inv[4]}", size=11, color="outline", italic=True),
                ], spacing=3, expand=True),
                ft.Container(
                    content=ft.Text(inv[3], size=12, weight="bold", color="white"),
                    bgcolor=status_color,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    border_radius=15,
                ),
                ft.IconButton(
                    icon=ft.icons.ARROW_FORWARD,
                    icon_color="primary",
                    tooltip="View Invoice",
                    on_click=lambda e, inv_id=inv[0]: e.page.go(f"/billing/invoice/{inv_id}"),
                ),
            ], spacing=10),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
            bgcolor="surface",
        )
    
    def create_activity_item(action, details, timestamp):
        action_icons = {'invoice_created': '📄', 'payment_received': '💰', 'invoice_cancelled': '❌'}
        icon = action_icons.get(action, '•')
        return ft.Text(f"{icon} {details}", size=12, color="outline")
    
    # Render dynamic lists
    invoice_widgets = [create_invoice_item(inv) for inv in recent_invoices] if recent_invoices else [ft.Container(content=ft.Text("No recent invoices", color="outline"), padding=20)]
    activity_widgets = [create_activity_item(a[0], a[1], a[2]) for a in recent_activities] if recent_activities else [ft.Text("No recent activity", color="outline")]
    
    return ft.Column([
        NavigationHeader(f"Welcome, {user_name}", "Billing Dashboard - Manage invoices and payments", show_back=False),
        
        ft.Container(
            content=ft.Column([
                # Stats (Fixed Height)
                ft.Row([
                    create_stat_card("Pending Invoices", pending_invoices, ft.icons.PENDING_ACTIONS, "error", "Awaiting payment"),
                    create_stat_card("Paid Today", paid_today, ft.icons.CHECK_CIRCLE, "primary", "Completed transactions"),
                    create_stat_card("Today's Revenue", revenue_today, ft.icons.ATTACH_MONEY, "primary", is_currency=True),
                    create_stat_card("Pending Amount", pending_amount, ft.icons.MONEY_OFF, "error", is_currency=True),
                ], spacing=15), 
                
                ft.Container(height=20),
                
                # Quick Actions
                ft.Container(
                    content=ft.Column([
                        ft.Text("Quick Actions", size=20, weight="bold"),
                        ft.Row([
                            create_action_button("Create Invoice", ft.icons.ADD_CARD, "/billing/create-invoice", "primary"),
                            create_action_button("View All Invoices", ft.icons.RECEIPT_LONG, "/billing/invoices", "secondary"),
                            create_action_button("Payment History", ft.icons.HISTORY, "/billing/payments", "tertiary"),
                            create_action_button("Generate Report", ft.icons.ANALYTICS, "/billing/reports", "primary"),
                            create_action_button("Verify Orders", ft.icons.VERIFIED, "/staff/orders", "secondary"),
                        ], spacing=15, wrap=True),
                    ], spacing=15),
                    padding=20, bgcolor="surface", border_radius=10, border=ft.border.all(1, "outlineVariant"),
                ),
                
                ft.Container(height=20),
                
                # Main Content Grid
                ft.Row([
                    # Recent Invoices Column
                    ft.Container(
                        content=ft.Column([
                            ft.Row([ft.Icon(ft.icons.RECEIPT, color="primary"), ft.Text("Recent Invoices", size=20, weight="bold")], spacing=10),
                            ft.Divider(),
                            *invoice_widgets,
                            ft.TextButton("View All Invoices →", on_click=lambda e: e.page.go("/billing/invoices")),
                        ], spacing=10),
                        padding=20, bgcolor="surface", border_radius=10, border=ft.border.all(1, "outlineVariant"), expand=2,
                    ),
                    
                    # Recent Activity Column
                    ft.Container(
                        content=ft.Column([
                            ft.Row([ft.Icon(ft.icons.HISTORY, color="primary"), ft.Text("Recent Activity", size=20, weight="bold")], spacing=10),
                            ft.Divider(),
                            ft.Container(content=ft.Column(activity_widgets, spacing=8), padding=10, border=ft.border.all(1, "outlineVariant"), border_radius=8),
                        ], spacing=10),
                        padding=20, bgcolor="surface", border_radius=10, border=ft.border.all(1, "outlineVariant"), expand=1,
                    ),
                ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
            ], spacing=0, expand=True),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0, expand=True)




