"""Patient view for their own invoices/bills."""

import flet as ft
from state.app_state import AppState
from services.database import get_db_connection
from datetime import datetime

def PatientInvoicesView():
    """View patient's own invoices and bills."""
    
    user = AppState.get_user()
    
    # Retrieve patient bills
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, invoice_number, subtotal, tax, discount, total_amount, 
               status, payment_method, created_at, notes
        FROM invoices 
        WHERE patient_id = ? 
        ORDER BY id ASC
    """, (user['id'],))
    invoices = cursor.fetchall()
    conn.close()
    
    def create_invoice_card(invoice):
        """Create invoice display card."""
        status_colors = {
            "Unpaid": ("error", ft.icons.ERROR_OUTLINE),
            "Paid": ("primary", ft.icons.CHECK_CIRCLE),
            "Cancelled": ("outline", ft.icons.CANCEL),
            "Partially Paid": ("tertiary", ft.icons.PENDING),
        }
        color, icon = status_colors.get(invoice['status'], ("outline", ft.icons.INFO))
        
        return ft.Container(
            content=ft.Column([
                # Header
                ft.Row([
                    ft.Column([
                        ft.Text(f"Invoice {invoice['invoice_number']}", size=16, weight="bold"),
                        ft.Text(f"Date: {invoice['created_at'][:10] if invoice['created_at'] else 'N/A'}", 
                               size=12, color="outline"),
                    ], expand=True),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(icon, size=16, color=color),
                            ft.Text(invoice['status'], weight="bold", color=color),
                        ], spacing=5),
                        bgcolor=ft.colors.with_opacity(0.1, color),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ]),
                
                ft.Divider(height=15),
                
                # Render financial breakdown
                ft.Column([
                    ft.Row([
                        ft.Text("Subtotal:", size=13, color="outline", expand=True),
                        ft.Text(f"₱{invoice['subtotal']:,.2f}", size=13),
                    ]),
                    ft.Row([
                        ft.Text("Tax (12%):", size=13, color="outline", expand=True),
                        ft.Text(f"₱{invoice['tax']:,.2f}", size=13),
                    ]),
                    ft.Row([
                        ft.Text("Discount:", size=13, color="outline", expand=True),
                        ft.Text(f"-₱{invoice['discount']:,.2f}", size=13, color="error"),
                    ]) if invoice['discount'] > 0 else ft.Container(),
                    ft.Divider(height=5),
                    ft.Row([
                        ft.Text("Total Amount:", size=14, weight="bold", expand=True),
                        ft.Text(f"₱{invoice['total_amount']:,.2f}", size=16, weight="bold", color="primary"),
                    ]),
                ], spacing=5),
                
                ft.Divider(height=10),
                
                # Render transaction metadata
                ft.Row([
                    ft.Icon(ft.icons.PAYMENT, size=16, color="outline"),
                    ft.Text(f"Payment Method: {invoice['payment_method']}", size=12, color="outline"),
                ], spacing=5),
                
                # Render accessory notes
                ft.Container(
                    content=ft.Column([
                        ft.Text("Notes:", size=12, weight="bold"),
                        ft.Text(invoice['notes'], size=12, italic=True),
                    ], spacing=3),
                    padding=10,
                    bgcolor=ft.colors.with_opacity(0.05, "outline"),
                    border_radius=5,
                ) if invoice['notes'] else ft.Container(),
                
                # Render contextual actions
                ft.Row([
                    ft.ElevatedButton(
                        "View Details",
                        icon=ft.icons.VISIBILITY,
                        on_click=lambda e, inv_id=invoice['id']: e.page.go(f"/patient/invoice/{inv_id}"),
                    ),
                    ft.ElevatedButton(
                        "Pay Now",
                        icon=ft.icons.PAYMENT,
                        bgcolor="primary",
                        color="onPrimary",
                        disabled=invoice['status'] != "Unpaid",
                        on_click=lambda e, inv_id=invoice['id']: pay_invoice(e, inv_id),
                    ) if invoice['status'] == "Unpaid" else ft.Container(),
                ], spacing=10),
            ], spacing=10),
            padding=20,
            border=ft.border.all(2, color),
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.03, color),
        )
    
    def pay_invoice(e, invoice_id):
        """Handle invoice payment with payment form dialog."""
        
        # Fetch target invoice
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT invoice_number, total_amount, status
            FROM invoices 
            WHERE id = ?
        """, (invoice_id,))
        invoice_data = cursor.fetchone()
        conn.close()
        
        if not invoice_data:
            e.page.snack_bar = ft.SnackBar(
                content=ft.Text("Invoice not found"),
                bgcolor="error",
            )
            e.page.snack_bar.open = True
            e.page.update()
            return
        
        invoice_number, total_amount, status = invoice_data
        
        # Initialize payment form inputs
        payment_method = ft.Dropdown(
            label="Payment Method *",
            options=[
                ft.dropdown.Option("Cash"),
                ft.dropdown.Option("Credit Card"),
                ft.dropdown.Option("Debit Card"),
                ft.dropdown.Option("GCash"),
                ft.dropdown.Option("PayMaya"),
                ft.dropdown.Option("Bank Transfer"),
            ],
            value="Cash",
            border_color="outline",
        )
        
        payment_amount = ft.TextField(
            label="Payment Amount *",
            value=f"{total_amount:.2f}",
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_text="₱ ",
            border_color="outline",
        )
        
        reference_number = ft.TextField(
            label="Reference Number (Optional)",
            hint_text="e.g., Transaction ID, Check Number",
            border_color="outline",
        )
        
        payment_notes = ft.TextField(
            label="Payment Notes (Optional)",
            multiline=True,
            min_lines=2,
            max_lines=3,
            border_color="outline",
        )
        
        error_text = ft.Text("", color="error", size=12)
        
        def submit_payment(dialog_e):
            """Process the payment submission."""
            # Validate form requirements
            if not payment_method.value:
                error_text.value = "Please select a payment method"
                dialog_e.page.update()
                return
            
            try:
                amount = float(payment_amount.value)
                if amount <= 0:
                    error_text.value = "Amount must be greater than 0"
                    dialog_e.page.update()
                    return
                
                if amount > total_amount:
                    error_text.value = f"Amount cannot exceed invoice total (₱{total_amount:.2f})"
                    dialog_e.page.update()
                    return
            except ValueError:
                error_text.value = "Please enter a valid amount"
                dialog_e.page.update()
                return
                        # Compute updated payment status
            if amount >= total_amount:
                new_status = "Paid"
            else:
                new_status = "Partially Paid"
                        # Construct payment annotation
            notes_parts = []
            if reference_number.value:
                notes_parts.append(f"Ref: {reference_number.value}")
            if payment_notes.value:
                notes_parts.append(payment_notes.value)
            combined_notes = " | ".join(notes_parts) if notes_parts else None
                        # Apply transaction records
            conn = get_db_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE invoices 
                    SET status = ?,
                        payment_method = ?,
                        payment_date = ?,
                        notes = ?
                    WHERE id = ?
                """, (
                    new_status,
                    payment_method.value,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    combined_notes,
                    invoice_id
                ))
                
                # Record system action
                cursor.execute("""
                    INSERT INTO activity_log (user_id, action, details, timestamp)
                    VALUES (?, ?, ?, ?)
                """, (
                    user['id'],
                    'payment_submitted',
                    f"Payment of ₱{amount:.2f} for invoice {invoice_number} via {payment_method.value}",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                
                conn.commit()
                conn.close()
                
                # Dismiss modal
                dialog_e.page.close(payment_dialog)
                
                # Display confirmation
                dialog_e.page.snack_bar = ft.SnackBar(
                    content=ft.Row([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color="white"),
                        ft.Text(f"Payment of ₱{amount:.2f} recorded successfully!", color="white"),
                    ]),
                    bgcolor="primary",
                    duration=3000,
                )
                dialog_e.page.snack_bar.open = True
                
                # Reload invoices view
                dialog_e.page.go("/patient/invoices")
                
            except Exception as ex:
                conn.rollback()
                conn.close()
                
                error_text.value = f"Payment failed: {str(ex)}"
                dialog_e.page.update()
        
        def close_dialog(dialog_e):
            dialog_e.page.close(payment_dialog)
        
        # Render payment modal
        payment_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.icons.PAYMENT, color="primary"),
                ft.Text("Make Payment"),
            ]),
            content=ft.Container(
                width=450,
                content=ft.Column([
                    # Invoice info
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Invoice:", size=13, color="outline", width=100),
                                ft.Text(invoice_number, size=13, weight="bold"),
                            ]),
                            ft.Row([
                                ft.Text("Total Due:", size=13, color="outline", width=100),
                                ft.Text(f"₱{total_amount:.2f}", size=16, weight="bold", color="primary"),
                            ]),
                        ], spacing=5),
                        padding=15,
                        bgcolor=ft.colors.with_opacity(0.05, "primary"),
                        border_radius=8,
                        border=ft.border.all(1, "primary"),
                    ),
                    
                    ft.Divider(height=20),
                    
                    # Payment form
                    payment_method,
                    payment_amount,
                    reference_number,
                    payment_notes,
                    
                    error_text,
                    
                    ft.Container(
                        content=ft.Text(
                            "Note: Payment will be recorded immediately. Please ensure all details are correct.",
                            size=11,
                            color="outline",
                            italic=True,
                        ),
                        padding=10,
                        bgcolor=ft.colors.with_opacity(0.05, "tertiary"),
                        border_radius=5,
                    ),
                ], spacing=10, scroll=ft.ScrollMode.AUTO, tight=True),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.ElevatedButton(
                    "Submit Payment",
                    icon=ft.icons.CHECK,
                    bgcolor="primary",
                    color="white",
                    on_click=submit_payment,
                ),
            ],
            actions_padding=20,
        )
        
        e.page.open(payment_dialog)
    
    # Compute aggregate balances
    total_unpaid = sum(inv['total_amount'] for inv in invoices if inv['status'] == 'Unpaid')
    total_paid = sum(inv['total_amount'] for inv in invoices if inv['status'] == 'Paid')
    
    # Primary layout
    return ft.Column([
        ft.Container(
            padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("My Bills & Invoices", size=28, weight="bold"),
                        ft.Text("View and manage your medical bills", size=14, color="outline"),
                    ], spacing=5, expand=True),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Render Financial Metrics
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.ERROR_OUTLINE, color="error", size=30),
                                ft.Column([
                                    ft.Text("Unpaid Bills", size=12, color="outline"),
                                    ft.Text(f"₱{total_unpaid:,.2f}", size=20, weight="bold", color="error"),
                                ], spacing=2, expand=True),
                            ], spacing=10),
                        ]),
                        padding=15,
                        bgcolor="surface",
                        border_radius=10,
                        border=ft.border.all(1, "error"),
                        expand=True,
                    ),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.CHECK_CIRCLE, color="primary", size=30),
                                ft.Column([
                                    ft.Text("Paid Bills", size=12, color="outline"),
                                    ft.Text(f"₱{total_paid:,.2f}", size=20, weight="bold", color="primary"),
                                ], spacing=2, expand=True),
                            ], spacing=10),
                        ]),
                        padding=15,
                        bgcolor="surface",
                        border_radius=10,
                        border=ft.border.all(1, "primary"),
                        expand=True,
                    ),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.icons.RECEIPT, color="secondary", size=30),
                                ft.Column([
                                    ft.Text("Total Invoices", size=12, color="outline"),
                                    ft.Text(str(len(invoices)), size=20, weight="bold", color="secondary"),
                                ], spacing=2, expand=True),
                            ], spacing=10),
                        ]),
                        padding=15,
                        bgcolor="surface",
                        border_radius=10,
                        border=ft.border.all(1, "secondary"),
                        expand=True,
                    ),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Informational Banner
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.INFO_OUTLINE, color="tertiary", size=20),
                        ft.Text(
                            "Invoices are automatically generated when you place orders. Pay unpaid bills using the payment form or contact the billing clerk.",
                            size=13,
                            expand=True,
                        ),
                    ], spacing=10),
                    padding=15,
                    bgcolor=ft.colors.with_opacity(0.1, "tertiary"),
                    border_radius=8,
                    border=ft.border.all(1, "tertiary"),
                ),
                
                ft.Container(height=20),
                
                # Render Record Collection
                ft.Container(height=10),
                
                ft.Column([
                    create_invoice_card(inv) for inv in invoices
                ], spacing=15) if invoices else ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.RECEIPT_LONG_OUTLINED, size=80, color="outline"),
                        ft.Text("No invoices yet", size=18, color="outline"),
                        ft.Text("Invoices will appear here when you place orders", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center,
                ),
            ]),
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)




