"""View all patients list for staff members."""

import flet as ft
from services.database import get_db_connection
from components.navigation_header import NavigationHeader
from utils.notifications import show_success, show_info

def AllPatientsView():
    """Display all registered patients."""
    
    patients_container = ft.Column(spacing=10)
    
    # Filter controls
    # Configure visibility for dark mode
    sort_dropdown = ft.Dropdown(
        label="Sort By",
        options=[
            ft.dropdown.Option("name_asc", "Name (A-Z)"),
            ft.dropdown.Option("name_desc", "Name (Z-A)"),
            ft.dropdown.Option("newest", "Newest First"),
        ],
        value="name_asc",
        width=200,
        border_color="primary", 
    )
    
    # Quick filter
    # Configure visibility for dark mode
    search_field = ft.TextField(
        hint_text="Quick filter by name...",
        prefix_icon=ft.icons.FILTER_LIST,
        expand=True,
        border_color="primary",
    )
    
    # Row Element Builder
    def create_patient_row(patient, index):
        return ft.Container(
            content=ft.Row([
                # Number
                ft.Text(f"#{index + 1}", weight="bold", width=40, color="primary"),
                
                # Avatar
                ft.Container(
                    content=ft.Icon(ft.icons.PERSON, size=20, color="onSecondaryContainer"),
                    bgcolor="secondaryContainer", width=40, height=40, border_radius=20,
                    alignment=ft.alignment.center
                ),
                
                # Name & ID
                ft.Column([
                    ft.Text(patient['full_name'], weight="bold", size=14),
                    ft.Text(f"ID: {patient['id']}", size=11, color="outline"),
                ], width=200),
                
                # Contact
                ft.Column([
                    ft.Text(patient['email'] or "-", size=12),
                    ft.Text(patient['phone'] or "-", size=12, color="outline"),
                ], expand=True),
                
                # View Details Button
                ft.IconButton(
                    icon=ft.icons.VISIBILITY,
                    tooltip="View Details",
                    icon_color="primary",
                    # Append '/all' to origin route for state recovery
                    on_click=lambda e, pid=patient['id']: e.page.go(f"/staff/patient/{pid}/all")
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            bgcolor="surface",
            border_radius=8,
            border=ft.border.all(1, "outlineVariant"),
        )
    
    # Data Retrieval and Processing
    def load_patients(e=None):
        patients_container.controls.clear()

        # Get inputs
        txt = search_field.value.lower() if search_field.value else ""
        sort = sort_dropdown.value

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query
        sql = "SELECT * FROM users WHERE role = 'Patient'"

        if txt:
            sql += f" AND LOWER(full_name) LIKE '%{txt}%'"

        if sort == "name_asc": sql += " ORDER BY full_name ASC"
        elif sort == "name_desc": sql += " ORDER BY full_name DESC"
        elif sort == "newest": sql += " ORDER BY created_at DESC"

        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        if rows:
            patients_container.controls.append(ft.Text(f"Total: {len(rows)} customers", color="outline"))
            for idx, row in enumerate(rows):
                p = {
                    'id': row[0], 'full_name': row[4],
                    'email': row[6], 'phone': row[7]
                }
                patients_container.controls.append(create_patient_row(p, idx))
            if e:
                show_info(e.page, f"Loaded {len(rows)} customer(s).", duration=2)
        else:
            patients_container.controls.append(
                ft.Container(
                    content=ft.Text("No customers found matching filter.", color="outline"),
                    alignment=ft.alignment.center,
                    padding=20
                )
            )

        if e: e.page.update()
        
    # Initialize component state
    class Dummy: 
        page = None
    load_patients(None)
    
    # Interface Layout Configuration
    return ft.Column([
        NavigationHeader("All Customers", "Full directory of registered customers", show_back=False),
        
        ft.Container(
            padding=20,
            content=ft.Column([
                # Filter Bar Row
                ft.Row([
                    search_field,
                    sort_dropdown,
                    # Implement explicit filtering action
                    ft.ElevatedButton(
                        "Apply Filter", 
                        on_click=load_patients, 
                        height=50, # Matches height of text fields
                        bgcolor="primary", 
                        color="onPrimary"
                    ),
                ]),
                
                ft.Divider(),
                
                # List
                patients_container
            ])
        )
    ], 
    scroll=ft.ScrollMode.AUTO, 
    spacing=0,
    # Ensure element alignment begins from top
    alignment=ft.MainAxisAlignment.START,
    expand=True
    )




