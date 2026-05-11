"""Pharmacist reports and analytics view."""

import flet as ft
from datetime import datetime, timedelta
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader
from utils.notifications import show_success, show_error

def ReportsView():
    """Generate and view pharmacist reports."""
    
    user = AppState.get_user()
    
    # Date range filters
    date_from = ft.TextField(
        label="From Date",
        value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        width=150,
        border_color="outline",
    )
    
    date_to = ft.TextField(
        label="To Date",
        value=datetime.now().strftime("%Y-%m-%d"),
        width=150,
        border_color="outline",
    )
    
    report_container = ft.Column(spacing=15)
    
    def generate_report(e):
        """Generate pharmacy report."""
        report_container.controls.clear()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get prescription statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) as approved,
                    SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) as rejected,
                    SUM(CASE WHEN status = 'Dispensed' THEN 1 ELSE 0 END) as dispensed
                FROM prescriptions
                WHERE DATE(created_at) BETWEEN ? AND ?
            """, (date_from.value, date_to.value))
            
            stats = cursor.fetchone()
            total, pending, approved, rejected, dispensed = stats if stats else (0, 0, 0, 0, 0)
            
            # Get top prescribed medicines
            cursor.execute("""
                SELECT m.name, COUNT(p.id) as count
                FROM prescriptions p
                LEFT JOIN medicines m ON p.medicine_id = m.id
                WHERE DATE(p.created_at) BETWEEN ? AND ?
                GROUP BY m.name
                ORDER BY count DESC
                LIMIT 5
            """, (date_from.value, date_to.value))
            
            top_medicines = cursor.fetchall()
            
            # Get pharmacist activity
            cursor.execute("""
                SELECT 
                    u.full_name,
                    COUNT(p.id) as reviewed_count
                FROM prescriptions p
                LEFT JOIN users u ON p.pharmacist_id = u.id
                WHERE p.pharmacist_id IS NOT NULL
                AND DATE(p.reviewed_date) BETWEEN ? AND ?
                GROUP BY u.full_name
                ORDER BY reviewed_count DESC
            """, (date_from.value, date_to.value))
            
            pharmacist_activity = cursor.fetchall()
            
            # Get low stock medicines
            cursor.execute("""
                SELECT name, stock, expiry_date
                FROM medicines
                WHERE stock < 10
                ORDER BY stock ASC
                LIMIT 10
            """)
            
            low_stock = cursor.fetchall()
            
            conn.close()
            
            # Build report UI
            report_container.controls.extend([
                # Summary statistics
                ft.Text("Prescription Summary", size=24, weight="bold"),
                ft.Row([
                    create_stat_box("Total Prescriptions", total, ft.icons.RECEIPT_LONG, "primary"),
                    create_stat_box("Pending", pending, ft.icons.PENDING, "tertiary"),
                    create_stat_box("Approved", approved, ft.icons.CHECK_CIRCLE, "primary"),
                    create_stat_box("Rejected", rejected, ft.icons.CANCEL, "error"),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Top medicines
                ft.Text("Top Prescribed Medicines", size=20, weight="bold"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([
                                ft.Text("Medicine", weight="bold", expand=True),
                                ft.Text("Count", weight="bold", width=100),
                            ]),
                            ft.Divider(),
                        ] + ([
                            ft.Row([
                                ft.Text(med[0] or "Unknown", expand=True),
                                ft.Text(str(med[1]), width=100, color="primary", weight="bold"),
                            ]) for med in top_medicines
                        ] if top_medicines else [ft.Text("No data available", color="outline", italic=True)]),
                        spacing=10
                    ),
                    padding=20,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=10,
                    bgcolor="surface",
                ),
                
                ft.Container(height=20),
                
                # Pharmacist activity
                ft.Text("Pharmacist Activity", size=20, weight="bold"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([
                                ft.Text("Pharmacist", weight="bold", expand=True),
                                ft.Text("Reviews", weight="bold", width=100),
                            ]),
                            ft.Divider(),
                        ] + ([
                            ft.Row([
                                ft.Text(pharm[0] or "Unknown", expand=True),
                                ft.Text(str(pharm[1]), width=100, color="primary", weight="bold"),
                            ]) for pharm in pharmacist_activity
                        ] if pharmacist_activity else [ft.Text("No activity recorded", color="outline", italic=True)]),
                        spacing=10
                    ),
                    padding=20,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=10,
                    bgcolor="surface",
                ),
                
                ft.Container(height=20),
                
                # Low stock alert
                ft.Text("Low Stock Alert", size=20, weight="bold"),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row([
                                ft.Text("Medicine", weight="bold", expand=True),
                                ft.Text("Stock", weight="bold", width=100),
                                ft.Text("Expiry", weight="bold", width=150),
                            ]),
                            ft.Divider(),
                        ] + ([
                            ft.Row([
                                ft.Text(med[0], expand=True),
                                ft.Text(
                                    str(med[1]),
                                    width=100,
                                    color="error" if med[1] < 5 else "tertiary",
                                    weight="bold"
                                ),
                                ft.Text(med[2] or "N/A", width=150, size=12),
                            ]) for med in low_stock
                        ] if low_stock else [ft.Text("All medicines well stocked!", color="primary", italic=True)]),
                        spacing=10
                    ),
                    padding=20,
                    border=ft.border.all(1, "outlineVariant"),
                    border_radius=10,
                    bgcolor="surface",
                ),
                
                ft.Container(height=20),
                
                # Export options
                ft.Row([
                    ft.ElevatedButton(
                        "Export as PDF",
                        icon=ft.icons.PICTURE_AS_PDF,
                        bgcolor="error",
                        color="white",
                        on_click=lambda e: export_report(e, "pdf"),
                    ),
                    ft.ElevatedButton(
                        "Export as CSV",
                        icon=ft.icons.TABLE_CHART,
                        bgcolor="primary",
                        color="white",
                        on_click=lambda e: export_report(e, "csv"),
                    ),
                    ft.OutlinedButton(
                        "Print Report",
                        icon=ft.icons.PRINT,
                        on_click=lambda e: print_report(e),
                    ),
                ], spacing=10),
            ])

            e.page.update()
            show_success(e.page, f"Report generated successfully!")

        except Exception as ex:
            report_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.ERROR_OUTLINE, size=60, color="error"),
                        ft.Text("Error generating report", size=18, weight="bold"),
                        ft.Text(str(ex), size=12, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                )
            )
            show_error(e.page, "Failed to generate report")
            conn.close()
            e.page.update()
    
    def create_stat_box(title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, color=color, size=40),
                ft.Text(str(value), size=32, weight="bold", color=color),
                ft.Text(title, size=12, color="outline", text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
            expand=True,
        )
    
    def export_report(e, format):
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Exporting report as {format.upper()}..."),
            bgcolor="primary",
        )
        e.page.snack_bar.open = True
        e.page.update()
        # TODO: Implement actual export functionality
    
    def print_report(e):
        e.page.snack_bar = ft.SnackBar(
            content=ft.Text("Opening print dialog..."),
            bgcolor="primary",
        )
        e.page.snack_bar.open = True
        e.page.update()
        # TODO: Implement actual print functionality
    
    return ft.Column([
        NavigationHeader(
            "Reports & Analytics",
            "Generate reports and view pharmacy statistics",
            show_back=True,
            back_route="/dashboard"
        ),
        
        ft.Container(
            content=ft.Column([
                # Filters
                ft.Row([
                    ft.Icon(ft.icons.DATE_RANGE, color="primary", size=32),
                    ft.Text("Report Date Range", size=20, weight="bold"),
                ], spacing=10),
                
                ft.Row([
                    date_from,
                    ft.Text("to", size=16),
                    date_to,
                    ft.ElevatedButton(
                        "Generate Report",
                        icon=ft.icons.ANALYTICS,
                        bgcolor="primary",
                        color="white",
                        on_click=generate_report,
                        style=ft.ButtonStyle(
                            padding=15,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ], spacing=15),
                
                ft.Divider(height=30),
                
                # Report container
                report_container,
            ], spacing=15),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)


