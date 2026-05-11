"""Enhanced patient search with detailed results."""

import flet as ft
from services.database import get_db_connection
from components.navigation_header import NavigationHeader
from utils.notifications import show_success, show_error, SEARCH_NO_RESULTS, SEARCH_ERROR

def StaffPatientSearch():
    """Search for patient records with detailed information."""
    
    # Dynamic container for search results
    results_container = ft.Column(spacing=15)
    
    # Target search phrase input
    search_field = ft.TextField(
        label="Search Customer",
        hint_text="Enter name or phone number...",
        prefix_icon=ft.icons.SEARCH,
        # Visual adjustments for layout consistency
        border_color="primary",
        expand=True,
        autofocus=True,
        text_size=14,
    )
    
    # Profile Card Component
    # Render visual card for patient record
    def create_patient_card(patient):
        return ft.Container(
            content=ft.Column([
                # Top part: Avatar and Name
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.icons.PERSON, size=30, color="onPrimaryContainer"),
                        width=60, height=60,
                        bgcolor="primaryContainer",
                        border_radius=30,
                        alignment=ft.alignment.CENTER,
                    ),
                    ft.Column([
                        ft.Text(patient['full_name'], size=18, weight="bold"),
                        ft.Text(f"ID: {patient['id']}", size=12, color="outline"),
                        # Role indicator
                        ft.Container(
                            content=ft.Text("Customer", size=10, weight="bold", color="white"),
                            bgcolor="primary",
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            border_radius=5,
                        )
                    ], spacing=2, expand=True),
                    
                    # Action indicator: View Details
                    ft.IconButton(
                        icon=ft.icons.ARROW_FORWARD,
                        icon_color="primary",
                        on_click=lambda e, pid=patient['id']: e.page.go(f"/staff/patient/{pid}"),
                        tooltip="Open Record"
                    )
                ], spacing=15),
                
                ft.Divider(height=20, color="outlineVariant"),
                
                # Contact and contextual details
                ft.Row([
                    ft.Column([
                        ft.Row([ft.Icon(ft.icons.PHONE, size=16, color="outline"), ft.Text(patient['phone'] or "N/A", size=13)], spacing=8),
                        ft.Row([ft.Icon(ft.icons.EMAIL, size=16, color="outline"), ft.Text(patient['email'] or "N/A", size=13)], spacing=8),
                    ]),
                    ft.Column([
                        ft.Row([ft.Icon(ft.icons.CALENDAR_TODAY, size=16, color="outline"), ft.Text(f"Reg: {patient['created_at'][:10]}", size=13)], spacing=8),
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
            ], spacing=5),
            padding=20,
            border_radius=12,
            bgcolor="surface", # Adapts to theme
            border=ft.border.all(1, "outlineVariant"),
            shadow=ft.BoxShadow(blur_radius=5, color=ft.colors.with_opacity(0.05, "black"))
        )
    
    # Search Query Execution
    def perform_search(e):
        # Clear previous results first
        results_container.controls.clear()
        term = search_field.value

        # Prompt when search term missing
        if not term:
            results_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.SEARCH, size=50, color="outline"),
                        ft.Text("Enter a name or phone number", color="outline"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    alignment=ft.alignment.CENTER,
                    padding=50
                )
            )
            e.page.update()
            return

        # Search the database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Execute parameterized fuzzy search
            cursor.execute("""
                SELECT * FROM users
                WHERE role = 'Patient'
                AND (LOWER(full_name) LIKE ? OR phone LIKE ?)
                ORDER BY full_name ASC
            """, (f'%{term.lower()}%', f'%{term}%'))
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                # Empty result state
                results_container.controls.append(
                    ft.Container(
                        content=ft.Text("No customers found.", size=16, color="error"),
                        alignment=ft.alignment.CENTER,
                        padding=20
                    )
                )
                show_error(e.page, SEARCH_NO_RESULTS.format(term), duration=2)
            else:
                # Result metrics
                results_container.controls.append(ft.Text(f"Found {len(rows)} results:", weight="bold"))
                # Populate result container
                for row in rows:
                    # Convert tuple to dictionary
                    p = {
                        'id': row[0], 'username': row[1], 'full_name': row[4],
                        'email': row[6], 'phone': row[7], 'created_at': row[10] or "N/A"
                    }
                    results_container.controls.append(create_patient_card(p))
                show_success(e.page, f"Found {len(rows)} customer(s).", duration=2)
        except Exception as ex:
            show_error(e.page, SEARCH_ERROR)
            results_container.controls.append(
                ft.Container(
                    content=ft.Text("Error during search. Please try again.", size=14, color="error"),
                    alignment=ft.alignment.CENTER,
                    padding=20
                )
            )

        e.page.update()
    
    # Overall View Construct
    return ft.Column([
        NavigationHeader("Customer Search", "Find customer records quickly", show_back=False),
        
        ft.Container(
            padding=20,
            content=ft.Column([
                # Search Bar Row
                ft.Row([
                    search_field,
                    ft.ElevatedButton(
                        "Search", 
                        icon=ft.icons.SEARCH, 
                        height=50, 
                        bgcolor="primary", 
                        color="onPrimary",
                        on_click=perform_search
                    )
                ]),
                
                ft.Container(height=10),
                
                # The Results area
                results_container
            ])
        )
    ], 
    scroll=ft.ScrollMode.AUTO, 
    spacing=0,
    # Vertical alignment enforcement
    alignment=ft.MainAxisAlignment.START,
    expand=True
    )


