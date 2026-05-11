"""Payment history view with transaction tracking."""

import flet as ft
from datetime import datetime, timedelta
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def PaymentHistoryView():
    """View all payment transactions and history."""
    
    payments_container = ft.Column(spacing=10)
    
    # Initialize filtering components
    # Apply theme border configuration
    payment_method_filter = ft.Dropdown(
        label="Payment Method",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Cash"),
            ft.dropdown.Option("Credit Card"),
            ft.dropdown.Option("Debit Card"),
            ft.dropdown.Option("Bank Transfer"),
            ft.dropdown.Option("GCash"),
            ft.dropdown.Option("PayMaya"),
        ],
        value="All",
        width=180,
        border_color="primary", 
    )
    
    date_from = ft.TextField(
        label="From Date", 
        value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"), 
        width=150, 
        border_color="primary" # Apply theme border
    )
    
    date_to = ft.TextField(
        label="To Date", 
        value=datetime.now().strftime("%Y-%m-%d"), 
        width=150, 
        border_color="primary" # Apply theme border
    )
    
    search_field = ft.TextField(
        hint_text="Search by invoice #, customer name...", 
        prefix_icon=ft.icons.SEARCH, 
        border_color="primary", # Apply theme border
        expand=True
    )
    
    # Query transaction records
    def get_payments_from_db(payment_method="All", date_start="", date_end="", search=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT i.id, i.invoice_number, i.total_amount, i.payment_method,
                   i.payment_date, i.created_at,
                   u.full_name as patient_name,
                   clerk.full_name as clerk_name
            FROM invoices i
            LEFT JOIN users u ON i.patient_id = u.id
            LEFT JOIN users clerk ON i.billing_clerk_id = clerk.id
            WHERE i.status = 'Paid'
        """
        
        params = []
        if payment_method != "All":
            query += " AND i.payment_method = ?"
            params.append(payment_method)
        if date_start:
            query += " AND DATE(i.payment_date) >= ?"
            params.append(date_start)
        if date_end:
            query += " AND DATE(i.payment_date) <= ?"
            params.append(date_end)
        if search:
            query += " AND (i.invoice_number LIKE ? OR u.full_name LIKE ?)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")
        
        query += " ORDER BY i.payment_date DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    # Render transaction component
    def create_payment_card(payment):
        inv_id, inv_number, amount, payment_method, payment_date, created_at, patient_name, clerk_name = payment
        
        payment_icons = {'Cash': ft.icons.MONEY, 'Credit Card': ft.icons.CREDIT_CARD}
        icon = payment_icons.get(payment_method, ft.icons.PAYMENT)
        color = 'primary'
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=32),
                    ft.Column([
                        ft.Row([
                            ft.Text(f"₱{amount:,.2f}", size=20, weight="bold", color="primary"),
                            ft.Container(content=ft.Text(payment_method, size=11, weight="bold", color="white"), bgcolor=color, padding=ft.padding.symmetric(horizontal=8, vertical=4), border_radius=10),
                        ], spacing=10),
                        ft.Text(f"Invoice #{inv_number}", size=13, color="outline"),
                    ], spacing=2, expand=True),
                ], spacing=15),
                
                ft.Divider(height=10),
                
                ft.Row([
                    ft.Column([ft.Text("Customer", size=11, color="outline"), ft.Text(patient_name, size=14, weight="bold")], spacing=2),
                    ft.VerticalDivider(width=20),
                    ft.Column([ft.Text("Processed By", size=11, color="outline"), ft.Text(clerk_name or "System", size=14, weight="bold")], spacing=2),
                    ft.VerticalDivider(width=20),
                    ft.Column([ft.Text("Payment Date", size=11, color="outline"), ft.Text(payment_date, size=14, weight="bold")], spacing=2),
                ], spacing=10, wrap=True),
                
                ft.Row([
                    ft.TextButton("View Invoice", icon=ft.icons.RECEIPT, on_click=lambda e, inv_id=inv_id: e.page.go(f"/billing/invoice/{inv_id}")),
                ], spacing=5),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    # Populate view list
    def load_payments(e=None):
        payments_container.controls.clear()
        
        payments = get_payments_from_db(
            payment_method_filter.value, 
            date_from.value, 
            date_to.value, 
            search_field.value if search_field.value else ""
        )
        
        if payments:
            total_revenue = sum(p[2] for p in payments)
            payments_container.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.PAYMENTS, color="primary", size=28),
                        ft.Column([
                            ft.Text(f"Total Revenue: ₱{total_revenue:,.2f}", size=20, weight="bold", color="primary"),
                            ft.Text(f"Showing {len(payments)} payment(s)", size=13, color="outline"),
                        ], spacing=2),
                    ], spacing=15),
                    padding=20,
                    bgcolor=ft.colors.with_opacity(0.05, "primary"),
                    border_radius=10,
                    border=ft.border.all(1, "primary"),
                )
            )
            for payment in payments:
                payments_container.controls.append(create_payment_card(payment))
        else:
            # Display empty state
            payments_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No payment history found", size=18, color="outline"),
                        ft.Text("Try adjusting your filters", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.CENTER
                )
            )
        
        if e and hasattr(e, 'page'): e.page.update()
    
    # Initial component mount
    load_payments(None)
    
    # Render primary structure
    return ft.Column([
        # Hide navigation back
        NavigationHeader("Payment History", "View all payment transactions and revenue", show_back=False),
        
        ft.Container(
            content=ft.Column([
                # Form parameter constraints
                ft.Text("Filter Payments", size=20, weight="bold"),
                ft.Row([payment_method_filter, date_from, date_to], spacing=10, wrap=True),
                
                ft.Row([
                    search_field,
                    ft.ElevatedButton("Apply Filters", icon=ft.icons.FILTER_ALT, bgcolor="primary", color="white", on_click=load_payments),
                    # Ensure standard controls
                ], spacing=10),
                
                # Ensure simplified layout
                
                ft.Divider(height=30),
                payments_container,
            ], spacing=15),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)


