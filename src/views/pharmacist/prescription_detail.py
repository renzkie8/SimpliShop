"""Detailed prescription review view - With Editable Prescription Details."""

import flet as ft
from datetime import datetime
from services.database import get_db_connection
from state.app_state import AppState
from components.navigation_header import NavigationHeader

def PrescriptionDetailView(prescription_id):
    """Detailed view for reviewing a single prescription."""
    
    # Retrieve authenticated user session
    user = AppState.get_user()
    
    # Component state definition
    is_editing = {"value": False}
    
    # Prescription data retrieval
    def get_prescription():
        conn = get_db_connection()
        cursor = conn.cursor()
        
        
        cursor.execute("""
            SELECT 
                p.id,               -- 0
                p.patient_id,       -- 1
                p.status,           -- 2
                p.notes,            -- 3
                p.created_at,       -- 4
                p.medicine_id,      -- 5
                p.dosage,           -- 6
                p.frequency,        -- 7
                p.duration,         -- 8
                p.doctor_name,      -- 9
                p.pharmacist_notes, -- 10
                p.reviewed_date,    -- 11
                u.full_name,        -- 12
                u.email,            -- 13
                u.phone,            -- 14
                m.name,             -- 15
                m.stock,            -- 16
                m.price             -- 17
            FROM prescriptions p
            LEFT JOIN users u ON p.patient_id = u.id
            LEFT JOIN medicines m ON p.medicine_id = m.id
            WHERE p.id = ?
        """, (prescription_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Map database row to dictionary struct
        return {
            'id': row[0],
            'status': row[2],
            'notes': row[3],
            'created_at': row[4],
            'dosage': row[6] if row[6] else '',
            'frequency': row[7] if row[7] else '',
            'duration': row[8] if row[8] else 0,
            'doctor_name': row[9] if row[9] else '',
            'pharmacist_notes': row[10] if row[10] else '',
            'reviewed_date': row[11],
            'patient_name': row[12] or 'Unknown',
            'patient_email': row[13] or 'N/A',
            'patient_phone': row[14] or 'N/A',
            'medicine_name': row[15] or 'Not specified',
            'medicine_stock': row[16] if row[16] is not None else 0,
            'medicine_price': row[17] if row[17] is not None else 0.0,
        }
    
    # Initialize component data state
    rx = get_prescription()
    
    # Validate data integrity
    if not rx:
        return ft.Text("Prescription not found")
    
    # Map prescription status to theme colors
    status_colors = {
        "Pending": "tertiary",
        "Approved": "primary",
        "Rejected": "error",
        "Dispensed": "secondary",
    }
    status_color = status_colors.get(rx['status'], "outline")
    
    # Editable Input Components
    medicine_field = ft.TextField(label="Medicine Name", value=rx['medicine_name'], border_color="outline")
    dosage_field = ft.TextField(label="Dosage", value=rx['dosage'], border_color="outline")
    frequency_field = ft.TextField(label="Frequency", value=rx['frequency'], border_color="outline")
    duration_field = ft.TextField(label="Duration (days)", value=str(rx['duration']), border_color="outline", keyboard_type=ft.KeyboardType.NUMBER)
    doctor_field = ft.TextField(label="Prescribed by", value=rx['doctor_name'], border_color="outline")
    
    # Input Component: Pharmacist Review Notes
    pharmacist_notes_field = ft.TextField(
        label="Pharmacist Notes (Optional)",
        multiline=True,
        min_lines=3,
        border_color="outline",
        value=rx['pharmacist_notes'] or "",
    )
    
    # Dynamic content container definition
    prescription_container = ft.Column()
    
    # Update transaction handler
    def save_prescription_details(e):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Resolve medicine reference by name
            cursor.execute("SELECT id FROM medicines WHERE name LIKE ?", (f"%{medicine_field.value}%",))
            match = cursor.fetchone()
            new_med_id = match[0] if match else None
            
            # Execute persistence update
            cursor.execute("""
                UPDATE prescriptions 
                SET medicine_id = ?, 
                    dosage = ?,
                    frequency = ?,
                    duration = ?,
                    doctor_name = ?
                WHERE id = ?
            """, (
                new_med_id,
                dosage_field.value,
                frequency_field.value,
                int(duration_field.value) if duration_field.value.isdigit() else 0,
                doctor_field.value,
                prescription_id
            ))
            
            conn.commit()
            conn.close()
            
            # Update local component state
            rx['medicine_name'] = medicine_field.value
            rx['dosage'] = dosage_field.value
            rx['frequency'] = frequency_field.value
            rx['duration'] = int(duration_field.value) if duration_field.value.isdigit() else 0
            rx['doctor_name'] = doctor_field.value
            
            # Reset interaction mode
            is_editing["value"] = False
            update_prescription_display(e)
            
            e.page.snack_bar = ft.SnackBar(content=ft.Text("Updated successfully!"), bgcolor="primary")
            e.page.snack_bar.open = True
            e.page.update()
            
        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()
    
    # Interaction mode toggle handler
    def toggle_edit_mode(e):
        is_editing["value"] = not is_editing["value"]
        update_prescription_display(e)
    
    # Render detail view components
    def update_prescription_display(e):
        medicine_stock = rx['medicine_stock']
        # Conditional stock warning logic
        stock_color = "error" if medicine_stock < 10 else "primary"
        
        if is_editing["value"]:
            # Render edit mode layout
            prescription_container.controls = [
                ft.Row([
                    ft.Icon(ft.icons.MEDICATION, color="primary", size=32),
                    ft.Column([
                        ft.Text("Medicine", size=12, color="outline"),
                        medicine_field,
                    ], spacing=2, expand=True),
                ], spacing=15),
                
                ft.Divider(height=20),
                
                ft.Row([
                    ft.Column([dosage_field], expand=True),
                    ft.Column([frequency_field], expand=True),
                    ft.Column([duration_field], expand=True),
                ], spacing=20),
                
                ft.Container(height=10),
                doctor_field,
                
                ft.Container(height=20),
                ft.Row([
                    ft.ElevatedButton("Save Changes", icon=ft.icons.SAVE, bgcolor="primary", color="white", on_click=save_prescription_details),
                    ft.OutlinedButton("Cancel", icon=ft.icons.CANCEL, on_click=toggle_edit_mode),
                ], spacing=10),
            ]
        else:
            # Render view mode layout
            prescription_container.controls = [
                ft.Row([
                    ft.Icon(ft.icons.MEDICATION, color="primary", size=32),
                    ft.Column([
                        ft.Text("Medicine", size=12, color="outline"),
                        ft.Text(rx['medicine_name'], size=20, weight="bold"),
                    ], spacing=2),
                ], spacing=15),
                
                ft.Divider(height=20),
                
                ft.Row([
                    ft.Column([
                        ft.Text("Dosage", size=12, color="outline"),
                        ft.Text(rx['dosage'] or 'N/A', size=16, weight="bold"),
                    ], expand=True),
                    ft.Column([
                        ft.Text("Frequency", size=12, color="outline"),
                        ft.Text(rx['frequency'] or 'N/A', size=16, weight="bold"),
                    ], expand=True),
                    ft.Column([
                        ft.Text("Duration", size=12, color="outline"),
                        ft.Text(f"{rx['duration']} days", size=16, weight="bold"),
                    ], expand=True),
                ], spacing=20),
                
                ft.Divider(height=20),
                
                ft.Row([
                    ft.Column([
                        ft.Text("Prescribed by", size=12, color="outline"),
                        ft.Text(rx['doctor_name'] or 'N/A', size=16, weight="bold"),
                    ], expand=True),
                    ft.Column([
                        ft.Text("Current Stock", size=12, color="outline"),
                        ft.Text(f"{medicine_stock} units", size=16, weight="bold", color=stock_color),
                    ], expand=True),
                    ft.Column([
                        ft.Text("Unit Price", size=12, color="outline"),
                        ft.Text(f"₱{rx['medicine_price']:.2f}", size=16, weight="bold"),
                    ], expand=True),
                ], spacing=20),
                
                # UI Component: Notes Display Area
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.icons.NOTE_ALT, size=20, color="tertiary"), ft.Text("Customer/Doctor Notes", weight="bold")]),
                        ft.Text(rx['notes'] or "No additional notes", italic=True),
                    ], spacing=5),
                    bgcolor=ft.colors.with_opacity(0.05, "tertiary"),
                    padding=15, border_radius=8,
                    border=ft.border.all(1, "tertiary")
                )
            ]
        
        # Trigger component repaint
        if e: e.page.update()
    
    # Workflow Handler: Approve Prescription
    def approve_prescription(e):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Execute status update transaction
            cursor.execute("""
                UPDATE prescriptions 
                SET status = 'Approved', pharmacist_id = ?, pharmacist_notes = ?, reviewed_date = ?
                WHERE id = ?
            """, (user['id'], pharmacist_notes_field.value or "", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rx['id']))
            
            conn.commit()
            conn.close()
            
            # Render success notification
            e.page.snack_bar = ft.SnackBar(content=ft.Text("Prescription Approved Successfully"), bgcolor="primary")
            e.page.snack_bar.open = True
            e.page.update()
            
            # Trigger route transition
            e.page.go("/pharmacist/prescriptions")
            
        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()

    # Workflow Handler: Reject Prescription
    def reject_prescription(e):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Execute status update transaction
            cursor.execute("""
                UPDATE prescriptions 
                SET status = 'Rejected', pharmacist_id = ?, pharmacist_notes = ?, reviewed_date = ?
                WHERE id = ?
            """, (user['id'], pharmacist_notes_field.value or "", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rx['id']))
            
            conn.commit()
            conn.close()
            
            # Show success message
            e.page.snack_bar = ft.SnackBar(content=ft.Text("Prescription Rejected Successfully"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()
            
            # Navigate back to prescriptions list
            e.page.go("/pharmacist/prescriptions")
            
        except Exception as ex:
            e.page.snack_bar = ft.SnackBar(content=ft.Text(f"Error: {str(ex)}"), bgcolor="error")
            e.page.snack_bar.open = True
            e.page.update()

    # Initial component mount render
    update_prescription_display(None)
    
    # UI Component: Summary Info Card
    def info_card(title, value, icon, color):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, color=color),
                ft.Column([
                    ft.Text(title, size=11, color="outline"),
                    ft.Text(str(value), weight="bold")
                ], spacing=2)
            ]),
            padding=15, border=ft.border.all(1, "outlineVariant"), border_radius=8, expand=True
        )

    # Main View Layout Structure
    return ft.Column([
        # Primary Navigation Header
        NavigationHeader(f"Prescription #{prescription_id}", "Review details", show_back=True, back_route="/pharmacist/prescriptions"),
        
        ft.Container(
            content=ft.Column([
                # Status Indicator Panel
                ft.Row([
                    ft.Container(
                        content=ft.Text(rx['status'], color="white", weight="bold"),
                        bgcolor=status_color, padding=ft.padding.symmetric(horizontal=20, vertical=10), border_radius=20
                    ),
                    ft.Text(f"Submitted: {rx['created_at']}", color="outline")
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Patient Identity Section
                ft.Text("Customer Information", size=20, weight="bold"),
                ft.Row([
                    info_card("Customer Name", rx['patient_name'], ft.icons.PERSON, "primary"),
                    info_card("Contact", rx['patient_email'], ft.icons.EMAIL, "secondary"),
                    info_card("Phone", rx['patient_phone'], ft.icons.PHONE, "tertiary"),
                ], spacing=15),
                
                ft.Container(height=20),
                
                # Prescription Specification Header
                ft.Row([
                    ft.Text("Prescription Details", size=20, weight="bold", expand=True),
                    # Contextual action visibility
                    ft.IconButton(icon=ft.icons.EDIT, tooltip="Edit Details", on_click=toggle_edit_mode, visible=rx['status']=='Pending')
                ]),
                
                # Dynamic component mounting area
                ft.Container(
                    content=prescription_container,
                    padding=20, border=ft.border.all(1, "outlineVariant"), border_radius=10, bgcolor="surface"
                ),
                
                ft.Container(height=20),
                
                # Processing Workflow Actions
                ft.Container(
                    content=ft.Column([
                        ft.Text("Pharmacist Review", size=20, weight="bold"),
                        pharmacist_notes_field,
                        ft.Container(height=10),
                        ft.Row([
                            ft.ElevatedButton("Approve Prescription", icon=ft.icons.CHECK_CIRCLE, bgcolor="primary", color="white", on_click=approve_prescription),
                            ft.ElevatedButton("Reject Prescription", icon=ft.icons.CANCEL, bgcolor="error", color="white", on_click=reject_prescription),
                            ft.OutlinedButton("Cancel", icon=ft.icons.ARROW_BACK, on_click=lambda e: e.page.go("/pharmacist/prescriptions"))
                        ], spacing=10)
                    ]),
                    visible=rx['status'] == 'Pending'
                ) if rx['status'] == 'Pending' else ft.Container(
                    # Render final state summary
                    content=ft.Column([
                        ft.Icon(ft.icons.INFO, size=40, color="outline"),
                        ft.Text(f"This prescription is {rx['status']}", size=16, color="outline")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=30, alignment=ft.alignment.CENTER
                )
                
            ]),
            padding=20
        )
    ], scroll=ft.ScrollMode.AUTO, spacing=0)


