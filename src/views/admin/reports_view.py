"""System reports generation with real database data - COMPLETE FIX."""

import flet as ft
from services.database import get_db_connection
from datetime import datetime, timedelta
from utils.notifications import show_success, show_error

def ReportsView():
    """Reports interface with real database statistics."""
    
    # This column holds the generated report content with proper scrolling
    report_output = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    
    # Dropdown to choose report type
    report_type = ft.Dropdown(
        label="Report Type",
        options=[
            ft.dropdown.Option("user_activity", "User Activity Report"),
            ft.dropdown.Option("inventory_status", "Inventory Status Report"),
            ft.dropdown.Option("prescription_summary", "Prescription Summary"),
            ft.dropdown.Option("low_stock", "Low Stock Alert Report"),
            ft.dropdown.Option("system_usage", "System Usage Statistics"),
            ft.dropdown.Option("orders_summary", "Orders Summary Report"),
        ],
        value="user_activity",
        width=300,
        border_color="primary",
    )
    
    # Date pickers
    date_from = ft.TextField(
        label="From Date",
        hint_text="YYYY-MM-DD",
        value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        width=200,
        border_color="primary",
    )
    
    date_to = ft.TextField(
        label="To Date",
        hint_text="YYYY-MM-DD",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=200,
        border_color="primary",
    )
    
    # Helper to make summary cards (expanded, consistent spacing)
    def create_summary_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=32),
                ft.Text(str(value), size=22, weight="bold", color=color, text_align=ft.TextAlign.CENTER),
                ft.Text(title, size=13, color="outline"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=20,
            bgcolor="surface",
            border_radius=12,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
            alignment=ft.alignment.CENTER,
        )

    # --- REPORT GENERATION FUNCTIONS ---
    
    def generate_user_activity_report():
        """Generate user activity report from real data."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get user counts by role
            cursor.execute("""
                SELECT role, COUNT(*) as count
                FROM users
                GROUP BY role
                ORDER BY count DESC
            """)
            role_stats = cursor.fetchall()
            
            # Get recent registrations
            cursor.execute("""
                SELECT username, full_name, role, created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT 10
            """)
            recent_users = cursor.fetchall()
            
            conn.close()
            
            # Build report
            controls = [
                ft.Text("User Activity Report", size=24, weight="bold"),
                ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                       size=12, color="outline"),
                ft.Divider(height=20),
                
                # Role statistics
                ft.Text("Users by Role", size=18, weight="bold"),
                ft.Container(height=10),
            ]
            
            # Role stats table
            if role_stats:
                for role_stat in role_stats:
                    controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.icons.PEOPLE, color="primary", size=20),
                                ft.Text("Customer" if str(role_stat[0]) == "Patient" else str(role_stat[0]), size=14, weight="bold", expand=1),
                                ft.Text(f"{role_stat[1]} users", size=14),
                            ], spacing=10),
                            padding=10,
                            border=ft.border.all(1, "outlineVariant"),
                            border_radius=8,
                        )
                    )
            
            controls.extend([
                ft.Container(height=20),
                ft.Text("Recent Registrations", size=18, weight="bold"),
                ft.Container(height=10),
            ])
            
            # Recent users table
            if recent_users:
                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Username", size=12, weight="bold", expand=1),
                            ft.Text("Full Name", size=12, weight="bold", expand=2),
                            ft.Text("Role", size=12, weight="bold", expand=1),
                            ft.Text("Registered", size=12, weight="bold", expand=1),
                        ]),
                        bgcolor="surfaceVariant",
                        padding=10,
                        border_radius=8,
                    )
                )
                
                for user in recent_users:
                    created_at = str(user[3])[:10] if user[3] else "N/A"
                    controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(str(user[0]), size=12, expand=1),
                                ft.Text(str(user[1]) if user[1] else "N/A", size=12, expand=2),
                                ft.Text("Customer" if str(user[2]) == "Patient" else str(user[2]), size=12, expand=1),
                                ft.Text(created_at, size=12, expand=1),
                            ]),
                            padding=10,
                            border=ft.border.all(1, "outlineVariant"),
                            border_radius=8,
                        )
                    )
            
            return controls
        except Exception as e:
            return [ft.Text(f"Error: {str(e)}", color="error", size=14)]

    def generate_inventory_report():
        """Generate inventory status report from real data."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get inventory statistics
            cursor.execute("SELECT COUNT(*) FROM medicines")
            total_meds = cursor.fetchone()[0] or 0
            
            # If no medicines, show a helpful message
            if total_meds == 0:
                conn.close()
                return [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.INFO, color="tertiary", size=50),
                            ft.Text("No inventory data available", size=18, weight="bold", color="tertiary"),
                            ft.Text("Run the database migration to seed medicines data.", size=13, color="outline"),
                            ft.Text("Command: python src\\services\\db_migration.py", size=11, color="outline", italic=True),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=50,
                    )
                ]
            
            cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock < 10")
            low_stock = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM medicines WHERE stock = 0")
            out_of_stock = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT SUM(CAST(stock AS REAL) * CAST(price AS REAL)) FROM medicines")
            result = cursor.fetchone()
            total_value = float(result[0]) if result and result[0] else 0.0
            
            # Get medicines by category
            cursor.execute("""
                SELECT category, COUNT(*) as count, SUM(stock) as total_stock
                FROM medicines
                GROUP BY category
                ORDER BY count DESC
            """)
            categories = cursor.fetchall()
            
            # Get top 10 medicines by stock
            cursor.execute("""
                SELECT name, category, stock, price, (CAST(stock AS REAL) * CAST(price AS REAL)) as value
                FROM medicines
                ORDER BY stock DESC
                LIMIT 10
            """)
            top_stock = cursor.fetchall()
            
            conn.close()
            
            # Build report
            controls = [
                ft.Text("Inventory Status Report", size=24, weight="bold"),
                ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                       size=12, color="outline"),
                ft.Divider(height=20),
                
                # Summary cards - expanded with even spacing
                ft.Row([
                    create_summary_card("Total Medicines", total_meds, ft.icons.MEDICATION, "primary"),
                    create_summary_card("Low Stock", low_stock, ft.icons.WARNING, "error"),
                    create_summary_card("Out of Stock", out_of_stock, ft.icons.ERROR, "error"),
                    create_summary_card("Total Value", f"₱{total_value:,.2f}", ft.icons.PAYMENTS, "secondary"),
                ], spacing=15, run_spacing=15),
                
                ft.Container(height=20),
                ft.Text("Inventory by Category", size=18, weight="bold"),
                ft.Container(height=10),
            ]
            
            # Category breakdown
            if categories:
                for cat in categories:
                    controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.icons.CATEGORY, color="secondary", size=20),
                                ft.Text(str(cat[0]), size=14, weight="bold", expand=1),
                                ft.Text(f"{cat[1]} items", size=14),
                                ft.Text(f"Stock: {cat[2]}", size=14),
                            ], spacing=10),
                            padding=10,
                            border=ft.border.all(1, "outlineVariant"),
                            border_radius=8,
                        )
                    )
            
            controls.extend([
                ft.Container(height=20),
                ft.Text("Top 10 Items by Stock", size=18, weight="bold"),
                ft.Container(height=10),
            ])
            
            # Top stock items
            if top_stock:
                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Medicine", size=12, weight="bold", expand=2),
                            ft.Text("Category", size=12, weight="bold", expand=1),
                            ft.Text("Stock", size=12, weight="bold", expand=1),
                            ft.Text("Price", size=12, weight="bold", expand=1),
                            ft.Text("Value", size=12, weight="bold", expand=1),
                        ]),
                        bgcolor="surfaceVariant",
                        padding=10,
                        border_radius=8,
                    )
                )
                
                for med in top_stock:
                    controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(str(med[0]), size=12, expand=2),
                                ft.Text(str(med[1]), size=12, expand=1),
                                ft.Text(str(med[2]), size=12, expand=1),
                                ft.Text(f"₱{float(med[3]):.2f}", size=12, expand=1),
                                ft.Text(f"₱{float(med[4]):.2f}", size=12, expand=1),
                            ]),
                            padding=10,
                            border=ft.border.all(1, "outlineVariant"),
                            border_radius=8,
                        )
                    )
            
            return controls
        except Exception as e:
            return [ft.Text(f"Error generating inventory report: {str(e)}", color="error", size=14)]

    def generate_prescription_report():
        """Generate prescription summary report from real data."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get prescription statistics
            cursor.execute("SELECT COUNT(*) FROM prescriptions")
            total_rx = cursor.fetchone()[0] or 0
            
            # If no prescriptions, show a helpful message
            if total_rx == 0:
                conn.close()
                return [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.INFO, color="tertiary", size=50),
                            ft.Text("No prescription data available", size=18, weight="bold", color="tertiary"),
                            ft.Text("Run the database migration to seed prescription data.", size=13, color="outline"),
                            ft.Text("Command: python src\\services\\db_migration.py", size=11, color="outline", italic=True),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=50,
                    )
                ]
            
            cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Pending'")
            pending = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Approved'")
            approved = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM prescriptions WHERE status = 'Rejected'")
            rejected = cursor.fetchone()[0] or 0
            
            # Get recent prescriptions
            cursor.execute("""
                SELECT p.id, p.status, p.created_at, u.full_name, u.username
                FROM prescriptions p
                JOIN users u ON p.patient_id = u.id
                ORDER BY p.created_at DESC
                LIMIT 15
            """)
            recent_rx = cursor.fetchall()
            
            conn.close()
            
            # Build report
            controls = [
                ft.Text("Prescription Summary Report", size=24, weight="bold"),
                ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                       size=12, color="outline"),
                ft.Divider(height=20),
                
                # Summary cards - expanded with even spacing
                ft.Row([
                    create_summary_card("Total Prescriptions", total_rx, ft.icons.DESCRIPTION, "primary"),
                    create_summary_card("Pending", pending, ft.icons.PENDING, "tertiary"),
                    create_summary_card("Approved", approved, ft.icons.CHECK_CIRCLE, "primary"),
                    create_summary_card("Rejected", rejected, ft.icons.CANCEL, "error"),
                ], spacing=15, run_spacing=15),
                
                ft.Container(height=20),
                ft.Text("Recent Prescriptions", size=18, weight="bold"),
                ft.Container(height=10),
            ]
            
            # Recent prescriptions table
            if recent_rx:
                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("ID", size=12, weight="bold", expand=1),
                            ft.Text("Customer", size=12, weight="bold", expand=2),
                            ft.Text("Status", size=12, weight="bold", expand=1),
                            ft.Text("Date", size=12, weight="bold", expand=1),
                        ]),
                        bgcolor="surfaceVariant",
                        padding=10,
                        border_radius=8,
                    )
                )
                
                for rx in recent_rx:
                    status_color = {
                        "Pending": "tertiary",
                        "Approved": "primary",
                        "Rejected": "error",
                        "Completed": "primary"
                    }.get(str(rx[1]), "outline")
                    
                    created_date = str(rx[2])[:10] if rx[2] else "N/A"
                    patient_name = str(rx[3]) if rx[3] else str(rx[4])
                    
                    controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(f"#{rx[0]}", size=12, expand=1),
                                ft.Text(patient_name, size=12, expand=2),
                                ft.Container(
                                    content=ft.Text(str(rx[1]), size=11, color="white"),
                                    bgcolor=status_color,
                                    padding=5,
                                    border_radius=5,
                                    expand=1,
                                ),
                                ft.Text(created_date, size=12, expand=1),
                            ]),
                            padding=10,
                            border=ft.border.all(1, "outlineVariant"),
                            border_radius=8,
                        )
                    )
            
            return controls
        except Exception as e:
            return [ft.Text(f"Error generating prescription report: {str(e)}", color="error", size=14)]

    def generate_low_stock_report():
        """Generate low stock alert report from real data."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get low stock items (stock < 10 but > 0)
            cursor.execute("""
                SELECT name, category, stock, price, supplier
                FROM medicines
                WHERE stock < 10 AND stock > 0
                ORDER BY stock ASC
            """)
            low_stock_items = cursor.fetchall()
            
            # Get out of stock items
            cursor.execute("""
                SELECT name, category, price, supplier
                FROM medicines
                WHERE stock = 0
                ORDER BY name
            """)
            out_of_stock_items = cursor.fetchall()
            
            conn.close()
            
            # Build report
            controls = [
                ft.Text("Low Stock Alert Report", size=24, weight="bold"),
                ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                       size=12, color="outline"),
                ft.Divider(height=20),
            ]
            
            # Out of stock section
            if out_of_stock_items:
                controls.extend([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.ERROR, color="error", size=30),
                            ft.Text(f"{len(out_of_stock_items)} items are OUT OF STOCK!", 
                                   size=16, weight="bold", color="error"),
                        ], spacing=10),
                        bgcolor=ft.colors.with_opacity(0.1, "error"),
                        padding=15,
                        border_radius=8,
                    ),
                    ft.Container(height=10),
                    
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Medicine", size=12, weight="bold", expand=2),
                            ft.Text("Category", size=12, weight="bold", expand=1),
                            ft.Text("Price", size=12, weight="bold", expand=1),
                            ft.Text("Supplier", size=12, weight="bold", expand=2),
                        ]),
                        bgcolor="surfaceVariant",
                        padding=10,
                        border_radius=8,
                    ),
                ])
                
                for item in out_of_stock_items:
                    controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(str(item[0]), size=12, expand=2),
                                ft.Text(str(item[1]), size=12, expand=1),
                                ft.Text(f"₱{float(item[2]):.2f}", size=12, expand=1),
                                ft.Text(str(item[3]) if item[3] else "N/A", size=12, expand=2),
                            ]),
                            padding=10,
                            border=ft.border.all(1, "error"),
                            border_radius=8,
                            bgcolor=ft.colors.with_opacity(0.05, "error"),
                        )
                    )
                
                controls.append(ft.Container(height=20))
            
            # Low stock section
            if low_stock_items:
                controls.extend([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.WARNING, color="tertiary", size=30),
                            ft.Text(f"{len(low_stock_items)} items have LOW STOCK (< 10 units)", 
                                   size=16, weight="bold", color="tertiary"),
                        ], spacing=10),
                        bgcolor=ft.colors.with_opacity(0.1, "tertiary"),
                        padding=15,
                        border_radius=8,
                    ),
                    ft.Container(height=10),
                    
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Medicine", size=12, weight="bold", expand=2),
                            ft.Text("Category", size=12, weight="bold", expand=1),
                            ft.Text("Stock", size=12, weight="bold", expand=1),
                            ft.Text("Price", size=12, weight="bold", expand=1),
                            ft.Text("Supplier", size=12, weight="bold", expand=2),
                        ]),
                        bgcolor="surfaceVariant",
                        padding=10,
                        border_radius=8,
                    ),
                ])
                
                for item in low_stock_items:
                    controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(str(item[0]), size=12, expand=2),
                                ft.Text(str(item[1]), size=12, expand=1),
                                ft.Text(str(item[2]), size=12, weight="bold", color="tertiary", expand=1),
                                ft.Text(f"₱{float(item[3]):.2f}", size=12, expand=1),
                                ft.Text(str(item[4]) if item[4] else "N/A", size=12, expand=2),
                            ]),
                            padding=10,
                            border=ft.border.all(1, "outlineVariant"),
                            border_radius=8,
                        )
                    )
            
            if not low_stock_items and not out_of_stock_items:
                controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.CHECK_CIRCLE, color="primary", size=50),
                            ft.Text("All inventory levels are healthy!", 
                                   size=18, weight="bold", color="primary"),
                        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=50,
                    )
                )
            
            return controls
        except Exception as e:
            return [ft.Text(f"Error generating low stock report: {str(e)}", color="error", size=14)]

    def generate_system_usage_report():
        """Generate system usage statistics from real data."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Get various counts
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM medicines")
            total_medicines = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM prescriptions")
            total_prescriptions = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM orders")
            total_orders = cursor.fetchone()[0] or 0
            
            # If no meaningful data beyond users, show a helpful message
            if total_medicines == 0 and total_orders == 0 and total_prescriptions == 0:
                conn.close()
                return [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.INFO, color="tertiary", size=50),
                            ft.Text("Limited system data available", size=18, weight="bold", color="tertiary"),
                            ft.Text("Run the database migration to seed complete demo data.", size=13, color="outline"),
                            ft.Text("Command: python src\\services\\db_migration.py", size=11, color="outline", italic=True),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=50,
                    )
                ]
            
            # Get users by role
            cursor.execute("""
                SELECT role, COUNT(*) as count
                FROM users
                GROUP BY role
            """)
            users_by_role = cursor.fetchall()
            
            conn.close()
            
            # Build report
            controls = [
                ft.Text("System Usage Statistics", size=24, weight="bold"),
                ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                       size=12, color="outline"),
                ft.Divider(height=20),
                
                ft.Text("Overall System Statistics", size=18, weight="bold"),
                ft.Container(height=10),
                
                ft.Row([
                    create_summary_card("Total Users", total_users, ft.icons.PEOPLE, "primary"),
                    create_summary_card("Total Medicines", total_medicines, ft.icons.MEDICATION, "secondary"),
                    create_summary_card("Prescriptions", total_prescriptions, ft.icons.DESCRIPTION, "tertiary"),
                    create_summary_card("Orders", total_orders, ft.icons.SHOPPING_CART, "primary"),
                ], spacing=15, run_spacing=15),
                
                ft.Container(height=20),
                ft.Text("User Distribution", size=18, weight="bold"),
                ft.Container(height=10),
            ]
            
            # User role distribution
            if users_by_role:
                for role_data in users_by_role:
                    percentage = (float(role_data[1]) / float(total_users) * 100) if total_users > 0 else 0
                    controls.append(
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text("Customer" if str(role_data[0]) == "Patient" else str(role_data[0]), size=14, weight="bold", expand=1),
                                    ft.Text(f"{role_data[1]} users ({percentage:.1f}%)", size=14),
                                ]),
                                ft.ProgressBar(
                                    value=percentage / 100,
                                    color="primary",
                                    bgcolor="surfaceVariant",
                                ),
                            ], spacing=5),
                            padding=15,
                            border=ft.border.all(1, "outlineVariant"),
                            border_radius=8,
                        )
                    )
            
            return controls
        except Exception as e:
            return [ft.Text(f"Error generating system usage report: {str(e)}", color="error", size=14)]

    def generate_orders_summary():
        """Generate orders summary report from real data."""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Parse date filters
            try:
                date_from = date_from.value if hasattr(date_from, 'value') else date_from
                date_to = date_to.value if hasattr(date_to, 'value') else date_to
            except:
                date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                date_to = datetime.now().strftime("%Y-%m-%d")
            
            # Get order statistics with date filter
            cursor.execute("""
                SELECT COUNT(*), SUM(total_amount) FROM orders 
                WHERE DATE(order_date) BETWEEN ? AND ?
            """, (date_from, date_to))
            result = cursor.fetchone()
            total_orders = result[0] or 0
            
            # Get total revenue from COMPLETED orders only within date range (per finance division)
            cursor.execute("""
                SELECT SUM(total_amount) FROM orders 
                WHERE status = 'Completed' AND DATE(order_date) BETWEEN ? AND ?
            """, (date_from, date_to))
            revenue_result = cursor.fetchone()
            total_revenue = float(revenue_result[0]) if revenue_result and revenue_result[0] else 0.0
            
            # If no orders, show a helpful message
            if total_orders == 0:
                conn.close()
                return [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.INFO, color="tertiary", size=50),
                            ft.Text("No orders data available", size=18, weight="bold", color="tertiary"),
                            ft.Text("Run the database migration to seed orders data.", size=13, color="outline"),
                            ft.Text("Command: python src\\services\\db_migration.py", size=11, color="outline", italic=True),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=50,
                    )
                ]
            
            cursor.execute("""
                SELECT COUNT(*) FROM orders 
                WHERE status = 'Pending' AND DATE(order_date) BETWEEN ? AND ?
            """, (date_from, date_to))
            pending = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT COUNT(*) FROM orders 
                WHERE status = 'Completed' AND DATE(order_date) BETWEEN ? AND ?
            """, (date_from, date_to))
            completed = cursor.fetchone()[0] or 0
            
            # Get recent orders
            cursor.execute("""
                SELECT o.id, o.total_amount, o.status, o.order_date, u.username
                FROM orders o
                JOIN users u ON o.patient_id = u.id
                ORDER BY o.order_date DESC
                LIMIT 15
            """)
            orders = cursor.fetchall()
            
            conn.close()
            
            controls = [
                ft.Text("Orders Summary Report", size=24, weight="bold"),
                ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", size=12, color="outline"),
                ft.Divider(height=20),
                
                ft.Row([
                    create_summary_card("Total Orders", total_orders, ft.icons.SHOPPING_CART, "primary"),
                    create_summary_card("Total Revenue", f"₱{total_revenue:,.2f}", ft.icons.PAYMENTS, "secondary"),
                    create_summary_card("Pending", pending, ft.icons.PENDING, "tertiary"),
                    create_summary_card("Completed", completed, ft.icons.CHECK_CIRCLE, "primary"),
                ], spacing=15, run_spacing=15),
                
                ft.Container(height=20),
                ft.Text("Recent Orders", size=18, weight="bold"),
                ft.Container(height=10),
            ]
            
            if orders:
                controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Order ID", size=12, weight="bold", expand=1),
                            ft.Text("Customer", size=12, weight="bold", expand=2),
                            ft.Text("Amount", size=12, weight="bold", expand=1),
                            ft.Text("Status", size=12, weight="bold", expand=1),
                            ft.Text("Date", size=12, weight="bold", expand=1),
                        ]),
                        bgcolor="surfaceVariant",
                        padding=10,
                        border_radius=8,
                    )
                )
                
                for order in orders:
                    order_date = str(order[3])[:10] if order[3] else "N/A"
                    controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(f"#{order[0]}", size=12, expand=1),
                                ft.Text(str(order[4]), size=12, expand=2),
                                ft.Text(f"₱{float(order[1]):.2f}", size=12, expand=1),
                                ft.Text(str(order[2]), size=12, expand=1),
                                ft.Text(order_date, size=12, expand=1),
                            ]),
                            padding=10,
                            border=ft.border.all(1, "outlineVariant"),
                            border_radius=8,
                        )
                    )
            
            return controls
        except Exception as e:
            return [ft.Text(f"Error generating orders report: {str(e)}", color="error", size=14)]
    
    def generate_report(e):
        """Execute selected report generator."""
        # Clear controls completely first
        report_output.controls.clear()
        e.page.update()

        # Dictionary mapping values to functions
        report_generators = {
            "user_activity": generate_user_activity_report,
            "inventory_status": generate_inventory_report,
            "prescription_summary": generate_prescription_report,
            "low_stock": generate_low_stock_report,
            "system_usage": generate_system_usage_report,
            "orders_summary": generate_orders_summary,
        }

        generator = report_generators.get(report_type.value)
        if generator:
            try:
                # Generate report and wrap in a Column to ensure proper rendering
                report_controls = generator()
                # Clear any previous content and set new
                report_output.controls.clear()
                for ctrl in report_controls:
                    report_output.controls.append(ctrl)
                show_success(e.page, f"Report generated successfully!")
            except Exception as ex:
                report_output.controls = [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.icons.ERROR, color="error", size=40),
                            ft.Text(f"Critical error: {str(ex)}", color="error", size=14),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                    )
                ]
                show_error(e.page, f"Failed to generate report")

        e.page.update()
    
    # --- PAGE LAYOUT ---
    return ft.Column([
        ft.Row([
            ft.Text("System Reports", size=28, weight="bold"),
        ]),
        ft.Text("Generate comprehensive system reports", size=14, color="outline"),
        
        ft.Container(height=20),
        
        # Report controls
        ft.Container(
            content=ft.Column([
                ft.Row([
                    report_type,
                    date_from,
                    date_to,
                ], spacing=10, wrap=True),
                
                ft.Row([
                    ft.ElevatedButton(
                        "Generate Report",
                        icon=ft.icons.ANALYTICS,
                        bgcolor="primary",
                        color="onPrimary",
                        on_click=generate_report,
                    ),
                ], spacing=10),
            ], spacing=15),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
        ),
        
        ft.Container(height=20),
        
        # Report output area
        ft.Container(
            content=report_output,
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)


