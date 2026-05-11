"""Orders history view with real database integration."""

import flet as ft
from state import AppState
from services.database import get_db_connection
from datetime import datetime

def OrdersView():
    """Orders history and tracking view with live data."""
    
    # Validate user session state
    user = AppState.get_user()
    if not user:
        return ft.Text("Please log in first", color="error")
    
    user_id = user['id']
    
    # Default search parameter
    current_filter = {"value": "All"}
    
    # Results array container
    orders_container = ft.Column(spacing=15)
    
    # Component style bindings
    btn_all = ft.Ref[ft.ElevatedButton]()
    btn_pending = ft.Ref[ft.ElevatedButton]()
    btn_completed = ft.Ref[ft.ElevatedButton]()
    
    # Retrieve order records
    def load_orders(filter_status="All"):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base Query
        sql = """
            SELECT 
                o.id,
                o.order_date,
                o.status,
                o.total_amount,
                o.payment_method,
                GROUP_CONCAT(m.name || ' x' || oi.quantity, ', ') as items
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            LEFT JOIN medicines m ON oi.medicine_id = m.id
            WHERE o.patient_id = ?
        """
        
        # Filter logic
        if filter_status == "Pending":
            sql += " AND o.status IN ('Pending', 'Processing')"
        elif filter_status == "Completed":
            sql += " AND o.status = 'Completed'"
            
        sql += " GROUP BY o.id ORDER BY o.id ASC"
        
        cursor.execute(sql, (user_id,))
        orders = cursor.fetchall()
        conn.close()
        
        return orders
    
    # Date formatter
    def format_date(date_str):
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%b %d, %Y")
        except:
            return date_str
    
    # Status theme resolver
    def get_status_color(status):
        colors = {
            'Pending': 'tertiary',
            'Processing': 'secondary',
            'Ready': 'primary',
            'Completed': 'outline',
            'Cancelled': 'error'
        }
        return colors.get(status, 'outline')
    
    # Component rendering
    def create_order_card(order):
        order_id = order[0]
        order_date = format_date(order[1])
        status = order[2]
        total = order[3]
        items = order[5] if order[5] else "No items"
        
        status_color = get_status_color(status)
        items_list = items.split(', ') if items != "No items" else []
        
        return ft.Container(
            content=ft.Column([
                # Top Row: ID, Date, Status
                ft.Row([
                    ft.Column([
                        ft.Text(f"Order #{order_id}", size=18, weight="bold"),
                        ft.Text(order_date, size=12, color="outline"),
                    ], spacing=2),
                    ft.Container(
                        content=ft.Text(status, size=12, weight="bold", color="onPrimaryContainer"),
                        bgcolor=ft.colors.with_opacity(0.2, status_color),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                # Middle: Items list
                ft.Column([
                    ft.Text("Items:", size=13, weight="bold", color="outline"),
                    *([ft.Text(f"• {item}", size=13) for item in items_list] if items_list else [ft.Text("No items", size=13, color="outline")]),
                ], spacing=5),
                
                ft.Divider(),
                
                # Bottom: Total and Button
                ft.Row([
                    ft.Text("Total:", size=14, weight="bold"),
                    ft.Text(f"₱ {total:.2f}", size=16, weight="bold", color="primary"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Row([
                    ft.OutlinedButton(
                        "View Receipt",
                        icon=ft.icons.RECEIPT,
                        on_click=lambda e: e.page.go(f"/patient/pos_receipt/{order_id}")
                    ),
                    ft.TextButton(
                        "View Details", 
                        icon=ft.icons.VISIBILITY,
                        on_click=lambda e: view_order_details(e, order_id)
                    ),
                ], alignment=ft.MainAxisAlignment.END, spacing=10),
                
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    # Modal trigger action
    def view_order_details(e, order_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query requested order
        cursor.execute("""
            SELECT o.id, o.order_date, o.status, o.total_amount, o.payment_method
            FROM orders o WHERE o.id = ?
        """, (order_id,))
        order = cursor.fetchone()
        
        # Retrieve corresponding items
        cursor.execute("""
            SELECT m.name, oi.quantity, oi.unit_price, oi.subtotal
            FROM order_items oi
            JOIN medicines m ON oi.medicine_id = m.id
            WHERE oi.order_id = ?
        """, (order_id,))
        items = cursor.fetchall()
        conn.close()
        
        if not order: return
        
        # Reconcile display inconsistencies
        # Compute dynamic item totals against stored snapshot for accurate metadata display
        calculated_subtotal = sum(item[3] for item in items)
        stored_total = order[3]
        tax_amount = max(0, stored_total - calculated_subtotal)
        
        # Construct items UI nodes
        items_widgets = []
        for item in items:
            items_widgets.append(
                ft.Row([
                    ft.Text(f"{item[0]} x{item[1]}", expand=True),
                    ft.Text(f"₱{item[3]:.2f}", weight="bold"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            )
        
        # Render detail modal
        dialog = ft.AlertDialog(
            title=ft.Text(f"Order #{order_id} Details"),
            content=ft.Column([
                ft.Text(f"Date: {format_date(order[1])}", size=13),
                ft.Text(f"Status: {order[2]}", size=13),
                ft.Text(f"Payment: {order[4] or 'Not specified'}", size=13),
                ft.Divider(),
                ft.Text("Items:", weight="bold"),
                *items_widgets,
                ft.Divider(),
                
                # Render financial summary
                ft.Row([
                    ft.Text("Subtotal:", size=13),
                    ft.Text(f"₱{calculated_subtotal:.2f}", size=13),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Row([
                    ft.Text("Tax/Fees:", size=13),
                    ft.Text(f"₱{tax_amount:.2f}", size=13),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Row([
                    ft.Text("Total:", weight="bold"),
                    ft.Text(f"₱{stored_total:.2f}", weight="bold", color="primary"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
            ], spacing=10, tight=True, width=400),
            actions=[
                ft.TextButton("Close", on_click=lambda e: e.page.close(dialog)),
            ],
            bgcolor="surface",
        )
        
        e.page.open(dialog)
    
    # Refresh data view
    def update_orders_list(e=None):
        orders = load_orders(current_filter["value"])
        orders_container.controls.clear()
        
        if orders:
            for order in orders:
                orders_container.controls.append(create_order_card(order))
        else:
            # Display fallback graphic
            orders_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.RECEIPT_LONG_OUTLINED, size=80, color="outline"),
                        ft.Text("No orders found", size=18, color="outline"),
                        ft.ElevatedButton(
                            "Start Shopping",
                            icon=ft.icons.SHOPPING_BAG,
                            on_click=lambda e: e.page.go("/patient/search"),
                            bgcolor="primary",
                            color="onPrimary",
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center,
                )
            )
        
        # Apply conditional classes
        status = current_filter["value"]
        style_outline = ft.ButtonStyle(color="primary", bgcolor=ft.colors.TRANSPARENT, side=ft.BorderSide(1, "primary"))
        style_fill = ft.ButtonStyle(color="white", bgcolor="primary")
        
        if btn_all.current: btn_all.current.style = style_fill if status == "All" else style_outline
        if btn_pending.current: btn_pending.current.style = style_fill if status == "Pending" else style_outline
        if btn_completed.current: btn_completed.current.style = style_fill if status == "Completed" else style_outline
            
        if e: e.page.update()
    
    # Filter execution callback
    def filter_click(e, status):
        current_filter["value"] = status
        update_orders_list(e)
    
    # Initial component mount
    update_orders_list(None)
    
    # Primary composition
    return ft.Column([
        ft.Text("My Orders", size=28, weight="bold"),
        ft.Text("View and track your medicine orders", size=14, color="outline"),
        ft.Container(height=20),
        
        # Filter Buttons
        ft.Row([
            ft.ElevatedButton("All Orders", ref=btn_all, on_click=lambda e: filter_click(e, "All")),
            ft.ElevatedButton("Pending", ref=btn_pending, on_click=lambda e: filter_click(e, "Pending")),
            ft.ElevatedButton("Completed", ref=btn_completed, on_click=lambda e: filter_click(e, "Completed")),
        ], spacing=10),
        
        ft.Container(height=20),
        
        # List of cards
        orders_container,
    ], scroll=ft.ScrollMode.AUTO, spacing=0)




