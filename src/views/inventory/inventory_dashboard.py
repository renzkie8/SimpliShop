import flet as ft
from services.database import get_db_connection

def InventoryDashboard():
    """Main screen for Inventory Manager."""
    
    # Retrieve KPIs from database
    conn = get_db_connection()
    total_meds = conn.execute("SELECT COUNT(*) FROM medicines").fetchone()[0]
    low_stock_count = conn.execute("SELECT COUNT(*) FROM medicines WHERE stock < 10").fetchone()[0]
    conn.close()

    # Metric card component factory
    def create_stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=40),
                    ft.Column([
                        ft.Text(title, size=14, color="outline"),
                        ft.Text(str(value), size=32, weight="bold", color=color),
                    ], spacing=2, expand=True),
                ], spacing=15),
            ]),
            padding=20,
            bgcolor="surface",
            border_radius=10,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
        )

    return ft.Column([
        ft.Text("Inventory Dashboard", size=28, weight="bold"),
        ft.Container(height=20),
        
        # Key Performance Indicators row
        ft.Row([
            create_stat_card("Total Products", total_meds, ft.icons.INVENTORY_2, "primary"),
            create_stat_card("Low Stock Items", low_stock_count, ft.icons.WARNING, "error"),
        ], spacing=15),

        ft.Container(height=20),
        
        # Navigation action buttons
        ft.Text("Quick Actions", size=20, weight="bold"),
        ft.ElevatedButton("Manage Stock", icon=ft.icons.EDIT, on_click=lambda e: e.page.go("/inventory/stock"), height=50),
        
    ], scroll=ft.ScrollMode.AUTO)


