"""Pharmacist medicine search and information view."""

import flet as ft
from services.database import get_db_connection
from components.navigation_header import NavigationHeader

def PharmacistMedicineSearch():
    """Medicine search for pharmacists with additional details."""
    
    results_container = ft.Column(spacing=10)
    
    search_field = ft.TextField(
        hint_text="Search medicines by name...",
        prefix_icon=ft.icons.SEARCH,
        border_color="outline",
        expand=True,
    )
    
    category_dropdown = ft.Dropdown(
        label="Category",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Pain Relief"),
            ft.dropdown.Option("Antibiotic"),
            ft.dropdown.Option("Supplement"),
            ft.dropdown.Option("Antacid"),
            ft.dropdown.Option("Antipyretic"),
        ],
        value="All",
        width=200,
    )
    
    stock_filter = ft.Dropdown(
        label="Stock Status",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("In Stock"),
            ft.dropdown.Option("Low Stock"),
            ft.dropdown.Option("Out of Stock"),
        ],
        value="All",
        width=150,
    )
    
    def create_medicine_card(med):
        """Create detailed medicine card for pharmacists."""
        
        # Determine stock status
        stock_color = "primary"
        stock_status = "In Stock"
        if med['stock'] == 0:
            stock_color = "error"
            stock_status = "Out of Stock"
        elif med['stock'] < 10:
            stock_color = "tertiary"
            stock_status = "Low Stock"
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    # Medicine icon
                    ft.Container(
                        width=80,
                        height=80,
                        bgcolor="surfaceVariant",
                        border_radius=10,
                        content=ft.Icon(ft.icons.MEDICATION, size=40, color="primary"),
                        alignment=ft.alignment.CENTER,
                    ),
                    
                    # Medicine details
                    ft.Column([
                        ft.Text(med['name'], size=18, weight="bold"),
                        ft.Text(f"Category: {med['category']}", size=13, color="outline"),
                        ft.Row([
                            ft.Text(f"₱ {med['price']:.2f}", size=16, weight="bold", color="primary"),
                            ft.Container(
                                content=ft.Text(
                                    stock_status,
                                    size=11,
                                    weight="bold",
                                    color="white",
                                ),
                                bgcolor=stock_color,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=10,
                            ),
                        ], spacing=10),
                    ], spacing=5, expand=True),
                    
                    # Stock and expiry info
                    ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Current Stock", size=11, color="outline"),
                                ft.Text(
                                    f"{med['stock']} units",
                                    size=20,
                                    weight="bold",
                                    color=stock_color,
                                ),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
                            padding=10,
                            border=ft.border.all(1, stock_color),
                            border_radius=8,
                        ),
                        ft.Text(f"Expires: {med['expiry_date']}", size=11, color="outline"),
                    ], spacing=5),
                ], spacing=15),
                
                # Additional info expandable
                ft.ExpansionTile(
                    title=ft.Text("View Medicine Details", size=13),
                    subtitle=ft.Text("Click to expand", size=11, color="outline"),
                    controls=[
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Column([
                                        ft.Text("Supplier", size=11, color="outline"),
                                        ft.Text(med.get('supplier', 'N/A'), size=13, weight="bold"),
                                    ], expand=True),
                                    ft.Column([
                                        ft.Text("Batch Number", size=11, color="outline"),
                                        ft.Text(med.get('batch_number', 'N/A'), size=13, weight="bold"),
                                    ], expand=True),
                                    ft.Column([
                                        ft.Text("Reorder Level", size=11, color="outline"),
                                        ft.Text(f"{med.get('reorder_level', 50)} units", size=13, weight="bold"),
                                    ], expand=True),
                                ]),
                                
                                ft.Divider(height=10),
                                
                                ft.Row([], spacing=10),
                            ], spacing=10),
                            padding=15,
                            bgcolor=ft.colors.with_opacity(0.05, "primary"),
                            border_radius=8,
                        ),
                    ],
                ),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    def view_medicine_details(e, medicine):
        """View full medicine details."""
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Viewing details for {medicine['name']}"),
            bgcolor="primary",
        )
        e.page.snack_bar.open = True
        e.page.update()
        # TODO: Navigate to detail page
    
    def update_stock(e, medicine):
        """Update medicine stock."""
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text("Stock update feature - Contact Inventory Manager"),
            bgcolor="secondary",
        )
        e.page.snack_bar.open = True
        e.page.update()
    
    def load_medicines(e=None):
        """Load medicines from database."""
        results_container.controls.clear()
        
        query = search_field.value.lower() if search_field.value else ""
        category = category_dropdown.value
        stock_status = stock_filter.value
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM medicines WHERE 1=1"
        params = []
        
        if query:
            sql += " AND LOWER(name) LIKE ?"
            params.append(f"%{query}%")
        
        if category != "All":
            sql += " AND category = ?"
            params.append(category)
        
        if stock_status == "In Stock":
            sql += " AND stock > 10"
        elif stock_status == "Low Stock":
            sql += " AND stock > 0 AND stock <= 10"
        elif stock_status == "Out of Stock":
            sql += " AND stock = 0"
        
        sql += " ORDER BY name ASC"
        
        cursor.execute(sql, params)
        medicines = cursor.fetchall()
        conn.close()
        
        if medicines:
            results_container.controls.append(
                ft.Text(
                    f"Found {len(medicines)} medicine(s)",
                    size=14,
                    color="outline",
                    weight="bold"
                )
            )
            
            for row in medicines:
                med_dict = {
                    'id': row[0],
                    'name': row[1],
                    'category': row[2],
                    'price': row[3],
                    'stock': row[4],
                    'expiry_date': row[5],
                    'supplier': row[6] if len(row) > 6 else 'N/A',
                    'batch_number': row[7] if len(row) > 7 else 'N/A',
                    'reorder_level': row[8] if len(row) > 8 else 50,
                }
                results_container.controls.append(create_medicine_card(med_dict))
        else:
            results_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No medicines found", size=18, color="outline"),
                        ft.Text("Try adjusting your search criteria", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                )
            )
        
        if e and hasattr(e, 'page'):
            e.page.update()
    
    # Initialize primary component state
    class FakePage:
        snack_bar = None
        def update(self): pass
    load_medicines(type('Event', (), {'page': FakePage()})())
    
    return ft.Column([
        NavigationHeader(
            "Medicine Database",
            "Search and view medicine information",
            show_back=True,
            back_route="/dashboard"
        ),
        
        ft.Container(
            content=ft.Column([
                # Search and filters
                ft.Row([
                    search_field,
                    category_dropdown,
                    stock_filter,
                    ft.ElevatedButton(
                        "Search",
                        icon=ft.icons.SEARCH,
                        bgcolor="primary",
                        color="white",
                        on_click=load_medicines,
                    ),
                    ft.IconButton(
                        icon=ft.icons.REFRESH,
                        icon_color="primary",
                        tooltip="Refresh",
                        on_click=load_medicines,
                    ),
                ], spacing=10),
                
                ft.Container(height=20),
                
                # Results
                results_container,
            ], spacing=0),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)


