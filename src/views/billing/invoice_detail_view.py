"""Invoice detail view - Shows complete of invoice information."""

import flet as ft
from services.database import get_db_connection
from state import AppState
from datetime import datetime

def InvoiceDetailView(invoice_id):
    """Display detailed invoice information."""
    
    user = AppState.get_user()
    if not user:
        return ft.Text("Please log in first", color="error")
    
    # Establish database connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query invoice metadata
    cursor.execute("""
        SELECT 
            i.id,
            i.invoice_number,
            i.patient_id,
            i.order_id,
            i.subtotal,
            i.tax,
            i.discount,
            i.total_amount,
            i.status,
            i.payment_method,
            i.payment_date,
            i.notes,
            i.created_at,
            u.full_name,
            u.username,
            u.email,
            u.phone,
            u.address
        FROM invoices i
        JOIN users u ON i.patient_id = u.id
        WHERE i.id = ?
    """, (invoice_id,))
    
    invoice = cursor.fetchone()
    
    if not invoice:
        conn.close()
        return ft.Column([
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.ERROR_OUTLINE, size=80, color="error"),
                    ft.Text("Invoice Not Found", size=24, weight="bold"),
                    ft.Text(f"Invoice #{invoice_id} does not exist", size=14, color="outline"),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Back to Invoices",
                        icon=ft.icons.ARROW_BACK,
                        on_click=lambda e: e.page.go("/billing/invoices"),
                        bgcolor="primary",
                        color="white",
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=50,
            )
        ])
    
    # Query related order line items
    order_items = []
    if invoice[3]:  # order_id
        cursor.execute("""
            SELECT 
                m.name,
                oi.quantity,
                oi.unit_price,
                oi.subtotal
            FROM order_items oi
            JOIN medicines m ON oi.medicine_id = m.id
            WHERE oi.order_id = ?
        """, (invoice[3],))
        order_items = cursor.fetchall()
    
    conn.close()
    
    # Unpack invoice record parameters
    inv_id, inv_num, patient_id, order_id, subtotal, tax, discount, total, status, payment_method, payment_date, notes, created_at, patient_name, username, email, phone, address = invoice
    
    # Helper function for date formatting
    def format_date(date_str):
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%B %d, %Y at %I:%M %p")
        except:
            return date_str
    
    # Configure state color mapping
    status_colors = {
        'Paid': 'primary',
        'Unpaid': 'error',
        'Partially Paid': 'tertiary',
        'Cancelled': 'outline',
    }
    status_color = status_colors.get(status, 'outline')
    
    return ft.Column([
        # Render view header
        ft.Row([
            ft.Text("Invoice Details", size=28, weight="bold"),
        ]),
        
        ft.Container(height=10),
        
        # Render biller and invoice metadata card
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("Kaputt Kommandos Pharmacy", size=24, weight="bold", color="primary"),
                        ft.Text("Pharmacy Management System", size=14, color="outline"),
                        ft.Text("Contact: KPharmacy@grp5.com | (123) 456-7890", size=12, color="outline"),
                    ], expand=True),
                    ft.Column([
                        ft.Text(inv_num, size=28, weight="bold"),
                        ft.Container(
                            content=ft.Text(status, size=14, weight="bold", color="white"),
                            bgcolor=status_color,
                            padding=10,
                            border_radius=5,
                        ),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=30),
                
                # Render client and transaction details
                ft.Row([
                    # Render bill to details
                    ft.Column([
                        ft.Text("BILL TO:", size=12, weight="bold", color="outline"),
                        ft.Container(height=5),
                        ft.Text(patient_name or username, size=16, weight="bold"),
                        ft.Text(f"Customer ID: {patient_id}", size=12, color="outline"),
                        ft.Text(email or "john@gmail.com", size=12),
                        ft.Text(phone or "+63947565643321", size=12),
                        ft.Text(address or "San Miguel", size=12),
                    ], expand=True),
                    
                    # Render transaction identifiers
                    ft.Column([
                        ft.Text("INVOICE DETAILS:", size=12, weight="bold", color="outline"),
                        ft.Container(height=5),
                        ft.Row([
                            ft.Text("Invoice Date:", size=12, width=120),
                            ft.Text(format_date(created_at), size=12, weight="bold"),
                        ]),
                        ft.Row([
                            ft.Text("Order ID:", size=12, width=120),
                            ft.Text(f"#{order_id}" if order_id else "N/A", size=12, weight="bold"),
                        ]),
                        ft.Row([
                            ft.Text("Payment Method:", size=12, width=120),
                            ft.Text(payment_method or "Not specified", size=12, weight="bold"),
                        ]),
                        ft.Row([
                            ft.Text("Payment Status or Date:", size=12, width=120),
                            ft.Text(format_date(payment_date) if payment_date else "Unpaid", size=12, weight="bold"),
                        ]),
                    ], horizontal_alignment=ft.CrossAxisAlignment.END),
                ], vertical_alignment=ft.CrossAxisAlignment.START),
            ], spacing=10),
            padding=30,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(2, "primary"),
        ),
        
        ft.Container(height=20),
        
        # Render line items collection
        ft.Container(
            content=ft.Column([
                ft.Text("Items", size=20, weight="bold"),
                ft.Divider(),
                
                # Render table header
                ft.Container(
                    content=ft.Row([
                        ft.Text("Item", size=13, weight="bold", expand=2),
                        ft.Text("Quantity", size=13, weight="bold", width=100, text_align=ft.TextAlign.CENTER),
                        ft.Text("Unit Price", size=13, weight="bold", width=120, text_align=ft.TextAlign.RIGHT),
                        ft.Text("Total", size=13, weight="bold", width=120, text_align=ft.TextAlign.RIGHT),
                    ]),
                    bgcolor="surfaceVariant",
                    padding=15,
                    border_radius=8,
                ),
                
                # Render line items
                ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Text(item[0], size=13, expand=2),
                            ft.Text(str(item[1]), size=13, width=100, text_align=ft.TextAlign.CENTER),
                            ft.Text(f"₱{item[2]:.2f}", size=13, width=120, text_align=ft.TextAlign.RIGHT),
                            ft.Text(f"₱{item[3]:.2f}", size=13, width=120, text_align=ft.TextAlign.RIGHT, weight="bold"),
                        ]),
                        padding=15,
                        border=ft.border.only(bottom=ft.border.BorderSide(1, "outlineVariant")),
                    ) for item in order_items
                ] if order_items else [
                    ft.Container(
                        content=ft.Text("No items found", size=13, color="outline", italic=True),
                        padding=20,
                    )
                ], spacing=0),
            ], spacing=10),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        # Render financial aggregation block
        ft.Row([
            # Render transaction annotations
            ft.Container(
                content=ft.Column([
                    ft.Text("Notes:", size=14, weight="bold"),
                    ft.Text(notes or "No additional notes", size=13, color="outline" if not notes else None),
                ], spacing=5),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                expand=True,
            ),
            
            # Render financial summary
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Subtotal:", size=14),
                        ft.Text(f"₱{subtotal:.2f}", size=14, weight="bold"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Row([
                        ft.Text("Tax (12%):", size=14),
                        ft.Text(f"₱{tax:.2f}", size=14, weight="bold"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Row([
                        ft.Text("Discount:", size=14),
                        ft.Text(f"-₱{discount:.2f}", size=14, weight="bold", color="error"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN) if discount > 0 else ft.Container(),
                    
                    ft.Divider(),
                    
                    ft.Row([
                        ft.Text("TOTAL:", size=18, weight="bold"),
                        ft.Text(f"₱{total:.2f}", size=24, weight="bold", color="primary"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ], spacing=10),
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(2, "primary"),
                width=400,
            ),
        ], spacing=15),
        
        ft.Container(height=30),
        
    ], scroll=ft.ScrollMode.AUTO, spacing=0)




