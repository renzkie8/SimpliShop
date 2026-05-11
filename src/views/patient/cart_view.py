"""Shopping cart view with real database integration - FIXED VERSION."""

import flet as ft
from state import AppState
from services.database import get_db_connection
from utils.notifications import show_success, show_error, show_warning, ITEM_REMOVED, ORDER_PLACED, OPERATION_FAILED

def CartView():
    """Shopping cart view with persistent cart data."""
    
    # Validate user session
    user = AppState.get_user()
    if not user:
        return ft.Text("Please log in first", color="error")
    
    user_id = user['id']
    
    # Initialize UI containers
    cart_container = ft.Column(spacing=10)
    summary_container = ft.Container()
    
    # Discount request dropdown
    discount_dropdown = ft.Dropdown(
        label="Discount Request (Subject to Verification)",
        options=[
            ft.dropdown.Option("None"),
            ft.dropdown.Option("Senior Citizen"),
            ft.dropdown.Option("PWD"),
        ],
        value="None",
        width=300,
        text_size=14,
        content_padding=10
    )
    
    # Retrieve cart contents
    def load_cart():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ensure schema exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                medicine_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES users(id),
                FOREIGN KEY (medicine_id) REFERENCES medicines(id)
            )
        """)
        
        # Query cart items
        cursor.execute("""
            SELECT 
                c.id,
                c.medicine_id,
                m.name,
                m.price,
                c.quantity,
                m.stock
            FROM cart c
            JOIN medicines m ON c.medicine_id = m.id
            WHERE c.patient_id = ?
        """, (user_id,))
        
        items = cursor.fetchall()
        conn.close()
        
        return items
    
    # Handle quantity updates with stock synchronization
    def update_quantity(cart_id, medicine_id, new_quantity, old_quantity, stock, e):
        if new_quantity <= 0:
            remove_from_cart(cart_id, medicine_id, old_quantity, e)
            return

        diff = new_quantity - old_quantity
        if diff == 0:
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # If incrementing, check if enough stock is actually available in DB (keeping at least 1)
            if diff > 0:
                cursor.execute("SELECT stock FROM medicines WHERE id = ?", (medicine_id,))
                db_stock = cursor.fetchone()[0]
                if db_stock - diff < 1:
                    show_error(e.page, f"At least 1 unit of {medicine_id} must remain in the warehouse stock")
                    return

            # Update both tables in a single transaction
            cursor.execute("UPDATE cart SET quantity = ? WHERE id = ?", (new_quantity, cart_id))
            cursor.execute("UPDATE medicines SET stock = stock - ? WHERE id = ?", (diff, medicine_id))
            
            conn.commit()

            # Emit cart changed event to update badge and sidebar
            try:
                AppState.emit('cart_changed')
            except Exception:
                pass

            # Show success indicator
            AppState.show_success()
            refresh_cart(e)
            
        except Exception as ex:
            if conn: conn.rollback()
            show_error(e.page, f"Update failed: {str(ex)}")
        finally:
            conn.close()
    
    # Handle item removal with stock restoration
    def remove_from_cart(cart_id, medicine_id, quantity, e):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Restore the stock in medicines table
            cursor.execute("UPDATE medicines SET stock = stock + ? WHERE id = ?", (quantity, medicine_id))
            
            # Delete from cart
            cursor.execute("DELETE FROM cart WHERE id = ?", (cart_id,))
            
            conn.commit()

            # Emit cart changed event to update badge and sidebar
            try:
                AppState.emit('cart_changed')
            except Exception:
                pass

            # Show success indicator
            AppState.show_success()
            show_success(e.page, ITEM_REMOVED.format("Item"))
            refresh_cart(e)
            
        except Exception as ex:
            if conn: conn.rollback()
            show_error(e.page, f"Removal failed: {str(ex)}")
        finally:
            conn.close()
    
    # Display notification
    def show_snackbar(e, message, error=False):
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor="error" if error else "primary",
        )
        e.page.snack_bar.open = True
        e.page.update()
    
    # Render cart item component
    def create_cart_item(item):
        cart_id = item[0]
        medicine_id = item[1]
        name = item[2]
        price = item[3]
        quantity = item[4]
        stock = item[5]
        
        quantity_field = ft.TextField(
            value=str(quantity),
            width=60,
            text_align=ft.TextAlign.CENTER,
            border_color="outline",
            on_submit=lambda e: update_quantity(cart_id, medicine_id, int(e.control.value), quantity, stock, e)
        )
        
        return ft.Container(
            content=ft.Row([
                # medicine icon
                ft.Container(
                    width=60,
                    height=60,
                    bgcolor="surfaceVariant",
                    border_radius=8,
                    content=ft.Icon(ft.icons.MEDICATION, size=30, color="outline"),
                    alignment=ft.alignment.CENTER,
                ),
                # name and price
                ft.Column([
                    ft.Text(name, size=16, weight="bold"),
                    ft.Text(f"₱ {price:.2f}", size=14, color="primary"),
                    ft.Text(f"Available: {stock}", size=11, color="outline"),
                ], spacing=5, expand=True),
                # plus minus buttons
                ft.Row([
                    ft.IconButton(
                        icon=ft.icons.REMOVE,
                        icon_size=16,
                        icon_color="primary",
                        on_click=lambda e: update_quantity(cart_id, medicine_id, quantity - 1, quantity, stock, e)
                    ),
                    quantity_field,
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        icon_size=16,
                        icon_color="primary",
                        on_click=lambda e: update_quantity(cart_id, medicine_id, quantity + 1, quantity, stock, e)
                    ),
                ], spacing=5),
                # total price for this line
                ft.Text(
                    f"₱ {price * quantity:.2f}",
                    size=16,
                    weight="bold",
                    color="primary",
                ),
                # delete button
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    icon_color="error",
                    tooltip="Remove from cart",
                    on_click=lambda e: remove_from_cart(cart_id, medicine_id, quantity, e)
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=15),
            padding=15,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    # ✅ FIXED: Process checkout with prescription approval tracking
    def proceed_to_checkout(e):
        items = load_cart()
        if not items:
            show_error(e.page, "Cart is empty")
            return

        # Create order records
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Calculate order totals
            subtotal = sum(item[3] * item[4] for item in items)
            tax = subtotal * 0.12
            total = subtotal + tax

            # Insert order record with discount request
            cursor.execute("""
                INSERT INTO orders (patient_id, total_amount, status, payment_status, discount_request)
                VALUES (?, ?, 'Pending', 'Unpaid', ?)
            """, (user_id, total, discount_dropdown.value))

            order_id = cursor.lastrowid

            # ✅ FIX: Process individual line items WITH prescription approval check
            for item in items:
                medicine_id = item[1]
                quantity = item[4]
                unit_price = item[3]
                subtotal_item = unit_price * quantity

                # ✅ KEY FIX: Check if this medicine is from an APPROVED prescription
                cursor.execute("""
                    SELECT id, pharmacist_id, reviewed_date
                    FROM prescriptions
                    WHERE patient_id = ?
                    AND medicine_id = ?
                    AND status = 'Approved'
                    ORDER BY reviewed_date DESC
                    LIMIT 1
                """, (user_id, medicine_id))
                
                approved_prescription = cursor.fetchone()
                
                # If prescription is approved, mark the order item as approved
                if approved_prescription:
                    prescription_id, pharmacist_id, reviewed_date = approved_prescription
                    
                    # ✅ Insert order item WITH pharmacist approval
                    cursor.execute("""
                        INSERT INTO order_items 
                        (order_id, medicine_id, quantity, unit_price, subtotal, 
                         pharmacist_approved, pharmacist_id, approval_notes)
                        VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                    """, (
                        order_id, 
                        medicine_id, 
                        quantity, 
                        unit_price, 
                        subtotal_item,
                        pharmacist_id,
                        f"Pre-approved via Prescription #{prescription_id}"
                    ))
                else:
                    # ⏳ Insert order item WITHOUT pharmacist approval (needs review)
                    cursor.execute("""
                        INSERT INTO order_items 
                        (order_id, medicine_id, quantity, unit_price, subtotal, 
                         pharmacist_approved, pharmacist_id, approval_notes)
                        VALUES (?, ?, ?, ?, ?, 0, NULL, NULL)
                    """, (order_id, medicine_id, quantity, unit_price, subtotal_item))

                # Inventory deduction REMOVED from here because it's now handled in real-time
                # when items are added to the cart or quantities are adjusted.

            # Clear processed cart
            cursor.execute("DELETE FROM cart WHERE patient_id = ?", (user_id,))

            conn.commit()

            # Emit cart changed event to update badge across app
            try:
                AppState.emit('cart_changed')
            except Exception:
                pass

            # Show success indicator
            AppState.show_success()
            show_success(e.page, ORDER_PLACED.format(order_id))
            refresh_cart(e)

            # Navigate to POS Receipt
            e.page.go(f"/patient/pos_receipt/{order_id}")

        except Exception as ex:
            conn.rollback()
            show_error(e.page, f"{OPERATION_FAILED}: {str(ex)}")
        finally:
            conn.close()
    
    # Refresh cart interface
    def refresh_cart(e):
        items = load_cart()
        
        cart_container.controls.clear()
        
        if items:
            for item in items:
                cart_container.controls.append(create_cart_item(item))
            
            # calculating totals
            subtotal = sum(item[3] * item[4] for item in items)
            tax = subtotal * 0.12
            total = subtotal + tax
            
            # Render order summary
            summary_container.content = ft.Column([
                ft.Text("Order Summary", size=20, weight="bold"),
                ft.Divider(),
                ft.Row([
                    ft.Text("Subtotal:", size=14),
                    ft.Text(f"₱ {subtotal:.2f}", size=14, weight="bold"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text("Tax (12%):", size=14),
                    ft.Text(f"₱ {tax:.2f}", size=14, weight="bold"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.Row([
                    ft.Text("Total:", size=18, weight="bold"),
                    ft.Text(f"₱ {total:.2f}", size=20, weight="bold", color="primary"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                
                # Discount dropdown
                discount_dropdown,
                ft.Container(height=10),
                
                # Render centered actions
                ft.ElevatedButton(
                    "Proceed to Checkout",
                    width=300,
                    height=50,
                    icon=ft.icons.PAYMENT,
                    bgcolor="primary",
                    color="onPrimary",
                    on_click=proceed_to_checkout,
                ),
                ft.OutlinedButton(
                    "Continue Shopping",
                    width=300,
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: e.page.go("/patient/search"),
                ),
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        else:
            # Render empty state
            summary_container.content = ft.Column([
                ft.Icon(ft.icons.SHOPPING_CART_OUTLINED, size=100, color="outline"),
                ft.Text("Your cart is empty", size=20, color="outline"),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Browse Medicines",
                    icon=ft.icons.SEARCH,
                    on_click=lambda e: e.page.go("/patient/search"),
                    bgcolor="primary",
                    color="onPrimary",
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
        
        e.page.update()
    
    # Initial component mount
    items = load_cart()
    
    if not items:
        # Handle initial empty cart
        return ft.Column([
            ft.Text("Shopping Cart", size=28, weight="bold"),
            ft.Container(height=20),
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.icons.SHOPPING_CART_OUTLINED, size=100, color="outline"),
                    ft.Text("Your cart is empty", size=20, color="outline"),
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Browse Medicines",
                        icon=ft.icons.SEARCH,
                        on_click=lambda e: e.page.go("/patient/search"),
                        bgcolor="primary",
                        color="onPrimary",
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=80,
                alignment=ft.alignment.CENTER,
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
    
    # Render initial cart inventory
    for item in items:
        cart_container.controls.append(create_cart_item(item))
    
    # Evaluate initial order totals
    subtotal = sum(item[3] * item[4] for item in items)
    tax = subtotal * 0.12
    total = subtotal + tax
    
    # Initial summary container
    summary_container.content = ft.Column([
        ft.Text("Order Summary", size=20, weight="bold"),
        ft.Divider(),
        ft.Row([
            ft.Text("Subtotal:", size=14),
            ft.Text(f"₱ {subtotal:.2f}", size=14, weight="bold"),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Row([
            ft.Text("Tax (12%):", size=14),
            ft.Text(f"₱ {tax:.2f}", size=14, weight="bold"),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(),
        ft.Row([
            ft.Text("Total:", size=18, weight="bold"),
            ft.Text(f"₱ {total:.2f}", size=20, weight="bold", color="primary"),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Container(height=10),
        
        # Discount dropdown
        discount_dropdown,
        ft.Container(height=10),
        
        # Navigation controls
        ft.ElevatedButton(
            "Proceed to Checkout",
            width=300,
            height=50,
            icon=ft.icons.PAYMENT,
            bgcolor="primary",
            color="onPrimary",
            on_click=proceed_to_checkout,
        ),
        ft.OutlinedButton(
            "Continue Shopping",
            width=300,
            icon=ft.icons.ARROW_BACK,
            on_click=lambda e: e.page.go("/patient/search"),
        ),
    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    # Primary layout structure
    return ft.Column([
        ft.Row([
            ft.Text("Shopping Cart", size=28, weight="bold"),
            ft.Text(f"({len(items)} items)", size=18, color="outline"),
        ], spacing=10),
        
        ft.Container(height=20),
        
        # cart items list
        cart_container,
        
        ft.Container(height=20),
        ft.Divider(),
        
        # summary section
        ft.Row([
            ft.Container(
                content=summary_container,
                padding=20,
                bgcolor="surface",
                border_radius=10,
                border=ft.border.all(1, "outlineVariant"),
                width=400,
            ),
        ], alignment=ft.MainAxisAlignment.CENTER),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)



