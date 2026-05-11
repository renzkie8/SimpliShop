import flet as ft
from services.database import get_db_connection
from datetime import datetime
from utils.notifications import show_success, show_error, show_warning, show_info, CREATE_SUCCESS, UPDATE_SUCCESS, DELETE_SUCCESS, REQUIRED_FIELDS, LOW_STOCK, OUT_OF_STOCK

def ManageStock():
    """Page to Add, Update, Delete, and Search Medicines."""
    
    # Component State Initialization
    selected_medicine_id = None 
    medicine_to_delete = None 
    
    # UI Component: Styled Input Field
    def create_input(label, icon=None, numeric=False, in_row=False):
        return ft.TextField(
            label=label,
            prefix_icon=icon,
            keyboard_type=ft.KeyboardType.NUMBER if numeric else ft.KeyboardType.TEXT,
            height=45, 
            text_size=13,
            border_color="outline",
            focused_border_color="primary",
            content_padding=10,
            expand=in_row 
        )

    # UI Components Assembly
    
    # Search input configuration
    search_txt = ft.TextField(
        hint_text="Search medicine name...",
        prefix_icon=ft.icons.SEARCH,
        expand=True,
        height=45,
        content_padding=10,
        border_color="primary", 
        on_submit=lambda e: load_data(e) 
    )
    
    # Filter dropdown controls
    category_filter = ft.Dropdown(
        label="Category",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Pain Relief"),
            ft.dropdown.Option("Antibiotics"),
            ft.dropdown.Option("Cough & Cold"),
            ft.dropdown.Option("Vitamins"),
            ft.dropdown.Option("Maintenance"),
            ft.dropdown.Option("Diabetes"),
            ft.dropdown.Option("Heart Health"),
            ft.dropdown.Option("Antacid"),
            ft.dropdown.Option("Antidiarrheal"),
            ft.dropdown.Option("Supplements"),
        ],
        value="All",
        width=200,
        content_padding=10,
        border_color="primary",
        on_change=lambda e: load_data(e) 
    )
    
    stock_filter = ft.Dropdown(
        label="Stock Status",
        options=[
            ft.dropdown.Option("All"),
            ft.dropdown.Option("Low Stock"),   
            ft.dropdown.Option("Out of Stock"), 
            ft.dropdown.Option("Good Stock"),   
        ],
        value="All",
        width=150,
        content_padding=10,
        border_color="primary",
        on_change=lambda e: load_data(e)
    )

    # Custom Table Row Helper (Proportional Stretching)
    def create_table_row(cells, is_header=False):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor="surfaceVariant" if is_header else None,
            border=ft.border.only(bottom=ft.border.BorderSide(1, "outlineVariant")) if not is_header else None,
            content=ft.Row([
                ft.Container(cells[0], expand=1),   # ID
                ft.Container(cells[1], expand=6),   # Name
                ft.Container(cells[2], expand=3),   # Category
                ft.Container(cells[3], expand=2.5), # Price
                ft.Container(cells[4], expand=2.5), # Stock
                ft.Container(cells[5], expand=3),   # Expiry
                ft.Container(cells[6], expand=3),   # Supplier
                ft.Container(cells[7], expand=2, alignment=ft.alignment.center_right), # Actions
            ], alignment=ft.MainAxisAlignment.START, spacing=20)
        )

    # Modal Form Fields
    name_input = create_input("Medicine Name", ft.icons.MEDICATION)
    category_input = ft.Dropdown(
        label="Category",
        options=category_filter.options[1:], 
        content_padding=10,
        border_color="outline",
        focused_border_color="primary",
    )
    price_input = create_input("Price (PHP)", None, numeric=True, in_row=True)
    stock_input = create_input("Stock Qty", None, numeric=True, in_row=True)
    expiry_input = create_input("Expiry (YYYY-MM-DD)", ft.icons.CALENDAR_TODAY)
    supplier_input = create_input("Supplier", ft.icons.LOCAL_SHIPPING)

    # Core Table Components
    table_header = create_table_row([
        ft.Text("ID", weight="bold"),
        ft.Text("Name", weight="bold"),
        ft.Text("Category", weight="bold"),
        ft.Text("Price", weight="bold"),
        ft.Text("Stock", weight="bold"),
        ft.Text("Expiry", weight="bold"),
        ft.Text("Supplier", weight="bold"),
        ft.Text("Actions", weight="bold", text_align=ft.TextAlign.RIGHT),
    ], is_header=True)

    stock_list = ft.ListView(expand=True, spacing=0)
    
    # Empty state container
    empty_state = ft.Container(
        content=ft.Column([
            ft.Icon(ft.icons.INVENTORY_2_OUTLINED, size=100, color="outline"),
            ft.Container(height=20),
            ft.Text("No medicines in inventory", size=20, weight="bold", color="outline"),
            ft.Container(height=10),
            ft.Text("To get started, click the 'Add Medicine' button above", 
                   size=14, color="outline", text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
        padding=80,
        alignment=ft.alignment.center,
        visible=False,
        expand=True,
    )
    
    # Main container for the scrolling list
    table_body_container = ft.Container(
        content=stock_list,
        padding=0,
        expand=True
    )

    # Application Business Logic

    def load_data(e=None):
        """Fetch and populate medicine inventory data."""
        conn = get_db_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM medicines WHERE 1=1"
        params = []

        if search_txt.value:
            query += " AND name LIKE ?"
            params.append(f"%{search_txt.value}%")

        if category_filter.value != "All":
            query += " AND category = ?"
            params.append(category_filter.value)

        if stock_filter.value == "Low Stock":
            query += " AND stock > 0 AND stock < 10"
        elif stock_filter.value == "Out of Stock":
            query += " AND stock = 0"
        elif stock_filter.value == "Good Stock":
            query += " AND stock >= 10"

        query += " ORDER BY id ASC"

        cursor.execute(query, params)
        meds = cursor.fetchall()
        conn.close()

        stock_list.controls.clear()

        if not meds:
            page = e.page if e else (stock_list.page if stock_list.page else None)
            if (search_txt.value or category_filter.value != "All" or stock_filter.value != "All") and page:
                show_info(page, "No medicine found matching your search criteria.")
                table_body_container.visible = True
                empty_state.visible = False
            else:
                table_body_container.visible = False
                empty_state.visible = True
            
            if stock_list.page:
                table_body_container.update()
                empty_state.update()
            return
        
        table_body_container.visible = True
        empty_state.visible = False

        for m in meds:
            if m['stock'] == 0:
                stock_color = "error"
            elif m['stock'] < 10:
                stock_color = "orange"
            else:
                stock_color = "primary"

            stock_list.controls.append(
                create_table_row([
                    ft.Text(str(m['id'])),
                    ft.Text(m['name'], weight="bold"),
                    ft.Text(m['category']),
                    ft.Text(f"₱{m['price']:.2f}"),
                    ft.Text(str(m['stock']), color=stock_color, weight="bold"),
                    ft.Text(m['expiry_date']),
                    ft.Text(m['supplier'] or "N/A"),
                    ft.Row([
                        ft.IconButton(
                            icon=ft.icons.EDIT,
                            icon_size=18,
                            icon_color="primary",
                            tooltip="Edit",
                            on_click=lambda e, med=m: open_edit_dialog(e, med)
                        ),
                        ft.IconButton(
                            icon=ft.icons.DELETE,
                            icon_size=18,
                            icon_color="error",
                            tooltip="Delete",
                            on_click=lambda e, mid=m['id']: prompt_delete(e, mid)
                        ),
                    ], spacing=0, alignment=ft.MainAxisAlignment.END),
                ])
            )

        if stock_list.page:
            table_body_container.update()
            empty_state.update()

    # Modal Operation Handlers (keeping original logic)
    def open_add_dialog(e):
        nonlocal selected_medicine_id
        selected_medicine_id = None 
        name_input.value = ""; category_input.value = None
        price_input.value = ""; stock_input.value = ""
        expiry_input.value = ""; supplier_input.value = ""
        dialog.title = ft.Row([ft.Icon(ft.icons.ADD_BOX, color="primary"), ft.Text("Add New Medicine")])
        e.page.open(dialog)

    def open_edit_dialog(e, med):
        nonlocal selected_medicine_id
        selected_medicine_id = med['id'] 
        name_input.value = med['name']; category_input.value = med['category']
        price_input.value = str(med['price']); stock_input.value = str(med['stock'])
        expiry_input.value = med['expiry_date']; supplier_input.value = med['supplier']
        dialog.title = ft.Row([ft.Icon(ft.icons.EDIT, color="primary"), ft.Text("Edit Medicine")])
        e.page.open(dialog)

    def save_medicine(e):
        if not name_input.value or not price_input.value or not stock_input.value:
            show_error(e.page, REQUIRED_FIELDS); e.page.update(); return
        try:
            conn = get_db_connection(); cursor = conn.cursor()
            if selected_medicine_id is None:
                cursor.execute("INSERT INTO medicines (name, category, price, stock, expiry_date, supplier) VALUES (?, ?, ?, ?, ?, ?)", 
                    (name_input.value, category_input.value, float(price_input.value), int(stock_input.value), expiry_input.value, supplier_input.value))
                msg = CREATE_SUCCESS.format(name_input.value)
            else:
                cursor.execute("UPDATE medicines SET name=?, category=?, price=?, stock=?, expiry_date=?, supplier=? WHERE id=?",
                    (name_input.value, category_input.value, float(price_input.value), int(stock_input.value), expiry_input.value, supplier_input.value, selected_medicine_id))
                msg = UPDATE_SUCCESS.format(name_input.value)
            conn.commit(); conn.close(); e.page.close(dialog); load_data(); show_success(e.page, msg); e.page.update()
        except Exception as ex: show_error(e.page, f"Error: {str(ex)}"); e.page.update()

    def prompt_delete(e, med_id):
        nonlocal medicine_to_delete; medicine_to_delete = med_id; e.page.open(del_dialog)

    def confirm_delete_action(e):
        if medicine_to_delete is None: return
        conn = get_db_connection(); conn.execute("DELETE FROM medicines WHERE id = ?", (medicine_to_delete,)); conn.commit(); conn.close()
        e.page.close(del_dialog); load_data(); show_success(e.page, DELETE_SUCCESS.format("Medicine")); e.page.update()

    # Modal Definitions
    dialog = ft.AlertDialog(bgcolor="surface", content=ft.Container(width=500, content=ft.Column([
        name_input, ft.Container(height=5), category_input, ft.Container(height=5),
        ft.Row([price_input, stock_input], spacing=15), ft.Container(height=5), expiry_input,
        ft.Container(height=5), supplier_input], tight=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)),
        actions=[ft.TextButton("Cancel", on_click=lambda e: e.page.close(dialog)), ft.ElevatedButton("Save", bgcolor="primary", color="onPrimary", on_click=save_medicine)])

    del_dialog = ft.AlertDialog(bgcolor="surface", title=ft.Text("Confirm Delete"), content=ft.Text("Are you sure you want to delete this medicine?"),
        actions=[ft.TextButton("Cancel", on_click=lambda e: e.page.close(del_dialog)), ft.ElevatedButton("Delete", bgcolor="error", color="white", on_click=confirm_delete_action)])

    load_data()

    # Main View Assembly
    return ft.Column([
        ft.Row([
            ft.Text("Stock Management", size=28, weight="bold"),
            ft.ElevatedButton("Add Medicine", icon=ft.icons.ADD, bgcolor="primary", color="onPrimary", on_click=open_add_dialog),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Container(height=10),
        
        ft.Container(
            content=ft.Row([
                search_txt, category_filter, stock_filter,
                ft.IconButton(icon=ft.icons.SEARCH, icon_color="primary", on_click=lambda e: load_data(e))
            ], spacing=10, expand=True),
            padding=15, bgcolor="surfaceVariant", border_radius=10,
        ),
        
        ft.Container(height=20),
        
        # Responsive Custom Table Box
        ft.Container(
            content=ft.Column([
                table_header,
                ft.Stack([table_body_container, empty_state], expand=True),
            ], spacing=0, expand=True),
            border=ft.border.all(1, "outline"),
            border_radius=10,
            expand=True,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS 
        ),
        
    ], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)




