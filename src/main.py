import flet as ft
from services.database import init_db
from services.google_auth import start_callback_server
from state.app_state import AppState
import ctypes

# Core Layout Components
from views.landing_page import LandingPage
from components.app_layout import AppLayout

# Role-Based Views
from views.patient.patient_dashboard import PatientDashboard
from views.patient.medicine_search import MedicineSearch
from views.patient.cart_view import CartView
from views.patient.orders_view import OrdersView
from views.patient.profile_view import ProfileView
from views.patient.prescription_view import PatientPrescriptionsView
from views.patient.invoices_view import PatientInvoicesView
from views.patient.pos_receipt import POSReceiptView

from views.admin.admin_dashboard import AdminDashboard
from views.admin.user_management import UserManagement
from views.admin.reports_view import ReportsView as AdminReportsView
from views.admin.logs_view import SystemLogs

from views.inventory.inventory_dashboard import InventoryDashboard
from views.inventory.manage_stock import ManageStock
from views.inventory.profile_view import InventoryProfileView

from views.pharmacist.pharmacist_dashboard import PharmacistDashboard
from views.pharmacist.prescriptions_view import PrescriptionsView as PharmacistPrescriptionsView
from views.pharmacist.prescription_detail import PrescriptionDetailView  
from views.pharmacist.reports_view import ReportsView as PharmacistReportsView  
from views.pharmacist.medicine_search import PharmacistMedicineSearch
from views.pharmacist.profile_view import PharmacistProfileView

from views.billing.billing_dashboard import BillingDashboard
from views.billing.create_invoices_view import CreateInvoicesView
from views.billing.billing_reports_view import BillingReportsView
from views.billing.invoices_list_view import InvoicesListView
from views.billing.payment_history_view import PaymentHistoryView
from views.billing.invoice_detail_view import InvoiceDetailView
from views.billing.profile_view import BillingProfileView

from views.staff.staff_dashboard import StaffDashboard
from views.staff.patient_search import StaffPatientSearch
from views.staff.patient_detail import StaffPatientDetail
from views.staff.all_patients import AllPatientsView
from views.staff.help_desk import HelpDeskView
from views.staff.order_tracking import StaffOrderTracking
from views.staff.profile_view import StaffProfileView
def main(page: ft.Page):
    page.title = "PharmaOps PMS"
    
    try:
        page.window.width = 1280
        page.window.height = 720
        page.window.resizable = True 
        page.window.CENTER()
    except:
        pass
    
    page.theme = ft.Theme(color_scheme_seed=ft.colors.TEAL)
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER 

    # Initialize database
    init_db()

    def route_change(route):
        page.views.clear()
        
        # Helper for view creation
        def create_view(route_path, controls, scroll_mode=ft.ScrollMode.AUTO):
            return ft.View(route_path, controls, padding=0, scroll=scroll_mode)

        troute = page.route

        # Public Landing Route
        if troute == "/":
            page.views.append(create_view("/", [ft.Container(content=LandingPage(page), expand=True)], None))

        # Authenticated Routes
        else:
            user = AppState.get_user()
            if not user:
                page.go("/")
                return

            content = ft.Text("Not Found")
            
            # Role-Specific Dashboards
            if troute == "/dashboard":
                role = user['role']
                if role == "Patient": content = PatientDashboard()
                elif role == "Pharmacist": content = PharmacistDashboard()
                elif role == "Inventory": content = InventoryDashboard()
                elif role == "Billing": content = BillingDashboard()
                elif role == "Admin": content = AdminDashboard()
                elif role == "Staff": content = StaffDashboard()
                else: content = ft.Text(f"Welcome {user['full_name']}")

            # Patient Component Routes
            elif troute == "/patient/search": content = MedicineSearch()
            elif troute == "/patient/cart": content = CartView()
            elif troute == "/patient/orders": content = OrdersView()
            elif troute == "/patient/profile": content = ProfileView()
            elif troute == "/patient/prescriptions" : content = PatientPrescriptionsView()
            elif troute == "/patient/invoices": content = PatientInvoicesView()
            elif troute.startswith("/patient/invoice/"):
                inv_id = troute.split("/")[-1]
                try:
                    inv_id = int(inv_id)
                    content = InvoiceDetailView(inv_id)
                except (ValueError, IndexError):
                    page.go("/patient/invoices")
                    return
            elif troute.startswith("/patient/pos_receipt/"):
                order_id = troute.split("/")[-1]
                try:
                    order_id = int(order_id)
                    content = POSReceiptView(order_id)
                except (ValueError, IndexError):
                    page.go("/patient/orders")
                    return
            
            # Pharmacist Component Routes
            elif troute == "/pharmacist/prescriptions": content = PharmacistPrescriptionsView()
            elif troute == "/pharmacist/reports": content = PharmacistReportsView() 
            elif troute == "/pharmacist/medicines": content = PharmacistMedicineSearch()
            elif troute == "/pharmacist/profile": content = PharmacistProfileView()
            elif troute.startswith("/pharmacist/prescription/"):
                rx_id = troute.split("/")[-1]
                try:
                    rx_id = int(rx_id)
                    content = PrescriptionDetailView(rx_id)
                except (ValueError, IndexError):
                    # Handle invalid prescription ID identifier
                    page.go("/pharmacist/prescriptions")
                    return

            # Inventory Component Routes
            elif troute == "/inventory/stock": content = ManageStock()
            elif troute == "/inventory/profile": content = InventoryProfileView()

            # Billing Component Routes
            elif troute == "/billing/create-invoice": content = CreateInvoicesView()
            elif troute == "/billing/invoices": content = InvoicesListView()
            elif troute == "/billing/payments": content = PaymentHistoryView()
            elif troute == "/billing/reports" : content = BillingReportsView()
            elif troute == "/billing/profile": content = BillingProfileView()
            elif troute.startswith("/billing/invoice/"):
                inv_id = troute.split("/")[-1]
                try:
                    inv_id = int(inv_id)
                    content = InvoiceDetailView(inv_id)
                except (ValueError, IndexError):
                    page.go("/billing/invoices")
                    return
                    
            # Administrator Component Routes
            elif troute == "/admin/users": content = UserManagement()
            elif troute == "/admin/reports": content = AdminReportsView()
            elif troute == "/admin/logs": content = SystemLogs()

            # Staff Component Routes
            elif troute == "/staff/search": content = StaffPatientSearch()
            elif troute == "/staff/patients": content = AllPatientsView() 
            elif troute == "/staff/orders": content = StaffOrderTracking()
            elif troute == "/staff/help": content = HelpDeskView()
            elif troute == "/staff/profile": content = StaffProfileView()
            # Dynamic Patient Detail Routing
            elif troute.startswith("/staff/patient/"):
                parts = troute.split("/")
                
                if len(parts) >= 4:
                    patient_id = parts[3] 
                    source = parts[4] if len(parts) > 4 else "search"
                    
                    content = StaffPatientDetail(patient_id, source)
                else:
                    page.go("/staff/search")
                    return

            page.views.append(create_view(troute, [AppLayout(page, content)], None))
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    # OAuth callback processing delegated to landing view
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")

if __name__ == "__main__":
    # Initialize OAuth callback listener
    start_callback_server(port=8551)
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)


