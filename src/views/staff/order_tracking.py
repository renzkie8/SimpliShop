"""Order Fulfillment & Tracking Dashboard for Staff."""

import flet as ft
from state.app_state import AppState
from services.database import get_db_connection
from datetime import datetime

def StaffOrderTracking():
    """Staff order tracking and fulfillment management with pharmacy approval visibility."""
    
    # Validate user session and role
    user = AppState.get_user()
    if not user:
        return ft.Text("Please log in first", color="error")
    
    # Role-based access control: ONLY Staff can access
    # Role-based access control: Allow Staff, Pharmacist, and Billing
    if user['role'] not in ["Staff", "Pharmacist", "Billing"]:
        return ft.Text("⛔ Unauthorized - This section is restricted to Staff, Pharmacist, or Billing roles", color="error", size=16, weight="bold")
    
    staff_id = user['id']
    staff_name = user['full_name']
    
    # UI State
    orders_container = ft.Column(spacing=15)
    status_options = ["All", "Pending", "Processing", "Ready", "Completed", "Cancelled"]

    # Search field and status dropdown (defined early so refresh_orders can access them)
    search_field = ft.TextField(label="Search by Patient Name or Order ID", expand=True)
    status_dropdown = ft.Dropdown(
        label="Status",
        options=[ft.dropdown.Option(s) for s in status_options],
        value="All",
        width=180,
        on_change=lambda e: refresh_orders(),
    )
    
    # Database functions
    def load_orders(search_text="", status_filter="All"):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            SELECT o.id, o.patient_id, u.full_name, u.phone, o.status, 
                   o.total_amount, o.order_date, COALESCE(o.updated_at, o.order_date), o.pharmacy_notes,
                   o.discount_request, o.discount_verified
            FROM orders o
            JOIN users u ON o.patient_id = u.id
            WHERE 1=1
        """
        params = []

        if status_filter != "All":
            sql += " AND o.status = ?"
            params.append(status_filter)

        if search_text:
            sql += " AND (u.full_name LIKE ? OR CAST(o.id AS TEXT) LIKE ?)"
            params.append(f"%{search_text}%")
            params.append(f"%{search_text}%")

        sql += " ORDER BY o.id ASC"
        cursor.execute(sql, params)
        orders = cursor.fetchall()
        conn.close()
        return orders
    
    def get_order_items(order_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT oi.id, m.name, oi.quantity, oi.unit_price, oi.pharmacist_approved, 
                   ph.full_name, oi.approval_notes
            FROM order_items oi
            JOIN medicines m ON oi.medicine_id = m.id
            LEFT JOIN users ph ON oi.pharmacist_id = ph.id
            WHERE oi.order_id = ?
        """, (order_id,))
        items = cursor.fetchall()
        conn.close()
        return items
    
    def format_date(date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y %I:%M %p")
        except:
            return date_str
    
    def create_order_card(order):
        order_id, patient_id, patient_name, phone = order[0:4]
        status, total, created_at, updated_at, pharmacy_notes = order[4:9]
        discount_request, discount_verified = order[9], order[10]
        items = get_order_items(order_id)
        color = {'Pending': 'orange', 'Processing': 'blue', 'Ready': 'teal', 'Completed': 'green', 'Cancelled': 'red'}.get(status, 'grey')
        
        # Check if ALL medicines were approved by pharmacist
        all_approved = all(item[4] for item in items) if items else False
        approval_summary = "✅ All Medicines Approved" if all_approved else "⚠️ Some Medicines Pending Approval"
        
        items_list = []
        for item in items:
            med_name, qty, unit_price, is_approved, pharm_name, pharm_notes = item[1], item[2], item[3], item[4], item[5], item[6]
            approval_icon = ft.Icon(ft.icons.CHECK_CIRCLE, color="green", size=16) if is_approved else ft.Icon(ft.icons.PENDING, color="orange", size=16)
            approval_text = "✅ Approved by Pharmacist" if is_approved else "⏳ Waiting for Pharmacist Approval"
            
            items_list.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"• {med_name}", weight="bold", expand=True),
                            ft.Text(f"Qty: {qty}", color="outline", size=11),
                        ], spacing=10),
                        ft.Row([
                            approval_icon,
                            ft.Text(approval_text, size=11, weight="bold", color="green" if is_approved else "orange"),
                            ft.Text(f"₱{unit_price:.2f}", color="primary", weight="bold"),
                        ], spacing=8),
                        *([ft.Text(f"🔬 Reviewed by: {pharm_name}", size=10, color="secondary", italic=True)] if pharm_name else []),
                        *([ft.Text(f"📝 {pharm_notes}", size=9, color="outline", italic=True)] if pharm_notes else []),
                    ], spacing=3),
                    padding=10,
                    bgcolor=ft.colors.with_opacity(0.05, "green" if is_approved else "orange"),
                    border_radius=8,
                    border=ft.border.all(1, "green" if is_approved else "orange"),
                )
            )
        
        # Status update function
        def update_status(new_status):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, order_id))
            conn.commit()
            conn.close()
            refresh_orders()
            
        def verify_discount(e):
            # Calculate new total (remove 12% tax, apply 20% discount)
            subtotal = total / 1.12
            new_total = subtotal * 0.80
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET discount_verified = 1, total_amount = ? WHERE id = ?", (new_total, order_id))
            conn.commit()
            conn.close()
            refresh_orders()
        
        # Disable status buttons if order is Completed or Cancelled
        is_locked = status in ["Completed", "Cancelled"]
        
        return ft.Container(
            content=ft.Column([
                # Header with order info
                ft.Row([
                    ft.Column([
                        ft.Text(f"Order #{order_id}", size=16, weight="bold"),
                        ft.Text(patient_name, size=13),
                        ft.Text(phone, size=11, color="outline"),
                    ], spacing=2),
                    ft.Row([
                        ft.Container(ft.Text(status, weight="bold"), bgcolor=ft.colors.with_opacity(0.3, color),
                                    padding=ft.padding.symmetric(horizontal=12, vertical=6), border_radius=20),
                        *(([ft.Text("🔒 LOCKED", size=10, weight="bold", color="red")]) if is_locked else []),
                    ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Discount section if requested
                *([ft.Row([
                    ft.Icon(ft.icons.DISCOUNT, size=16, color="green" if discount_verified == 1 else "orange"),
                    ft.Text(f"Discount Requested: {discount_request}", weight="bold", color="green" if discount_verified == 1 else "orange"),
                    ft.Text("(Verified)" if discount_verified == 1 else "(Pending Verification)", size=12, color="green" if discount_verified == 1 else "orange", italic=True),
                    *([ft.ElevatedButton("Verify Discount", icon=ft.icons.VERIFIED, on_click=verify_discount, bgcolor="green", color="white", height=30, style=ft.ButtonStyle(padding=5))] if discount_verified == 0 and not is_locked else [])
                ], spacing=8)] if discount_request and discount_request != "None" else []),
                
                ft.Divider(),
                
                # Date info
                ft.Row([
                    ft.Column([ft.Text("Created", size=10, color="outline"), ft.Text(format_date(created_at), size=11, weight="bold")], spacing=1),
                    ft.Column([ft.Text("Updated", size=10, color="outline"), ft.Text(format_date(updated_at), size=11, weight="bold")], spacing=1),
                ], spacing=20),
                ft.Divider(),
                
                # PHARMACY APPROVAL STATUS - MAIN FEATURE
                ft.Container(
                    content=ft.Column([
                        ft.Text("💊 Pharmacist Approval Status:", weight="bold", size=12, color="primary"),
                        ft.Text(approval_summary, size=12, weight="bold", color="green" if all_approved else "orange"),
                        ft.Text("Each medicine below shows if it was approved by the pharmacist", size=10, color="outline", italic=True),
                    ], spacing=5),
                    padding=12,
                    border=ft.border.all(2, "green" if all_approved else "orange"),
                    border_radius=8,
                    bgcolor=ft.colors.with_opacity(0.08, "green" if all_approved else "orange"),
                ),
                ft.Divider(),
                
                # Medicines
                ft.Text("📦 Order Items with Pharmacy Approval:", weight="bold", color="primary", size=12),
                *items_list,
                ft.Divider(),
                
                # Total
                ft.Row([ft.Text("Total:", weight="bold"), ft.Text(f"₱{total:.2f}", size=14, weight="bold", color="primary")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                
                # STATUS UPDATE CONTROLS - LOCKED IF COMPLETED/CANCELLED
                ft.Column([
                    ft.Text("⚙️ Update Order Status:", weight="bold", size=12),
                    *(([ft.Text("🔒 This order is LOCKED and cannot be changed", size=11, weight="bold", color="red")]) if is_locked else []),
                    ft.Row([
                        ft.ElevatedButton(
                            "Pending",
                            icon=ft.icons.PENDING_ACTIONS,
                            on_click=lambda e: update_status("Pending"),
                            disabled=is_locked,
                        ),
                        ft.ElevatedButton(
                            "Processing",
                            icon=ft.icons.HOURGLASS_BOTTOM,
                            on_click=lambda e: update_status("Processing"),
                            disabled=is_locked,
                        ),
                        ft.ElevatedButton(
                            "Ready",
                            icon=ft.icons.CHECK_BOX,
                            on_click=lambda e: update_status("Ready"),
                            disabled=is_locked,
                        ),
                        ft.ElevatedButton(
                            "Completed",
                            icon=ft.icons.DONE_ALL,
                            on_click=lambda e: update_status("Completed"),
                            disabled=is_locked,
                        ),
                        ft.ElevatedButton(
                            "Cancelled",
                            icon=ft.icons.CANCEL,
                            on_click=lambda e: update_status("Cancelled"),
                            disabled=is_locked,
                        ),
                    ], wrap=True, spacing=8),
                ], spacing=8),
            ], spacing=10),
            padding=15,
            border=ft.border.all(2, "red" if is_locked else color),
            border_radius=10,
            bgcolor="surface",
        )
    
    def refresh_orders(e=None):
        orders_container.controls.clear()
        try:
            search_text = search_field.value or ""
            status_filter = status_dropdown.value or "All"
            orders = load_orders(search_text, status_filter)
            if not orders:
                orders_container.controls.append(ft.Text("No orders found", size=14, color="outline", text_align=ft.TextAlign.CENTER))
            else:
                for order in orders:
                    orders_container.controls.append(create_order_card(order))
        except Exception as ex:
            orders_container.controls.append(ft.Text(f"Error: {str(ex)}", color="error", size=12))
        if orders_container.page:
            orders_container.update()
    
    # Load initial orders
    try:
        orders = load_orders()
        if not orders:
            orders_container.controls.append(ft.Text("No orders", size=14, color="outline", text_align=ft.TextAlign.CENTER))
        else:
            for order in orders:
                orders_container.controls.append(create_order_card(order))
    except Exception as ex:
        orders_container.controls.append(ft.Text(f"Error: {str(ex)}", color="error", size=12))
    
    return ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Text("📦 Order Tracking", size=24, weight="bold"),
                    ft.Text(f"{staff_name}", size=12, color="outline"),
                ], spacing=5),
                padding=20,
                bgcolor="primaryContainer",
                border_radius=10,
            ),
            ft.Row([
                search_field,
                status_dropdown,
                ft.ElevatedButton(
                    "Search",
                    icon=ft.icons.SEARCH,
                    on_click=refresh_orders,
                ),
            ], spacing=15),
            ft.Divider(),
            ft.Container(
                content=ft.ListView([orders_container], expand=True, spacing=15),
                expand=True,
            ),
        ], spacing=15, expand=True),
        padding=15,
        expand=True,
    )




