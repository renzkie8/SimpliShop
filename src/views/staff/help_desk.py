"""Help desk / FAQ for staff members."""

import flet as ft
from components.navigation_header import NavigationHeader
from state.app_state import AppState

def HelpDeskView():
    """Staff help desk with FAQs and quick guides."""
    
    user = AppState.get_user()
    
    # Interface Components
    
    # Expandable FAQ element
    def create_faq(question, answer):
        return ft.Container(
            content=ft.ExpansionTile(
                title=ft.Text(question, weight="bold", size=14),
                controls=[
                    ft.Container(
                        content=ft.Text(answer, size=13, color="onSurfaceVariant"),
                        padding=15,
                    )
                ],
                collapsed_text_color="onSurface",
                text_color="primary",
            ),
            bgcolor="surface",
            border_radius=8,
            border=ft.border.all(1, "outlineVariant"),
            margin=ft.margin.only(bottom=5)
        )
    
    # Instruction card element
    def create_guide_card(title, steps):
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=16, weight="bold", color="primary"),
                ft.Divider(height=10, color="transparent"),
                # Enumerate steps algorithmically
                *[ft.Row([
                    ft.Container(
                        content=ft.Text(str(i+1), size=10, color="white", weight="bold"),
                        bgcolor="secondary", width=20, height=20, border_radius=10, alignment=ft.alignment.CENTER
                    ),
                    ft.Text(step, size=13, expand=True)
                ], vertical_alignment=ft.CrossAxisAlignment.START) for i, step in enumerate(steps)]
            ], spacing=8),
            padding=20,
            bgcolor="surface",
            border_radius=12,
            border=ft.border.all(1, "outlineVariant"),
            expand=True, # Makes cards same height
        )
    
    # Contact information element
    def create_contact_card(role, email, ext):
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.icons.SUPPORT_AGENT, size=30, color="primary"),
                ft.Text(role, weight="bold", size=14),
                ft.Text(email, size=12, color="outline"),
                ft.Text(f"Ext: {ext}", size=12, weight="bold", color="secondary"),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor="surface",
            border_radius=12,
            border=ft.border.all(1, "outlineVariant"),
            expand=True,
        )

    # View Structure
    return ft.Column([
        NavigationHeader("Help Desk", "Guides and Support", show_back=False),
        
        ft.Container(
            padding=20,
            content=ft.Column([
                
                # 1. Guides Section (Grid-like)
                ft.Text("Quick Guides", size=20, weight="bold"),
                ft.Row([
                    create_guide_card("How to Search", [
                        "Click 'Find Customer' on sidebar",
                        "Type name/phone",
                        "Click Search button"
                    ]),
                    create_guide_card("Customer Records", [
                        "You have Read-Only access",
                        "Cannot edit details",
                        "Report errors to Admin"
                    ]),
                    create_guide_card("Assisting", [
                        "Verify ID first",
                        "Direct medical Qs to Pharmacist",
                        "Be polite!"
                    ]),
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
                
                ft.Container(height=30),
                
                # 2. FAQs Section
                ft.Text("Frequently Asked Questions", size=20, weight="bold"),
                ft.Column([
                    create_faq("Can I edit customer info?", "No. Staff access is read-only. Contact an Admin to make changes."),
                    create_faq("How do I report a bug?", "Take a screenshot and email IT Support immediately."),
                    create_faq("System is slow?", "Try refreshing the page by going on dashboard."),
                    create_faq("Forgot Password?", "Ask the System Admin to reset your credentials or go to My profile in you dashboard."),
                ]),
                
                ft.Container(height=30),
                
                # 3. Contact Support Section
                ft.Text("Need More Help?", size=20, weight="bold"),
                ft.Row([
                    create_contact_card("System Admin", "admin@pharmacy.com","ext"),
                    create_contact_card("Head Pharmacist", "pharm@pharmacy.com","ext"),
                    create_contact_card("Staff Support", "support@pharmacy.com","ext"),
                ]),
                
                ft.Container(height=20),
                
                # Footer info
                ft.Container(
                    content=ft.Text("Kaputt Kommandos PMS v1.0", size=11, color="outline"),
                    alignment=ft.alignment.CENTER
                )
            ])
        )
    ], scroll=ft.ScrollMode.AUTO, spacing=0)


