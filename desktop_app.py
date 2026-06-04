"""
╔══════════════════════════════════════════════════════╗
║                   GYM  PLATFORM                       ║
║          Train · Track · Transform  ·  v2.0           ║
║   With Animations, Responsive Design & Services      ║
╚══════════════════════════════════════════════════════╝
"""
import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import sys
import os
import math
import calendar
import webbrowser
from datetime import date, datetime, timedelta
import threading
import time
import json

# Windows terminals default to cp1252 and crash on the emoji in our log lines.
# Force UTF-8 so the app launches from any console (PowerShell, cmd, double-click).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import init_db, get_db_session
from backend.models import (
    SystemUser, Member, MemberActivity, Product,
    Purchase, Payment, Expense, EmployeeLog
)
from backend.utils.auth import verify_password, get_password_hash, create_token
from backend.utils.app_settings import load_settings, save_settings, update_setting
from backend.services.whatsapp_service import (
    send_whatsapp, render_template, compute_age, clean_phone
)

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Deep red & black color scheme
COLORS = {
    "bg_dark": "#0a0506",        # near-black with a faint warm tint
    "bg_card": "#160d0e",        # black card surface
    "bg_elevated": "#211314",    # elevated surface
    "bg_hover": "#2e1a1b",       # hover state
    "primary": "#e11d2e",        # deep red (brand accent)
    "primary_dark": "#991b1b",   # darker red (pressed/hover)
    "primary_light": "#f87171",  # light red (highlights)
    "primary_glow": "#1c0a0c",   # ambient red-black glow
    "secondary": "#b91c1c",      # crimson (secondary accent)
    "success": "#22c55e",        # green (kept for semantic clarity)
    "success_dark": "#16a34a",
    "warning": "#f59e0b",        # amber (kept for semantic clarity)
    "warning_dark": "#d97706",
    "danger": "#ef4444",         # red for destructive actions
    "danger_dark": "#b91c1c",
    "info": "#fb7185",           # soft rose for info accents
    "text": "#f8fafc",
    "text_secondary": "#cbb6b8",
    "text_muted": "#8b7173",
    "border": "#2c1819",         # dark red border
    "gradient_start": "#e11d2e",
    "gradient_end": "#7f1d1d",
    "accent": "#fb7185",         # rose accent
    "gold": "#fbbf24"
}

# International dialing codes (flag, country, dial code). Sorted by country.
COUNTRY_CODES = [
    ("🇲🇦", "Morocco", "+212"), ("🇩🇿", "Algeria", "+213"), ("🇹🇳", "Tunisia", "+216"),
    ("🇪🇬", "Egypt", "+20"), ("🇸🇦", "Saudi Arabia", "+966"), ("🇦🇪", "UAE", "+971"),
    ("🇶🇦", "Qatar", "+974"), ("🇰🇼", "Kuwait", "+965"), ("🇧🇭", "Bahrain", "+973"),
    ("🇴🇲", "Oman", "+968"), ("🇯🇴", "Jordan", "+962"), ("🇱🇧", "Lebanon", "+961"),
    ("🇮🇶", "Iraq", "+964"), ("🇸🇾", "Syria", "+963"), ("🇾🇪", "Yemen", "+967"),
    ("🇵🇸", "Palestine", "+970"), ("🇱🇾", "Libya", "+218"), ("🇸🇩", "Sudan", "+249"),
    ("🇲🇷", "Mauritania", "+222"), ("🇺🇸", "United States", "+1"), ("🇨🇦", "Canada", "+1"),
    ("🇬🇧", "United Kingdom", "+44"), ("🇫🇷", "France", "+33"), ("🇪🇸", "Spain", "+34"),
    ("🇮🇹", "Italy", "+39"), ("🇩🇪", "Germany", "+49"), ("🇳🇱", "Netherlands", "+31"),
    ("🇧🇪", "Belgium", "+32"), ("🇨🇭", "Switzerland", "+41"), ("🇦🇹", "Austria", "+43"),
    ("🇵🇹", "Portugal", "+351"), ("🇮🇪", "Ireland", "+353"), ("🇸🇪", "Sweden", "+46"),
    ("🇳🇴", "Norway", "+47"), ("🇩🇰", "Denmark", "+45"), ("🇫🇮", "Finland", "+358"),
    ("🇵🇱", "Poland", "+48"), ("🇷🇺", "Russia", "+7"), ("🇹🇷", "Turkey", "+90"),
    ("🇬🇷", "Greece", "+30"), ("🇷🇴", "Romania", "+40"), ("🇺🇦", "Ukraine", "+380"),
    ("🇨🇳", "China", "+86"), ("🇯🇵", "Japan", "+81"), ("🇰🇷", "South Korea", "+82"),
    ("🇮🇳", "India", "+91"), ("🇵🇰", "Pakistan", "+92"), ("🇧🇩", "Bangladesh", "+880"),
    ("🇮🇩", "Indonesia", "+62"), ("🇲🇾", "Malaysia", "+60"), ("🇸🇬", "Singapore", "+65"),
    ("🇹🇭", "Thailand", "+66"), ("🇵🇭", "Philippines", "+63"), ("🇻🇳", "Vietnam", "+84"),
    ("🇦🇺", "Australia", "+61"), ("🇳🇿", "New Zealand", "+64"), ("🇧🇷", "Brazil", "+55"),
    ("🇦🇷", "Argentina", "+54"), ("🇲🇽", "Mexico", "+52"), ("🇿🇦", "South Africa", "+27"),
    ("🇳🇬", "Nigeria", "+234"), ("🇰🇪", "Kenya", "+254"), ("🇬🇭", "Ghana", "+233"),
    ("🇸🇳", "Senegal", "+221"), ("🇨🇮", "Ivory Coast", "+225"),
]

# Membership plan suggestions (the field is editable, so staff can type their own)
PLAN_OPTIONS = ["Daily", "Weekly", "Monthly", "Quarterly", "Half-Year", "Yearly", "Student", "VIP"]

# Default duration (days) auto-filled when a plan is selected (still editable)
PLAN_DURATIONS = {
    "Daily": 1, "Weekly": 7, "Monthly": 30, "Quarterly": 90,
    "Half-Year": 180, "Yearly": 365, "Student": 30, "VIP": 30,
}

# Comprehensive expense categories with groupings
EXPENSE_CATEGORIES = [
    # Utilities
    "Electricity", "Water", "Internet", "Gas", "Phone Bill",
    # Facility
    "Rent", "Maintenance", "Equipment", "Cleaning", "Security",
    # Operations
    "Supplies", "Office Supplies", "Refreshments", "Transportation",
    # Staff
    "Employee Salary", "Bonus", "Training", "Uniforms",
    # Business
    "Marketing", "Advertising", "Software", "Subscriptions",
    # Legal & Finance
    "Taxes", "Insurance", "Licenses", "Bank Fees", "Legal Fees",
    # Other
    "Miscellaneous", "Emergency", "Other",
]

# Expense category groups for better organization
EXPENSE_CATEGORY_GROUPS = {
    "💡 Utilities": ["Electricity", "Water", "Internet", "Gas", "Phone Bill"],
    "🏠 Facility": ["Rent", "Maintenance", "Equipment", "Cleaning", "Security"],
    "📦 Operations": ["Supplies", "Office Supplies", "Refreshments", "Transportation"],
    "👔 Staff": ["Employee Salary", "Bonus", "Training", "Uniforms"],
    "📣 Business": ["Marketing", "Advertising", "Software", "Subscriptions"],
    "🧾 Legal & Finance": ["Taxes", "Insurance", "Licenses", "Bank Fees", "Legal Fees"],
    "📝 Other": ["Miscellaneous", "Emergency", "Other"],
}

# Emoji per expense category (used in lists)
EXPENSE_ICONS = {
    "electricity": "💡", "water": "🚰", "internet": "🌐", "gas": "🔥", "phone bill": "📱",
    "rent": "🏠", "maintenance": "🔧", "equipment": "🏋️", "cleaning": "🧹", "security": "🔐",
    "supplies": "📦", "office supplies": "✏️", "refreshments": "☕", "transportation": "🚗",
    "employee salary": "👔", "salary": "💵", "bonus": "🎁", "training": "📚", "uniforms": "👕",
    "marketing": "📣", "advertising": "📺", "software": "💻", "subscriptions": "📱",
    "taxes": "🧾", "insurance": "🛡️", "licenses": "📋", "bank fees": "🏦", "legal fees": "⚖️",
    "miscellaneous": "📝", "emergency": "🚨", "other": "📝", "utilities": "💡",
}

# Quick expense presets for common items
QUICK_EXPENSE_PRESETS = [
    ("💡 Electricity", "Electricity", "Monthly electricity bill"),
    ("🚰 Water", "Water", "Monthly water bill"),
    ("🌐 Internet", "Internet", "Monthly internet service"),
    ("🔧 Maintenance", "Maintenance", "Equipment/facility maintenance"),
    ("👔 Salary", "Employee Salary", "Staff salary payment"),
    ("🧹 Cleaning", "Cleaning", "Cleaning services"),
]


def present_modal(dialog, width, height, animate=True):
    """Give every modal a consistent, professional, responsive presentation.

    - Centers the dialog over the *app window* (not the whole screen) so it
      feels attached to the workspace.
    - Clamps the size to the screen so large forms still fit small laptops.
    - Fades the window in smoothly instead of popping.
    - Adds Escape-to-close and proper focus/stacking.

    Replaces the copy-pasted geometry/centering block each dialog used to carry.
    """
    dialog.configure(fg_color=COLORS["bg_card"])

    sw, sh = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
    # Responsive clamp — never let a dialog exceed the visible screen.
    width = max(280, min(width, sw - 80))
    height = max(200, min(height, sh - 120))

    # Prefer centering over the parent application window.
    top = None
    try:
        master = dialog.master
        top = master.winfo_toplevel() if master is not None else None
    except Exception:
        top = None

    try:
        if top is not None and top.winfo_viewable():
            top.update_idletasks()
            px, py = top.winfo_rootx(), top.winfo_rooty()
            pw, ph = top.winfo_width(), top.winfo_height()
            x = px + (pw - width) // 2
            y = py + (ph - height) // 2
        else:
            x = (sw - width) // 2
            y = (sh - height) // 2
    except Exception:
        x = (sw - width) // 2
        y = (sh - height) // 2

    # Keep the dialog fully on-screen.
    x = max(10, min(x, sw - width - 10))
    y = max(10, min(y, sh - height - 10))

    dialog.geometry(f"{width}x{height}+{x}+{y}")
    if top is not None:
        dialog.transient(top)
    dialog.grab_set()
    dialog.bind("<Escape>", lambda _e: dialog.destroy())

    # Smooth fade-in (best-effort; falls back to instant on unsupported WMs).
    if animate:
        try:
            dialog.attributes("-alpha", 0.0)
            dialog.update_idletasks()

            def _fade(step=0):
                alpha = min(1.0, step / 8)
                try:
                    dialog.attributes("-alpha", alpha)
                except Exception:
                    return
                if alpha < 1.0:
                    dialog.after(16, lambda: _fade(step + 1))

            _fade()
        except Exception:
            pass

    dialog.lift()
    dialog.focus_force()


class ScrollableContent(ctk.CTkScrollableFrame):
    """A scrollable page container that still fills the viewport.

    A plain CTkScrollableFrame shrinks its inner frame to its content's natural
    height, which would collapse pages that rely on ``fill="both", expand=True``
    (e.g. list pages). This subclass keeps the inner frame at least as tall as
    the visible area, so those pages get a full-height viewport — yet when a
    page's content is taller than the window, it scrolls all the way to the
    footer. The whole platform becomes scrollable without breaking layouts.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._busy = False
        self._parent_canvas.bind("<Configure>", self._queue, add="+")
        self._parent_frame.bind("<Configure>", self._queue, add="+")

    def _queue(self, _event=None):
        # Coalesce the burst of <Configure> events from a page rebuild/resize
        # into a single re-stretch. _busy stays set for the whole operation so
        # the configures we cause ourselves can't re-trigger it (no oscillation).
        if not self._busy:
            self._busy = True
            self.after_idle(self._restretch)

    def _restretch(self):
        canvas = self._parent_canvas
        win = self._create_window_id
        try:
            canvas_h = canvas.winfo_height()
            # Release the inner frame to its natural height, then measure the
            # true content extent via the canvas bounding box (widget reqheight
            # under-reports for nested CTk frames, so bbox is the reliable source).
            canvas.itemconfigure(win, height=0)
            canvas.update_idletasks()
            bbox = canvas.bbox(win)
            content_h = (bbox[3] - bbox[1]) if bbox else 0
            # Fill the viewport when content is short (so expand=True pages don't
            # collapse); grow past it when content is tall (so the page scrolls).
            target = max(canvas_h, content_h + 12) if content_h else canvas_h
            canvas.itemconfigure(win, height=target)
            canvas.update_idletasks()
        except Exception:
            pass
        finally:
            self._busy = False


def scrollable_page(load_fn):
    """Make a page method build into a scrollable body that fills the content area.

    The page keeps using ``self.content_frame``; we transparently point it at a
    fresh ScrollableContent for the duration of the build, then restore it. Used
    only for pages that don't already host their own scrolling list, so on small
    windows those pages can be scrolled all the way down to their footer.
    """
    def wrapper(self, *args, **kwargs):
        host = self.content_frame
        body = ScrollableContent(host, fg_color=COLORS["bg_dark"])
        body.pack(fill="both", expand=True)
        self.content_frame = body
        try:
            return load_fn(self, *args, **kwargs)
        finally:
            self.content_frame = host
    return wrapper


class CalendarPopup(ctk.CTkToplevel):
    """Themed calendar with year + month dropdowns for quick date picking."""
    def __init__(self, parent, on_select, initial=None, year_range=None):
        super().__init__(parent)
        self.on_select = on_select
        self.title("Select date")
        self.configure(fg_color=COLORS["bg_card"])
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        base = initial or date.today()
        self.year, self.month = base.year, base.month
        self.selected = initial

        # Year list (newest first) — wide enough for birthdays and future dates
        if year_range is None:
            lo, hi = 1920, date.today().year + 6
        else:
            lo, hi = year_range
        lo = min(lo, self.year)
        hi = max(hi, self.year)
        self._years = [str(y) for y in range(hi, lo - 1, -1)]

        self._build_header()
        self.grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_frame.pack(padx=14, pady=(0, 14))
        self._draw_month()

        # Position near the cursor / centered
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        self.grab_set()

    def _build_header(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=14, pady=14)

        ctk.CTkButton(bar, text="‹", width=32, height=34, corner_radius=8,
                      fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_hover"],
                      command=self._prev).pack(side="left")

        # Month dropdown
        self.month_var = ctk.StringVar(value=calendar.month_name[self.month])
        self.month_menu = ctk.CTkOptionMenu(
            bar, values=[calendar.month_name[m] for m in range(1, 13)],
            variable=self.month_var, width=116, height=34,
            fg_color=COLORS["bg_elevated"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_dark"], corner_radius=8,
            font=ctk.CTkFont(size=13), command=self._on_month
        )
        self.month_menu.pack(side="left", padx=6, expand=True)

        # Year dropdown
        self.year_var = ctk.StringVar(value=str(self.year))
        self.year_menu = ctk.CTkOptionMenu(
            bar, values=self._years, variable=self.year_var, width=84, height=34,
            fg_color=COLORS["bg_elevated"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_dark"], corner_radius=8,
            font=ctk.CTkFont(size=13), command=self._on_year
        )
        self.year_menu.pack(side="left", padx=6, expand=True)

        ctk.CTkButton(bar, text="›", width=32, height=34, corner_radius=8,
                      fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_hover"],
                      command=self._next).pack(side="right")

    def _on_month(self, name):
        self.month = list(calendar.month_name).index(name)
        self._draw_month()

    def _on_year(self, value):
        self.year = int(value)
        self._draw_month()

    def _sync_header(self):
        self.month_var.set(calendar.month_name[self.month])
        self.year_var.set(str(self.year))

    def _prev(self):
        self.month -= 1
        if self.month < 1:
            self.month, self.year = 12, self.year - 1
        self._sync_header()
        self._draw_month()

    def _next(self):
        self.month += 1
        if self.month > 12:
            self.month, self.year = 1, self.year + 1
        self._sync_header()
        self._draw_month()

    def _draw_month(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        # Weekday header row
        for i, wd in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            ctk.CTkLabel(self.grid_frame, text=wd, width=36,
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=COLORS["text_muted"]).grid(row=0, column=i, padx=2, pady=2)

        today = date.today()
        cal = calendar.Calendar(firstweekday=0)
        row = 1
        col = 0
        for d in cal.itermonthdates(self.year, self.month):
            if d.month != self.month:
                ctk.CTkLabel(self.grid_frame, text="", width=36).grid(row=row, column=col, padx=2, pady=2)
            else:
                is_today = (d == today)
                is_sel = (self.selected == d)
                fg = COLORS["primary"] if is_sel else (COLORS["bg_elevated"] if is_today else "transparent")
                ctk.CTkButton(
                    self.grid_frame, text=str(d.day), width=36, height=32, corner_radius=8,
                    fg_color=fg, hover_color=COLORS["primary_dark"],
                    text_color=COLORS["text"],
                    font=ctk.CTkFont(size=12, weight="bold" if is_today else "normal"),
                    command=lambda dd=d: self._pick(dd)
                ).grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 6:
                col = 0
                row += 1

    def _pick(self, d):
        self.on_select(d)
        self.destroy()


class DateField(ctk.CTkFrame):
    """Read-only entry + calendar button that returns YYYY-MM-DD."""
    def __init__(self, parent, initial=None, placeholder="Select date…", height=45, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._date = None
        self.placeholder = placeholder

        self.entry = ctk.CTkEntry(
            self, height=height, font=ctk.CTkFont(size=14),
            fg_color=COLORS["bg_dark"], border_color=COLORS["border"], corner_radius=10
        )
        self.entry.pack(side="left", fill="x", expand=True)
        # Block typing — force calendar use
        self.entry.bind("<Key>", lambda e: "break")
        self.entry.bind("<Button-1>", lambda e: self.open_picker())

        ctk.CTkButton(
            self, text="📅", width=46, height=height, corner_radius=10,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
            command=self.open_picker
        ).pack(side="left", padx=(8, 0))

        if initial:
            self.set_date(initial)
        else:
            self._show_placeholder()

    def _show_placeholder(self):
        self.entry.configure(text_color=COLORS["text_muted"])
        self.entry.delete(0, "end")
        self.entry.insert(0, self.placeholder)

    def open_picker(self):
        CalendarPopup(self, on_select=self.set_date, initial=self._date)

    def set_date(self, d):
        if isinstance(d, str):
            try:
                d = datetime.strptime(d, "%Y-%m-%d").date()
            except ValueError:
                return
        self._date = d
        self.entry.configure(text_color=COLORS["text"])
        self.entry.delete(0, "end")
        self.entry.insert(0, d.strftime("%Y-%m-%d"))

    def get(self):
        """Return YYYY-MM-DD string, or '' if nothing selected."""
        return self._date.strftime("%Y-%m-%d") if self._date else ""

    def get_date(self):
        return self._date


class SearchableDropdown(ctk.CTkFrame):
    """A dropdown button that opens a searchable, scrollable picker popup.

    Generic over arbitrary items via small label/search callbacks so it can be
    reused (e.g. country codes). get_selected() returns the chosen item.
    """
    def __init__(self, parent, items, button_label, list_label, search_text,
                 on_select=None, initial=None, width=130, height=45,
                 title="Select", placeholder="Select ▾", **kwargs):
        super().__init__(parent, fg_color="transparent", width=width, height=height, **kwargs)
        self.items = list(items)
        self._fb = button_label
        self._fl = list_label
        self._fs = search_text
        self._on_select = on_select
        self._title = title
        self._placeholder = placeholder
        self.selected = initial

        self.btn = ctk.CTkButton(
            self, text=self._fb(initial) if initial else placeholder,
            width=width, height=height, corner_radius=10, anchor="w",
            fg_color=COLORS["bg_dark"], hover_color=COLORS["bg_elevated"],
            text_color=COLORS["text"], font=ctk.CTkFont(size=13),
            command=self._open
        )
        self.btn.pack(fill="both", expand=True)

    def get_selected(self):
        return self.selected

    def set_selected(self, item):
        self.selected = item
        self.btn.configure(text=self._fb(item) if item else self._placeholder)

    def _open(self):
        win = ctk.CTkToplevel(self)
        win.title(self._title)
        win.configure(fg_color=COLORS["bg_card"])
        win.geometry("340x430")
        win.transient(self.winfo_toplevel())
        win.update_idletasks()
        # Drop the popup just under the button when there's room
        bx = self.btn.winfo_rootx()
        by = self.btn.winfo_rooty() + self.btn.winfo_height() + 4
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        x = max(0, min(bx, sw - 350))
        y = max(0, min(by, sh - 450))
        win.geometry(f"+{x}+{y}")
        win.grab_set()

        search = ctk.CTkEntry(
            win, placeholder_text="🔍  Search…", height=40,
            fg_color=COLORS["bg_dark"], border_color=COLORS["border"], corner_radius=8,
            font=ctk.CTkFont(size=13)
        )
        search.pack(fill="x", padx=12, pady=12)
        search.after(120, search.focus)

        listf = ctk.CTkScrollableFrame(win, fg_color="transparent")
        listf.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        def choose(it):
            self.set_selected(it)
            if self._on_select:
                self._on_select(it)
            win.destroy()

        def render(query=""):
            for w in listf.winfo_children():
                w.destroy()
            q = query.lower().strip()
            shown = 0
            for it in self.items:
                if q and q not in self._fs(it):
                    continue
                ctk.CTkButton(
                    listf, text=self._fl(it), anchor="w", height=36,
                    fg_color="transparent", hover_color=COLORS["bg_elevated"],
                    text_color=COLORS["text"], font=ctk.CTkFont(size=13),
                    command=lambda i=it: choose(i)
                ).pack(fill="x", pady=1)
                shown += 1
            if shown == 0:
                ctk.CTkLabel(listf, text="No matches",
                             text_color=COLORS["text_muted"]).pack(pady=20)

        search.bind("<KeyRelease>", lambda e: render(search.get()))
        win.bind("<Escape>", lambda e: win.destroy())
        render()


class SearchableSelect(ctk.CTkFrame):
    """Drop-in replacement for CTkOptionMenu with a searchable popup.

    Keeps the CTkOptionMenu essentials (``values``, ``variable``, ``command``,
    ``get()``, ``set()``, ``configure(values=…, command=…)``) but clicking it
    opens a search box + scrollable list, so long option lists (employees,
    categories, plans, periods…) can be filtered by typing.
    """
    def __init__(self, parent, values=None, variable=None, command=None,
                 width=160, height=32, fg_color=None, button_color=None,
                 button_hover_color=None, corner_radius=8, font=None,
                 placeholder="Select  ▾", title="Select", **kwargs):
        super().__init__(parent, fg_color="transparent", width=width, height=height)
        self._values = [str(v) for v in (values or [])]
        self._variable = variable
        self._command = command
        self._title = title
        self._placeholder = placeholder
        self._accent = button_color or COLORS["primary"]
        font = font or ctk.CTkFont(size=13)

        # Initial value: variable wins, else first option.
        init = None
        if variable is not None and variable.get():
            init = variable.get()
        elif self._values:
            init = self._values[0]
        self._value = init
        if variable is not None and not variable.get() and init is not None:
            variable.set(init)

        self.btn = ctk.CTkButton(
            self, text=self._display(init), width=width, height=height,
            corner_radius=corner_radius, anchor="w",
            fg_color=fg_color or COLORS["bg_elevated"],
            hover_color=button_hover_color or COLORS["bg_hover"],
            text_color=COLORS["text"], font=font, command=self._open,
        )
        self.btn.pack(fill="both", expand=True)

    def _display(self, v):
        return f"  {v}     ▾" if v not in (None, "") else self._placeholder

    def get(self):
        return self._value if self._value is not None else ""

    def set(self, value):
        self._value = value
        self.btn.configure(text=self._display(value))
        if self._variable is not None:
            self._variable.set(value)

    def configure(self, **kwargs):
        if "values" in kwargs:
            self._values = [str(v) for v in (kwargs.pop("values") or [])]
            if self._value not in self._values and self._values:
                self.set(self._values[0])
        if "command" in kwargs:
            self._command = kwargs.pop("command")
        if "variable" in kwargs:
            self._variable = kwargs.pop("variable")
        if kwargs:
            try:
                super().configure(**kwargs)
            except Exception:
                pass

    def _choose(self, value):
        self.set(value)
        if self._command:
            self._command(value)

    def _open(self):
        win = ctk.CTkToplevel(self)
        win.title(self._title)
        win.configure(fg_color=COLORS["bg_card"])
        win.geometry("300x360")
        win.transient(self.winfo_toplevel())
        win.update_idletasks()
        # Drop the popup just under the button, kept on-screen.
        bx = self.btn.winfo_rootx()
        by = self.btn.winfo_rooty() + self.btn.winfo_height() + 4
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        x = max(10, min(bx, sw - 310))
        y = max(10, min(by, sh - 380))
        win.geometry(f"300x360+{x}+{y}")
        win.grab_set()
        win.bind("<Escape>", lambda _e: win.destroy())

        search = ctk.CTkEntry(
            win, placeholder_text="🔍  Search…", height=38,
            fg_color=COLORS["bg_dark"], border_color=COLORS["border"],
            corner_radius=8, font=ctk.CTkFont(size=13)
        )
        search.pack(fill="x", padx=12, pady=12)
        search.after(120, search.focus)

        listf = ctk.CTkScrollableFrame(win, fg_color="transparent")
        listf.pack(fill="both", expand=True, padx=8, pady=(0, 12))

        def render(query=""):
            for w in listf.winfo_children():
                w.destroy()
            q = query.lower().strip()
            shown = 0
            for v in self._values:
                if q and q not in v.lower():
                    continue
                is_sel = (v == self._value)
                ctk.CTkButton(
                    listf, text=v, anchor="w", height=34, corner_radius=8,
                    fg_color=self._accent if is_sel else "transparent",
                    hover_color=COLORS["bg_elevated"], text_color=COLORS["text"],
                    font=ctk.CTkFont(size=13),
                    command=lambda val=v: (win.destroy(), self._choose(val))
                ).pack(fill="x", pady=1)
                shown += 1
            if shown == 0:
                ctk.CTkLabel(listf, text="No matches",
                             text_color=COLORS["text_muted"]).pack(pady=20)

        search.bind("<KeyRelease>", lambda _e: render(search.get()))
        win.bind("<Return>", lambda _e: None)
        render()


class PhoneField(ctk.CTkFrame):
    """Searchable country-code picker + number entry. get() returns +CCNNN."""
    def __init__(self, parent, initial="", default_code="+212", height=45, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        default_item = next((c for c in COUNTRY_CODES if c[2] == default_code),
                            COUNTRY_CODES[0])
        self.code_dd = SearchableDropdown(
            self, COUNTRY_CODES,
            button_label=lambda it: f"{it[0]} {it[2]}",
            list_label=lambda it: f"{it[0]}   {it[1]}  ({it[2]})",
            search_text=lambda it: f"{it[1]} {it[2]}".lower(),
            initial=default_item, width=118, height=height, title="Select country"
        )
        self.code_dd.pack(side="left")

        self.number = ctk.CTkEntry(
            self, height=height, font=ctk.CTkFont(size=14), placeholder_text="6 12 34 56 78",
            fg_color=COLORS["bg_dark"], border_color=COLORS["border"], corner_radius=10
        )
        self.number.pack(side="left", fill="x", expand=True, padx=(8, 0))

        if initial:
            self.set_value(initial, default_code)

    def set_value(self, full, default_code="+212"):
        full = (full or "").strip()
        matched = None
        rest = full.lstrip("+")
        # Longest dial-code prefix wins (e.g. +1 vs +212)
        for item in sorted(COUNTRY_CODES, key=lambda c: len(c[2]), reverse=True):
            if full.startswith(item[2]):
                matched = item
                rest = full[len(item[2]):]
                break
        item = matched or next((c for c in COUNTRY_CODES if c[2] == default_code),
                               COUNTRY_CODES[0])
        self.code_dd.set_selected(item)
        self.number.delete(0, "end")
        self.number.insert(0, rest.strip())

    def get(self):
        it = self.code_dd.get_selected()
        code = it[2] if it else ""
        num = "".join(ch for ch in self.number.get() if ch.isdigit()).lstrip("0")
        return f"{code}{num}" if num else ""


# Animation helper class
class AnimationManager:
    @staticmethod
    def fade_in(widget, duration=300, steps=10):
        """Animate widget fade in"""
        def animate():
            for i in range(steps + 1):
                alpha = i / steps
                try:
                    widget.configure(fg_color=widget.cget("fg_color"))
                except:
                    pass
                time.sleep(duration / 1000 / steps)
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def slide_in(widget, start_x, end_x, duration=300):
        """Animate widget slide in"""
        steps = 20
        delta = (end_x - start_x) / steps
        def animate():
            for i in range(steps + 1):
                x = start_x + (delta * i)
                try:
                    widget.place(relx=x/1000)
                except:
                    break
                time.sleep(duration / 1000 / steps)
        threading.Thread(target=animate, daemon=True).start()


class AnimatedButton(ctk.CTkButton):
    """Custom button with hover animations"""
    def __init__(self, *args, **kwargs):
        self.original_fg = kwargs.get('fg_color', COLORS["primary"])
        self.hover_fg = kwargs.get('hover_color', COLORS["primary_dark"])
        super().__init__(*args, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.configure(fg_color=self.hover_fg)
    
    def _on_leave(self, event):
        self.configure(fg_color=self.original_fg)


class GlowingCard(ctk.CTkFrame):
    """Card with subtle glow effect"""
    def __init__(self, parent, glow_color=COLORS["primary"], **kwargs):
        self.glow_color = glow_color
        kwargs.setdefault('fg_color', COLORS["bg_card"])
        kwargs.setdefault('corner_radius', 16)
        super().__init__(parent, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.configure(border_color=self.glow_color, border_width=1)
    
    def _on_leave(self, event):
        self.configure(border_width=0)


class PulsingDot(ctk.CTkLabel):
    """Animated pulsing indicator"""
    def __init__(self, parent, color=COLORS["success"], **kwargs):
        super().__init__(parent, text="●", text_color=color, font=ctk.CTkFont(size=12), **kwargs)
        self.color = color
        self.pulsing = True
        self._pulse()
    
    def _pulse(self):
        if self.pulsing:
            try:
                current = self.cget("text_color")
                if current == self.color:
                    self.configure(text_color=COLORS["bg_dark"])
                else:
                    self.configure(text_color=self.color)
                self.after(800, self._pulse)
            except:
                pass
    
    def stop(self):
        self.pulsing = False


class LoadingSpinner(ctk.CTkFrame):
    """Animated loading spinner"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.frames = ["◐", "◓", "◑", "◒"]
        self.current = 0
        self.spinning = True
        self.label = ctk.CTkLabel(
            self, text=self.frames[0], 
            font=ctk.CTkFont(size=24),
            text_color=COLORS["primary"]
        )
        self.label.pack()
        self._spin()
    
    def _spin(self):
        if self.spinning:
            self.current = (self.current + 1) % len(self.frames)
            self.label.configure(text=self.frames[self.current])
            self.after(100, self._spin)
    
    def stop(self):
        self.spinning = False


class CircularLoader(ctk.CTkCanvas):
    """Smooth canvas-based circular spinner (professional indeterminate loader)."""
    def __init__(self, parent, size=64, thickness=6,
                 color=COLORS["primary"], track=COLORS["bg_elevated"],
                 bg=COLORS["bg_dark"], **kwargs):
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, bg=bg, **kwargs)
        self.size = size
        self.thickness = thickness
        self.color = color
        self.track = track
        self.angle = 0
        self.extent = 90
        self.spinning = True
        self._draw()

    def _draw(self):
        if not self.spinning:
            return
        self.delete("all")
        pad = self.thickness
        box = (pad, pad, self.size - pad, self.size - pad)
        # Track ring
        self.create_arc(*box, start=0, extent=359.9, style="arc",
                        outline=self.track, width=self.thickness)
        # Moving arc
        self.create_arc(*box, start=self.angle, extent=self.extent, style="arc",
                        outline=self.color, width=self.thickness)
        self.angle = (self.angle - 12) % 360
        # Gentle "breathing" of the arc length
        self.extent = 90 + 50 * (0.5 + 0.5 * math.sin(self.angle / 40))
        try:
            self.after(28, self._draw)
        except Exception:
            pass

    def stop(self):
        self.spinning = False


class SplashScreen(ctk.CTkFrame):
    """Professional animated loading/splash screen shown on startup."""
    def __init__(self, parent, on_done, steps=None):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.on_done = on_done
        self.steps = steps or [
            "Warming up the engine…",
            "Racking the weights…",
            "Counting reps & members…",
            "Calibrating the scoreboard…",
            "Ready to train! 💪",
        ]
        self._build()
        self.after(150, self._run)

    def _build(self):
        # Decorative ambient circles
        for i in range(4):
            s = 160 + i * 90
            ctk.CTkFrame(
                self, width=s, height=s, corner_radius=s // 2,
                fg_color=COLORS["primary_glow"], border_width=0
            ).place(relx=0.15 + (i % 2) * 0.7, rely=0.2 + (i % 2) * 0.5, anchor="center")

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logo badge with glow
        badge = ctk.CTkFrame(center, width=110, height=110, corner_radius=28,
                             fg_color=COLORS["primary"])
        badge.pack(pady=(0, 25))
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="🏋️", font=ctk.CTkFont(size=52)).place(
            relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            center, text="GYM PLATFORM",
            font=ctk.CTkFont(family="Segoe UI", size=34, weight="bold"),
            text_color=COLORS["text"]
        ).pack()
        ctk.CTkLabel(
            center, text="TRAIN · TRACK · TRANSFORM",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["primary_light"]
        ).pack(pady=(4, 30))

        # Circular spinner
        self.loader = CircularLoader(center, size=58, thickness=5)
        self.loader.pack(pady=(0, 22))

        # Determinate progress bar
        self.progress = ctk.CTkProgressBar(
            center, width=320, height=8, corner_radius=4,
            progress_color=COLORS["primary"], fg_color=COLORS["bg_elevated"]
        )
        self.progress.pack()
        self.progress.set(0)

        self.status = ctk.CTkLabel(
            center, text=self.steps[0],
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]
        )
        self.status.pack(pady=(14, 0))

    def _run(self, idx=0):
        total = len(self.steps)
        if idx >= total:
            self.loader.stop()
            self.after(250, self.on_done)
            return
        self.status.configure(text=self.steps[idx])
        # Animate the bar toward the next checkpoint
        target = (idx + 1) / total
        self._animate_to(self.progress.get(), target,
                         lambda: self.after(260, lambda: self._run(idx + 1)))

    def _animate_to(self, start, target, done, frames=14, i=0):
        if i > frames:
            self.progress.set(target)
            done()
            return
        # ease-out
        t = i / frames
        value = start + (target - start) * (1 - (1 - t) ** 2)
        self.progress.set(value)
        self.after(16, lambda: self._animate_to(start, target, done, frames, i + 1))


class StatCard(GlowingCard):
    """Animated stat card with icon"""
    def __init__(self, parent, icon, value, label, color=COLORS["primary"], trend=None, **kwargs):
        super().__init__(parent, glow_color=color, **kwargs)
        
        # Icon
        icon_label = ctk.CTkLabel(
            self, text=icon,
            font=ctk.CTkFont(size=36)
        )
        icon_label.pack(pady=(25, 10))
        
        # Value with animation placeholder
        self.value_label = ctk.CTkLabel(
            self, text=value,
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=color
        )
        self.value_label.pack()
        
        # Trend indicator
        if trend:
            trend_frame = ctk.CTkFrame(self, fg_color="transparent")
            trend_frame.pack()
            trend_icon = "↑" if trend > 0 else "↓"
            trend_color = COLORS["success"] if trend > 0 else COLORS["danger"]
            ctk.CTkLabel(
                trend_frame, text=f"{trend_icon} {abs(trend)}%",
                font=ctk.CTkFont(size=11),
                text_color=trend_color
            ).pack(side="left")
        
        # Label
        ctk.CTkLabel(
            self, text=label,
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"]
        ).pack(pady=(5, 25))


class SearchBar(ctk.CTkFrame):
    """Modern search bar with icon"""
    def __init__(self, parent, placeholder="Search...", command=None, **kwargs):
        super().__init__(parent, fg_color=COLORS["bg_elevated"], corner_radius=12, **kwargs)
        
        ctk.CTkLabel(
            self, text="🔍",
            font=ctk.CTkFont(size=16)
        ).pack(side="left", padx=(15, 5))
        
        self.entry = ctk.CTkEntry(
            self, placeholder_text=placeholder,
            border_width=0,
            fg_color="transparent",
            font=ctk.CTkFont(size=14),
            width=250
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=5, pady=8)
        
        if command:
            self.entry.bind("<Return>", lambda e: command(self.entry.get()))
            self.entry.bind("<KeyRelease>", lambda e: command(self.entry.get()))
    
    def get(self):
        return self.entry.get()


class TabButton(ctk.CTkButton):
    """Tab-style button for sections"""
    def __init__(self, parent, text, active=False, **kwargs):
        self.active = active
        fg = COLORS["primary"] if active else "transparent"
        text_color = COLORS["text"] if active else COLORS["text_secondary"]
        super().__init__(
            parent, text=text,
            fg_color=fg,
            text_color=text_color,
            hover_color=COLORS["bg_elevated"],
            corner_radius=10,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold" if active else "normal"),
            **kwargs
        )
    
    def set_active(self, active):
        self.active = active
        if active:
            self.configure(fg_color=COLORS["primary"], text_color=COLORS["text"])
        else:
            self.configure(fg_color="transparent", text_color=COLORS["text_secondary"])


class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login_success):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.on_login_success = on_login_success
        self.setup_ui()
    
    def setup_ui(self):
        # Background decoration
        for i in range(5):
            size = 100 + i * 50
            circle = ctk.CTkFrame(
                self,
                width=size, height=size,
                corner_radius=size//2,
                fg_color=COLORS["primary_glow"],
                border_width=0
            )
            circle.place(relx=0.1 + i*0.2, rely=0.1 + (i%2)*0.6, anchor="center")
        
        # Center container with glass effect
        center_frame = ctk.CTkFrame(
            self, 
            fg_color=COLORS["bg_card"],
            corner_radius=24,
            border_color=COLORS["border"],
            border_width=1
        )
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo with glow
        logo_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        logo_frame.pack(pady=(50, 15))
        
        logo_bg = ctk.CTkLabel(
            logo_frame,
            text="",
            width=80, height=80,
            corner_radius=40,
            fg_color=COLORS["primary"]
        )
        logo_bg.pack()
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🏋️",
            font=ctk.CTkFont(size=38)
        )
        logo_label.place(relx=0.5, rely=0.5, anchor="center")

        # Title with gradient effect (simulated)
        title = ctk.CTkLabel(
            center_frame,
            text="GYM PLATFORM",
            font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
            text_color=COLORS["text"]
        )
        title.pack(pady=(0, 5))

        subtitle = ctk.CTkLabel(
            center_frame,
            text="💪  Welcome back, let's get to work",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_muted"]
        )
        subtitle.pack(pady=(0, 35))
        
        # Username with icon
        username_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        username_frame.pack(pady=8, padx=50)
        
        user_icon_bg = ctk.CTkLabel(
            username_frame,
            text="👤",
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["bg_elevated"],
            width=45, height=45,
            corner_radius=10
        )
        user_icon_bg.pack(side="left")
        
        self.username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text="Username",
            width=260,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            corner_radius=10
        )
        self.username_entry.pack(side="left", padx=(10, 0))
        
        # Password with icon
        password_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        password_frame.pack(pady=8, padx=50)
        
        pass_icon_bg = ctk.CTkLabel(
            password_frame,
            text="🔒",
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["bg_elevated"],
            width=45, height=45,
            corner_radius=10
        )
        pass_icon_bg.pack(side="left")
        
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Password",
            show="•",
            width=260,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"],
            corner_radius=10
        )
        self.password_entry.pack(side="left", padx=(10, 0))
        
        # Remember me
        remember_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
        remember_frame.pack(pady=(10, 5), padx=50, fill="x")
        
        self.remember_var = ctk.BooleanVar(value=False)
        remember_cb = ctk.CTkCheckBox(
            remember_frame,
            text="Remember me",
            variable=self.remember_var,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"],
            checkbox_height=18,
            checkbox_width=18
        )
        remember_cb.pack(side="left")
        
        # Login button with gradient effect
        login_btn = ctk.CTkButton(
            center_frame,
            text="Sign In →",
            width=315,
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            corner_radius=12,
            command=self.login
        )
        login_btn.pack(pady=25, padx=50)
        
        # Error label with animation
        self.error_label = ctk.CTkLabel(
            center_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["danger"]
        )
        self.error_label.pack(pady=(0, 5))
        
        # Demo credentials
        demo_frame = ctk.CTkFrame(center_frame, fg_color=COLORS["bg_elevated"], corner_radius=10)
        demo_frame.pack(pady=(0, 40), padx=50)
        
        ctk.CTkLabel(
            demo_frame,
            text="💡 Demo: admin / admin123",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        ).pack(padx=20, pady=10)
        
        # Bind Enter key
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
    
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_error("Please enter username and password")
            return
        
        # Show loading
        self.error_label.configure(text="Authenticating...", text_color=COLORS["info"])
        self.update()
        
        db = get_db_session()
        try:
            user = db.query(SystemUser).filter(
                SystemUser.username == username,
                SystemUser.is_active == True
            ).first()
            
            if user and verify_password(password, user.hashed_password):
                # Log login
                log = EmployeeLog(
                    employee_id=user.id,
                    employee_username=user.username,
                    action="Logged in"
                )
                db.add(log)
                db.commit()
                
                self.on_login_success({
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role
                })
            else:
                self.show_error("Invalid username or password")
        except Exception as e:
            self.show_error(f"Connection error: {str(e)[:30]}")
        finally:
            db.close()
    
    def show_error(self, message):
        self.error_label.configure(text=f"⚠️ {message}", text_color=COLORS["danger"])


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, user, on_logout):
        super().__init__(parent, fg_color=COLORS["bg_dark"])
        self.user = user
        self.on_logout = on_logout
        self.current_page = "dashboard"
        self.search_text = ""
        self.sidebar_collapsed = False
        self._auto_collapsed = False
        self._last_width = 0
        self._resize_job = None
        self.setup_ui()
        self.load_dashboard()
        # Responsive behaviour + startup reminders
        self.bind("<Configure>", self._on_resize)
        self.after(800, self._show_startup_reminders)
    
    def setup_ui(self):
        # Sidebar with gradient effect
        self.sidebar = ctk.CTkFrame(
            self, width=280,
            fg_color=COLORS["bg_card"],
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Brand section
        self.brand_frame = brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", pady=25, padx=20)

        # Animated logo
        self.logo_container = logo_container = ctk.CTkFrame(
            brand_frame,
            fg_color=COLORS["primary"],
            corner_radius=12,
            width=45, height=45
        )
        logo_container.pack(side="left")
        logo_container.pack_propagate(False)

        brand_logo = ctk.CTkLabel(
            logo_container,
            text="GP",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=COLORS["text"]
        )
        brand_logo.place(relx=0.5, rely=0.5, anchor="center")

        self.brand_text_frame = ctk.CTkFrame(brand_frame, fg_color="transparent")
        self.brand_text_frame.pack(side="left", padx=12)

        ctk.CTkLabel(
            self.brand_text_frame,
            text="Gym Platform",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            self.brand_text_frame,
            text="Train · Track · Transform",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["primary_light"]
        ).pack(anchor="w")

        # Sidebar collapse / expand toggle
        self.collapse_btn = ctk.CTkButton(
            brand_frame, text="☰", width=34, height=34,
            font=ctk.CTkFont(size=16),
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["bg_hover"],
            text_color=COLORS["text_secondary"], corner_radius=8,
            command=self.toggle_sidebar
        )
        self.collapse_btn.pack(side="right")

        # Separator
        sep = ctk.CTkFrame(self.sidebar, fg_color=COLORS["border"], height=1)
        sep.pack(fill="x", padx=20, pady=10)
        
        # Navigation sections
        nav_frame = ctk.CTkScrollableFrame(
            self.sidebar, 
            fg_color="transparent",
            scrollbar_button_color=COLORS["bg_elevated"]
        )
        nav_frame.pack(fill="both", expand=True, pady=5)

        self.nav_buttons = {}
        self.nav_meta = {}
        self.nav_section_labels = []

        # Main navigation
        _main_lbl = ctk.CTkLabel(
            nav_frame,
            text="MAIN MENU",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_muted"]
        )
        _main_lbl.pack(anchor="w", padx=20, pady=(10, 5))
        self.nav_section_labels.append(_main_lbl)

        main_items = [
            ("dashboard", "📊", "Dashboard"),
            ("members", "👥", "Members"),
            ("payments", "💳", "Payments"),
            ("alerts", "🔔", "Alerts"),
        ]
        
        for key, icon, text in main_items:
            btn_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=2)
            
            btn = ctk.CTkButton(
                btn_frame,
                text=f"  {icon}  {text}",
                anchor="w",
                height=42,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_elevated"],
                corner_radius=10,
                command=lambda k=key: self.switch_page(k)
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn
            self.nav_meta[key] = (icon, text)

        # Engagement / outreach services (WhatsApp powered)
        _eng_lbl = ctk.CTkLabel(
            nav_frame,
            text="ENGAGEMENT",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_muted"]
        )
        _eng_lbl.pack(anchor="w", padx=20, pady=(20, 5))
        self.nav_section_labels.append(_eng_lbl)

        engagement_items = [
            ("birthdays", "🎂", "Birthdays"),
            ("broadcast", "📢", "Broadcast"),
        ]

        for key, icon, text in engagement_items:
            btn_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=2)

            btn = ctk.CTkButton(
                btn_frame,
                text=f"  {icon}  {text}",
                anchor="w",
                height=42,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_elevated"],
                corner_radius=10,
                command=lambda k=key: self.switch_page(k)
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn
            self.nav_meta[key] = (icon, text)

        # Employee services
        _svc_lbl = ctk.CTkLabel(
            nav_frame,
            text="SERVICES",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=COLORS["text_muted"]
        )
        _svc_lbl.pack(anchor="w", padx=20, pady=(20, 5))
        self.nav_section_labels.append(_svc_lbl)
        
        service_items = [
            ("checkin", "✅", "Check-In"),
            ("leave", "🏖️", "Leave Request"),
            ("expenses", "💰", "Expenses"),
            ("maintenance", "🔧", "Maintenance"),
        ]
        
        for key, icon, text in service_items:
            btn_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=10, pady=2)
            
            btn = ctk.CTkButton(
                btn_frame,
                text=f"  {icon}  {text}",
                anchor="w",
                height=42,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=COLORS["text_secondary"],
                hover_color=COLORS["bg_elevated"],
                corner_radius=10,
                command=lambda k=key: self.switch_page(k)
            )
            btn.pack(fill="x")
            self.nav_buttons[key] = btn
            self.nav_meta[key] = (icon, text)

        # Admin only sections
        if self.user["role"] == "admin":
            _admin_lbl = ctk.CTkLabel(
                nav_frame,
                text="ADMIN TOOLS",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text_muted"]
            )
            _admin_lbl.pack(anchor="w", padx=20, pady=(20, 5))
            self.nav_section_labels.append(_admin_lbl)
            
            admin_items = [
                ("employees", "👔", "Employees"),
                ("activity", "👁️", "Activity Tracker"),
                ("products", "📦", "Products"),
                ("finance", "💵", "Finance"),
                ("reports", "📈", "Reports"),
                ("settings", "⚙️", "Settings"),
                ("logs", "📜", "Audit Logs"),
            ]
            
            for key, icon, text in admin_items:
                btn_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
                btn_frame.pack(fill="x", padx=10, pady=2)
                
                btn = ctk.CTkButton(
                    btn_frame,
                    text=f"  {icon}  {text}",
                    anchor="w",
                    height=42,
                    font=ctk.CTkFont(size=14),
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"],
                    hover_color=COLORS["bg_elevated"],
                    corner_radius=10,
                    command=lambda k=key: self.switch_page(k)
                )
                btn.pack(fill="x")
                self.nav_buttons[key] = btn
                self.nav_meta[key] = (icon, text)
        
        # User section at bottom
        user_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=COLORS["bg_elevated"],
            corner_radius=12
        )
        user_frame.pack(fill="x", padx=15, pady=20)
        
        user_inner = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_inner.pack(fill="x", padx=12, pady=12)
        
        # User avatar
        avatar = ctk.CTkLabel(
            user_inner,
            text=self.user["full_name"][0].upper(),
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS["primary"],
            text_color=COLORS["text"],
            width=42,
            height=42,
            corner_radius=10
        )
        avatar.pack(side="left")
        
        # User info
        user_info = ctk.CTkFrame(user_inner, fg_color="transparent")
        user_info.pack(side="left", fill="x", expand=True, padx=10)
        self.user_text_frame = user_info

        ctk.CTkLabel(
            user_info,
            text=self.user["full_name"],
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")
        
        role_colors = {"admin": COLORS["gold"], "employee": COLORS["info"]}
        ctk.CTkLabel(
            user_info,
            text=f"● {self.user['role'].title()}",
            font=ctk.CTkFont(size=11),
            text_color=role_colors.get(self.user["role"], COLORS["text_muted"])
        ).pack(anchor="w")
        
        # Logout button
        logout_btn = ctk.CTkButton(
            user_inner,
            text="⏻",
            width=38,
            height=38,
            font=ctk.CTkFont(size=18),
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_dark"],
            corner_radius=10,
            command=self.on_logout
        )
        logout_btn.pack(side="right")
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"])
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        # Update initial button state
        self.nav_buttons["dashboard"].configure(
            fg_color=COLORS["primary"],
            text_color=COLORS["text"]
        )

    # ------------------------------------------------------------------
    # Responsive layout helpers
    # ------------------------------------------------------------------
    def toggle_sidebar(self):
        self._apply_sidebar_state(not self.sidebar_collapsed)

    def _apply_sidebar_state(self, collapsed):
        if collapsed == self.sidebar_collapsed:
            return
        self.sidebar_collapsed = collapsed

        if collapsed:
            self.sidebar.configure(width=74)
            # Hide the brand text + logo and center the ☰ toggle so it stays
            # fully visible and clickable to re-open the sidebar.
            self.brand_text_frame.pack_forget()
            self.logo_container.pack_forget()
            self.user_text_frame.pack_forget()
            self.brand_frame.pack_configure(padx=12)
            self.collapse_btn.configure(text="☰")
            self.collapse_btn.pack_configure(side="top")
            for lbl in self.nav_section_labels:
                if not hasattr(lbl, "_orig_text"):
                    lbl._orig_text = lbl.cget("text")
                lbl.configure(text="")
            for key, btn in self.nav_buttons.items():
                icon, _ = self.nav_meta.get(key, ("•", ""))
                btn.configure(text=icon, anchor="center")
        else:
            self.sidebar.configure(width=280)
            self.brand_frame.pack_configure(padx=20)
            # Restore logo, brand text, and the toggle on the right (keep order).
            self.logo_container.pack_forget()
            self.brand_text_frame.pack_forget()
            self.collapse_btn.pack_forget()
            self.logo_container.pack(side="left")
            self.brand_text_frame.pack(side="left", padx=12)
            self.collapse_btn.configure(text="☰")
            self.collapse_btn.pack(side="right")
            self.user_text_frame.pack(side="left", fill="x", expand=True, padx=10)
            for lbl in self.nav_section_labels:
                if hasattr(lbl, "_orig_text"):
                    lbl.configure(text=lbl._orig_text)
            for key, btn in self.nav_buttons.items():
                icon, text = self.nav_meta.get(key, ("•", ""))
                btn.configure(text=f"  {icon}  {text}", anchor="w")

    def grid_cols(self, wide=4, narrow=2, tiny=1):
        """Choose a responsive column count based on the current window width."""
        w = self.winfo_width() or 1200
        if w < 820:
            return tiny
        if w < 1180:
            return narrow
        return wide

    def _on_resize(self, event):
        # Only react to top-level window resizes
        if event.widget is not self:
            return
        w = event.width
        if w == self._last_width:
            return
        self._last_width = w

        # Auto-collapse the sidebar on narrow windows (respect manual toggle)
        if w < 1080 and not self.sidebar_collapsed:
            self._auto_collapsed = True
            self._apply_sidebar_state(True)
        elif w >= 1080 and self.sidebar_collapsed and self._auto_collapsed:
            self._auto_collapsed = False
            self._apply_sidebar_state(False)

        # Debounced reflow of the active page's responsive grids
        if self._resize_job is not None:
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(220, self._reflow_current_page)

    def _reflow_current_page(self):
        self._resize_job = None
        # Re-render pages that use responsive card grids
        if self.current_page in ("dashboard", "expenses", "payments", "finance",
                                  "birthdays", "broadcast"):
            self.switch_page(self.current_page)

    # ------------------------------------------------------------------
    # WhatsApp helpers
    # ------------------------------------------------------------------
    def _log_action(self, action):
        db = get_db_session()
        try:
            db.add(EmployeeLog(
                employee_id=self.user["id"],
                employee_username=self.user["username"],
                action=action
            ))
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

    def open_whatsapp(self, phone, message, log_label=None):
        """Open WhatsApp (Desktop/Web) with a pre-filled message."""
        if not phone:
            messagebox.showwarning("No phone number", "This member has no phone number on file.")
            return
        try:
            send_whatsapp(phone, message)
            if log_label:
                self._log_action(log_label)
        except Exception as e:
            messagebox.showerror("WhatsApp error", str(e))

    def whatsapp_message_dialog(self, phone, default_message, title="Send WhatsApp",
                                recipient="", log_label=None):
        """Show an editable message before opening WhatsApp."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("480x440")
        dialog.configure(fg_color=COLORS["bg_card"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        present_modal(dialog, 480, 440)

        header = ctk.CTkFrame(dialog, fg_color=COLORS["success"], corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header, text=f"💬 {title}",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text"]
        ).pack(pady=18)

        body = ctk.CTkFrame(dialog, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=18)

        if recipient:
            ctk.CTkLabel(
                body, text=f"📞 {recipient}  •  {phone}",
                font=ctk.CTkFont(size=13), text_color=COLORS["text_secondary"]
            ).pack(anchor="w", pady=(0, 10))

        textbox = ctk.CTkTextbox(
            body, height=170, fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"], border_width=1, corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        textbox.pack(fill="both", expand=True)
        textbox.insert("1.0", default_message)

        btns = ctk.CTkFrame(dialog, fg_color="transparent")
        btns.pack(fill="x", padx=24, pady=(0, 20))

        def do_send():
            msg = textbox.get("1.0", "end").strip()
            dialog.destroy()
            self.open_whatsapp(phone, msg, log_label=log_label)

        ctk.CTkButton(
            btns, text="Cancel", fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["bg_hover"], height=44, corner_radius=10,
            command=dialog.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(
            btns, text="📲 Open WhatsApp", fg_color=COLORS["success"],
            hover_color=COLORS["success_dark"], height=44, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"), command=do_send
        ).pack(side="right", expand=True, fill="x")

    # ------------------------------------------------------------------
    # Startup expiry / birthday reminders
    # ------------------------------------------------------------------
    def _show_startup_reminders(self):
        settings = load_settings()
        show_exp = settings.get("auto_expiry_enabled", True)
        show_bday = settings.get("auto_birthday_enabled", True)
        if not show_exp and not show_bday:
            return
        db = get_db_session()
        try:
            today = date.today()
            soon = today + timedelta(days=7)
            expiring = db.query(Member).filter(
                Member.is_active == True,
                Member.end_date >= today,
                Member.end_date <= soon
            ).order_by(Member.end_date.asc()).all() if show_exp else []

            birthdays = []
            if show_bday:
                for m in db.query(Member).filter(Member.is_active == True).all():
                    if m.date_of_birth and m.date_of_birth.month == today.month \
                            and m.date_of_birth.day == today.day:
                        birthdays.append(m)

            data = [{
                "id": m.id, "name": m.full_name, "phone": m.phone_number,
                "end_date": m.end_date, "plan": m.gym_plan,
                "days": (m.end_date - today).days
            } for m in expiring]
            bdays = [{
                "id": m.id, "name": m.full_name, "phone": m.phone_number,
                "age": compute_age(m.date_of_birth)
            } for m in birthdays]
        finally:
            db.close()

        if data or bdays:
            self._reminder_popup(data, bdays, settings)

    def _reminder_popup(self, expiring, birthdays, settings):
        popup = ctk.CTkToplevel(self)
        popup.title("Today's Reminders")
        popup.geometry("560x600")
        popup.configure(fg_color=COLORS["bg_card"])
        popup.transient(self.winfo_toplevel())
        present_modal(popup, 560, 600)

        header = ctk.CTkFrame(popup, fg_color=COLORS["primary"], corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header, text="🔔 Daily Reminders",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["text"]
        ).pack(pady=18)

        body = ctk.CTkScrollableFrame(popup, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=14)

        if birthdays:
            ctk.CTkLabel(
                body, text="🎂 Birthdays Today",
                font=ctk.CTkFont(size=15, weight="bold"), text_color=COLORS["accent"]
            ).pack(anchor="w", pady=(6, 6))
            for b in birthdays:
                self._reminder_row(
                    body, f"{b['name']} turns {b['age']} 🎉", b["phone"],
                    COLORS["accent"],
                    lambda b=b: self.whatsapp_message_dialog(
                        b["phone"],
                        render_template(settings["birthday_message"],
                                        name=b["name"], age=b["age"]),
                        title=f"Birthday wish · {b['name']}",
                        recipient=b["name"], log_label=f"Birthday WhatsApp: {b['name']}")
                )

        if expiring:
            ctk.CTkLabel(
                body, text="⏰ Memberships Expiring Soon",
                font=ctk.CTkFont(size=15, weight="bold"), text_color=COLORS["warning"]
            ).pack(anchor="w", pady=(14, 6))
            for e in expiring:
                label = f"{e['name']} · expires in {e['days']}d ({e['end_date']})"
                self._reminder_row(
                    body, label, e["phone"], COLORS["warning"],
                    lambda e=e: self.whatsapp_message_dialog(
                        e["phone"],
                        render_template(settings["expiry_message"],
                                        name=e["name"], days=e["days"],
                                        plan=e["plan"], date=str(e["end_date"])),
                        title=f"Renewal reminder · {e['name']}",
                        recipient=e["name"], log_label=f"Expiry WhatsApp: {e['name']}"),
                    on_renew=lambda e=e: (popup.destroy(), self.renew_member(e["id"]))
                )

        ctk.CTkButton(
            popup, text="Close", fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["bg_hover"], height=44, corner_radius=10,
            command=popup.destroy
        ).pack(fill="x", padx=18, pady=(0, 18))

    def _reminder_row(self, parent, text, phone, color, on_send, on_renew=None):
        row = ctk.CTkFrame(parent, fg_color=COLORS["bg_elevated"], corner_radius=10)
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(
            row, text=text, font=ctk.CTkFont(size=13),
            text_color=COLORS["text"], anchor="w", justify="left"
        ).pack(side="left", padx=14, pady=12, fill="x", expand=True)
        ctk.CTkButton(
            row, text="📲 WhatsApp", width=110, height=34,
            fg_color=COLORS["success"], hover_color=COLORS["success_dark"],
            corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"),
            command=on_send
        ).pack(side="right", padx=(6, 12))
        if on_renew:
            ctk.CTkButton(
                row, text="🔄 Renew", width=90, height=34,
                fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"),
                command=on_renew
            ).pack(side="right", padx=2)

    def switch_page(self, page):
        # Update button states with animation
        for key, btn in self.nav_buttons.items():
            if key == page:
                btn.configure(fg_color=COLORS["primary"], text_color=COLORS["text"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_secondary"])
        
        self.current_page = page
        
        # Clear content with transition
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Load page
        pages = {
            "dashboard": self.load_dashboard,
            "members": self.load_members,
            "employees": self.load_employees,
            "activity": self.load_activity,
            "birthdays": self.load_birthdays,
            "broadcast": self.load_broadcast,
            "expenses": self.load_expenses,
            "payments": self.load_payments,
            "alerts": self.load_alerts,
            "finance": self.load_finance,
            "checkin": self.load_checkin,
            "leave": self.load_leave,
            "products": self.load_products,
            "reports": self.load_reports,
            "settings": self.load_settings,
            "logs": self.load_logs,
            "maintenance": self.load_maintenance,
        }
        
        if page in pages:
            pages[page]()
    
    def create_header(self, title, subtitle=None, show_search=False, search_command=None):
        """Create a consistent header for all pages"""
        header = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 15))
        
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left")
        
        ctk.CTkLabel(
            title_frame,
            text=title,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")
        
        if subtitle:
            ctk.CTkLabel(
                title_frame,
                text=subtitle,
                font=ctk.CTkFont(size=13),
                text_color=COLORS["text_muted"]
            ).pack(anchor="w")
        
        if show_search:
            search = SearchBar(header, command=search_command)
            search.pack(side="right")
            return header, search
        
        return header
    
    @scrollable_page
    def load_dashboard(self):
        self.create_header("Dashboard", f"Welcome back, {self.user['full_name']}!")
        
        # Stats grid
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=10)
        
        db = get_db_session()
        try:
            today = date.today()
            week = today + timedelta(days=7)
            month_start = today.replace(day=1)
            
            # Get stats
            active = db.query(Member).filter(Member.is_active == True).count()
            expiring = db.query(Member).filter(
                Member.is_active == True,
                Member.end_date >= today,
                Member.end_date <= week
            ).count()
            expired = db.query(Member).filter(
                Member.is_active == True,
                Member.end_date < today
            ).count()
            
            payments = db.query(Payment).filter(Payment.paid_at >= month_start).all()
            revenue = sum(float(p.amount) for p in payments) if payments else 0
            
            # Additional stats
            total_members = db.query(Member).count()
            new_this_month = db.query(Member).filter(Member.created_at >= month_start).count()
            
            stats = [
                ("👥", str(active), "Active Members", COLORS["primary"], 5),
                ("⏰", str(expiring), "Expiring Soon", COLORS["warning"], None),
                ("⚠️", str(expired), "Expired", COLORS["danger"], -12),
                ("💵", f"${revenue:,.0f}", "Monthly Revenue", COLORS["success"], 8),
            ]
            
            cols = self.grid_cols(wide=4, narrow=2, tiny=1)
            for i, (icon, value, label, color, trend) in enumerate(stats):
                card = StatCard(stats_frame, icon, value, label, color, trend)
                card.grid(row=i // cols, column=i % cols, padx=10, pady=10, sticky="nsew")
            for c in range(cols):
                stats_frame.grid_columnconfigure(c, weight=1)
            
        finally:
            db.close()
        
        # Quick actions and recent activity
        main_content = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_content.pack(fill="both", expand=True, padx=30, pady=10)
        # Responsive: stack the two panels on narrow windows
        stacked = (self.winfo_width() or 1200) < 1000
        if stacked:
            main_content.grid_columnconfigure(0, weight=1)
        else:
            main_content.grid_columnconfigure(0, weight=2)
            main_content.grid_columnconfigure(1, weight=1)

        # Recent members
        recent_frame = GlowingCard(main_content)
        recent_frame.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        recent_header = ctk.CTkFrame(recent_frame, fg_color="transparent")
        recent_header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            recent_header,
            text="📋 Recent Members",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"]
        ).pack(side="left")
        
        ctk.CTkButton(
            recent_header,
            text="View All →",
            fg_color="transparent",
            text_color=COLORS["primary"],
            hover_color=COLORS["bg_elevated"],
            font=ctk.CTkFont(size=12),
            width=80,
            command=lambda: self.switch_page("members")
        ).pack(side="right")
        
        # Members list
        db = get_db_session()
        try:
            members = db.query(Member).order_by(Member.id.desc()).limit(8).all()
            today = date.today()
            
            for m in members:
                row = ctk.CTkFrame(recent_frame, fg_color=COLORS["bg_elevated"], corner_radius=10)
                row.pack(fill="x", padx=15, pady=4)
                
                # Avatar
                avatar = ctk.CTkLabel(
                    row,
                    text=m.full_name[0].upper(),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    fg_color=COLORS["primary"],
                    width=35, height=35,
                    corner_radius=8
                )
                avatar.pack(side="left", padx=10, pady=8)
                
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)
                
                ctk.CTkLabel(
                    info,
                    text=m.full_name,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS["text"]
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    info,
                    text=f"📞 {m.phone_number}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_muted"]
                ).pack(anchor="w")
                
                # Status badge
                if m.is_active and m.end_date >= today:
                    status, color = "Active", COLORS["success"]
                elif m.is_active and m.end_date < today:
                    status, color = "Expired", COLORS["danger"]
                else:
                    status, color = "Inactive", COLORS["text_muted"]
                
                status_badge = ctk.CTkLabel(
                    row,
                    text=f"● {status}",
                    font=ctk.CTkFont(size=11),
                    text_color=color
                )
                status_badge.pack(side="right", padx=15)
                
        finally:
            db.close()
        
        # Quick actions
        actions_frame = GlowingCard(main_content, glow_color=COLORS["secondary"])
        if stacked:
            actions_frame.grid(row=1, column=0, padx=0, pady=10, sticky="nsew")
        else:
            actions_frame.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        
        ctk.CTkLabel(
            actions_frame,
            text="⚡ Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=15)
        
        actions = [
            ("➕ Add Member", COLORS["success"], lambda: self.add_member_dialog()),
            ("🎂 Birthdays", COLORS["accent"], lambda: self.switch_page("birthdays")),
            ("💳 New Payment", COLORS["primary"], lambda: self.switch_page("payments")),
            ("📢 Broadcast", COLORS["info"], lambda: self.switch_page("broadcast")),
        ]
        
        for text, color, cmd in actions:
            btn = ctk.CTkButton(
                actions_frame,
                text=text,
                fg_color=color,
                hover_color=COLORS["bg_hover"],
                font=ctk.CTkFont(size=13, weight="bold"),
                height=45,
                corner_radius=10,
                anchor="w",
                command=cmd
            )
            btn.pack(fill="x", padx=15, pady=5)
        
        # Today's summary
        summary_frame = ctk.CTkFrame(actions_frame, fg_color=COLORS["bg_elevated"], corner_radius=10)
        summary_frame.pack(fill="x", padx=15, pady=(15, 15))
        
        ctk.CTkLabel(
            summary_frame,
            text="📊 Today's Summary",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=15, pady=(12, 8))
        
        db = get_db_session()
        try:
            today_payments = db.query(Payment).filter(
                Payment.paid_at >= datetime.combine(today, datetime.min.time())
            ).all()
            today_revenue = sum(float(p.amount) for p in today_payments) if today_payments else 0
            
            ctk.CTkLabel(
                summary_frame,
                text=f"Revenue: ${today_revenue:,.2f}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["success"]
            ).pack(anchor="w", padx=15)
            
            ctk.CTkLabel(
                summary_frame,
                text=f"Transactions: {len(today_payments)}",
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            ).pack(anchor="w", padx=15, pady=(0, 12))
        finally:
            db.close()
    
    def load_members(self):
        header, search = self.create_header(
            "Members Management", 
            "Manage your gym members",
            show_search=True,
            search_command=self.filter_members
        )
        
        # Action buttons
        action_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=(0, 10))
        
        ctk.CTkButton(
            action_frame,
            text="➕ Add Member",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=10,
            command=self.add_member_dialog
        ).pack(side="left")
        
        ctk.CTkButton(
            action_frame,
            text="📤 Export",
            fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_elevated"],
            font=ctk.CTkFont(size=13),
            height=40,
            corner_radius=10,
            command=self.export_members
        ).pack(side="left", padx=10)
        
        # Filter tabs
        tabs_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        tabs_frame.pack(side="right")
        
        self.member_filter = "all"
        self.member_tabs = {}
        
        for filter_key, label in [("all", "All"), ("active", "Active"), ("expired", "Expired"), ("inactive", "Inactive")]:
            tab = TabButton(
                tabs_frame, text=label, 
                active=(filter_key == "all"),
                command=lambda f=filter_key: self.filter_members_by_status(f)
            )
            tab.pack(side="left", padx=3)
            self.member_tabs[filter_key] = tab
        
        # Members list
        self.members_list = ctk.CTkScrollableFrame(
            self.content_frame, 
            fg_color=COLORS["bg_card"], 
            corner_radius=16
        )
        self.members_list.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.refresh_members_list()
    
    def refresh_members_list(self, search_text=""):
        # Clear existing
        for widget in self.members_list.winfo_children():
            widget.destroy()
        
        db = get_db_session()
        try:
            query = db.query(Member).order_by(Member.id.desc())
            
            if search_text:
                query = query.filter(
                    Member.full_name.ilike(f"%{search_text}%") | 
                    Member.phone_number.ilike(f"%{search_text}%")
                )
            
            members = query.all()
            today = date.today()
            
            # Table header
            header = ctk.CTkFrame(self.members_list, fg_color=COLORS["bg_elevated"], corner_radius=8)
            header.pack(fill="x", padx=10, pady=(10, 5))
            
            headers = [("ID", 60), ("Member", 200), ("Phone", 120), ("Plan", 100), ("Expires", 100), ("Status", 80), ("Actions", 100)]
            for text, width in headers:
                ctk.CTkLabel(
                    header, text=text,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["text_muted"],
                    width=width
                ).pack(side="left", padx=10, pady=10)
            
            for m in members:
                # Filter logic
                is_active = m.is_active and m.end_date >= today
                is_expired = m.is_active and m.end_date < today
                
                if self.member_filter == "active" and not is_active:
                    continue
                if self.member_filter == "expired" and not is_expired:
                    continue
                if self.member_filter == "inactive" and m.is_active:
                    continue
                
                row = ctk.CTkFrame(self.members_list, fg_color=COLORS["bg_elevated"], corner_radius=10)
                row.pack(fill="x", padx=10, pady=3)
                
                # ID
                ctk.CTkLabel(
                    row, text=f"#{m.id}",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_muted"],
                    width=60
                ).pack(side="left", padx=10, pady=12)
                
                # Member info
                member_frame = ctk.CTkFrame(row, fg_color="transparent", width=200)
                member_frame.pack(side="left", padx=10)
                member_frame.pack_propagate(False)
                
                ctk.CTkLabel(
                    member_frame,
                    text=m.full_name,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS["text"]
                ).pack(anchor="w")
                
                # Phone
                ctk.CTkLabel(
                    row, text=m.phone_number,
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_secondary"],
                    width=120
                ).pack(side="left", padx=10)
                
                # Plan
                ctk.CTkLabel(
                    row, text=m.gym_plan or "Standard",
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_secondary"],
                    width=100
                ).pack(side="left", padx=10)
                
                # Expiry
                ctk.CTkLabel(
                    row, text=str(m.end_date),
                    font=ctk.CTkFont(size=12),
                    text_color=COLORS["text_secondary"],
                    width=100
                ).pack(side="left", padx=10)
                
                # Status
                if is_active:
                    status, color = "Active", COLORS["success"]
                elif is_expired:
                    status, color = "Expired", COLORS["danger"]
                else:
                    status, color = "Inactive", COLORS["text_muted"]
                
                ctk.CTkLabel(
                    row, text=f"● {status}",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=color,
                    width=80
                ).pack(side="left", padx=10)
                
                # Actions
                actions_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
                actions_frame.pack(side="left", padx=10)
                
                ctk.CTkButton(
                    actions_frame,
                    text="✏️",
                    width=32, height=32,
                    fg_color=COLORS["bg_card"],
                    hover_color=COLORS["primary"],
                    corner_radius=8,
                    command=lambda mid=m.id: self.edit_member_dialog(mid)
                ).pack(side="left", padx=2)
                
                if is_expired:
                    ctk.CTkButton(
                        actions_frame,
                        text="🔄",
                        width=32, height=32,
                        fg_color=COLORS["success"],
                        hover_color=COLORS["success_dark"],
                        corner_radius=8,
                        command=lambda mid=m.id: self.renew_member(mid)
                    ).pack(side="left", padx=2)
                
        finally:
            db.close()
    
    def filter_members(self, text):
        self.search_text = text
        self.refresh_members_list(text)
    
    def filter_members_by_status(self, status):
        self.member_filter = status
        for key, tab in self.member_tabs.items():
            tab.set_active(key == status)
        self.refresh_members_list(self.search_text)
    
    def _apply_plan_days(self, fields, plan):
        """When a plan is chosen, auto-fill the editable Duration (Days) field."""
        days = PLAN_DURATIONS.get(plan)
        if days and "duration_days" in fields:
            w = fields["duration_days"]
            w.delete(0, "end")
            w.insert(0, str(days))

    def _apply_plan_end(self, fields, plan):
        """When a plan is chosen during edit/renew, recompute the end date."""
        days = PLAN_DURATIONS.get(plan)
        if days and "end_date" in fields:
            fields["end_date"].set_date(date.today() + timedelta(days=days))

    def add_member_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Member")
        dialog.geometry("500x650")
        dialog.configure(fg_color=COLORS["bg_card"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center
        present_modal(dialog, 500, 650)
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color=COLORS["primary"], corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text="➕ Add New Member",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"]
        ).pack(pady=20)
        
        # Form
        form_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        fields = {}
        field_configs = [
            ("full_name", "Full Name", "Enter full name"),
            ("phone_number", "Phone Number", "+1234567890"),
            ("date_of_birth", "Date of Birth", "YYYY-MM-DD"),
            ("gym_plan", "Gym Plan", "Monthly, Quarterly, Yearly"),
            ("gym_fee", "Fee Paid ($)", "0.00"),
            ("duration_days", "Duration (Days)", "30"),
        ]
        
        for key, label, placeholder in field_configs:
            ctk.CTkLabel(
                form_frame,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text"]
            ).pack(anchor="w", pady=(15, 5))

            if key == "phone_number":
                widget = PhoneField(
                    form_frame,
                    default_code=f"+{load_settings().get('country_code', '212')}")
            elif key == "date_of_birth":
                widget = DateField(form_frame, placeholder="Pick date of birth…")
            elif key == "gym_plan":
                widget = ctk.CTkComboBox(
                    form_frame, values=PLAN_OPTIONS, height=45,
                    font=ctk.CTkFont(size=14), fg_color=COLORS["bg_dark"],
                    border_color=COLORS["border"], button_color=COLORS["primary"],
                    button_hover_color=COLORS["primary_dark"], corner_radius=10,
                    command=lambda v: self._apply_plan_days(fields, v)
                )
                widget.set("Monthly")
            else:
                widget = ctk.CTkEntry(
                    form_frame,
                    placeholder_text=placeholder,
                    height=45,
                    font=ctk.CTkFont(size=14),
                    fg_color=COLORS["bg_dark"],
                    border_color=COLORS["border"],
                    corner_radius=10
                )
            widget.pack(fill="x")
            fields[key] = widget

        # Pre-fill the duration for the default plan
        self._apply_plan_days(fields, "Monthly")

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)

        def save_member():
            db = get_db_session()
            try:
                if not fields["full_name"].get().strip():
                    messagebox.showwarning("Missing name", "Please enter the member's full name.")
                    return
                if not fields["phone_number"].get():
                    messagebox.showwarning("Missing phone", "Please enter a phone number.")
                    return
                today = date.today()
                duration = int(fields["duration_days"].get() or 30)

                member = Member(
                    full_name=fields["full_name"].get(),
                    phone_number=fields["phone_number"].get(),
                    date_of_birth=fields["date_of_birth"].get() or "2000-01-01",
                    gym_plan=fields["gym_plan"].get() or "Monthly",
                    gym_fee_paid=float(fields["gym_fee"].get() or 0),
                    start_date=today,
                    end_date=today + timedelta(days=duration),
                    is_active=True
                )
                db.add(member)
                
                # Log action
                log = EmployeeLog(
                    employee_id=self.user["id"],
                    employee_username=self.user["username"],
                    action=f"Added member: {member.full_name}"
                )
                db.add(log)
                db.commit()
                
                dialog.destroy()
                self.switch_page("members")
                messagebox.showinfo("Success", "Member added successfully!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                db.close()
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["bg_hover"],
            height=45,
            corner_radius=10,
            command=dialog.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Save Member",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            height=45,
            corner_radius=10,
            command=save_member
        ).pack(side="right", expand=True, fill="x")
    
    def edit_member_dialog(self, member_id, renew=False):
        db = get_db_session()
        try:
            member = db.query(Member).filter(Member.id == member_id).first()
            if not member:
                messagebox.showerror("Error", "Member not found")
                return

            dialog = ctk.CTkToplevel(self)
            dialog.title(f"{'Renew' if renew else 'Edit'} Member - {member.full_name}")
            dialog.geometry("500x640")
            dialog.configure(fg_color=COLORS["bg_card"])
            dialog.transient(self.winfo_toplevel())
            dialog.grab_set()

            # Center
            present_modal(dialog, 500, 640)

            # Header
            header = ctk.CTkFrame(
                dialog, fg_color=COLORS["success"] if renew else COLORS["info"],
                corner_radius=0)
            header.pack(fill="x")

            ctk.CTkLabel(
                header,
                text=(f"🔄 Renew Membership — {member.full_name}" if renew
                      else f"✏️ Edit Member #{member_id}"),
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=COLORS["text"]
            ).pack(pady=20)

            if renew:
                ctk.CTkLabel(
                    header,
                    text="Pick a plan to auto-set the new expiry date, then save.",
                    font=ctk.CTkFont(size=12), text_color=COLORS["text"]
                ).pack(pady=(0, 14))
            
            # Form
            form_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
            form_frame.pack(fill="both", expand=True, padx=30, pady=20)
            
            fields = {}
            field_configs = [
                ("full_name", "Full Name", member.full_name),
                ("phone_number", "Phone Number", member.phone_number),
                ("date_of_birth", "Date of Birth", str(member.date_of_birth)),
                ("gym_plan", "Gym Plan", member.gym_plan),
                ("gym_fee", "Fee Paid ($)", str(member.gym_fee_paid)),
                ("end_date", "End Date", str(member.end_date)),
            ]

            for key, label, value in field_configs:
                ctk.CTkLabel(
                    form_frame,
                    text=label,
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS["text"]
                ).pack(anchor="w", pady=(15, 5))

                if key == "phone_number":
                    widget = PhoneField(
                        form_frame, initial=value,
                        default_code=f"+{load_settings().get('country_code', '212')}")
                elif key in ("date_of_birth", "end_date"):
                    widget = DateField(form_frame, initial=value)
                elif key == "gym_plan":
                    widget = ctk.CTkComboBox(
                        form_frame, values=PLAN_OPTIONS, height=45,
                        font=ctk.CTkFont(size=14), fg_color=COLORS["bg_dark"],
                        border_color=COLORS["border"], button_color=COLORS["primary"],
                        button_hover_color=COLORS["primary_dark"], corner_radius=10,
                        command=lambda v: self._apply_plan_end(fields, v)
                    )
                    widget.set(value or "Monthly")
                else:
                    widget = ctk.CTkEntry(
                        form_frame,
                        height=45,
                        font=ctk.CTkFont(size=14),
                        fg_color=COLORS["bg_dark"],
                        border_color=COLORS["border"],
                        corner_radius=10
                    )
                    widget.insert(0, value)
                widget.pack(fill="x")
                fields[key] = widget

            # In renew mode, default the new expiry from the current plan right away
            if renew:
                self._apply_plan_end(fields, fields["gym_plan"].get())
            
            # Active status
            ctk.CTkLabel(
                form_frame,
                text="Status",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text"]
            ).pack(anchor="w", pady=(15, 5))
            
            active_var = ctk.BooleanVar(value=True if renew else member.is_active)
            ctk.CTkSwitch(
                form_frame,
                text="Active",
                variable=active_var,
                onvalue=True,
                offvalue=False
            ).pack(anchor="w")

            # Buttons
            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(fill="x", padx=30, pady=20)

            def update_member():
                db2 = get_db_session()
                try:
                    m = db2.query(Member).filter(Member.id == member_id).first()
                    m.full_name = fields["full_name"].get()
                    m.phone_number = fields["phone_number"].get() or m.phone_number
                    if fields["date_of_birth"].get():
                        m.date_of_birth = fields["date_of_birth"].get()
                    m.gym_plan = fields["gym_plan"].get()
                    fee = float(fields["gym_fee"].get() or 0)
                    m.gym_fee_paid = fee
                    if fields["end_date"].get():
                        m.end_date = fields["end_date"].get()
                    m.is_active = active_var.get()
                    m.renewal_notified = False

                    action = (f"Renewed membership: {m.full_name} (until {m.end_date})"
                              if renew else f"Updated member: {m.full_name}")
                    db2.add(EmployeeLog(
                        employee_id=self.user["id"],
                        employee_username=self.user["username"],
                        action=action
                    ))
                    # On renewal, record the payment so it shows in Payments
                    if renew and fee > 0:
                        db2.add(Payment(
                            member_id=m.id, amount=fee, payment_type="Renewal",
                            description=f"{m.gym_plan} plan renewal"
                        ))
                    db2.commit()

                    dialog.destroy()
                    self.switch_page("members")
                    messagebox.showinfo(
                        "Success",
                        "Membership renewed!" if renew else "Member updated!")
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                finally:
                    db2.close()

            ctk.CTkButton(
                btn_frame,
                text="Cancel",
                fg_color=COLORS["bg_elevated"],
                hover_color=COLORS["bg_hover"],
                height=45,
                corner_radius=10,
                command=dialog.destroy
            ).pack(side="left", expand=True, fill="x", padx=(0, 10))

            ctk.CTkButton(
                btn_frame,
                text="🔄 Confirm Renewal" if renew else "Update Member",
                fg_color=COLORS["success"] if renew else COLORS["info"],
                hover_color=COLORS["success_dark"] if renew else COLORS["primary_dark"],
                height=45,
                corner_radius=10,
                command=update_member
            ).pack(side="right", expand=True, fill="x")

        finally:
            db.close()

    def renew_member(self, member_id):
        # Renewal uses the same data-entry form as Update (pre-filled)
        self.edit_member_dialog(member_id, renew=True)

    def _renew_member_legacy(self, member_id):
        if messagebox.askyesno("Renew Membership", "Renew membership for 30 days?"):
            db = get_db_session()
            try:
                member = db.query(Member).filter(Member.id == member_id).first()
                if member:
                    today = date.today()
                    member.end_date = today + timedelta(days=30)
                    member.is_active = True

                    log = EmployeeLog(
                        employee_id=self.user["id"],
                        employee_username=self.user["username"],
                        action=f"Renewed membership: {member.full_name}"
                    )
                    db.add(log)
                    db.commit()
                    
                    self.switch_page("members")
                    messagebox.showinfo("Success", "Membership renewed!")
            finally:
                db.close()
    
    def export_members(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if filepath:
            db = get_db_session()
            try:
                members = db.query(Member).all()
                with open(filepath, 'w') as f:
                    f.write("ID,Name,Phone,Plan,Start Date,End Date,Fee,Active\n")
                    for m in members:
                        f.write(f"{m.id},{m.full_name},{m.phone_number},{m.gym_plan},{m.start_date},{m.end_date},{m.gym_fee_paid},{m.is_active}\n")
                messagebox.showinfo("Success", f"Exported {len(members)} members!")
            finally:
                db.close()
    
    def load_employees(self):
        header = self.create_header("Employee Management", "Manage staff and permissions")
        
        # Add employee button
        action_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=(0, 10))
        
        if self.user["role"] == "admin":
            ctk.CTkButton(
                action_frame,
                text="➕ Add Employee",
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_dark"],
                font=ctk.CTkFont(size=13, weight="bold"),
                height=40,
                corner_radius=10,
                command=self.add_employee_dialog
            ).pack(side="left")
        
        list_frame = ctk.CTkScrollableFrame(
            self.content_frame, 
            fg_color=COLORS["bg_card"], 
            corner_radius=16
        )
        list_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        db = get_db_session()
        try:
            employees = db.query(SystemUser).all()
            
            for e in employees:
                row = ctk.CTkFrame(list_frame, fg_color=COLORS["bg_elevated"], corner_radius=12)
                row.pack(fill="x", padx=10, pady=5)
                
                # Avatar
                avatar_color = COLORS["gold"] if e.role == "admin" else COLORS["primary"]
                avatar = ctk.CTkLabel(
                    row,
                    text=e.full_name[0].upper(),
                    font=ctk.CTkFont(size=16, weight="bold"),
                    fg_color=avatar_color,
                    width=45, height=45,
                    corner_radius=10
                )
                avatar.pack(side="left", padx=15, pady=12)
                
                # Info
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)
                
                name_frame = ctk.CTkFrame(info, fg_color="transparent")
                name_frame.pack(anchor="w")
                
                ctk.CTkLabel(
                    name_frame,
                    text=e.full_name,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["text"]
                ).pack(side="left")
                
                role_color = COLORS["gold"] if e.role == "admin" else COLORS["info"]
                ctk.CTkLabel(
                    name_frame,
                    text=f" • {e.role.title()}",
                    font=ctk.CTkFont(size=12),
                    text_color=role_color
                ).pack(side="left")
                
                ctk.CTkLabel(
                    info,
                    text=f"@{e.username}  •  💵 ${e.salary or 0}/month  •  📞 {e.phone or 'N/A'}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_muted"]
                ).pack(anchor="w")
                
                # Status
                status_color = COLORS["success"] if e.is_active else COLORS["text_muted"]
                status_text = "● Active" if e.is_active else "● Inactive"
                
                ctk.CTkLabel(
                    row,
                    text=status_text,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=status_color
                ).pack(side="right", padx=15)
                
        finally:
            db.close()
    
    def add_employee_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Employee")
        dialog.geometry("500x700")
        dialog.configure(fg_color=COLORS["bg_card"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center
        present_modal(dialog, 500, 700)
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color=COLORS["secondary"], corner_radius=0)
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text="👔 Add New Employee",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"]
        ).pack(pady=20)
        
        # Form
        form_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        fields = {}
        field_configs = [
            ("username", "Username", "unique_username"),
            ("password", "Password", "••••••••"),
            ("full_name", "Full Name", "John Doe"),
            ("phone", "Phone Number", "+1234567890"),
            ("salary", "Monthly Salary ($)", "0.00"),
            ("address", "Address", "123 Main St"),
        ]
        
        for key, label, placeholder in field_configs:
            ctk.CTkLabel(
                form_frame,
                text=label,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text"]
            ).pack(anchor="w", pady=(12, 5))
            
            if key == "phone":
                widget = PhoneField(
                    form_frame,
                    default_code=f"+{load_settings().get('country_code', '212')}")
            else:
                widget = ctk.CTkEntry(
                    form_frame,
                    placeholder_text=placeholder,
                    height=45,
                    font=ctk.CTkFont(size=14),
                    fg_color=COLORS["bg_dark"],
                    border_color=COLORS["border"],
                    corner_radius=10,
                    show="•" if key == "password" else ""
                )
            widget.pack(fill="x")
            fields[key] = widget

        # Role selection
        ctk.CTkLabel(
            form_frame,
            text="Role",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", pady=(12, 5))
        
        role_var = ctk.StringVar(value="employee")
        role_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        role_frame.pack(fill="x")
        
        ctk.CTkRadioButton(
            role_frame,
            text="Employee",
            variable=role_var,
            value="employee"
        ).pack(side="left", padx=(0, 20))
        
        ctk.CTkRadioButton(
            role_frame,
            text="Admin",
            variable=role_var,
            value="admin"
        ).pack(side="left")
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=20)
        
        def save_employee():
            db = get_db_session()
            try:
                # Check username exists
                existing = db.query(SystemUser).filter(
                    SystemUser.username == fields["username"].get()
                ).first()
                
                if existing:
                    messagebox.showerror("Error", "Username already exists!")
                    return
                
                employee = SystemUser(
                    username=fields["username"].get(),
                    hashed_password=get_password_hash(fields["password"].get()),
                    full_name=fields["full_name"].get(),
                    phone=fields["phone"].get(),
                    salary=float(fields["salary"].get() or 0),
                    address=fields["address"].get(),
                    role=role_var.get(),
                    is_active=True,
                    hire_date=date.today()
                )
                db.add(employee)
                
                log = EmployeeLog(
                    employee_id=self.user["id"],
                    employee_username=self.user["username"],
                    action=f"Added employee: {employee.full_name}"
                )
                db.add(log)
                db.commit()
                
                dialog.destroy()
                self.switch_page("employees")
                messagebox.showinfo("Success", "Employee added!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                db.close()
        
        ctk.CTkButton(
            btn_frame,
            text="Cancel",
            fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["bg_hover"],
            height=45,
            corner_radius=10,
            command=dialog.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        ctk.CTkButton(
            btn_frame,
            text="Save Employee",
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary_dark"],
            height=45,
            corner_radius=10,
            command=save_employee
        ).pack(side="right", expand=True, fill="x")
    
    def load_expenses(self):
        """Enhanced expenses page with filters, search, and better UI for employees and admins."""
        header, search = self.create_header(
            "💰 Expense Manager",
            "Track, manage, and analyze all expenses",
            show_search=True,
            search_command=self._filter_expenses
        )
        
        # Store search reference for filtering
        self._expense_search = search
        self._expense_filter_category = "All"
        self._expense_filter_period = "All Time"
        
        # Main container with two columns on wide screens
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Left column - Actions and Quick Add
        left_col = ctk.CTkFrame(main_container, fg_color="transparent", width=320)
        left_col.pack(side="left", fill="y", padx=(0, 15))
        left_col.pack_propagate(False)
        
        # Quick Actions Card
        quick_card = GlowingCard(left_col, glow_color=COLORS["primary"])
        quick_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            quick_card, text="⚡ Quick Actions",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Add new expense button (prominent)
        ctk.CTkButton(
            quick_card, text="➕ Add New Expense",
            fg_color=COLORS["success"], hover_color=COLORS["success_dark"],
            font=ctk.CTkFont(size=14, weight="bold"), height=45, corner_radius=10,
            command=self.add_expense_dialog
        ).pack(fill="x", padx=15, pady=(0, 10))
        
        # Quick expense buttons grid
        quick_btns = ctk.CTkFrame(quick_card, fg_color="transparent")
        quick_btns.pack(fill="x", padx=15, pady=(0, 15))
        
        quick_items = [
            ("💡", "Electricity", COLORS["warning"]),
            ("🚰", "Water", COLORS["info"]),
            ("🌐", "Internet", COLORS["primary"]),
            ("🔧", "Maintenance", COLORS["secondary"]),
            ("👔", "Employee Salary", COLORS["gold"]),
            ("🧹", "Cleaning", COLORS["success"]),
        ]
        
        for i, (icon, cat, color) in enumerate(quick_items):
            btn = ctk.CTkButton(
                quick_btns, text=icon, width=45, height=45,
                fg_color=COLORS["bg_elevated"], hover_color=color,
                font=ctk.CTkFont(size=18), corner_radius=10,
                command=lambda c=cat: self.add_expense_dialog(default_category=c)
            )
            btn.grid(row=i//3, column=i%3, padx=3, pady=3, sticky="nsew")
        
        for c in range(3):
            quick_btns.grid_columnconfigure(c, weight=1)
        
        # Summary Statistics Card
        stats_card = GlowingCard(left_col, glow_color=COLORS["warning"])
        stats_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            stats_card, text="📊 Summary",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        db = get_db_session()
        try:
            today = date.today()
            month_start = today.replace(day=1)
            week_start = today - timedelta(days=today.weekday())
            
            # Calculate totals
            all_expenses = db.query(Expense).all()
            total_amount = sum(float(e.amount) for e in all_expenses) if all_expenses else 0
            
            monthly_expenses = [e for e in all_expenses if e.created_at.date() >= month_start]
            monthly_amount = sum(float(e.amount) for e in monthly_expenses)
            
            weekly_expenses = [e for e in all_expenses if e.created_at.date() >= week_start]
            weekly_amount = sum(float(e.amount) for e in weekly_expenses)
            
            today_expenses = [e for e in all_expenses if e.created_at.date() == today]
            today_amount = sum(float(e.amount) for e in today_expenses)
            
            # Staff salaries
            staff = db.query(SystemUser).filter(SystemUser.is_active == True).all()
            salary_total = sum(float(u.salary or 0) for u in staff)
            
            # Category breakdown
            cat_totals = {}
            for e in all_expenses:
                cat_totals[e.category] = cat_totals.get(e.category, 0.0) + float(e.amount)
            
            # Store for later use
            self._expense_cat_totals = cat_totals
            self._expense_salary_total = salary_total
            
        finally:
            db.close()
        
        # Stats rows
        stats_data = [
            ("📅 Today", f"${today_amount:,.2f}", COLORS["info"]),
            ("📆 This Week", f"${weekly_amount:,.2f}", COLORS["primary"]),
            ("🗓️ This Month", f"${monthly_amount:,.2f}", COLORS["warning"]),
            ("💰 All Time", f"${total_amount:,.2f}", COLORS["danger"]),
            ("👔 Staff Salaries/mo", f"${salary_total:,.2f}", COLORS["secondary"]),
        ]
        
        for label, value, color in stats_data:
            row = ctk.CTkFrame(stats_card, fg_color=COLORS["bg_elevated"], corner_radius=8)
            row.pack(fill="x", padx=15, pady=2)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12),
                        text_color=COLORS["text_secondary"]).pack(side="left", padx=12, pady=8)
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=color).pack(side="right", padx=12)
        
        # Grand total
        grand_row = ctk.CTkFrame(stats_card, fg_color=COLORS["bg_dark"], corner_radius=8)
        grand_row.pack(fill="x", padx=15, pady=(8, 15))
        ctk.CTkLabel(grand_row, text="💎 Grand Total", font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS["text"]).pack(side="left", padx=12, pady=10)
        ctk.CTkLabel(grand_row, text=f"${(total_amount + salary_total):,.2f}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=COLORS["gold"]).pack(side="right", padx=12)
        
        # Category Breakdown Card
        breakdown_card = GlowingCard(left_col, glow_color=COLORS["danger"])
        breakdown_card.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(
            breakdown_card, text="📈 By Category",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        breakdown_scroll = ctk.CTkScrollableFrame(breakdown_card, fg_color="transparent", height=200)
        breakdown_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        
        # Sort categories by amount
        sorted_cats = sorted(cat_totals.items(), key=lambda x: x[1], reverse=True)
        
        for cat, amount in sorted_cats[:10]:  # Top 10 categories
            row = ctk.CTkFrame(breakdown_scroll, fg_color=COLORS["bg_elevated"], corner_radius=6)
            row.pack(fill="x", pady=2, padx=5)
            icon = EXPENSE_ICONS.get(cat.lower(), "📝")
            ctk.CTkLabel(row, text=f"{icon} {cat}", font=ctk.CTkFont(size=11),
                        text_color=COLORS["text"]).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(row, text=f"${amount:,.2f}", font=ctk.CTkFont(size=11, weight="bold"),
                        text_color=COLORS["danger"]).pack(side="right", padx=10)
        
        # Right column - Expenses List
        right_col = ctk.CTkFrame(main_container, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True)
        
        # Filters bar
        filters_frame = ctk.CTkFrame(right_col, fg_color=COLORS["bg_card"], corner_radius=12)
        filters_frame.pack(fill="x", pady=(0, 10))
        
        filter_inner = ctk.CTkFrame(filters_frame, fg_color="transparent")
        filter_inner.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(filter_inner, text="🔍 Filter:", font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 10))
        
        # Period filter
        period_options = ["All Time", "Today", "This Week", "This Month", "Last 3 Months", "This Year"]
        self._expense_period_var = ctk.StringVar(value="All Time")
        period_menu = SearchableSelect(
            filter_inner, values=period_options, variable=self._expense_period_var,
            fg_color=COLORS["bg_elevated"], button_color=COLORS["primary"],
            width=130, height=32, corner_radius=8,
            command=lambda v: self._refresh_expense_list()
        )
        period_menu.pack(side="left", padx=5)
        
        # Category filter
        cat_options = ["All Categories"] + EXPENSE_CATEGORIES
        self._expense_category_var = ctk.StringVar(value="All Categories")
        cat_menu = SearchableSelect(
            filter_inner, values=cat_options, variable=self._expense_category_var,
            fg_color=COLORS["bg_elevated"], button_color=COLORS["secondary"],
            width=150, height=32, corner_radius=8,
            command=lambda v: self._refresh_expense_list()
        )
        cat_menu.pack(side="left", padx=5)
        
        # Refresh button
        ctk.CTkButton(
            filter_inner, text="🔄", width=32, height=32,
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["primary"],
            corner_radius=8, command=lambda: self._refresh_expense_list()
        ).pack(side="right")
        
        # Export button
        ctk.CTkButton(
            filter_inner, text="📤 Export", width=80, height=32,
            fg_color=COLORS["bg_elevated"], hover_color=COLORS["info"],
            font=ctk.CTkFont(size=11), corner_radius=8,
            command=self._export_expenses
        ).pack(side="right", padx=5)
        
        # Expenses list
        list_header = ctk.CTkFrame(right_col, fg_color=COLORS["bg_elevated"], corner_radius=10)
        list_header.pack(fill="x", pady=(0, 5))
        
        headers = [("", 40), ("Description", 200), ("Category", 120), ("Date", 100), ("Amount", 100), ("Actions", 80)]
        for text, width in headers:
            ctk.CTkLabel(
                list_header, text=text, width=width,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text_muted"]
            ).pack(side="left", padx=8, pady=10)
        
        # Scrollable expense list
        self._expense_list_frame = ctk.CTkScrollableFrame(
            right_col, fg_color=COLORS["bg_card"], corner_radius=12
        )
        self._expense_list_frame.pack(fill="both", expand=True)
        
        # Load expenses
        self._refresh_expense_list()
    
    def _filter_expenses(self, text):
        """Filter expenses by search text."""
        self._expense_search_text = text
        self._refresh_expense_list()
    
    def _refresh_expense_list(self):
        """Refresh the expense list with current filters."""
        # Clear existing
        for widget in self._expense_list_frame.winfo_children():
            widget.destroy()
        
        # Get filter values
        period = self._expense_period_var.get() if hasattr(self, '_expense_period_var') else "All Time"
        category = self._expense_category_var.get() if hasattr(self, '_expense_category_var') else "All Categories"
        search_text = getattr(self, '_expense_search_text', '')
        
        db = get_db_session()
        try:
            today = date.today()
            query = db.query(Expense)
            
            # Apply period filter
            if period == "Today":
                query = query.filter(Expense.created_at >= datetime.combine(today, datetime.min.time()))
            elif period == "This Week":
                week_start = today - timedelta(days=today.weekday())
                query = query.filter(Expense.created_at >= datetime.combine(week_start, datetime.min.time()))
            elif period == "This Month":
                month_start = today.replace(day=1)
                query = query.filter(Expense.created_at >= datetime.combine(month_start, datetime.min.time()))
            elif period == "Last 3 Months":
                three_months_ago = today - timedelta(days=90)
                query = query.filter(Expense.created_at >= datetime.combine(three_months_ago, datetime.min.time()))
            elif period == "This Year":
                year_start = today.replace(month=1, day=1)
                query = query.filter(Expense.created_at >= datetime.combine(year_start, datetime.min.time()))
            
            # Apply category filter
            if category != "All Categories":
                query = query.filter(Expense.category == category)
            
            # Apply search filter
            if search_text:
                query = query.filter(
                    Expense.title.ilike(f"%{search_text}%") |
                    Expense.description.ilike(f"%{search_text}%") |
                    Expense.created_by.ilike(f"%{search_text}%")
                )
            
            expenses = query.order_by(Expense.created_at.desc()).all()
            
            if not expenses:
                empty_label = ctk.CTkLabel(
                    self._expense_list_frame,
                    text="📭 No expenses found matching your filters",
                    font=ctk.CTkFont(size=14),
                    text_color=COLORS["text_muted"]
                )
                empty_label.pack(pady=50)
                return
            
            # Calculate filtered total
            filtered_total = sum(float(e.amount) for e in expenses)
            
            # Show filtered total
            total_row = ctk.CTkFrame(self._expense_list_frame, fg_color=COLORS["primary_glow"], corner_radius=8)
            total_row.pack(fill="x", padx=10, pady=(10, 5))
            ctk.CTkLabel(total_row, text=f"📊 Showing {len(expenses)} expenses",
                        font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(side="left", padx=15, pady=8)
            ctk.CTkLabel(total_row, text=f"Total: ${filtered_total:,.2f}",
                        font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["warning"]).pack(side="right", padx=15)
            
            for e in expenses:
                self._create_expense_row(e)
                
        finally:
            db.close()
    
    def _create_expense_row(self, expense):
        """Create a row for an expense item."""
        row = ctk.CTkFrame(self._expense_list_frame, fg_color=COLORS["bg_elevated"], corner_radius=10)
        row.pack(fill="x", padx=10, pady=3)
        
        # Category icon
        icon = EXPENSE_ICONS.get(expense.category.lower(), "📝")
        ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=20), width=40).pack(side="left", padx=10, pady=10)
        
        # Description
        desc_frame = ctk.CTkFrame(row, fg_color="transparent", width=200)
        desc_frame.pack(side="left", padx=5)
        desc_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            desc_frame, text=expense.title[:25] + ("..." if len(expense.title) > 25 else ""),
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"], anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            desc_frame, text=f"By: {expense.created_by}",
            font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"], anchor="w"
        ).pack(anchor="w")
        
        # Category badge
        cat_frame = ctk.CTkFrame(row, fg_color=COLORS["bg_dark"], corner_radius=6, width=120)
        cat_frame.pack(side="left", padx=5)
        cat_frame.pack_propagate(False)
        ctk.CTkLabel(
            cat_frame, text=expense.category[:15],
            font=ctk.CTkFont(size=11), text_color=COLORS["text_secondary"]
        ).pack(pady=8)
        
        # Date
        ctk.CTkLabel(
            row, text=expense.created_at.strftime("%Y-%m-%d"),
            font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"], width=100
        ).pack(side="left", padx=5)
        
        # Amount
        ctk.CTkLabel(
            row, text=f"-${expense.amount:.2f}",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["danger"], width=100
        ).pack(side="left", padx=5)
        
        # Actions
        actions = ctk.CTkFrame(row, fg_color="transparent", width=80)
        actions.pack(side="left", padx=5)
        
        # View/Edit button
        ctk.CTkButton(
            actions, text="👁️", width=30, height=30,
            fg_color=COLORS["bg_dark"], hover_color=COLORS["info"],
            corner_radius=6, command=lambda eid=expense.id: self._view_expense_dialog(eid)
        ).pack(side="left", padx=2)
        
        # Delete button (admin only or own expense)
        if self.user["role"] == "admin" or expense.created_by == self.user["username"]:
            ctk.CTkButton(
                actions, text="🗑️", width=30, height=30,
                fg_color=COLORS["bg_dark"], hover_color=COLORS["danger"],
                corner_radius=6, command=lambda eid=expense.id: self._delete_expense(eid)
            ).pack(side="left", padx=2)
    
    def _view_expense_dialog(self, expense_id):
        """View expense details in a dialog."""
        db = get_db_session()
        try:
            expense = db.query(Expense).filter(Expense.id == expense_id).first()
            if not expense:
                messagebox.showerror("Error", "Expense not found")
                return
            
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"Expense Details - #{expense_id}")
            dialog.geometry("450x500")
            dialog.configure(fg_color=COLORS["bg_card"])
            dialog.transient(self.winfo_toplevel())
            dialog.grab_set()
            
            # Center
            present_modal(dialog, 450, 500)
            
            # Header
            header = ctk.CTkFrame(dialog, fg_color=COLORS["warning"], corner_radius=0)
            header.pack(fill="x")
            
            icon = EXPENSE_ICONS.get(expense.category.lower(), "📝")
            ctk.CTkLabel(
                header, text=f"{icon} Expense Details",
                font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["bg_dark"]
            ).pack(pady=20)
            
            # Details
            details = ctk.CTkFrame(dialog, fg_color="transparent")
            details.pack(fill="both", expand=True, padx=25, pady=20)
            
            # Amount (prominent)
            amount_frame = ctk.CTkFrame(details, fg_color=COLORS["bg_elevated"], corner_radius=12)
            amount_frame.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(
                amount_frame, text=f"-${expense.amount:.2f}",
                font=ctk.CTkFont(size=32, weight="bold"), text_color=COLORS["danger"]
            ).pack(pady=20)
            
            # Info rows
            info_items = [
                ("📝 Title", expense.title),
                ("📂 Category", expense.category),
                ("📅 Date", expense.created_at.strftime("%Y-%m-%d %H:%M")),
                ("👤 Created By", expense.created_by),
                ("🧾 Receipt #", expense.receipt_number or "N/A"),
            ]
            
            for label, value in info_items:
                row = ctk.CTkFrame(details, fg_color="transparent")
                row.pack(fill="x", pady=3)
                ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                            text_color=COLORS["text_secondary"], width=120, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=str(value), font=ctk.CTkFont(size=13),
                            text_color=COLORS["text"]).pack(side="left", padx=10)
            
            # Description
            if expense.description:
                ctk.CTkLabel(details, text="📋 Description", font=ctk.CTkFont(size=12, weight="bold"),
                            text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(15, 5))
                desc_box = ctk.CTkTextbox(details, height=80, fg_color=COLORS["bg_elevated"], corner_radius=8)
                desc_box.pack(fill="x")
                desc_box.insert("1.0", expense.description)
                desc_box.configure(state="disabled")
            
            # Close button
            ctk.CTkButton(
                dialog, text="Close", fg_color=COLORS["bg_elevated"],
                hover_color=COLORS["bg_hover"], height=45, corner_radius=10,
                command=dialog.destroy
            ).pack(fill="x", padx=25, pady=20)
            
        finally:
            db.close()
    
    def _delete_expense(self, expense_id):
        """Delete an expense after confirmation."""
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this expense?"):
            return
        
        db = get_db_session()
        try:
            expense = db.query(Expense).filter(Expense.id == expense_id).first()
            if expense:
                # Log the deletion
                db.add(EmployeeLog(
                    employee_id=self.user["id"],
                    employee_username=self.user["username"],
                    action=f"Deleted expense: {expense.title} - ${expense.amount}"
                ))
                db.delete(expense)
                db.commit()
                messagebox.showinfo("Success", "Expense deleted successfully!")
                self.switch_page("expenses")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            db.close()
    
    def _export_expenses(self):
        """Export expenses to CSV file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfilename=f"expenses_{date.today().strftime('%Y%m%d')}.csv"
        )
        if filepath:
            db = get_db_session()
            try:
                expenses = db.query(Expense).order_by(Expense.created_at.desc()).all()
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write("ID,Title,Category,Amount,Date,Created By,Receipt Number,Description\n")
                    for e in expenses:
                        desc = (e.description or "").replace('"', '""').replace('\n', ' ')
                        f.write(f'{e.id},"{e.title}","{e.category}",{e.amount},{e.created_at.strftime("%Y-%m-%d")},"{e.created_by}","{e.receipt_number or ""}","{desc}"\n')
                messagebox.showinfo("Success", f"Exported {len(expenses)} expenses to {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {str(e)}")
            finally:
                db.close()
    
    def add_expense_dialog(self, default_category="Electricity"):
        """Enhanced expense dialog with better UX and category suggestions."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Expense")
        dialog.geometry("520x720")
        dialog.configure(fg_color=COLORS["bg_card"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # Center
        present_modal(dialog, 520, 720)

        # Header with gradient effect
        header = ctk.CTkFrame(dialog, fg_color=COLORS["warning"], corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            header_content, text="💰",
            font=ctk.CTkFont(size=32)
        ).pack(side="left", padx=(0, 10))
        
        header_text = ctk.CTkFrame(header_content, fg_color="transparent")
        header_text.pack(side="left")
        
        ctk.CTkLabel(
            header_text, text="Add New Expense",
            font=ctk.CTkFont(size=20, weight="bold"), text_color=COLORS["bg_dark"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            header_text, text="Track your business spending",
            font=ctk.CTkFont(size=11), text_color=COLORS["bg_elevated"]
        ).pack(anchor="w")

        # Load employees for salary payments
        db = get_db_session()
        try:
            emps = db.query(SystemUser).order_by(SystemUser.full_name).all()
            emp_map = {f"{e.full_name} (@{e.username})": float(e.salary or 0) for e in emps}
        finally:
            db.close()

        form_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=25, pady=15)

        # Quick category buttons
        ctk.CTkLabel(
            form_frame, text="⚡ Quick Select Category",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", pady=(0, 8))
        
        quick_cat_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        quick_cat_frame.pack(fill="x", pady=(0, 15))
        
        category_var = ctk.StringVar(value=default_category)

        # Suggested title for each quick-select category button.
        quick_titles = {
            "Electricity": "Monthly electricity bill",
            "Water": "Monthly water bill",
            "Internet": "Internet service fee",
            "Maintenance": "Equipment maintenance",
            "Employee Salary": "Staff salary payment",
            "Rent": "Monthly rent payment",
        }
        # Titles we auto-filled — safe to overwrite. A hand-typed title is kept.
        _auto_titles = set(quick_titles.values()) | {
            "Internet service fee", "Cleaning services", "Equipment maintenance",
        }

        def set_quick_category(cat):
            # Decide before on_category runs whether the current title was
            # auto-filled (empty / a known preset / a salary line) vs. custom.
            current = title_entry.get().strip()
            title_is_auto = (
                current == "" or current in _auto_titles
                or current.startswith("Salary") or current.startswith("Bonus")
            )
            # Clear an auto-filled title so the category logic can refill it
            # (this lets the salary/bonus branch in on_category set its title too).
            if title_is_auto:
                title_entry.delete(0, "end")

            category_var.set(cat)
            on_category(cat)

            # Make the title follow the selected button (unless user customised it).
            if title_is_auto and cat not in ("Employee Salary", "Bonus"):
                suggestion = quick_titles.get(cat, cat)
                title_entry.delete(0, "end")
                title_entry.insert(0, suggestion)

            # Update button states
            for btn_cat, btn in quick_cat_buttons.items():
                if btn_cat == cat:
                    btn.configure(fg_color=COLORS["primary"])
                else:
                    btn.configure(fg_color=COLORS["bg_elevated"])
        
        quick_cats = [
            ("💡", "Electricity"), ("🚰", "Water"), ("🌐", "Internet"),
            ("🔧", "Maintenance"), ("👔", "Employee Salary"), ("🏠", "Rent"),
        ]
        
        quick_cat_buttons = {}
        for i, (icon, cat) in enumerate(quick_cats):
            btn = ctk.CTkButton(
                quick_cat_frame, text=f"{icon}", width=50, height=40,
                fg_color=COLORS["primary"] if cat == default_category else COLORS["bg_elevated"],
                hover_color=COLORS["primary_dark"], corner_radius=8,
                font=ctk.CTkFont(size=16),
                command=lambda c=cat: set_quick_category(c)
            )
            btn.grid(row=0, column=i, padx=3, pady=2, sticky="nsew")
            quick_cat_buttons[cat] = btn
        
        for c in range(6):
            quick_cat_frame.grid_columnconfigure(c, weight=1)

        # Title field
        ctk.CTkLabel(
            form_frame, text="📝 Title *",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", pady=(10, 5))
        
        title_entry = ctk.CTkEntry(
            form_frame, height=48, fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"], corner_radius=10,
            placeholder_text="e.g., Monthly electricity bill",
            font=ctk.CTkFont(size=14)
        )
        title_entry.pack(fill="x")

        # Amount field with currency indicator
        ctk.CTkLabel(
            form_frame, text="💵 Amount *",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", pady=(15, 5))
        
        amount_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        amount_frame.pack(fill="x")
        
        currency_label = ctk.CTkLabel(
            amount_frame, text="$", font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["success"], fg_color=COLORS["bg_elevated"],
            width=45, height=48, corner_radius=10
        )
        currency_label.pack(side="left")
        
        amount_entry = ctk.CTkEntry(
            amount_frame, height=48, fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"], corner_radius=10,
            placeholder_text="0.00", font=ctk.CTkFont(size=16)
        )
        amount_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Category dropdown
        ctk.CTkLabel(
            form_frame, text="📂 Category *",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", pady=(15, 5))

        # Employee selector (used for salary payments)
        emp_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        emp_label = ctk.CTkLabel(
            emp_frame, text="👤 Select Employee",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"]
        )
        emp_var = ctk.StringVar(value="— select employee —")
        emp_menu = SearchableSelect(
            emp_frame, values=(list(emp_map.keys()) or ["— no employees —"]),
            variable=emp_var, fg_color=COLORS["bg_dark"],
            button_color=COLORS["secondary"], button_hover_color=COLORS["primary"],
            height=48, corner_radius=10, font=ctk.CTkFont(size=13)
        )

        def on_employee(choice):
            if choice in emp_map:
                amount_entry.delete(0, "end")
                amount_entry.insert(0, f"{emp_map[choice]:.2f}")
                title_entry.delete(0, "end")
                title_entry.insert(0, f"Salary - {choice.split(' (@')[0]}")
        emp_menu.configure(command=on_employee)

        def on_category(choice):
            # Reveal the employee picker only for salary/bonus payments
            if choice in ["Employee Salary", "Bonus"]:
                emp_frame.pack(fill="x", pady=(10, 0))
                emp_label.pack(anchor="w", pady=(0, 5))
                emp_menu.pack(fill="x")
                if not title_entry.get() or title_entry.get().startswith("Salary"):
                    title_entry.delete(0, "end")
                    title_entry.insert(0, f"{'Salary' if choice == 'Employee Salary' else 'Bonus'} - ")
            else:
                emp_frame.pack_forget()
                # Auto-suggest title based on category
                if not title_entry.get():
                    suggestions = {
                        "Electricity": "Monthly electricity bill",
                        "Water": "Monthly water bill",
                        "Internet": "Internet service fee",
                        "Rent": "Monthly rent payment",
                        "Maintenance": "Equipment maintenance",
                        "Cleaning": "Cleaning services",
                    }
                    if choice in suggestions:
                        title_entry.insert(0, suggestions[choice])

        category_menu = SearchableSelect(
            form_frame, values=EXPENSE_CATEGORIES, variable=category_var,
            fg_color=COLORS["bg_dark"], button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_dark"],
            height=48, corner_radius=10, font=ctk.CTkFont(size=13),
            command=on_category
        )
        category_menu.pack(fill="x")

        # Receipt number (optional)
        ctk.CTkLabel(
            form_frame, text="🧾 Receipt Number (optional)",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", pady=(15, 5))
        
        receipt_entry = ctk.CTkEntry(
            form_frame, height=48, fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"], corner_radius=10,
            placeholder_text="Auto-generated if empty",
            font=ctk.CTkFont(size=14)
        )
        receipt_entry.pack(fill="x")

        # Description
        ctk.CTkLabel(
            form_frame, text="📋 Description (optional)",
            font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", pady=(15, 5))
        
        desc_entry = ctk.CTkTextbox(
            form_frame, height=80, fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"], corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        desc_entry.pack(fill="x")

        on_category(default_category)  # show employee picker if opened for salary

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=25, pady=20)

        def save_expense():
            db = get_db_session()
            try:
                import uuid
                amount_text = amount_entry.get().replace(",", "").strip()
                amount = float(amount_text) if amount_text else 0
                title = title_entry.get().strip()
                
                if not title:
                    messagebox.showwarning("Missing Title", "Please enter a title for this expense.")
                    title_entry.focus()
                    return
                if amount <= 0:
                    messagebox.showwarning("Invalid Amount", "Please enter an amount greater than 0.")
                    amount_entry.focus()
                    return
                
                receipt = receipt_entry.get().strip() or str(uuid.uuid4())[:8].upper()
                
                expense = Expense(
                    title=title,
                    amount=amount,
                    category=category_var.get(),
                    description=desc_entry.get("1.0", "end").strip(),
                    receipt_number=receipt,
                    created_by=self.user["username"]
                )
                db.add(expense)
                db.add(EmployeeLog(
                    employee_id=self.user["id"],
                    employee_username=self.user["username"],
                    action=f"Added expense ({expense.category}): {expense.title} - ${expense.amount:.2f}"
                ))
                db.commit()

                dialog.destroy()
                self.switch_page("expenses")
                messagebox.showinfo("Success", f"Expense of ${amount:.2f} added successfully!")
            except ValueError:
                messagebox.showerror("Invalid Amount", "Please enter a valid number for the amount.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                db.close()

        ctk.CTkButton(
            btn_frame, text="Cancel", fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["bg_hover"], height=50, corner_radius=10,
            font=ctk.CTkFont(size=14), command=dialog.destroy
        ).pack(side="left", expand=True, fill="x", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="💾 Save Expense", fg_color=COLORS["success"],
            hover_color=COLORS["success_dark"], height=50, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"), command=save_expense
        ).pack(side="right", expand=True, fill="x")
    
    def _refresh_client_payments(self, container):
        for w in container.winfo_children():
            w.destroy()

        period = self._pay_period.get()
        today = date.today()
        db = get_db_session()
        try:
            q = db.query(Payment)
            if period == "This Month":
                q = q.filter(Payment.paid_at >= today.replace(day=1))
            elif period == "This Year":
                q = q.filter(Payment.paid_at >= today.replace(month=1, day=1))
            payments = q.all()

            # Aggregate per member
            totals = {}
            for p in payments:
                key = p.member_id or 0
                agg = totals.setdefault(key, {"total": 0.0, "count": 0})
                agg["total"] += float(p.amount)
                agg["count"] += 1

            rows = []
            for mid, agg in totals.items():
                if mid:
                    m = db.query(Member).filter(Member.id == mid).first()
                    name = m.full_name if m else f"Member #{mid}"
                    plan = m.gym_plan if m else ""
                else:
                    name, plan = "Walk-in / Other", ""
                rows.append((name, plan, agg["total"], agg["count"]))
            rows.sort(key=lambda r: r[2], reverse=True)
        finally:
            db.close()

        if not rows:
            ctk.CTkLabel(container, text=f"No payments for: {period}",
                         text_color=COLORS["text_muted"]).pack(pady=20)
            return

        grand = sum(r[2] for r in rows)
        ctk.CTkLabel(
            container, text=f"{period} total: ${grand:,.2f}  •  {len(rows)} client(s)",
            font=ctk.CTkFont(size=12, weight="bold"), text_color=COLORS["primary_light"]
        ).pack(anchor="w", padx=6, pady=(4, 8))

        for name, plan, total, count in rows:
            row = ctk.CTkFrame(container, fg_color=COLORS["bg_elevated"], corner_radius=10)
            row.pack(fill="x", padx=4, pady=3)
            avatar = ctk.CTkLabel(
                row, text=name[0].upper() if name else "?",
                font=ctk.CTkFont(size=13, weight="bold"),
                fg_color=COLORS["primary"], width=36, height=36, corner_radius=9
            )
            avatar.pack(side="left", padx=10, pady=8)
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(info, text=name, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=COLORS["text"]).pack(anchor="w")
            sub = f"{count} payment(s)" + (f"  •  {plan}" if plan else "")
            ctk.CTkLabel(info, text=sub, font=ctk.CTkFont(size=11),
                         text_color=COLORS["text_muted"]).pack(anchor="w")
            ctk.CTkLabel(row, text=f"${total:,.2f}",
                         font=ctk.CTkFont(size=15, weight="bold"),
                         text_color=COLORS["success"]).pack(side="right", padx=18)

    def load_payments(self):
        header = self.create_header("Payments", "Track member payments and per-client totals")
        
        # Stats
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=10)
        
        db = get_db_session()
        try:
            today = date.today()
            month_start = today.replace(day=1)
            
            total = db.query(Payment).all()
            total_amount = sum(float(p.amount) for p in total) if total else 0
            
            monthly = db.query(Payment).filter(Payment.paid_at >= month_start).all()
            monthly_amount = sum(float(p.amount) for p in monthly) if monthly else 0
            
            summaries = [
                ("💰", f"${total_amount:,.2f}", "Total Revenue", COLORS["success"]),
                ("📅", f"${monthly_amount:,.2f}", "This Month", COLORS["primary"]),
                ("📊", str(len(monthly)), "Monthly Transactions", COLORS["info"]),
            ]
            
            for i, (icon, value, label, color) in enumerate(summaries):
                card = StatCard(stats_frame, icon, value, label, color)
                card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
                stats_frame.grid_columnconfigure(i, weight=1)
        finally:
            db.close()
        
        # ---- Per-client summary (how much each client pays, by period) ----
        client_card = GlowingCard(self.content_frame, glow_color=COLORS["primary"])
        client_card.pack(fill="x", padx=30, pady=(4, 6))

        head = ctk.CTkFrame(client_card, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(
            head, text="👥 Payments by Client",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(side="left")

        self._pay_period = ctk.StringVar(value="This Month")
        SearchableSelect(
            head, values=["This Month", "This Year", "All Time"],
            variable=self._pay_period, width=150,
            fg_color=COLORS["bg_dark"], button_color=COLORS["primary"],
            command=lambda _v: self._refresh_client_payments(client_body)
        ).pack(side="right")

        client_body = ctk.CTkScrollableFrame(client_card, fg_color="transparent", height=220)
        client_body.pack(fill="x", padx=15, pady=(0, 15))
        self._refresh_client_payments(client_body)

        # Payments list (recent transactions)
        ctk.CTkLabel(
            self.content_frame, text="🧾 Recent Transactions",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=34, pady=(6, 0))

        list_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=16
        )
        list_frame.pack(fill="both", expand=True, padx=30, pady=10)

        db = get_db_session()
        try:
            payments = db.query(Payment).order_by(Payment.paid_at.desc()).limit(50).all()
            
            for p in payments:
                member = db.query(Member).filter(Member.id == p.member_id).first()
                member_name = member.full_name if member else "Walk-in"
                
                row = ctk.CTkFrame(list_frame, fg_color=COLORS["bg_elevated"], corner_radius=10)
                row.pack(fill="x", padx=10, pady=4)
                
                ctk.CTkLabel(
                    row,
                    text="💳",
                    font=ctk.CTkFont(size=24)
                ).pack(side="left", padx=15, pady=12)
                
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)
                
                ctk.CTkLabel(
                    info,
                    text=member_name,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["text"]
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    info,
                    text=f"{p.payment_type} • {p.paid_at.strftime('%Y-%m-%d %H:%M')}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_muted"]
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    row,
                    text=f"+${p.amount:.2f}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=COLORS["success"]
                ).pack(side="right", padx=20)
                
        finally:
            db.close()
    
    def load_alerts(self):
        header = self.create_header("Alerts & Notifications", "Stay updated on important events")
        settings = load_settings()

        content = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=10)
        
        db = get_db_session()
        try:
            today = date.today()
            
            # Expired memberships
            expired_card = GlowingCard(content, glow_color=COLORS["danger"])
            expired_card.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                expired_card,
                text="🚨 Expired Memberships",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["danger"]
            ).pack(anchor="w", padx=20, pady=15)
            
            expired = db.query(Member).filter(
                Member.is_active == True,
                Member.end_date < today
            ).all()
            
            if expired:
                for m in expired:
                    days = (today - m.end_date).days
                    mid = m.id
                    name, phone, plan = m.full_name, m.phone_number, m.gym_plan
                    end_str = str(m.end_date)
                    row = ctk.CTkFrame(expired_card, fg_color=COLORS["bg_elevated"], corner_radius=8)
                    row.pack(fill="x", padx=15, pady=3)

                    ctk.CTkLabel(
                        row, text="⚠️",
                        font=ctk.CTkFont(size=16)
                    ).pack(side="left", padx=10, pady=10)

                    ctk.CTkLabel(
                        row,
                        text=f"{name}",
                        font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=COLORS["text"]
                    ).pack(side="left", padx=5)

                    ctk.CTkButton(
                        row, text="🔄 Renew", width=80, height=30,
                        fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                        corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"),
                        command=lambda i=mid: self.renew_member(i)
                    ).pack(side="right", padx=(4, 10))

                    ctk.CTkButton(
                        row, text="📲", width=40, height=30,
                        fg_color=COLORS["success"], hover_color=COLORS["success_dark"],
                        corner_radius=8,
                        command=lambda n=name, p=phone, pl=plan, d=end_str: self.whatsapp_message_dialog(
                            p, render_template(settings["expiry_message"], name=n, days=0,
                                               plan=pl, date=d),
                            title=f"Renewal · {n}", recipient=n,
                            log_label=f"Expiry WhatsApp: {n}")
                    ).pack(side="right", padx=2)

                    ctk.CTkLabel(
                        row,
                        text=f"Expired {days} days ago",
                        font=ctk.CTkFont(size=12),
                        text_color=COLORS["danger"]
                    ).pack(side="right", padx=5)
            else:
                ctk.CTkLabel(
                    expired_card,
                    text="✓ No expired memberships",
                    text_color=COLORS["success"]
                ).pack(padx=20, pady=10)
            
            # Expiring soon
            expiring_card = GlowingCard(content, glow_color=COLORS["warning"])
            expiring_card.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                expiring_card,
                text="⏰ Expiring Soon (7 days)",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=COLORS["warning"]
            ).pack(anchor="w", padx=20, pady=15)
            
            week = today + timedelta(days=7)
            expiring = db.query(Member).filter(
                Member.is_active == True,
                Member.end_date >= today,
                Member.end_date <= week
            ).all()
            
            if expiring:
                for m in expiring:
                    days = (m.end_date - today).days
                    mid = m.id
                    name, phone, plan = m.full_name, m.phone_number, m.gym_plan
                    end_str = str(m.end_date)
                    row = ctk.CTkFrame(expiring_card, fg_color=COLORS["bg_elevated"], corner_radius=8)
                    row.pack(fill="x", padx=15, pady=3)

                    ctk.CTkLabel(
                        row, text="⏳",
                        font=ctk.CTkFont(size=16)
                    ).pack(side="left", padx=10, pady=10)

                    ctk.CTkLabel(
                        row,
                        text=f"{name}",
                        font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=COLORS["text"]
                    ).pack(side="left", padx=5)

                    ctk.CTkButton(
                        row, text="🔄 Renew", width=80, height=30,
                        fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                        corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"),
                        command=lambda i=mid: self.renew_member(i)
                    ).pack(side="right", padx=(4, 10))

                    ctk.CTkButton(
                        row, text="📲", width=40, height=30,
                        fg_color=COLORS["success"], hover_color=COLORS["success_dark"],
                        corner_radius=8,
                        command=lambda n=name, p=phone, pl=plan, d=end_str, dy=days: self.whatsapp_message_dialog(
                            p, render_template(settings["expiry_message"], name=n, days=dy,
                                               plan=pl, date=d),
                            title=f"Renewal · {n}", recipient=n,
                            log_label=f"Expiry WhatsApp: {n}")
                    ).pack(side="right", padx=2)

                    ctk.CTkLabel(
                        row,
                        text=f"Expires in {days} days",
                        font=ctk.CTkFont(size=12),
                        text_color=COLORS["warning"]
                    ).pack(side="right", padx=5)
            else:
                ctk.CTkLabel(
                    expiring_card,
                    text="✓ No memberships expiring soon",
                    text_color=COLORS["success"]
                ).pack(padx=20, pady=10)
                
        finally:
            db.close()
    
    @scrollable_page
    def load_finance(self):
        header = self.create_header("Finance Dashboard", "Complete financial overview")
        
        db = get_db_session()
        try:
            today = date.today()
            month_start = today.replace(day=1)
            
            # Get totals
            payments = db.query(Payment).all()
            total_revenue = sum(float(p.amount) for p in payments) if payments else 0
            
            expenses = db.query(Expense).all()
            recorded_expenses = sum(float(e.amount) for e in expenses) if expenses else 0

            # Include active staff salaries (recurring monthly) in expenses
            staff = db.query(SystemUser).filter(SystemUser.is_active == True).all()
            salary_total = sum(float(u.salary or 0) for u in staff)

            total_expenses = recorded_expenses + salary_total
            profit = total_revenue - total_expenses

            # Monthly
            monthly_payments = db.query(Payment).filter(Payment.paid_at >= month_start).all()
            monthly_revenue = sum(float(p.amount) for p in monthly_payments) if monthly_payments else 0

            monthly_expenses = db.query(Expense).filter(Expense.created_at >= month_start).all()
            monthly_expense = (sum(float(e.amount) for e in monthly_expenses)
                               if monthly_expenses else 0) + salary_total

            monthly_profit = monthly_revenue - monthly_expense
            
        finally:
            db.close()
        
        # Main stats
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=30, pady=10)
        
        stats = [
            ("💰", f"${total_revenue:,.2f}", "Total Revenue", COLORS["success"]),
            ("📉", f"${total_expenses:,.2f}", "Total Expenses", COLORS["danger"]),
            ("📈", f"${profit:,.2f}", "Net Profit", COLORS["primary"] if profit >= 0 else COLORS["danger"]),
        ]
        
        for i, (icon, value, label, color) in enumerate(stats):
            card = StatCard(stats_frame, icon, value, label, color)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)
        
        # Monthly breakdown
        monthly_frame = GlowingCard(self.content_frame)
        monthly_frame.pack(fill="x", padx=30, pady=15)
        
        ctk.CTkLabel(
            monthly_frame,
            text="📅 This Month's Summary",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=15)
        
        month_stats = ctk.CTkFrame(monthly_frame, fg_color="transparent")
        month_stats.pack(fill="x", padx=20, pady=10)
        
        for i, (label, value, color) in enumerate([
            ("Revenue", f"${monthly_revenue:,.2f}", COLORS["success"]),
            ("Expenses", f"${monthly_expense:,.2f}", COLORS["danger"]),
            ("Profit", f"${monthly_profit:,.2f}", COLORS["primary"] if monthly_profit >= 0 else COLORS["danger"])
        ]):
            stat_item = ctk.CTkFrame(month_stats, fg_color=COLORS["bg_elevated"], corner_radius=10)
            stat_item.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            month_stats.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                stat_item,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_muted"]
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                stat_item,
                text=value,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color
            ).pack(pady=(0, 15))
    
    @scrollable_page
    def load_checkin(self):
        """Front-desk member check-in / attendance.

        Search a member, tap Check In to log their gym visit, and see a live
        list of everyone who came in today. Check-ins also appear (with a ✅)
        in the admin Activity Tracker.
        """
        self.create_header("Check-In", "Record member attendance at the gym")

        # --- Search & results ---
        search_card = GlowingCard(self.content_frame, glow_color=COLORS["primary"])
        search_card.pack(fill="x", padx=30, pady=(10, 8))
        ctk.CTkLabel(
            search_card, text="🔎 Find a member to check in",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 8))
        search_entry = ctk.CTkEntry(
            search_card, placeholder_text="Type a name or phone number…",
            height=46, fg_color=COLORS["bg_dark"], border_color=COLORS["border"],
            corner_radius=10, font=ctk.CTkFont(size=14)
        )
        search_entry.pack(fill="x", padx=20, pady=(0, 12))
        results = ctk.CTkFrame(search_card, fg_color="transparent")
        results.pack(fill="x", padx=12, pady=(0, 14))

        # --- Today's check-ins ---
        today_card = GlowingCard(self.content_frame, glow_color=COLORS["success"])
        today_card.pack(fill="both", expand=True, padx=30, pady=(8, 12))
        count_label = ctk.CTkLabel(
            today_card, text="", font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["success"]
        )
        count_label.pack(anchor="w", padx=20, pady=15)
        today_list = ctk.CTkFrame(today_card, fg_color="transparent")
        today_list.pack(fill="x", padx=12, pady=(0, 14))

        def _today_start():
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        def _checked_in_today():
            db = get_db_session()
            try:
                rows = db.query(EmployeeLog).filter(
                    EmployeeLog.action.like("Check-in:%"),
                    EmployeeLog.created_at >= _today_start()
                ).order_by(EmployeeLog.created_at.desc()).all()
                return [(r.action.replace("Check-in: ", ""), r.created_at) for r in rows]
            finally:
                db.close()

        def refresh_today():
            rows = _checked_in_today()
            count_label.configure(text=f"✅ Today's Check-Ins  ·  {len(rows)}")
            for w in today_list.winfo_children():
                w.destroy()
            if not rows:
                ctk.CTkLabel(today_list, text="No check-ins yet today.",
                             text_color=COLORS["text_muted"]).pack(pady=16)
                return
            for name, ts in rows:
                row = ctk.CTkFrame(today_list, fg_color=COLORS["bg_elevated"], corner_radius=10)
                row.pack(fill="x", padx=4, pady=3)
                ctk.CTkLabel(row, text="✅", font=ctk.CTkFont(size=15)).pack(
                    side="left", padx=12, pady=9)
                ctk.CTkLabel(row, text=name, font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=COLORS["text"], anchor="w").pack(
                    side="left", fill="x", expand=True)
                ctk.CTkLabel(row, text=ts.strftime("%H:%M"), font=ctk.CTkFont(size=12),
                             text_color=COLORS["text_muted"]).pack(side="right", padx=15)

        def do_checkin(name):
            self._log_action(f"Check-in: {name}")
            refresh_today()
            render_results(search_entry.get())

        def render_results(query=""):
            for w in results.winfo_children():
                w.destroy()
            q = query.strip()
            if not q:
                ctk.CTkLabel(results, text="Start typing to find a member…",
                             text_color=COLORS["text_muted"]).pack(pady=14)
                return
            db = get_db_session()
            try:
                today = date.today()
                members = db.query(Member).filter(
                    Member.full_name.ilike(f"%{q}%") | Member.phone_number.ilike(f"%{q}%")
                ).order_by(Member.full_name).limit(12).all()
                data = [{
                    "name": m.full_name, "phone": m.phone_number,
                    "active": bool(m.is_active and m.end_date and m.end_date >= today),
                    "expired": bool(m.end_date and m.end_date < today),
                    "end": m.end_date,
                } for m in members]
            finally:
                db.close()
            checked = {n for n, _ in _checked_in_today()}
            if not data:
                ctk.CTkLabel(results, text=f"No members match “{q}”.",
                             text_color=COLORS["text_muted"]).pack(pady=14)
                return
            for m in data:
                row = ctk.CTkFrame(results, fg_color=COLORS["bg_elevated"], corner_radius=10)
                row.pack(fill="x", padx=4, pady=3)
                ctk.CTkLabel(
                    row, text=m["name"][0].upper(),
                    font=ctk.CTkFont(size=14, weight="bold"), fg_color=COLORS["primary"],
                    text_color=COLORS["text"], width=38, height=38, corner_radius=10
                ).pack(side="left", padx=12, pady=10)
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(info, text=m["name"], font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=COLORS["text"]).pack(anchor="w")
                if m["expired"]:
                    badge, bc = f"⚠ Expired ({m['end']})", COLORS["danger"]
                elif m["active"]:
                    badge, bc = "● Active membership", COLORS["success"]
                else:
                    badge, bc = "● Inactive", COLORS["text_muted"]
                ctk.CTkLabel(info, text=badge, font=ctk.CTkFont(size=11),
                             text_color=bc).pack(anchor="w")
                if m["name"] in checked:
                    ctk.CTkLabel(row, text="✅ Checked in",
                                 font=ctk.CTkFont(size=12, weight="bold"),
                                 text_color=COLORS["success"]).pack(side="right", padx=16)
                else:
                    ctk.CTkButton(
                        row, text="Check In", width=104, height=34,
                        fg_color=COLORS["success"], hover_color=COLORS["success_dark"],
                        corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"),
                        command=lambda nm=m["name"]: do_checkin(nm)
                    ).pack(side="right", padx=12)

        search_entry.bind("<KeyRelease>", lambda _e: render_results(search_entry.get()))
        render_results("")
        refresh_today()

    @scrollable_page
    def load_leave(self):
        header = self.create_header("Leave Requests", "Submit and track leave requests")
        
        # Request form
        form_card = GlowingCard(self.content_frame, glow_color=COLORS["secondary"])
        form_card.pack(fill="x", padx=30, pady=15)
        
        ctk.CTkLabel(
            form_card,
            text="🏖️ Submit Leave Request",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=15)
        
        form_frame = ctk.CTkFrame(form_card, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Leave type
        ctk.CTkLabel(form_frame, text="Leave Type:", font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="w", pady=5)
        leave_type = SearchableSelect(
            form_frame,
            values=["Vacation", "Sick Leave", "Personal", "Emergency"],
            fg_color=COLORS["bg_dark"],
            button_color=COLORS["primary"]
        )
        leave_type.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        # Dates
        ctk.CTkLabel(form_frame, text="Start Date:", font=ctk.CTkFont(size=12)).grid(row=1, column=0, sticky="w", pady=5)
        start_date = DateField(form_frame, height=36)
        start_date.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="End Date:", font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", pady=5)
        end_date = DateField(form_frame, height=36)
        end_date.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        
        # Reason
        ctk.CTkLabel(form_frame, text="Reason:", font=ctk.CTkFont(size=12)).grid(row=3, column=0, sticky="nw", pady=5)
        reason = ctk.CTkTextbox(form_frame, height=60, fg_color=COLORS["bg_dark"])
        reason.grid(row=3, column=1, sticky="ew", padx=10, pady=5)
        
        form_frame.grid_columnconfigure(1, weight=1)
        
        def submit_leave():
            db = get_db_session()
            try:
                log = EmployeeLog(
                    employee_id=self.user["id"],
                    employee_username=self.user["username"],
                    action=f"Leave Request: {leave_type.get()} from {start_date.get()} to {end_date.get()}"
                )
                db.add(log)
                db.commit()
                messagebox.showinfo("Success", "Leave request submitted!")
                self.switch_page("leave")
            finally:
                db.close()
        
        ctk.CTkButton(
            form_card,
            text="Submit Request",
            fg_color=COLORS["secondary"],
            hover_color=COLORS["primary_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
            height=42,
            corner_radius=10,
            command=submit_leave
        ).pack(pady=20)
        
        # Leave balance
        balance_card = GlowingCard(self.content_frame)
        balance_card.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(
            balance_card,
            text="📊 Leave Balance",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=15)
        
        balance_frame = ctk.CTkFrame(balance_card, fg_color="transparent")
        balance_frame.pack(fill="x", padx=20, pady=10)
        
        for i, (label, used, total, color) in enumerate([
            ("Vacation", 5, 15, COLORS["success"]),
            ("Sick Leave", 2, 10, COLORS["info"]),
            ("Personal", 1, 3, COLORS["warning"])
        ]):
            item = ctk.CTkFrame(balance_frame, fg_color=COLORS["bg_elevated"], corner_radius=10)
            item.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            balance_frame.grid_columnconfigure(i, weight=1)
            
            ctk.CTkLabel(
                item, text=label,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_muted"]
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                item, text=f"{total - used}/{total}",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=color
            ).pack()
            
            ctk.CTkLabel(
                item, text="days remaining",
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_muted"]
            ).pack(pady=(0, 15))
    
    def load_products(self):
        header = self.create_header("Products & Inventory", "Manage gym products")
        
        # Add product button
        action_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=30, pady=(0, 10))
        
        ctk.CTkButton(
            action_frame,
            text="➕ Add Product",
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            font=ctk.CTkFont(size=13, weight="bold"),
            height=40,
            corner_radius=10,
            command=self.add_product_dialog
        ).pack(side="left")
        
        # Products list
        list_frame = ctk.CTkScrollableFrame(
            self.content_frame, 
            fg_color=COLORS["bg_card"], 
            corner_radius=16
        )
        list_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        db = get_db_session()
        try:
            products = db.query(Product).all()
            
            for p in products:
                row = ctk.CTkFrame(list_frame, fg_color=COLORS["bg_elevated"], corner_radius=10)
                row.pack(fill="x", padx=10, pady=4)
                
                ctk.CTkLabel(
                    row, text="📦",
                    font=ctk.CTkFont(size=24)
                ).pack(side="left", padx=15, pady=12)
                
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)
                
                ctk.CTkLabel(
                    info, text=p.name,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["text"]
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    info, text=f"{p.category} • Stock: {p.stock}",
                    font=ctk.CTkFont(size=11),
                    text_color=COLORS["text_muted"]
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    row, text=f"${p.price:.2f}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=COLORS["success"]
                ).pack(side="right", padx=20)
        finally:
            db.close()
    
    def add_product_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Product")
        dialog.geometry("400x450")
        dialog.configure(fg_color=COLORS["bg_card"])
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Center
        present_modal(dialog, 400, 450)
        
        ctk.CTkLabel(
            dialog, text="📦 Add New Product",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)
        
        # Form
        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=30)
        
        fields = {}
        for key, label in [("name", "Product Name"), ("category", "Category"), ("price", "Price ($)"), ("stock", "Stock Quantity")]:
            ctk.CTkLabel(form, text=label, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 3))
            entry = ctk.CTkEntry(form, height=40, fg_color=COLORS["bg_dark"], corner_radius=8)
            entry.pack(fill="x")
            fields[key] = entry
        
        def save():
            db = get_db_session()
            try:
                product = Product(
                    name=fields["name"].get(),
                    category=fields["category"].get(),
                    price=float(fields["price"].get() or 0),
                    stock=int(fields["stock"].get() or 0),
                    is_available=True
                )
                db.add(product)
                db.commit()
                dialog.destroy()
                self.switch_page("products")
            finally:
                db.close()
        
        ctk.CTkButton(dialog, text="Save Product", fg_color=COLORS["primary"], height=45, command=save).pack(pady=20)
    
    @scrollable_page
    def load_reports(self):
        header = self.create_header("Reports & Analytics", "Generate business reports")
        
        # Report types
        reports_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        reports_frame.pack(fill="x", padx=30, pady=15)
        
        reports = [
            ("📊", "Revenue Report", "Monthly revenue breakdown", COLORS["success"]),
            ("👥", "Members Report", "Membership statistics", COLORS["primary"]),
            ("📝", "Expenses Report", "Expense analysis", COLORS["warning"]),
            ("📈", "Growth Report", "Business growth metrics", COLORS["info"]),
        ]
        
        for i, (icon, title, desc, color) in enumerate(reports):
            card = GlowingCard(reports_frame, glow_color=color)
            card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            reports_frame.grid_columnconfigure(i%2, weight=1)
            
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=32)).pack(pady=(20, 10))
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold")).pack()
            ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"]).pack()
            
            ctk.CTkButton(
                card, text="Generate", fg_color=color,
                height=35, corner_radius=8,
                command=lambda t=title: self.generate_report(t)
            ).pack(pady=15)
    
    def generate_report(self, report_type):
        """Compute a real report from the database and show it in a modal."""
        db = get_db_session()
        try:
            items = self._compute_report(db, report_type)
        except Exception as e:
            messagebox.showerror("Report error", f"Could not generate report:\n{e}")
            return
        finally:
            db.close()
        self._show_report_dialog(report_type, items)

    def _compute_report(self, db, report_type):
        """Return a list of display items: ("head", txt) / ("row", label, value)."""
        from collections import defaultdict
        today = date.today()
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)

        def as_date(dt):
            if dt is None:
                return None
            try:
                return dt.replace(tzinfo=None).date()
            except Exception:
                try:
                    return dt.date()
                except Exception:
                    return None

        items = []

        if report_type == "Revenue Report":
            payments = db.query(Payment).all()
            total = sum(p.amount or 0 for p in payments)
            this_month = sum(p.amount or 0 for p in payments
                             if (as_date(p.paid_at) or today) >= month_start)
            this_year = sum(p.amount or 0 for p in payments
                            if (as_date(p.paid_at) or today) >= year_start)
            by_type = defaultdict(float)
            for p in payments:
                by_type[(p.payment_type or "Other")] += p.amount or 0
            items += [
                ("head", "💰 Revenue Summary"),
                ("row", "Total revenue (all time)", f"${total:,.2f}"),
                ("row", "This month", f"${this_month:,.2f}"),
                ("row", "This year", f"${this_year:,.2f}"),
                ("row", "Transactions", str(len(payments))),
                ("head", "Breakdown by type"),
            ]
            if by_type:
                for k, v in sorted(by_type.items(), key=lambda kv: -kv[1]):
                    items.append(("row", k, f"${v:,.2f}"))
            else:
                items.append(("row", "No payments recorded", "—"))

        elif report_type == "Members Report":
            members = db.query(Member).all()
            active = [m for m in members if m.is_active]
            expiring = [m for m in active if m.end_date and today <= m.end_date <= today + timedelta(days=7)]
            expired = [m for m in members if m.end_date and m.end_date < today]
            new_month = [m for m in members if (as_date(m.created_at) or today) >= month_start]
            by_plan = defaultdict(int)
            for m in members:
                by_plan[(m.gym_plan or "Unspecified")] += 1
            items += [
                ("head", "👥 Membership Summary"),
                ("row", "Total members", str(len(members))),
                ("row", "Active", str(len(active))),
                ("row", "Inactive", str(len(members) - len(active))),
                ("row", "Expiring within 7 days", str(len(expiring))),
                ("row", "Expired", str(len(expired))),
                ("row", "New this month", str(len(new_month))),
                ("head", "By plan"),
            ]
            for k, v in sorted(by_plan.items(), key=lambda kv: -kv[1]):
                items.append(("row", k, str(v)))

        elif report_type == "Expenses Report":
            expenses = db.query(Expense).all()
            payments = db.query(Payment).all()
            total = sum(e.amount or 0 for e in expenses)
            this_month = sum(e.amount or 0 for e in expenses
                             if (as_date(e.created_at) or today) >= month_start)
            this_year = sum(e.amount or 0 for e in expenses
                            if (as_date(e.created_at) or today) >= year_start)
            revenue = sum(p.amount or 0 for p in payments)
            by_cat = defaultdict(float)
            for e in expenses:
                by_cat[(e.category or "Other")] += e.amount or 0
            items += [
                ("head", "🧾 Expense Summary"),
                ("row", "Total expenses (all time)", f"${total:,.2f}"),
                ("row", "This month", f"${this_month:,.2f}"),
                ("row", "This year", f"${this_year:,.2f}"),
                ("row", "Entries", str(len(expenses))),
                ("head", "Net position (all time)"),
                ("row", "Revenue", f"${revenue:,.2f}"),
                ("row", "Expenses", f"${total:,.2f}"),
                ("row", "Net profit", f"${revenue - total:,.2f}"),
                ("head", "Top categories"),
            ]
            top = sorted(by_cat.items(), key=lambda kv: -kv[1])[:8]
            if top:
                for k, v in top:
                    items.append(("row", k, f"${v:,.2f}"))
            else:
                items.append(("row", "No expenses recorded", "—"))

        elif report_type == "Growth Report":
            members = db.query(Member).all()
            payments = db.query(Payment).all()
            expenses = db.query(Expense).all()
            items.append(("head", "📈 Last 6 Months"))
            for back in range(5, -1, -1):
                m_year = today.year + (today.month - 1 - back) // 12
                m_month = (today.month - 1 - back) % 12 + 1
                m_start = date(m_year, m_month, 1)
                m_end = date(m_year + (m_month // 12), (m_month % 12) + 1, 1)
                label = m_start.strftime("%b %Y")
                joined = sum(1 for m in members
                             if m_start <= (as_date(m.created_at) or date(1900, 1, 1)) < m_end)
                rev = sum(p.amount or 0 for p in payments
                          if m_start <= (as_date(p.paid_at) or date(1900, 1, 1)) < m_end)
                exp = sum(e.amount or 0 for e in expenses
                          if m_start <= (as_date(e.created_at) or date(1900, 1, 1)) < m_end)
                items.append(("row", label,
                              f"+{joined} members  •  ${rev:,.0f} in / ${exp:,.0f} out  •  net ${rev - exp:,.0f}"))
            items.append(("head", "Totals (6 months)"))
            tot_rev = sum(p.amount or 0 for p in payments)
            tot_exp = sum(e.amount or 0 for e in expenses)
            items += [
                ("row", "Members", str(len(members))),
                ("row", "Net profit (all time)", f"${tot_rev - tot_exp:,.2f}"),
            ]
        else:
            items.append(("row", "Unknown report", report_type))

        return items

    def _report_to_text(self, report_type, items):
        lines = [f"{report_type}",
                 f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                 "=" * 50, ""]
        for it in items:
            if it[0] == "head":
                lines += ["", it[1], "-" * len(it[1])]
            elif it[0] == "row":
                lines.append(f"{it[1]:<32} {it[2]}")
        return "\n".join(lines)

    def _show_report_dialog(self, report_type, items):
        dialog = ctk.CTkToplevel(self)
        dialog.title(report_type)
        present_modal(dialog, 560, 620)

        header = ctk.CTkFrame(dialog, fg_color=COLORS["primary"], corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(
            header, text=f"📊 {report_type}",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text"]
        ).pack(pady=(16, 2))
        ctk.CTkLabel(
            header, text=f"Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            font=ctk.CTkFont(size=11), text_color=COLORS["text"]
        ).pack(pady=(0, 14))

        body = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=18, pady=14)

        for it in items:
            if it[0] == "head":
                ctk.CTkLabel(
                    body, text=it[1], font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=COLORS["primary_light"]
                ).pack(anchor="w", pady=(14, 4))
            elif it[0] == "row":
                row = ctk.CTkFrame(body, fg_color=COLORS["bg_elevated"], corner_radius=8)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=it[1], font=ctk.CTkFont(size=13),
                             text_color=COLORS["text_secondary"], anchor="w").pack(
                    side="left", padx=14, pady=8, fill="x", expand=True)
                ctk.CTkLabel(row, text=it[2], font=ctk.CTkFont(size=13, weight="bold"),
                             text_color=COLORS["text"]).pack(side="right", padx=14)

        btns = ctk.CTkFrame(dialog, fg_color="transparent")
        btns.pack(fill="x", padx=18, pady=(0, 16))

        def export():
            path = filedialog.asksaveasfilename(
                parent=dialog, defaultextension=".txt",
                initialfile=f"{report_type.replace(' ', '_')}_{date.today()}.txt",
                filetypes=[("Text file", "*.txt"), ("All files", "*.*")])
            if not path:
                return
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self._report_to_text(report_type, items))
                self._log_action(f"Exported {report_type}")
                messagebox.showinfo("Exported", f"Report saved to:\n{path}", parent=dialog)
            except Exception as e:
                messagebox.showerror("Export failed", str(e), parent=dialog)

        ctk.CTkButton(
            btns, text="📤 Export to file", fg_color=COLORS["success"],
            hover_color=COLORS["success_dark"], height=44, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"), command=export
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ctk.CTkButton(
            btns, text="Close", fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["bg_hover"], height=44, corner_radius=10,
            command=dialog.destroy
        ).pack(side="right", expand=True, fill="x")

    def load_birthdays(self):
        self.create_header("Birthdays", "Send WhatsApp birthday wishes to members")
        settings = load_settings()

        db = get_db_session()
        try:
            today = date.today()
            members = db.query(Member).filter(Member.is_active == True).all()
            today_list, upcoming = [], []
            for m in members:
                if not m.date_of_birth:
                    continue
                bm, bd = m.date_of_birth.month, m.date_of_birth.day
                rec = {
                    "id": m.id, "name": m.full_name, "phone": m.phone_number,
                    "age": compute_age(m.date_of_birth), "dob": str(m.date_of_birth),
                }
                if bm == today.month and bd == today.day:
                    today_list.append(rec)
                else:
                    try:
                        nxt = m.date_of_birth.replace(year=today.year)
                        if nxt < today:
                            nxt = m.date_of_birth.replace(year=today.year + 1)
                        diff = (nxt - today).days
                        if 0 < diff <= 30:
                            rec["days"] = diff
                            rec["date"] = str(nxt)
                            upcoming.append(rec)
                    except ValueError:
                        continue
            upcoming.sort(key=lambda r: r["days"])
        finally:
            db.close()

        content = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=10)

        # Today's birthdays
        today_card = GlowingCard(content, glow_color=COLORS["accent"])
        today_card.pack(fill="x", pady=10)
        head = ctk.CTkFrame(today_card, fg_color="transparent")
        head.pack(fill="x", padx=20, pady=15)
        ctk.CTkLabel(
            head, text="🎂 Birthdays Today",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["accent"]
        ).pack(side="left")
        if today_list:
            ctk.CTkButton(
                head, text="📲 Wish All", fg_color=COLORS["success"],
                hover_color=COLORS["success_dark"], height=34, corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda: self._wish_all_birthdays(today_list, settings)
            ).pack(side="right")

        if today_list:
            for b in today_list:
                self._birthday_row(today_card, b, settings, is_today=True)
        else:
            ctk.CTkLabel(today_card, text="No birthdays today 🎈",
                         text_color=COLORS["text_muted"]).pack(padx=20, pady=15)

        # Upcoming birthdays
        up_card = GlowingCard(content)
        up_card.pack(fill="x", pady=10)
        ctk.CTkLabel(
            up_card, text="📅 Upcoming (next 30 days)",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=15)
        if upcoming:
            for b in upcoming:
                self._birthday_row(up_card, b, settings, is_today=False)
        else:
            ctk.CTkLabel(up_card, text="No upcoming birthdays in the next 30 days",
                         text_color=COLORS["text_muted"]).pack(padx=20, pady=15)

    def _birthday_row(self, parent, b, settings, is_today):
        row = ctk.CTkFrame(parent, fg_color=COLORS["bg_elevated"], corner_radius=10)
        row.pack(fill="x", padx=15, pady=4)
        avatar = ctk.CTkLabel(
            row, text=b["name"][0].upper(),
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"], width=38, height=38, corner_radius=10
        )
        avatar.pack(side="left", padx=12, pady=10)
        info = ctk.CTkFrame(row, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(info, text=b["name"], font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=COLORS["text"]).pack(anchor="w")
        sub = f"🎂 turns {b['age'] + (0 if is_today else 1)}"
        if is_today:
            sub += "  •  Today!"
        else:
            sub += f"  •  in {b['days']} days ({b['date']})"
        sub += f"  •  📞 {b['phone'] or 'N/A'}"
        ctk.CTkLabel(info, text=sub, font=ctk.CTkFont(size=11),
                     text_color=COLORS["text_muted"]).pack(anchor="w")
        ctk.CTkButton(
            row, text="📲 WhatsApp", width=110, height=34,
            fg_color=COLORS["success"], hover_color=COLORS["success_dark"],
            corner_radius=8, font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self.whatsapp_message_dialog(
                b["phone"],
                render_template(settings["birthday_message"],
                                name=b["name"], age=b["age"]),
                title=f"Birthday wish · {b['name']}",
                recipient=b["name"], log_label=f"Birthday WhatsApp: {b['name']}")
        ).pack(side="right", padx=12)

    def _wish_all_birthdays(self, people, settings):
        if not messagebox.askyesno(
            "Wish all",
            f"Open WhatsApp for {len(people)} member(s) with today's birthday?\n"
            "Each opens in WhatsApp Web/Desktop one after another."):
            return
        self._broadcast_run([
            {"phone": p["phone"],
             "message": render_template(settings["birthday_message"],
                                        name=p["name"], age=p["age"]),
             "name": p["name"]}
            for p in people if p["phone"]
        ], log_label="Birthday broadcast")

    def load_broadcast(self):
        self.create_header("Broadcast & Events", "Send an announcement to members via WhatsApp")
        settings = load_settings()

        wrapper = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        wrapper.pack(fill="both", expand=True, padx=30, pady=10)

        compose = GlowingCard(wrapper, glow_color=COLORS["info"])
        compose.pack(fill="x", pady=10)
        ctk.CTkLabel(
            compose, text="📢 Compose Announcement",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(
            compose, text="Tip: use {name} to personalise, {gym_name} for the gym name.",
            font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=20)

        msg_box = ctk.CTkTextbox(
            compose, height=140, fg_color=COLORS["bg_dark"],
            border_color=COLORS["border"], border_width=1, corner_radius=10,
            font=ctk.CTkFont(size=13)
        )
        msg_box.pack(fill="x", padx=20, pady=12)
        msg_box.insert("1.0", settings.get("broadcast_message", ""))

        # Audience selector
        aud_frame = ctk.CTkFrame(compose, fg_color="transparent")
        aud_frame.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(aud_frame, text="Audience:",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(0, 10))
        audience_var = ctk.StringVar(value="All Members")
        SearchableSelect(
            aud_frame, values=["All Members", "Active Only", "Expiring (7 days)", "Expired"],
            variable=audience_var, fg_color=COLORS["bg_dark"],
            button_color=COLORS["primary"], width=200
        ).pack(side="left")

        count_label = ctk.CTkLabel(aud_frame, text="", font=ctk.CTkFont(size=12),
                                   text_color=COLORS["info"])
        count_label.pack(side="left", padx=15)

        def resolve_recipients():
            db = get_db_session()
            try:
                today = date.today()
                aud = audience_var.get()
                q = db.query(Member)
                if aud == "Active Only":
                    q = q.filter(Member.is_active == True, Member.end_date >= today)
                elif aud == "Expiring (7 days)":
                    q = q.filter(Member.is_active == True, Member.end_date >= today,
                                 Member.end_date <= today + timedelta(days=7))
                elif aud == "Expired":
                    q = q.filter(Member.is_active == True, Member.end_date < today)
                return [{"name": m.full_name, "phone": m.phone_number}
                        for m in q.all() if m.phone_number]
            finally:
                db.close()

        def preview():
            recips = resolve_recipients()
            count_label.configure(text=f"{len(recips)} recipient(s)")

        def send():
            template = msg_box.get("1.0", "end").strip()
            if not template:
                messagebox.showwarning("Empty message", "Please write a message first.")
                return
            recips = resolve_recipients()
            if not recips:
                messagebox.showinfo("No recipients", "No members match this audience.")
                return
            if not messagebox.askyesno(
                "Send broadcast",
                f"Open WhatsApp for {len(recips)} member(s)?\n\n"
                "Each message opens in WhatsApp Web/Desktop one after another, "
                "where you press send."):
                return
            jobs = [{"phone": r["phone"],
                     "message": render_template(template, name=r["name"]),
                     "name": r["name"]} for r in recips]
            self._broadcast_run(jobs, log_label=f"Broadcast to {len(jobs)} members")

        btns = ctk.CTkFrame(compose, fg_color="transparent")
        btns.pack(fill="x", padx=20, pady=(0, 18))
        ctk.CTkButton(
            btns, text="👁️ Preview Count", fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["bg_hover"], height=42, corner_radius=10, command=preview
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            btns, text="💾 Save as Default", fg_color=COLORS["bg_elevated"],
            hover_color=COLORS["bg_hover"], height=42, corner_radius=10,
            command=lambda: (update_setting("broadcast_message",
                                            msg_box.get("1.0", "end").strip()),
                             messagebox.showinfo("Saved", "Default broadcast message saved."))
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            btns, text="📲 Send Broadcast", fg_color=COLORS["success"],
            hover_color=COLORS["success_dark"], height=42, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"), command=send
        ).pack(side="right")

        # Live progress card (populated during a broadcast run)
        self.broadcast_status = GlowingCard(wrapper)
        self.broadcast_status.pack(fill="x", pady=10)
        ctk.CTkLabel(
            self.broadcast_status, text="ℹ️ Broadcasts open one WhatsApp chat at a time so you "
            "stay in control. Progress will appear here.",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
            wraplength=700, justify="left"
        ).pack(anchor="w", padx=20, pady=18)

    def _broadcast_run(self, jobs, log_label=None, index=0):
        """Open WhatsApp for each recipient sequentially with a small stagger."""
        jobs = [j for j in jobs if j.get("phone")]
        if not jobs:
            return
        if index == 0 and log_label:
            self._log_action(log_label)

        if index >= len(jobs):
            if getattr(self, "broadcast_status", None) and self.broadcast_status.winfo_exists():
                for w in self.broadcast_status.winfo_children():
                    w.destroy()
                ctk.CTkLabel(
                    self.broadcast_status,
                    text=f"✅ Done — opened {len(jobs)} WhatsApp chat(s).",
                    font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["success"]
                ).pack(anchor="w", padx=20, pady=18)
            return

        job = jobs[index]
        try:
            send_whatsapp(job["phone"], job["message"])
        except Exception:
            pass

        if getattr(self, "broadcast_status", None) and self.broadcast_status.winfo_exists():
            for w in self.broadcast_status.winfo_children():
                w.destroy()
            ctk.CTkLabel(
                self.broadcast_status,
                text=f"📲 Sending… {index + 1}/{len(jobs)}  →  {job['name']}",
                font=ctk.CTkFont(size=13, weight="bold"), text_color=COLORS["info"]
            ).pack(anchor="w", padx=20, pady=(16, 4))
            bar = ctk.CTkProgressBar(self.broadcast_status, height=8,
                                     progress_color=COLORS["success"])
            bar.pack(fill="x", padx=20, pady=(0, 16))
            bar.set((index + 1) / len(jobs))

        # Stagger the next one so the browser/WhatsApp keeps up
        self.after(1200, lambda: self._broadcast_run(jobs, log_label, index + 1))

    def load_activity(self):
        self.create_header("Activity Tracker", "Monitor employee logins, actions and attendance")

        if self.user.get("role") != "admin":
            ctk.CTkLabel(
                self.content_frame,
                text="🔒 This area is available to administrators only.",
                font=ctk.CTkFont(size=15), text_color=COLORS["text_muted"]
            ).pack(pady=60)
            return

        db = get_db_session()
        try:
            employees = db.query(SystemUser).order_by(SystemUser.full_name).all()
            emp_data = [{"id": e.id, "username": e.username,
                         "name": e.full_name, "role": e.role} for e in employees]
        finally:
            db.close()

        if not emp_data:
            ctk.CTkLabel(self.content_frame, text="No employees found.",
                         text_color=COLORS["text_muted"]).pack(pady=40)
            return

        selector = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        selector.pack(fill="x", padx=30, pady=(0, 10))
        ctk.CTkLabel(selector, text="Employee:",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=(0, 12))

        name_to_id = {f"{e['name']} (@{e['username']})": e["id"] for e in emp_data}
        self._activity_var = ctk.StringVar(value=list(name_to_id.keys())[0])
        SearchableSelect(
            selector, values=list(name_to_id.keys()), variable=self._activity_var,
            fg_color=COLORS["bg_card"], button_color=COLORS["primary"], width=280,
            command=lambda _v: self._render_activity(name_to_id[self._activity_var.get()])
        ).pack(side="left")

        self._activity_body = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self._activity_body.pack(fill="both", expand=True, padx=30, pady=10)

        self._render_activity(name_to_id[self._activity_var.get()])

    def _render_activity(self, employee_id):
        for w in self._activity_body.winfo_children():
            w.destroy()

        db = get_db_session()
        try:
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            logs = db.query(EmployeeLog).filter(
                EmployeeLog.employee_id == employee_id
            ).order_by(EmployeeLog.created_at.desc()).limit(200).all()

            total = len(logs)
            today_count = sum(1 for l in logs if l.created_at and l.created_at.replace(tzinfo=None) >= today)
            logins = sum(1 for l in logs if l.action == "Logged in")
            last_login = next((l.created_at for l in logs if l.action == "Logged in"), None)
            last_active = logs[0].created_at if logs else None

            log_rows = [{
                "action": l.action,
                "ts": l.created_at.strftime("%Y-%m-%d %H:%M") if l.created_at else ""
            } for l in logs]
        finally:
            db.close()

        # Stat cards
        stats_frame = ctk.CTkFrame(self._activity_body, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 10))
        stats = [
            ("📋", str(total), "Total Actions", COLORS["primary"]),
            ("📅", str(today_count), "Actions Today", COLORS["info"]),
            ("🔑", str(logins), "Total Logins", COLORS["success"]),
            ("🕒", last_active.strftime("%m-%d %H:%M") if last_active else "—",
             "Last Active", COLORS["secondary"]),
        ]
        cols = self.grid_cols(wide=4, narrow=2, tiny=1)
        for i, (icon, value, label, color) in enumerate(stats):
            card = StatCard(stats_frame, icon, value, label, color)
            card.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="nsew")
        for c in range(cols):
            stats_frame.grid_columnconfigure(c, weight=1)

        if last_login:
            ctk.CTkLabel(
                self._activity_body,
                text=f"🔑 Last login: {last_login.strftime('%Y-%m-%d %H:%M')}",
                font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]
            ).pack(anchor="w", pady=(0, 6))

        # Timeline
        timeline = ctk.CTkScrollableFrame(self._activity_body, fg_color=COLORS["bg_card"],
                                          corner_radius=16)
        timeline.pack(fill="both", expand=True, pady=6)
        ctk.CTkLabel(
            timeline, text="🕒 Activity Timeline",
            font=ctk.CTkFont(size=15, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=15, pady=12)

        if not log_rows:
            ctk.CTkLabel(timeline, text="No activity recorded yet.",
                         text_color=COLORS["text_muted"]).pack(pady=20)
        for r in log_rows:
            action = r["action"]
            if "In" in action and "Clock" in action:
                icon = "🟢"
            elif "Out" in action and "Clock" in action:
                icon = "🔴"
            elif action.startswith("Check-in"):
                icon = "✅"
            elif action == "Logged in":
                icon = "🔑"
            elif action.startswith("Task"):
                icon = "📌"
            else:
                icon = "📝"
            row = ctk.CTkFrame(timeline, fg_color=COLORS["bg_elevated"], corner_radius=8)
            row.pack(fill="x", padx=12, pady=3)
            ctk.CTkLabel(row, text=icon, font=ctk.CTkFont(size=14)).pack(side="left", padx=10, pady=8)
            ctk.CTkLabel(row, text=action, font=ctk.CTkFont(size=13),
                         text_color=COLORS["text"], anchor="w").pack(
                side="left", padx=5, fill="x", expand=True)
            ctk.CTkLabel(row, text=r["ts"], font=ctk.CTkFont(size=11),
                         text_color=COLORS["text_muted"]).pack(side="right", padx=15)

    def load_settings(self):
        header = self.create_header("Settings", "Configure system preferences")
        settings = load_settings()

        settings_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Appearance
        appear_card = GlowingCard(settings_frame)
        appear_card.pack(fill="x", pady=10)

        ctk.CTkLabel(appear_card, text="🎨 Appearance", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=15)

        theme_frame = ctk.CTkFrame(appear_card, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(theme_frame, text="Theme Mode:").pack(side="left")
        SearchableSelect(
            theme_frame, values=["Dark", "Light", "System"], width=140,
            command=lambda v: ctk.set_appearance_mode(v.lower())
        ).pack(side="right")

        # ---- Messaging & WhatsApp ----
        msg_card = GlowingCard(settings_frame, glow_color=COLORS["success"])
        msg_card.pack(fill="x", pady=10)
        ctk.CTkLabel(msg_card, text="💬 Messaging & WhatsApp",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=15)
        ctk.CTkLabel(
            msg_card,
            text="Placeholders: {name} {age} {days} {plan} {date} {gym_name}",
            font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=20)

        grid = ctk.CTkFrame(msg_card, fg_color="transparent")
        grid.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(grid, text="Gym Name").grid(row=0, column=0, sticky="w", pady=6, padx=(0, 10))
        gym_entry = ctk.CTkEntry(grid, height=40, fg_color=COLORS["bg_dark"], corner_radius=8)
        gym_entry.insert(0, settings.get("gym_name", ""))
        gym_entry.grid(row=0, column=1, sticky="ew", pady=6)

        ctk.CTkLabel(grid, text="Country Code (no +)").grid(row=1, column=0, sticky="w", pady=6, padx=(0, 10))
        cc_entry = ctk.CTkEntry(grid, height=40, fg_color=COLORS["bg_dark"], corner_radius=8)
        cc_entry.insert(0, settings.get("country_code", "212"))
        cc_entry.grid(row=1, column=1, sticky="ew", pady=6)
        grid.grid_columnconfigure(1, weight=1)

        def template_box(title, key):
            ctk.CTkLabel(msg_card, text=title, font=ctk.CTkFont(size=13, weight="bold")).pack(
                anchor="w", padx=20, pady=(12, 4))
            box = ctk.CTkTextbox(msg_card, height=90, fg_color=COLORS["bg_dark"],
                                 border_color=COLORS["border"], border_width=1, corner_radius=8,
                                 font=ctk.CTkFont(size=12))
            box.pack(fill="x", padx=20)
            box.insert("1.0", settings.get(key, ""))
            return box

        bday_box = template_box("🎂 Birthday Auto-Message", "birthday_message")
        exp_box = template_box("⏰ Expiry Reminder Message", "expiry_message")
        bcast_box = template_box("📢 Default Broadcast Message", "broadcast_message")

        def save_messaging():
            s = load_settings()
            s["gym_name"] = gym_entry.get().strip() or "Gym Platform"
            s["country_code"] = "".join(c for c in cc_entry.get() if c.isdigit()) or "212"
            s["birthday_message"] = bday_box.get("1.0", "end").strip()
            s["expiry_message"] = exp_box.get("1.0", "end").strip()
            s["broadcast_message"] = bcast_box.get("1.0", "end").strip()
            save_settings(s)
            self._log_action("Updated messaging settings")
            messagebox.showinfo("Saved", "Messaging settings saved successfully!")

        ctk.CTkButton(
            msg_card, text="💾 Save Messaging Settings", fg_color=COLORS["success"],
            hover_color=COLORS["success_dark"], height=44, corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"), command=save_messaging
        ).pack(fill="x", padx=20, pady=18)

        # ---- Automation / Notifications ----
        notif_card = GlowingCard(settings_frame)
        notif_card.pack(fill="x", pady=10)
        ctk.CTkLabel(notif_card, text="🔔 Automation & Reminders",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=15)

        toggles = [
            ("Show birthday reminders on startup", "auto_birthday_enabled"),
            ("Show expiry reminders on startup", "auto_expiry_enabled"),
        ]
        for label, key in toggles:
            row = ctk.CTkFrame(notif_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=6)
            ctk.CTkLabel(row, text=label).pack(side="left")
            var = ctk.BooleanVar(value=bool(settings.get(key, True)))
            ctk.CTkSwitch(
                row, text="", variable=var,
                command=lambda k=key, v=var: update_setting(k, v.get())
            ).pack(side="right")

        ctk.CTkFrame(notif_card, height=10, fg_color="transparent").pack()
    
    def load_maintenance(self):
        """Maintenance & Financial Overview - Shows all expenses, revenue, and savings."""
        self.create_header("🔧 Maintenance & Financial Overview", 
                          "Track expenses, revenue, and savings for your gym platform")
        
        db = get_db_session()
        try:
            today = date.today()
            month_start = today.replace(day=1)
            year_start = today.replace(month=1, day=1)
            
            # Get all expenses
            all_expenses = db.query(Expense).all()
            total_expenses = sum(float(e.amount) for e in all_expenses) if all_expenses else 0
            
            monthly_exp = [e for e in all_expenses if e.created_at.date() >= month_start]
            monthly_expenses = sum(float(e.amount) for e in monthly_exp)
            
            yearly_exp = [e for e in all_expenses if e.created_at.date() >= year_start]
            yearly_expenses = sum(float(e.amount) for e in yearly_exp)
            
            # Get staff salaries (monthly recurring)
            staff = db.query(SystemUser).filter(SystemUser.is_active == True).all()
            monthly_salaries = sum(float(u.salary or 0) for u in staff)
            
            # Get all revenue from payments
            all_payments = db.query(Payment).all()
            total_revenue = sum(float(p.amount) for p in all_payments) if all_payments else 0
            
            monthly_pay = [p for p in all_payments if p.paid_at.date() >= month_start]
            monthly_revenue = sum(float(p.amount) for p in monthly_pay)
            
            yearly_pay = [p for p in all_payments if p.paid_at.date() >= year_start]
            yearly_revenue = sum(float(p.amount) for p in yearly_pay)
            
            # Calculate savings/profit
            total_profit = total_revenue - (total_expenses + monthly_salaries)
            monthly_profit = monthly_revenue - (monthly_expenses + monthly_salaries)
            yearly_profit = yearly_revenue - (yearly_expenses + (monthly_salaries * (today.month)))
            
            # Category breakdown for expenses
            expense_by_category = {}
            for e in all_expenses:
                expense_by_category[e.category] = expense_by_category.get(e.category, 0) + float(e.amount)
            
            # Active members count
            active_members = db.query(Member).filter(Member.is_active == True, Member.end_date >= today).count()
            
        finally:
            db.close()
        
        # Main content
        content = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=10)
        
        # Financial Overview Stats
        stats_frame = ctk.CTkFrame(content, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 15))
        
        stats = [
            ("💵", f"${total_revenue:,.2f}", "Total Revenue", COLORS["success"]),
            ("📉", f"${total_expenses + monthly_salaries:,.2f}", "Total Expenses", COLORS["danger"]),
            ("💰", f"${total_profit:,.2f}", "Total Savings", COLORS["gold"] if total_profit >= 0 else COLORS["danger"]),
            ("👥", str(active_members), "Active Members", COLORS["primary"]),
        ]
        
        cols = self.grid_cols(wide=4, narrow=2, tiny=1)
        for i, (icon, value, label, color) in enumerate(stats):
            card = StatCard(stats_frame, icon, value, label, color)
            card.grid(row=i // cols, column=i % cols, padx=8, pady=8, sticky="nsew")
        for c in range(cols):
            stats_frame.grid_columnconfigure(c, weight=1)
        
        # Two-column layout
        main_row = ctk.CTkFrame(content, fg_color="transparent")
        main_row.pack(fill="both", expand=True)
        main_row.grid_columnconfigure(0, weight=1)
        main_row.grid_columnconfigure(1, weight=1)
        
        # Left Column - Revenue & Profit Analysis
        left_col = ctk.CTkFrame(main_row, fg_color="transparent")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Monthly Summary Card
        monthly_card = GlowingCard(left_col, glow_color=COLORS["primary"])
        monthly_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            monthly_card, text="📅 This Month's Summary",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        month_data = [
            ("💵 Revenue", f"${monthly_revenue:,.2f}", COLORS["success"]),
            ("📉 Expenses", f"${monthly_expenses:,.2f}", COLORS["danger"]),
            ("👔 Salaries", f"${monthly_salaries:,.2f}", COLORS["warning"]),
            ("💰 Net Savings", f"${monthly_profit:,.2f}", COLORS["gold"] if monthly_profit >= 0 else COLORS["danger"]),
        ]
        
        for label, value, color in month_data:
            row = ctk.CTkFrame(monthly_card, fg_color=COLORS["bg_elevated"], corner_radius=8)
            row.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=13),
                        text_color=COLORS["text"]).pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=color).pack(side="right", padx=15)
        
        ctk.CTkFrame(monthly_card, height=15, fg_color="transparent").pack()
        
        # Yearly Summary Card
        yearly_card = GlowingCard(left_col, glow_color=COLORS["success"])
        yearly_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            yearly_card, text="📊 This Year's Summary",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        year_data = [
            ("💵 Total Revenue", f"${yearly_revenue:,.2f}", COLORS["success"]),
            ("📉 Total Expenses", f"${yearly_expenses:,.2f}", COLORS["danger"]),
            ("👔 Est. Salaries", f"${monthly_salaries * today.month:,.2f}", COLORS["warning"]),
            ("💰 Net Savings", f"${yearly_profit:,.2f}", COLORS["gold"] if yearly_profit >= 0 else COLORS["danger"]),
        ]
        
        for label, value, color in year_data:
            row = ctk.CTkFrame(yearly_card, fg_color=COLORS["bg_elevated"], corner_radius=8)
            row.pack(fill="x", padx=15, pady=3)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=13),
                        text_color=COLORS["text"]).pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=14, weight="bold"),
                        text_color=color).pack(side="right", padx=15)
        
        ctk.CTkFrame(yearly_card, height=15, fg_color="transparent").pack()
        
        # Right Column - Expense Breakdown
        right_col = ctk.CTkFrame(main_row, fg_color="transparent")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Expense Categories Breakdown
        expense_card = GlowingCard(right_col, glow_color=COLORS["danger"])
        expense_card.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            expense_card, text="📈 Expense Breakdown by Category",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        expense_scroll = ctk.CTkScrollableFrame(expense_card, fg_color="transparent", height=200)
        expense_scroll.pack(fill="x", padx=10, pady=(0, 15))
        
        sorted_expenses = sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_expenses:
            for cat, amount in sorted_expenses[:12]:
                row = ctk.CTkFrame(expense_scroll, fg_color=COLORS["bg_elevated"], corner_radius=6)
                row.pack(fill="x", pady=2, padx=5)
                icon = EXPENSE_ICONS.get(cat.lower(), "📝")
                ctk.CTkLabel(row, text=f"{icon} {cat}", font=ctk.CTkFont(size=12),
                            text_color=COLORS["text"]).pack(side="left", padx=12, pady=8)
                # Calculate percentage
                pct = (amount / total_expenses * 100) if total_expenses > 0 else 0
                ctk.CTkLabel(row, text=f"${amount:,.2f} ({pct:.1f}%)", 
                            font=ctk.CTkFont(size=12, weight="bold"),
                            text_color=COLORS["danger"]).pack(side="right", padx=12)
        else:
            ctk.CTkLabel(expense_scroll, text="No expenses recorded yet",
                        text_color=COLORS["text_muted"]).pack(pady=20)
        
        # Staff Costs Card
        staff_card = GlowingCard(right_col, glow_color=COLORS["warning"])
        staff_card.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            staff_card, text="👔 Staff Costs (Monthly)",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        db = get_db_session()
        try:
            staff_list = db.query(SystemUser).filter(SystemUser.is_active == True).all()
            for emp in staff_list[:8]:
                row = ctk.CTkFrame(staff_card, fg_color=COLORS["bg_elevated"], corner_radius=6)
                row.pack(fill="x", padx=15, pady=2)
                ctk.CTkLabel(row, text=f"👤 {emp.full_name}", font=ctk.CTkFont(size=12),
                            text_color=COLORS["text"]).pack(side="left", padx=12, pady=8)
                ctk.CTkLabel(row, text=f"${emp.salary or 0:,.2f}/mo", 
                            font=ctk.CTkFont(size=12, weight="bold"),
                            text_color=COLORS["warning"]).pack(side="right", padx=12)
        finally:
            db.close()
        
        # Total staff cost
        total_row = ctk.CTkFrame(staff_card, fg_color=COLORS["bg_dark"], corner_radius=8)
        total_row.pack(fill="x", padx=15, pady=(8, 15))
        ctk.CTkLabel(total_row, text="💰 Total Monthly Staff Cost", 
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=COLORS["text"]).pack(side="left", padx=15, pady=10)
        ctk.CTkLabel(total_row, text=f"${monthly_salaries:,.2f}", 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=COLORS["gold"]).pack(side="right", padx=15)
        
        # Maintenance Items Card
        maint_card = GlowingCard(content, glow_color=COLORS["info"])
        maint_card.pack(fill="x", pady=15)
        
        ctk.CTkLabel(
            maint_card, text="🛠️ Maintenance & Operational Items",
            font=ctk.CTkFont(size=16, weight="bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(
            maint_card, text="Common maintenance expenses for gym operations",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=20, pady=(0, 10))
        
        # Common maintenance items with descriptions and typical prices
        maintenance_items = [
            ("🏋️ Equipment Maintenance", "Regular servicing of gym machines, treadmills, weights", "$200-500/month"),
            ("🔧 Building Repairs", "HVAC, plumbing, electrical repairs", "$100-300/month"),
            ("🧹 Cleaning Services", "Daily cleaning, sanitization, waste disposal", "$300-600/month"),
            ("💡 Utilities", "Electricity, water, gas, internet", "$500-1500/month"),
            ("🔐 Security", "Security system, cameras, monitoring", "$100-250/month"),
            ("🏠 Rent/Lease", "Monthly facility rent or mortgage", "Varies"),
            ("🧴 Supplies", "Cleaning supplies, toiletries, towels", "$100-200/month"),
            ("📋 Insurance", "Liability, property, equipment insurance", "$200-500/month"),
        ]
        
        for name, desc, price in maintenance_items:
            row = ctk.CTkFrame(maint_card, fg_color=COLORS["bg_elevated"], corner_radius=8)
            row.pack(fill="x", padx=15, pady=3)
            
            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True, padx=15, pady=10)
            
            ctk.CTkLabel(info, text=name, font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=COLORS["text"]).pack(anchor="w")
            ctk.CTkLabel(info, text=desc, font=ctk.CTkFont(size=11),
                        text_color=COLORS["text_muted"]).pack(anchor="w")
            
            ctk.CTkLabel(row, text=price, font=ctk.CTkFont(size=13, weight="bold"),
                        text_color=COLORS["info"]).pack(side="right", padx=20, pady=10)
        
        ctk.CTkFrame(maint_card, height=10, fg_color="transparent").pack()
    
    def load_logs(self):
        header = self.create_header("Audit Logs", "Track all system activities")
        
        list_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color=COLORS["bg_card"], corner_radius=16)
        list_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        db = get_db_session()
        try:
            logs = db.query(EmployeeLog).order_by(EmployeeLog.created_at.desc()).limit(100).all()
            
            for log in logs:
                row = ctk.CTkFrame(list_frame, fg_color=COLORS["bg_elevated"], corner_radius=8)
                row.pack(fill="x", padx=10, pady=3)
                
                ctk.CTkLabel(row, text="📝", font=ctk.CTkFont(size=14)).pack(side="left", padx=10, pady=8)
                
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)
                
                ctk.CTkLabel(info, text=log.action, font=ctk.CTkFont(size=12), text_color=COLORS["text"]).pack(anchor="w")
                ctk.CTkLabel(info, text=f"By: {log.employee_username}", font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"]).pack(anchor="w")
                
                ctk.CTkLabel(row, text=log.created_at.strftime("%Y-%m-%d %H:%M"), font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"]).pack(side="right", padx=15)
        finally:
            db.close()


class EliteFitnessApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gym Platform")

        # Responsive: size the window to a sensible fraction of the screen,
        # clamped so it works on small laptops and large monitors alike.
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        win_w = max(1000, min(1500, int(sw * 0.85)))
        win_h = max(640, min(900, int(sh * 0.85)))
        x = (sw - win_w) // 2
        y = (sh - win_h) // 3
        self.geometry(f"{win_w}x{win_h}+{x}+{y}")
        # Allow shrinking on small screens while staying usable
        self.minsize(900, 600)
        self.configure(fg_color=COLORS["bg_dark"])

        self.current_user = None
        self._db_ready = False

        # Kick off database init in the background while the splash animates
        threading.Thread(target=self._init_db_bg, daemon=True).start()
        self.show_splash()

    def _init_db_bg(self):
        try:
            init_db()
        except Exception as e:
            print(f"DB init error: {e}")
        finally:
            self._db_ready = True

    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_splash(self):
        self._clear()
        SplashScreen(self, on_done=self._splash_done).pack(fill="both", expand=True)

    def _splash_done(self):
        # Wait for the DB thread to finish before showing login
        if not self._db_ready:
            self.after(120, self._splash_done)
            return
        self.show_login()

    def show_login(self):
        self._clear()
        LoginFrame(self, self.on_login_success).pack(fill="both", expand=True)

    def on_login_success(self, user):
        self.current_user = user
        self.show_post_login_loading()

    def show_post_login_loading(self):
        """Professional loading animation that previews the app's content."""
        self._clear()
        name = (self.current_user or {}).get("full_name", "")
        steps = [
            f"Welcome back, {name}! 💪" if name else "Welcome back! 💪",
            "Loading members & check-ins…",
            "Calculating payments & finance…",
            "Reviewing expenses & salaries…",
            "Checking memberships & birthdays…",
            "Stepping onto the floor…",
        ]
        SplashScreen(self, on_done=self.show_dashboard, steps=steps).pack(
            fill="both", expand=True)

    def show_dashboard(self):
        self._clear()
        DashboardFrame(self, self.current_user, self.logout).pack(fill="both", expand=True)

    def logout(self):
        self.current_user = None
        self.show_login()


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("   🏋️  GYM PLATFORM  v2.0")
    print("=" * 50)
    print("🚀 Launching desktop application...")

    app = EliteFitnessApp()
    app.mainloop()
