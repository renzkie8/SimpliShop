"""Notification utilities for toast messages throughout the app."""

import flet as ft
from state.app_state import AppState


def show_success(page, message, duration=3):
    """Show a success toast notification."""
    AppState.show_toast(page, message, type="success", duration=duration)


def show_error(page, message, duration=3):
    """Show an error toast notification."""
    AppState.show_toast(page, message, type="error", duration=duration)


def show_warning(page, message, duration=3):
    """Show a warning toast notification."""
    AppState.show_toast(page, message, type="warning", duration=duration)


def show_info(page, message, duration=3):
    """Show an info toast notification."""
    AppState.show_toast(page, message, type="info", duration=duration)


# Standardized system responses

# Authentication contextual messages
LOGIN_SUCCESS = "Login successful! Welcome back."
LOGIN_FAILED = "Invalid username or password."
LOGOUT_SUCCESS = "You have been logged out successfully."
SIGNUP_SUCCESS = "Account created successfully! Please login."
ACCESS_DENIED = "Access denied. You don't have permission for this action."

# Content mutability responses
CREATE_SUCCESS = "{} created successfully."
UPDATE_SUCCESS = "{} updated successfully."
DELETE_SUCCESS = "{} deleted successfully."
DELETE_CONFIRM = "Are you sure you want to delete this? This action cannot be undone."

# Input sanitization messages
REQUIRED_FIELDS = "Please fill in all required fields."
INVALID_EMAIL = "Please enter a valid email address."
PASSWORD_MISMATCH = "Passwords do not match."
DUPLICATE_USERNAME = "Username already exists."
DUPLICATE_EMAIL = "Email already exists."
WEAK_PASSWORD = "Password is too weak. Please use a stronger password."

# Resource allocation messages
LOW_STOCK = "{} is running low (only {} units remaining)."
OUT_OF_STOCK = "{} is out of stock."
STOCK_UPDATED = "Stock levels updated successfully."
REORDER_SUCCESS = "Reorder request submitted successfully."

# Commerce transaction messages
ITEM_ADDED = "{} added to cart."
ITEM_REMOVED = "{} removed from cart."
CART_CLEARED = "Cart cleared."
ORDER_PLACED = "Order placed successfully. Order ID: {}."
ORDER_CANCELLED = "Order cancelled successfully."

# Accounting transaction messages
INVOICE_CREATED = "Invoice created successfully."
PAYMENT_PROCESSED = "Payment processed successfully."
PAYMENT_FAILED = "Payment failed. Please try again."

# Query lookup responses
SEARCH_NO_RESULTS = "No results found for '{}'."
SEARCH_ERROR = "Error during search. Please try again."

# Global runtime states
SOMETHING_WENT_WRONG = "Something went wrong. Please try again."
OPERATION_FAILED = "Operation failed. Please try again."
LOADING = "Loading..."
OPERATION_SUCCESS = "Operation completed successfully."




