"""Prescriptions list and management with real database."""

import flet as ft
from datetime import datetime
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def PrescriptionsView():
    """List all prescriptions with filters."""
    
    # Container for prescription item components
    prescriptions_container = ft.Column(spacing=10)
    
    # Filtering Components
    # Status selection dropdown
    status_filter = ft.Dropdown(
        label="Status",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Pending"),
            ft.dropdown.Option("Approved"),
            ft.dropdown.Option("Rejected"),
            ft.dropdown.Option("Dispensed"),
        ],
        value="All",
        width=150,
        border_color="primary",
    )
    
    # Search input configuration
    search_field = ft.TextField(
        hint_text="Search by customer name or prescription ID...",
        prefix_icon=ft.icons.SEARCH,
        border_color="primary",
        expand=True,
    )
    
    # Data Retrieval Logic
    def get_prescriptions_from_db(status_val="All", search_query=""):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Base query
        query = """
            SELECT p.id, p.status, p.created_at, p.dosage, p.frequency, p.duration,
                   p.notes, p.pharmacist_notes, p.reviewed_date,
                   u.full_name as patient_name, u.id as patient_id,
                   m.name as medicine_name
            FROM prescriptions p
            LEFT JOIN users u ON p.patient_id = u.id
            LEFT JOIN medicines m ON p.medicine_id = m.id
            WHERE 1=1
        """
        
        params = []
        
        # Apply status filter constraint
        if status_val != "All":
            query += " AND p.status = ?"
            params.append(status_val)
        
        # Apply text search constraint
        if search_query:
            query += " AND (u.full_name LIKE ? OR p.id LIKE ?)"
            params.append(f"%{search_query}%")
            params.append(f"%{search_query}%")
        
        # Apply chronological sort
        query += " ORDER BY p.created_at DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        # Map database rows to dictionaries
        prescriptions = []
        for row in results:
            prescriptions.append({
                'id': row[0],
                'status': row[1],
                'created_at': row[2],
                'dosage': row[3],
                'frequency': row[4],
                'duration': row[5],
                'notes': row[6],
                'pharmacist_notes': row[7],
                'reviewed_date': row[8],
                'patient_name': row[9],
                'patient_id': row[10],
                'medicine': row[11],
            })
        
        return prescriptions
    
    # UI Component: Prescription Card
    def create_prescription_card(rx):
        # Status color mappings
        status_colors = {
            "Pending": "tertiary",
            "Approved": "primary",
            "Rejected": "error",
            "Dispensed": "secondary",
        }
        
        status_color = status_colors.get(rx['status'], "outline")
        
        return ft.Container(
            content=ft.Column([
                # Header and Status Panel
                ft.Row([
                    ft.Column([
                        ft.Text(f"Prescription #{rx['id']}", size=16, weight="bold"),
                        ft.Text(f"Customer: {rx['patient_name']} (ID: {rx['patient_id']})", 
                               size=13, color="outline"),
                    ], spacing=2, expand=True),
                    ft.Container(
                        content=ft.Text(
                            rx['status'],
                            size=12,
                            weight="bold",
                            color="white",
                        ),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=10),
                
                # Medicine Details Panel
                ft.Row([
                    ft.Column([
                        ft.Text("Medicine:", size=11, color="outline"),
                        ft.Text(rx['medicine'], size=13, weight="bold"),
                    ], spacing=2),
                    ft.VerticalDivider(width=20),
                    ft.Column([
                        ft.Text("Dosage:", size=11, color="outline"),
                        ft.Text(rx['dosage'], size=13),
                    ], spacing=2),
                    ft.VerticalDivider(width=20),
                    ft.Column([
                        ft.Text("Duration:", size=11, color="outline"),
                        ft.Text(f"{rx['duration']} days", size=13),
                    ], spacing=2),
                ], spacing=10, wrap=True),
                
                ft.Container(height=5),
                
                # Submission Timestamp
                ft.Row([
                    ft.Icon(ft.icons.ACCESS_TIME, size=14, color="outline"),
                    ft.Text(f"Submitted: {rx['created_at']}", size=12, color="outline"),
                ], spacing=5),
                
                # Review Notes Area
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.NOTE, size=16, color="tertiary"),
                        ft.Text(rx['notes'], size=12, italic=True),
                    ], spacing=5),
                    visible=bool(rx.get('notes')),
                    bgcolor=ft.colors.with_opacity(0.1, "tertiary"),
                    padding=8,
                    border_radius=5,
                ),
                
                # Workflow Actions Panel
                ft.Row([
                    ft.ElevatedButton(
                        "Review Details",
                        icon=ft.icons.VISIBILITY,
                        bgcolor="primary",
                        color="onPrimary",
                        on_click=lambda e, rx_id=rx['id']: e.page.go(f"/pharmacist/prescription/{rx_id}"),
                    ),
                    ft.OutlinedButton(
                        "Quick Approve",
                        icon=ft.icons.CHECK_CIRCLE,
                        disabled=rx['status'] != "Pending",
                        on_click=lambda e, rx_id=rx['id']: quick_approve(e, rx_id),
                    ),
                    ft.OutlinedButton(
                        "Quick Reject",
                        icon=ft.icons.CANCEL,
                        disabled=rx['status'] != "Pending",
                        on_click=lambda e, rx_id=rx['id']: quick_reject(e, rx_id),
                    ),
                ], spacing=10, wrap=True),
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, "outlineVariant"),
            border_radius=10,
            bgcolor="surface",
        )
    
    # Action Handlers
    def quick_approve(e, rx_id):
        user = AppState.get_user()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE prescriptions 
                SET status = 'Approved',
                    pharmacist_id = ?,
                    reviewed_date = ?
                WHERE id = ?
            """, (user['id'], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rx_id))
            
            cursor.execute("""
                INSERT INTO activity_log (user_id, action, details, timestamp)
                VALUES (?, ?, ?, ?)
            """, (
                user['id'],
                'prescription_approved',
                f"Quick approved prescription #{rx_id}",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            e.page.snack_bar = ft.SnackBar(content=ft.Text(f"Prescription #{rx_id} approved!"), bgcolor="primary")
            e.page.snack_bar.open = True
            
        except Exception as ex:
            conn.rollback()
            e.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="error")
            e.page.snack_bar.open = True
        
        finally:
            conn.close()
            load_prescriptions(e)
    
    def quick_reject(e, rx_id):
        e.page.go(f"/pharmacist/prescription/{rx_id}")
    
    # Data Loading Logic
    def load_prescriptions(e=None):
        prescriptions_container.controls.clear()
        
        status = status_filter.value
        query = search_field.value if search_field.value else ""
        
        all_prescriptions = get_prescriptions_from_db(status, query)
        
        if all_prescriptions:
            prescriptions_container.controls.append(
                ft.Text(f"Showing {len(all_prescriptions)} prescription(s)", 
                       size=14, color="outline", weight="bold")
            )
            for rx in all_prescriptions:
                prescriptions_container.controls.append(create_prescription_card(rx))
        else:
            # Render Empty State
            prescriptions_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SEARCH_OFF, size=80, color="outline"),
                        ft.Text("No prescriptions found", size=18, color="outline"),
                        ft.Text("Try adjusting your filters", size=14, color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.CENTER,
                )
            )
        
        if e and hasattr(e, 'page'):
            e.page.update()
    
    # Initial Render
    class FakePage:
        snack_bar = None
        def update(self): pass
        def go(self, route): pass
    
    load_prescriptions(type('Event', (), {'page': FakePage()})())
    
    # Main View Assembly
    return ft.Column([
        NavigationHeader(
            "Prescription Management",
            "Review, approve, or reject customer prescriptions",
            show_back=False,
        ),
        
        ft.Container(
            content=ft.Column([
                # Filters Area
                ft.Row([
                    search_field,
                    status_filter,
                    ft.ElevatedButton(
                        "Filter",
                        icon=ft.icons.FILTER_ALT,
                        bgcolor="primary",
                        color="onPrimary",
                        on_click=load_prescriptions,
                    ),
                ], spacing=10),
                
                ft.Container(height=20),
                
                # Active List
                prescriptions_container,
            ], spacing=0),
            padding=20,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)


