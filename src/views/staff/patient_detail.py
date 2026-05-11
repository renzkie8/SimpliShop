"""Patient detail view for staff (read-only)."""

import flet as ft
from services.database import get_db_connection
from components.navigation_header import NavigationHeader

def StaffPatientDetail(patient_id, source="search"):
    """Display detailed patient information (read-only)."""
    
    # Retrieve target patient demographic data
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ? AND role = 'Patient'", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    
    # Determine back route based on source
    back_route = "/staff/patients" if source == "all" else "/staff/search"
    back_title = "All Customers" if source == "all" else "Customer Search"
    
    # Handle case where patient not found
    if not row:
        return ft.Column([
            NavigationHeader("Error", show_back=True, back_route=back_route),
            ft.Text("Customer not found", color="error")
        ])
    
    # Convert tuple to dictionary
    patient = {
        'id': row[0], 'full_name': row[4], 'email': row[6],
        'phone': row[7], 'dob': row[8], 'address': row[9],
        'created_at': row[10]
    }
    
    # Information tile component
    def info_tile(label, value, icon):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color="secondary", size=20),
                ft.Column([
                    ft.Text(label, size=11, color="outline"),
                    ft.Text(value or "N/A", size=14, weight="bold"),
                ])
            ]),
            padding=15,
            bgcolor="surface",
            border_radius=8,
            border=ft.border.all(1, "outlineVariant"),
            expand=True # Ensures they fill the width evenly
        )
    
    # --- LAYOUT ---
    return ft.Column([
        # Dynamic back route based on where user came from
        NavigationHeader(
            f"Customer: {patient['full_name']}", 
            "View Details (Read-Only)", 
            show_back=True, 
            back_route=back_route
        ),
        
        ft.Container(
            padding=20,
            content=ft.Column([
                # Render patient contextual header
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.ACCOUNT_CIRCLE, size=80, color="primary"),
                        ft.Column([
                            ft.Text(patient['full_name'], size=24, weight="bold"),
                            ft.Text(f"ID: {patient['id']}", size=14, color="outline"),
                            ft.Container(
                                content=ft.Text("Customer", color="white", size=10, weight="bold"),
                                bgcolor="primary", padding=5, border_radius=5
                            )
                        ], spacing=2)
                    ], spacing=20),
                    padding=20,
                    bgcolor="surface",
                    border_radius=12,
                    border=ft.border.all(1, "outlineVariant")
                ),
                
                ft.Container(height=20),
                
                # Contact Info Row
                ft.Text("Contact Info", size=18, weight="bold"),
                ft.Row([
                    info_tile("Email Address", patient['email'], ft.icons.EMAIL),
                    info_tile("Phone Number", patient['phone'], ft.icons.PHONE),
                ]),
                
                ft.Container(height=10),
                
                # Personal Info Row
                ft.Text("Personal Details", size=18, weight="bold"),
                ft.Row([
                    info_tile("Date of Birth", patient['dob'], ft.icons.CAKE),
                    info_tile("Home Address", patient['address'], ft.icons.HOME),
                ]),
                
                ft.Container(height=30),
                
                # Display read-only restriction
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.icons.LOCK, color="white"),
                        ft.Text("You are viewing this record in Read-Only mode.", color="white")
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor="grey",
                    padding=10,
                    border_radius=8
                )
            ])
        )
    ], scroll=ft.ScrollMode.AUTO, spacing=0)




