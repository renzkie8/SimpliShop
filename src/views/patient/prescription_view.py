"""Patient prescriptions view with enhanced submission form."""

import flet as ft
from state.app_state import AppState
from services.database import get_db_connection
from datetime import datetime
from utils.notifications import show_success, show_error

def PatientPrescriptionsView():
    """View patient's own prescriptions and submit new ones."""
    
    # Authenticate user session
    user = AppState.get_user()
    
    # Connect to active database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query existing prescriptions
    cursor.execute("""
        SELECT id, status, notes, created_at 
        FROM prescriptions 
        WHERE patient_id = ? 
        ORDER BY created_at DESC
    """, (user['id'],))
    
    prescriptions = cursor.fetchall()
    conn.close()
    
    # Render prescription card component
    def create_prescription_card(rx):
        # Define colors for different statuses
        status_colors = {
            "Pending": ("tertiary", ft.icons.PENDING_ACTIONS),
            "Approved": ("primary", ft.icons.CHECK_CIRCLE),
            "Rejected": ("error", ft.icons.CANCEL),
        }
        
        # Get the color and icon based on status, default to gray if unknown
        color, icon = status_colors.get(rx['status'], ("outline", ft.icons.INFO))
        
        # Return the UI container
        return ft.Container(
            content=ft.Column([
                # Top row with ID and Date
                ft.Row([
                    ft.Column([
                        ft.Text(f"Prescription #{rx['id']}", size=16, weight="bold"),
                        # Slice the date string to remove seconds/decimals
                        ft.Text(f"Submitted: {rx['created_at'][:16] if rx['created_at'] else 'N/A'}", 
                               size=12, color="outline"),
                    ], expand=True),
                    
                    # The status badge on the right
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(icon, size=16, color=color),
                            ft.Text(rx['status'], weight="bold", color=color),
                        ], spacing=5),
                        bgcolor=ft.colors.with_opacity(0.1, color),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        border_radius=15,
                    ),
                ]),
                
                # If there are notes (like rejection reasons), show them
                ft.Divider(height=10) if rx['notes'] else ft.Container(),
                ft.Text(rx['notes'], size=13, italic=True) if rx['notes'] else ft.Container(),
            ], spacing=8),
            padding=15,
            border=ft.border.all(1, color),
            border_radius=8,
            bgcolor=ft.colors.with_opacity(0.05, color),
        )
    
    # New Prescription Form
    def submit_prescription_dialog(e):
        
        # Fetch active inventory
        conn_med = get_db_connection()
        cursor_med = conn_med.cursor()
        cursor_med.execute("SELECT id, name FROM medicines WHERE stock > 0 ORDER BY name")
        available_medicines = cursor_med.fetchall()
        conn_med.close()
        
        # Fetch active medical staff
        conn_doc = get_db_connection()
        cursor_doc = conn_doc.cursor()
        cursor_doc.execute("SELECT id, full_name FROM users WHERE role IN ('Pharmacist', 'Doctor', 'Staff') ORDER BY full_name")
        available_doctors = cursor_doc.fetchall()
        conn_doc.close()
        
        # Form input generator
        def create_input(label, multiline=False, keyboard_type=None):
            return ft.TextField(
                label=label,
                multiline=multiline,
                width=None,
                expand=True,
                border_color="outline",
                text_size=14,
                keyboard_type=keyboard_type if keyboard_type else None,
            )

        # Doctor dropdown - pre-selected with current user if they're a doctor
        doctor_dropdown = ft.Dropdown(
            label="Doctor's Name *",
            expand=True,
            border_color="outline",
            options=[ft.dropdown.Option(str(doc[0]), doc[1]) for doc in available_doctors],
        )
        
        # Medicine dropdown - showing only available medicines with stock
        medicine_dropdown = ft.Dropdown(
            label="Medicine Prescribed *",
            expand=True,
            border_color="outline",
            options=[ft.dropdown.Option(str(med[0]), med[1]) for med in available_medicines],
        )
        
        dosage = create_input("Dosage (e.g., 500mg, 1 tablet) *")
        frequency = create_input("Frequency (e.g., Once daily) *")
        # Ensure duration is a number for the database
        duration = create_input("Duration (in days) *", keyboard_type=ft.KeyboardType.NUMBER)
        additional_notes = create_input("Additional Notes", multiline=True)
        
        # Error feedback node
        error_text = ft.Text("", color="error", size=12)
        
        # Submission execution handler
        def save_prescription(dialog_e):
            # Validate required fields
            if not all([doctor_dropdown.value, medicine_dropdown.value, dosage.value, frequency.value, duration.value]):
                error_text.value = "Please fill in all required fields!"
                show_error(dialog_e.control.page, "Please fill in all required fields!")
                dialog_e.control.page.update()
                return

            # Enforce numerical bounds
            try:
                duration_days = int(duration.value)
            except:
                error_text.value = "Duration must be a number (days)"
                show_error(dialog_e.control.page, "Duration must be a number!")
                dialog_e.control.page.update()
                return
            
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Map selected physician
                doctor_id = int(doctor_dropdown.value)
                cursor.execute("SELECT full_name FROM users WHERE id = ?", (doctor_id,))
                doctor_result = cursor.fetchone()
                doctor_name = doctor_result[0] if doctor_result else "Unknown Doctor"
                
                # Get the selected medicine ID from dropdown
                medicine_id = int(medicine_dropdown.value)
                
                # Get medicine name for notes
                cursor.execute("SELECT name FROM medicines WHERE id = ?", (medicine_id,))
                medicine_result = cursor.fetchone()
                medicine_name = medicine_result[0] if medicine_result else "Unknown Medicine"
                
                # Construct legacy annotation string
                notes_text = f"Doctor: {doctor_name}\nMedicine: {medicine_name}\nDosage: {dosage.value}\nFrequency: {frequency.value}\nDuration: {duration_days} days\nNotes: {additional_notes.value or 'None'}"
                
                # Write structured fields
                # Ensure dimensional parameters correctly route to respective independent schema columns
                cursor.execute("""
                    INSERT INTO prescriptions 
                    (patient_id, medicine_id, status, notes, created_at, dosage, frequency, duration, doctor_name)
                    VALUES (?, ?, 'Pending', ?, ?, ?, ?, ?, ?)
                """, (
                    user['id'], 
                    medicine_id, # This links to the stock!
                    notes_text, 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    dosage.value,
                    frequency.value,
                    duration_days,
                    doctor_name
                ))
                
                conn.commit()
                conn.close()

                # Dismiss modal dialog
                dialog_e.control.page.close(prescription_form)

                # Trigger confirmation toast
                show_success(dialog_e.control.page, "Prescription submitted! Waiting for review.")

                # Execute navigation reset
                dialog_e.control.page.go("/patient/prescriptions")
                
            except Exception as ex:
                # Handle execution failure
                error_text.value = f"Error: {str(ex)}"
                show_error(dialog_e.control.page, "Failed to submit prescription")
                dialog_e.control.page.update()

        # View Structure Modal
        prescription_form = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.icons.MEDICAL_SERVICES, color="primary"), 
                ft.Text("New Prescription")
            ]),
            bgcolor="surface", 
            shape=ft.RoundedRectangleBorder(radius=12),
            content=ft.Container(
                width=500,
                padding=10,
                content=ft.Column([
                    ft.Text("Enter details from your doctor's prescription:", size=13, color="outline"),
                    doctor_dropdown,
                    medicine_dropdown,
                    dosage,
                    frequency,
                    duration,
                    ft.Text("✓ Only medicines with available stock are shown", 
                           size=11, color="outline", italic=True),
                    additional_notes,
                    error_text,
                ], scroll=ft.ScrollMode.AUTO, tight=True)
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: e.page.close(prescription_form)),
                ft.ElevatedButton(
                    "Submit", 
                    icon=ft.icons.SEND, 
                    bgcolor="primary", 
                    color="white", 
                    on_click=save_prescription
                ),
            ],
            actions_padding=20,
        )
        
        # Reveal modal layer
        e.page.open(prescription_form)

    # Render Primary Screen
    return ft.Column([
        # The top header section
        ft.Row([
            ft.Icon(ft.icons.MEDICAL_SERVICES, color="primary", size=32),
            ft.Column([
                ft.Text("My Prescriptions", size=28, weight="bold"),
                ft.Text("Submit prescription requests and track their status", size=14, color="outline"),
            ], spacing=5, expand=True),
            
            # The big button to add a prescription
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.icons.ADD, color="white"),
                    ft.Text("Submit Prescription", color="white"),
                ], spacing=8),
                bgcolor="primary",
                style=ft.ButtonStyle(padding=15, shape=ft.RoundedRectangleBorder(radius=8)),
                on_click=submit_prescription_dialog, 
            ),
        ], spacing=15),
        
        ft.Container(height=20),
        
        # Instructions / Info box
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.icons.INFO_OUTLINE, color="primary", size=20),
                    ft.Text("How it works:", size=14, weight="bold"),
                ]),
                ft.Text("1. Fill in prescription details from your doctor", size=13),
                ft.Text("2. Pharmacist will review and approve/reject", size=13),
                ft.Text("3. Once approved, you can order the medicine", size=13),
            ], spacing=8),
            padding=15,
            bgcolor=ft.colors.with_opacity(0.1, "primary"),
            border_radius=8,
            border=ft.border.all(1, "primary"),
        ),
        
        ft.Container(height=20),
        
        # Title for the list
        ft.Text(f"Your Prescriptions ({len(prescriptions)})", size=20, weight="bold"),
        ft.Container(height=10),
        
        # The list of cards OR an empty state message
        ft.Column([
            create_prescription_card(rx) for rx in prescriptions
        ], spacing=10) if prescriptions else ft.Container(
            content=ft.Column([
        ft.Icon(ft.icons.DESCRIPTION_OUTLINED, size=100, color="outline"),
        ft.Container(height=20),
        ft.Text("No prescriptions yet", size=20, weight="bold", color="outline"),
        ft.Container(height=10),
        ft.Text("To get started, click the 'Submit Prescription' button above", 
               size=14, color="outline", text_align=ft.TextAlign.CENTER),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
    padding=80,
    alignment=ft.alignment.center,
        ),
    ], scroll=ft.ScrollMode.AUTO, spacing=0)




