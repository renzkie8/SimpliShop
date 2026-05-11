import flet as ft
from services.database import get_db_connection
from datetime import datetime

def POSReceiptView(order_id: int):
    from state.app_state import AppState
    user = AppState.get_user()
    if not user:
        return ft.Container(content=ft.Text("Unauthorized", color="error"), alignment=ft.alignment.center, expand=True)
        
    # Fetch order data
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get order details
    cursor.execute("""
        SELECT o.id, o.order_date, o.status, o.total_amount, o.payment_method, 
               o.payment_status, o.discount_request, o.discount_verified,
               u.full_name, u.last_name, o.patient_id
        FROM orders o
        JOIN users u ON o.patient_id = u.id
        WHERE o.id = ?
    """, (order_id,))
    order_data = cursor.fetchone()
    
    if not order_data or (order_data[10] != user['id'] and user['role'] not in ["Staff", "Admin", "Pharmacist", "Billing"]):
        conn.close()
        return ft.Container(
            content=ft.Text("Order not found or invalid access.", color="error", size=18),
            alignment=ft.alignment.center,
            expand=True
        )
        
    (o_id, order_date, status, db_total_amount, payment_method, 
     payment_status, discount_request, discount_verified, fname, lname, _) = order_data
     
    customer_name = f"{fname} {lname}".strip()
    
    # Parse date
    try:
        dt_obj = datetime.strptime(order_date, "%Y-%m-%d %H:%M:%S")
        formatted_date = dt_obj.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        formatted_date = order_date
    
    # Get order items
    cursor.execute("""
        SELECT m.name, oi.quantity, oi.unit_price, oi.subtotal
        FROM order_items oi
        JOIN medicines m ON oi.medicine_id = m.id
        WHERE oi.order_id = ?
    """, (order_id,))
    items = cursor.fetchall()
    conn.close()

    # Calculations
    subtotal = sum(item[3] for item in items)
    tax = subtotal * 0.12
    discount_amount = 0
    final_total = subtotal + tax
    
    is_discount_pending = False
    discount_label = ""
    
    if discount_request and discount_request != "None":
        if discount_verified == 1:
            # 20% discount and VAT exempt
            tax = 0
            discount_amount = subtotal * 0.20
            final_total = subtotal - discount_amount
            discount_label = f"Discount ({discount_request} - 20%)"
        else:
            is_discount_pending = True
            discount_label = f"Discount ({discount_request}) [Pending]"

    # Receipt UI Building
    def create_receipt_row(label, value, bold=False, color=None):
        return ft.Row([
            ft.Text(label, size=13, weight="bold" if bold else "normal", color=color or "onSurfaceVariant"),
            ft.Text(value, size=13, weight="bold" if bold else "normal", color=color or "onSurfaceVariant", text_align=ft.TextAlign.RIGHT)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Item List
    items_column = ft.Column(spacing=8)
    for item in items:
        name, qty, price, item_sub = item
        items_column.controls.append(
            ft.Row([
                ft.Column([
                    ft.Text(name, size=13, weight="bold"),
                    ft.Text(f"{qty} x ₱{price:.2f}", size=11, color="outline")
                ], expand=1, spacing=2),
                ft.Text(f"₱{item_sub:.2f}", size=13)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

    receipt_card = ft.Container(
        width=400,
        bgcolor="#FFFFFF", # Paper white
        border_radius=0, # Square like receipt
        padding=40,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=15,
            color=ft.colors.with_opacity(0.1, "#000000"),
            offset=ft.Offset(0, 10),
        ),
        content=ft.Column([
            # Pharmacy Header
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.LOCAL_PHARMACY, size=40, color="primary"),
                    ft.Text("PharmaOps", size=24, weight="w900", color="primary"),
                    ft.Text("Official Receipt", size=12, color="outline"),
                    ft.Text("123 Healthcare Blvd, Medical District", size=10, color="outline"),
                    ft.Text("Tel: (02) 8888-9999", size=10, color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                alignment=ft.alignment.center,
                padding=ft.padding.only(bottom=20)
            ),
            
            ft.Divider(height=1, color="#E0E0E0"),
            
            # Transaction Info
            ft.Container(
                content=ft.Column([
                    create_receipt_row("Txn No:", f"TXN-{o_id:06d}"),
                    create_receipt_row("Date:", formatted_date),
                    create_receipt_row("Customer:", customer_name),
                    create_receipt_row("Status:", status, bold=True, color="primary" if status == "Completed" else "error" if status == "Cancelled" else "orange"),
                ], spacing=6),
                padding=ft.padding.symmetric(vertical=15)
            ),
            
            ft.Divider(height=1, color="#E0E0E0"),
            
            # Items
            ft.Container(
                content=items_column,
                padding=ft.padding.symmetric(vertical=15)
            ),
            
            ft.Divider(height=1, color="#E0E0E0"),
            
            # Totals
            ft.Container(
                content=ft.Column([
                    create_receipt_row("Subtotal", f"₱{subtotal:.2f}"),
                    create_receipt_row("VAT (12%)", f"₱{tax:.2f}" if tax > 0 else "Exempt"),
                ] + ([create_receipt_row(discount_label, f"-₱{discount_amount:.2f}", color="green")] if discount_request and discount_request != "None" else []) + [
                    ft.Container(height=5),
                    create_receipt_row("TOTAL DUE", f"₱{final_total:.2f}", bold=True, color="#000000")
                ], spacing=8),
                padding=ft.padding.symmetric(vertical=15)
            ),
            
            ft.Divider(height=1, color="#E0E0E0"),
            
            # Pending Verification Notice
            *( [ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.INFO_OUTLINE, size=16, color="orange"),
                    ft.Text("Discount pending pharmacist verification. Final amount may adjust.", size=10, color="orange", italic=True, expand=True)
                ], spacing=8),
                padding=ft.padding.only(top=10, bottom=10),
                bgcolor=ft.colors.with_opacity(0.1, "orange"),
                border_radius=4
            )] if is_discount_pending else []),
            
            # Footer
            ft.Container(
                content=ft.Column([
                    # Barcode mock
                    ft.Container(
                        content=ft.Text(f"|| | ||| | || || | || | |||", size=24, weight="bold", color="#000000"),
                        alignment=ft.alignment.center,
                        padding=ft.padding.symmetric(vertical=10)
                    ),
                    ft.Text("Thank you for choosing PharmaOps!", size=12, italic=True, color="outline"),
                    ft.Text("Please retain this receipt for your records.", size=10, color="outline"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=15)
            ),
            
        ])
    )

    # Wrap in a beautiful container background
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK_IOS_NEW,
                    icon_color="primary",
                    on_click=lambda e: e.page.go("/patient/orders"),
                    tooltip="Back to Orders"
                ),
                ft.Text("Digital POS Receipt", size=20, weight="bold", color="onSurface"),
                ft.Container(width=40) # Spacer
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, width=400),
            ft.Container(height=20),
            receipt_card,
            ft.Container(height=20),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
        alignment=ft.alignment.center,
        bgcolor="surface", # subtle background
        padding=40
    )




