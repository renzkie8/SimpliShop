"""System activity logs with real database data."""

import flet as ft
from services.database import get_db_connection
from datetime import datetime, timedelta, timezone

def SystemLogs():
    """System logs and activity monitoring with real data."""
    
    logs_container = ft.Column(spacing=10)
    
    # Filter controls
    log_type_filter = ft.Dropdown(
        label="Log Type",
        options=[
            ft.dropdown.Option("all", "All Activities"),
            ft.dropdown.Option("users", "User Activity"),
            ft.dropdown.Option("prescriptions", "Prescriptions"),
            ft.dropdown.Option("orders", "Orders"),
            ft.dropdown.Option("inventory", "Inventory Changes"),
        ],
        value="all",
        width=250,
        border_color="primary", # Adjust visibility parameter
    )
    
    date_filter = ft.Dropdown(
        label="Time Period",
        options=[
            ft.dropdown.Option("today", "Today"),
            ft.dropdown.Option("week", "Last 7 Days"),
            ft.dropdown.Option("month", "Last 30 Days"),
            ft.dropdown.Option("all", "All Time"),
        ],
        value="week",
        width=200,
        border_color="primary", # Adjust visibility parameter
    )
    
    search_field = ft.TextField(
        hint_text="Search logs...",
        prefix_icon=ft.icons.SEARCH,
        border_color="primary", # Adjust visibility parameter
        width=300,
    )
    
    def get_real_logs():
        """Get real activity logs from database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logs = []
        
        # Query system registration volume
        cursor.execute("""
            SELECT id, username, full_name, role, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 20
        """)
        users = cursor.fetchall()
        
        for user in users:
            logs.append({
                "timestamp": user[4],
                "user": user[1],
                "action": f"New {'Customer' if user[3] == 'Patient' else user[3]} Registered",
                "details": f"User '{user[2] or user[1]}' created account",
                "type": "users",
                "icon": ft.icons.PERSON_ADD,
                "color": "primary",
            })
        
        # Query system prescription volume
        cursor.execute("""
            SELECT p.id, p.status, p.created_at, u.username, u.full_name
            FROM prescriptions p
            JOIN users u ON p.patient_id = u.id
            ORDER BY p.created_at DESC
            LIMIT 20
        """)
        prescriptions = cursor.fetchall()
        
        for rx in prescriptions:
            status = rx[1]
            color = "primary" if status == "Approved" else "tertiary" if status == "Pending" else "error"
            icon = ft.icons.CHECK_CIRCLE if status == "Approved" else ft.icons.PENDING if status == "Pending" else ft.icons.CANCEL
            
            logs.append({
                "timestamp": rx[2],
                "user": rx[3],
                "action": f"Prescription #{rx[0]} {status}",
                "details": f"Prescription for {rx[4] or rx[3]} status: {status}",
                "type": "prescriptions",
                "icon": icon,
                "color": color,
            })
        
        # Query commerce operations volume
        cursor.execute("""
            SELECT o.id, o.status, o.order_date, o.total_amount, u.username, u.full_name
            FROM orders o
            JOIN users u ON o.patient_id = u.id
            ORDER BY o.order_date DESC
            LIMIT 20
        """)
        orders = cursor.fetchall()
        
        for order in orders:
            status = order[1]
            color = "primary" if status == "Completed" else "tertiary" if status == "Pending" else "secondary"
            
            logs.append({
                "timestamp": order[2],
                "user": order[4],
                "action": f"Order #{order[0]} - {status}",
                "details": f"{order[5] or order[4]} placed order for ₱{order[3]:.2f}",
                "type": "orders",
                "icon": ft.icons.SHOPPING_CART,
                "color": color,
            })
        
        # Query inventory modifications
        cursor.execute("""
            SELECT id, name, stock, created_at
            FROM medicines
            ORDER BY created_at DESC
            LIMIT 15
        """)
        medicines = cursor.fetchall()
        
        for med in medicines:
            logs.append({
                "timestamp": med[3],
                "user": "system",
                "action": "Medicine Added",
                "details": f"{med[1]} added to inventory (Stock: {med[2]})",
                "type": "inventory",
                "icon": ft.icons.INVENTORY,
                "color": "secondary",
            })
        
        # Query billing generation activity
        cursor.execute("""
            SELECT i.id, i.invoice_number, i.total_amount, i.status, i.created_at, u.username
            FROM invoices i
            JOIN users u ON i.patient_id = u.id
            ORDER BY i.created_at DESC
            LIMIT 15
        """)
        invoices = cursor.fetchall()
        
        for inv in invoices:
            logs.append({
                "timestamp": inv[4],
                "user": inv[5],
                "action": f"Invoice {inv[1]} Generated",
                "details": f"Invoice for ₱{inv[2]:.2f} - Status: {inv[3]}",
                "type": "billing",
                "icon": ft.icons.RECEIPT,
                "color": "tertiary",
            })
            
        # Query system action audit table
        try:
            cursor.execute("""
                SELECT timestamp, user_id, action, details 
                FROM activity_log 
                ORDER BY timestamp DESC 
                LIMIT 30
            """)
            activities = cursor.fetchall()
            for act in activities:
                logs.append({
                    "timestamp": act[0],
                    "user": str(act[1]), # User ID
                    "action": act[2],
                    "details": act[3],
                    "type": "system",
                    "icon": ft.icons.SETTINGS,
                    "color": "secondary",
                })
        except:
            pass # Table might not exist
        
        conn.close()
        
        # Enforce reverse chronological order
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return logs
    
    def create_log_entry(log):
        """Create a log entry card."""
        # Determine relative elapsed time
        try:
            log_time = datetime.strptime(log['timestamp'], "%Y-%m-%d %H:%M:%S")
            time_ago = get_time_ago(log_time)
        except:
            time_ago = log['timestamp']
        
        return ft.Container(
            content=ft.Row([
                # Icon
                ft.Container(
                    content=ft.Icon(log['icon'], color=log['color'], size=24),
                    bgcolor=ft.colors.with_opacity(0.1, log['color']),
                    width=50,
                    height=50,
                    border_radius=25,
                    alignment=ft.alignment.CENTER,
                ),
                # Log details
                ft.Column([
                    ft.Row([
                        ft.Text(log['action'], size=15, weight="bold"),
                        ft.Container(
                            content=ft.Text(log['type'], size=11, color="onSecondaryContainer"),
                            bgcolor="secondaryContainer",
                            padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            border_radius=10,
                        ),
                    ], spacing=10),
                    ft.Text(log['details'], size=13, color="outline"),
                    ft.Row([
                        ft.Icon(ft.icons.PERSON, size=14, color="outline"),
                        ft.Text(log['user'], size=12, color="outline"),
                        ft.Icon(ft.icons.ACCESS_TIME, size=14, color="outline"),
                        ft.Text(time_ago, size=12, color="outline"),
                    ], spacing=5),
                ], spacing=5, expand=True),
            ], spacing=15),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface", # Adjust visibility parameter
        )
    
    def get_time_ago(log_time):
        """Convert UTC datetime to 'time ago' format."""
        # Use UTC time since SQLite stores CURRENT_TIMESTAMP in UTC
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        
        # Handle potential microseconds in timestamp
        try:
            if '.' in str(log_time):
                log_time = datetime.strptime(str(log_time).split('.')[0], "%Y-%m-%d %H:%M:%S")
            else:
                log_time = datetime.strptime(str(log_time), "%Y-%m-%d %H:%M:%S")
        except:
            return str(log_time)
        
        diff = now - log_time
        
        if diff.days > 30:
            return f"{diff.days // 30} months ago"
        elif diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "Just now"
    
    def load_logs(e=None):
        """Load and filter logs."""
        logs_container.controls.clear()
        
        # Get logs from database
        all_logs = get_real_logs()
        
        # Apply filters
        log_type = log_type_filter.value
        date_range = date_filter.value
        search_query = search_field.value.lower() if search_field.value else ""
        
        # Filter by type
        if log_type != "all":
            all_logs = [log for log in all_logs if log['type'] == log_type]
        
        # Filter by date
        if date_range != "all":
            # Use UTC since SQLite stores CURRENT_TIMESTAMP in UTC
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            
            if date_range == "today":
                # Get start of today (UTC)
                cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif date_range == "week":
                cutoff = now - timedelta(days=7)
            else:  # month
                cutoff = now - timedelta(days=30)
            
            # Filter with proper timestamp parsing
            filtered_logs = []
            for log in all_logs:
                try:
                    # Handle potential microseconds in timestamp
                    timestamp_str = str(log['timestamp']).split('.')[0]
                    log_datetime = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    if log_datetime >= cutoff:
                        filtered_logs.append(log)
                except:
                    # If parsing fails, include the log to be safe
                    filtered_logs.append(log)
            
            all_logs = filtered_logs
        
        # Execute client-side fuzzy search filter
        if search_query:
            all_logs = [
                log for log in all_logs
                if search_query in log['action'].lower() 
                or search_query in log['details'].lower()
                or search_query in log['user'].lower()
            ]
        
        # Conditional empty state rendering
        if all_logs:
            logs_container.controls.append(
                ft.Text(
                    f"Showing {len(all_logs)} log entries",
                    size=14,
                    color="outline",
                    weight="bold",
                )
            )
            
            for log in all_logs[:50]:  # Show max 50 logs
                logs_container.controls.append(create_log_entry(log))
        else:
            logs_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No logs found", size=18, color="outline"),
                        ft.Text("Try adjusting your filters", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.CENTER,
                )
            )
        
        if e:
            e.page.update()
    
    # Initialize primary component state
    class FakePage:
        dialog = None
        snack_bar = None
        def update(self): pass
    load_logs(type('Event', (), {'page': FakePage()})())
    
    return ft.Column([
        # Header
        ft.Row([
            ft.Text("System Activity Logs", size=28, weight="bold"),
        ]),
        ft.Text("Monitor real-time user activities and system events", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Filters and controls
        ft.Container(
            content=ft.Column([
                ft.Row([
                    log_type_filter,
                    date_filter,
                    search_field,
                ], spacing=10, wrap=True),
                
                ft.Row([
                    ft.ElevatedButton(
                        "Refresh Logs",
                        icon=ft.icons.REFRESH,
                        bgcolor="primary",
                        color="onPrimary",
                        on_click=load_logs,
                    ),
                    # REMOVED EXPORT AND CLEAR BUTTONS
                ], spacing=10, wrap=True),
            ], spacing=15),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        # Activity timeline
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.TIMELINE, color="primary", size=24),
                    ft.Text("Activity Timeline", size=20, weight="bold"),
                ], spacing=10),
                ft.Divider(height=20),
                logs_container,
            ], spacing=10),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)


