"""Patient dashboard with real database integration."""

import flet as ft
from state import AppState
from services.database import get_db_connection

def PatientDashboard():
    """Main patient dashboard with live data from database."""
    
    # Retrieve authenticated user session
    user = AppState.get_user()
    if not user:
        return ft.Text("Please log in first", color="error")
    
    user_id = user['id']
    user_name = user['full_name'] if user.get('full_name') else "Customer"
    
    # Fetch dashboard statistics from database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch active prescription metrics
    cursor.execute("""
        SELECT COUNT(*) FROM prescriptions 
        WHERE patient_id = ? AND status IN ('Pending', 'Approved')
    """, (user_id,))
    active_prescriptions = cursor.fetchone()[0]
    
    # Fetch pending order metrics
    cursor.execute("""
        SELECT COUNT(*) FROM orders 
        WHERE patient_id = ? AND status IN ('Pending', 'Processing')
    """, (user_id,))
    pending_orders = cursor.fetchone()[0]
    
    # Fetch completed order metrics
    cursor.execute("""
        SELECT COUNT(*) FROM orders 
        WHERE patient_id = ? AND status = 'Completed'
    """, (user_id,))
    completed_orders = cursor.fetchone()[0]
    
    # Fetch recent order activity
    cursor.execute("""
        SELECT 
            o.id,
            o.status,
            o.order_date,
            o.total_amount,
            GROUP_CONCAT(m.name, ', ') as items
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN medicines m ON oi.medicine_id = m.id
        WHERE o.patient_id = ?
        GROUP BY o.id
        ORDER BY o.order_date DESC
        LIMIT 3
    """, (user_id,))
    recent_orders = cursor.fetchall()
    
    # Fetch recent prescription updates
    cursor.execute("""
        SELECT 
            p.id,
            p.status,
            p.created_at,
            m.name as medicine_name
        FROM prescriptions p
        LEFT JOIN medicines m ON p.medicine_id = m.id
        WHERE p.patient_id = ?
        ORDER BY p.created_at DESC
        LIMIT 2
    """, (user_id,))
    recent_prescriptions = cursor.fetchall()
    
    # Fetch low stock alerts
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
    def create_stat_card(title, value, icon, color):
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
                    ], spacing=2, expand=True),
                ], spacing=15),
            ]),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
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
    
    # UI Component: Order List Item
    def create_order_item(order):
        order_id = order[0]
        status = order[1]
        items = order[4] if order[4] else "No items"
        
        # Format item string length
        if len(items) > 30:
            items = items[:27] + "..."
        
        # Map order status to theme colors
        status_colors = {
            'Pending': 'tertiary',
            'Processing': 'secondary',
            'Ready': 'primary',
            'Completed': 'outline',
            'Cancelled': 'error'
        }
        status_color = status_colors.get(status, 'outline')
        
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"Order #{order_id}", weight="bold"),
                    ft.Text(items, size=12, color="outline"),
                ], spacing=2, expand=True),
                ft.Container(
                    content=ft.Text(
                        status, 
                        size=12, 
                        weight="bold", 
                        color="onPrimaryContainer"
                    ),
                    bgcolor=ft.colors.with_opacity(0.1, status_color),
                    padding=ft.padding.symmetric(horizontal=10, vertical=5),
                    border_radius=5,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
        )
    
    # UI Component: Notification Item
    def create_notification(title, time_str, icon, icon_color):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=icon_color, size=30),
                ft.Column([
                    ft.Text(title, size=13),
                    ft.Text(time_str, size=11, color="outline"),
                ], spacing=2, expand=True),
            ], spacing=10),
            padding=10,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=8,
        )
    
    # Render order timeline
    order_widgets = []
    if recent_orders:
        for order in recent_orders:
            order_widgets.append(create_order_item(order))
    else:
        order_widgets.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SHOPPING_BAG_OUTLINED, size=40, color="outline"),
                    ft.Text("No orders yet", color="outline"),
                    ft.Text("Start shopping to create your first order!", 
                           size=12, color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=20,
                alignment=ft.alignment.center,
            )
        )
    
    # Render notification feed
    notification_widgets = []
    
    # Append low stock warnings
    if low_stock_medicines:
        notification_widgets.append(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.icons.WARNING, color="error", size=24),
                        ft.Text("Low Stock Alert", size=13, weight="bold", color="error"),
                    ], spacing=5),
                    ft.Text(
                        f"{len(low_stock_medicines)} medicine(s) running low. Order soon!",
                        size=11,
                        color="outline"
                    ),
                ], spacing=3),
                padding=10,
                border=ft.border.all(1, "error"),
                border_radius=8,
                bgcolor=ft.colors.with_opacity(0.05, "error"),
            )
        )
    
    # Append prescription alerts
    if recent_prescriptions:
        for presc in recent_prescriptions:
            status = presc[1]
            medicine = presc[3] if presc[3] else "Prescription"
            created = presc[2]
            
            if status == 'Approved':
                notification_widgets.append(
                    create_notification(
                        f"{medicine} prescription approved",
                        created,
                        ft.icons.CHECK_CIRCLE,
                        "primary"
                    )
                )
            elif status == 'Pending':
                notification_widgets.append(
                    create_notification(
                        f"{medicine} prescription pending review",
                        created,
                        ft.icons.PENDING,
                        "tertiary"
                    )
                )
    
    # Render empty state
    if not notification_widgets:
        notification_widgets.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.NOTIFICATIONS_NONE, size=40, color="outline"),
                    ft.Text("No notifications", color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=20,
                alignment=ft.alignment.center,
            )
        )
    
    return ft.Column([
        # Header section
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.icons.WAVING_HAND, color="tertiary", size=40),
                ft.Column([
                    ft.Text(
                        f"Welcome back, {user_name}!",
                        size=28,
                        weight="bold",
                    ),
                    ft.Text(
                        "Here's your health overview",
                        size=14,
                        color="outline",
                    ),
                ], spacing=5),
            ], spacing=15),
            padding=20,
        ),
        
        # KPI metric cards
        ft.Row([
            create_stat_card(
                "Active Prescriptions", 
                active_prescriptions, 
                ft.icons.MEDICATION, 
                "primary"
            ),
            create_stat_card(
                "Pending Orders", 
                pending_orders, 
                ft.icons.PENDING_ACTIONS, 
                "tertiary"
            ),
            create_stat_card(
                "Completed Orders", 
                completed_orders, 
                ft.icons.CHECK_CIRCLE, 
                "primary"
            ),
        ], spacing=15, expand=True),
        
        ft.Container(height=20),
        
        # Fast navigation actions
        ft.Container(
            content=ft.Column([
                ft.Text("Quick Actions", size=20, weight="bold"),
                ft.Row([
                    create_action_button(
                        "Browse Medicines", 
                        ft.icons.SEARCH, 
                        "/patient/search", 
                        "primary"
                    ),
                    create_action_button(
                        "Upload Prescription", 
                        ft.icons.UPLOAD_FILE, 
                        "/patient/prescriptions", 
                        "secondary"
                    ),
                    create_action_button(
                        "View Cart", 
                        ft.icons.SHOPPING_CART, 
                        "/patient/cart", 
                        "tertiary"
                    ),
                ], spacing=15, wrap=True),
            ], spacing=15),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=False,
        ),
        
        ft.Container(height=20),
        
        # Activity feed and notifications panel
        ft.Row([
            # Order history panel
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Recent Orders", size=20, weight="bold"),
                        ft.TextButton(
                            "View All →", 
                            on_click=lambda e: e.page.go("/patient/orders")
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    ft.Column(order_widgets, spacing=10, expand=True),
                ], spacing=10, expand=True),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=1,
                height=300,
            ),
            
            # Notification panel
            ft.Container(
                content=ft.Column([
                    ft.Text("Notifications", size=20, weight="bold"),
                    ft.Divider(),
                    ft.Column(notification_widgets, spacing=10, expand=True),
                ], spacing=10, expand=True),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=1,
                height=300,
            ),
        ], spacing=15, expand=True),
    ], scroll=ft.ScrollMode.AUTO, spacing=0, expand=True)




