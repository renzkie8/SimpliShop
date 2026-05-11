# Manages global application state and user sessions
import flet as ft

class AppState:
    current_user = None
    app_layout = None  # Reference to AppLayout for global success indicator
    _listeners = {}

    @staticmethod
    def set_user(user_row):
        if user_row:
            # Save the important details
            AppState.current_user = {
                "id": user_row["id"],
                "username": user_row["username"],
                "role": user_row["role"],
                "full_name": user_row["full_name"]
            }
        else:
            AppState.current_user = None

    @staticmethod
    def get_user():
        return AppState.current_user
    
    @staticmethod
    def set_app_layout(layout):
        """Store the AppLayout reference for global access"""
        AppState.app_layout = layout
    
    @staticmethod
    def show_success(duration=2):
        """Show the success indicator from anywhere in the app"""
        if AppState.app_layout:
            AppState.app_layout.show_success_indicator(duration)
    
    @staticmethod
    def add_listener(event_name, callback):
        """Register a listener for an event."""
        if event_name not in AppState._listeners:
            AppState._listeners[event_name] = []
        AppState._listeners[event_name].append(callback)
    
    @staticmethod
    def remove_listener(event_name, callback):
        """Remove a listener for an event."""
        if event_name in AppState._listeners:
            if callback in AppState._listeners[event_name]:
                AppState._listeners[event_name].remove(callback)
    
    @staticmethod
    def show_toast(page, message, type="success", duration=0.8):
        """Show a toast notification using AlertDialog.

        Args:
            page: The Flet page object
            message: The message to display
            type: 'success', 'error', or 'warning'
            duration: Duration in seconds before auto-dismiss
        """
        colors = {
            "success": "primary",
            "error": "error",
            "warning": "warning",
            "info": "primary"
        }
        icons = {
            "success": ft.icons.CHECK_CIRCLE,
            "error": ft.icons.ERROR,
            "warning": ft.icons.WARNING,
            "info": ft.icons.INFO
        }

        # Create a simple dialog as toast
        dialog = ft.AlertDialog(
            modal=False,
            title=None,
            bgcolor="transparent",
            surface_tint_color="transparent",
            shadow_color="transparent",
            inset_padding=0,
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(icons.get(type, ft.icons.INFO), color="white", size=20),
                    ft.Text(message, color="white", size=13, expand=True),
                ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=colors.get(type, "primary"),
                padding=15,
                border_radius=8,
                width=400,
            ),
            actions=[],
        )

        page.open(dialog)

        # Auto-close after duration
        import threading
        import time
        def close_toast():
            time.sleep(duration)
            try:
                page.close(dialog)
            except:
                pass

        threading.Thread(target=close_toast, daemon=True).START()

    @staticmethod
    def emit_event(event_name, *args, **kwargs):
        """Emit an event to all registered listeners."""
        if event_name in AppState._listeners:
            for callback in AppState._listeners[event_name]:
                try:
                    callback(*args, **kwargs)
                except Exception:
                    pass

    # Alias for emit_event
    @staticmethod
    def emit(event_name, *args, **kwargs):
        AppState.emit_event(event_name, *args, **kwargs)


