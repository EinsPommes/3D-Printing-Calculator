import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from typing import Dict
import glob
from pathlib import Path
import subprocess
import sys
import shutil
import requests
import webbrowser

class Printer:
    def __init__(self, name, power_consumption):
        self.name = name
        self.power_consumption = power_consumption

    def to_dict(self):
        return {
            "name": self.name,
            "power_consumption": self.power_consumption
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data["name"],
            power_consumption=data["power_consumption"]
        )

class PrintCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Druck Kostenrechner")
        self.root.geometry("900x800")
        
        # Farben definieren
        self.colors = {
            'bg': '#1a1a1a',           # Sehr dunkler Hintergrund
            'bg_light': '#2d2d2d',     # Dunkelgrauer Hintergrund
            'card': '#333333',         # Kartenhintergrund
            'accent': '#0d99ff',       # Helles Blau
            'success': '#2ea043',      # Grün
            'text': '#ffffff',         # Weiß
            'text_dim': '#999999',     # Gedimmtes Grau
            'input_bg': '#404040',     # Eingabefeld Hintergrund
            'footer_text': '#666666',  # Footer Text
            'button': '#9b30ff',       # Helles Lila
            'button_hover': '#a560ff'  # Helleres Lila beim Hover
        }
        
        # Theme und Styles setzen
        self.setup_styles()
        
        # Version und Copyright
        self.version = "1.0.0"
        self.copyright = " 2024 chill-zone.xyz"
        self.github_url = "https://github.com/EinsPommes/3D-Printing-Calculator"
        
        # Initialisiere Variablen
        self.printer_var = tk.StringVar()
        self.printers = []
        self.orca_path = tk.StringVar()
        self.cost_entries = {}
        self.result_labels = {}
        self.config = {}
        
        # Erstelle das Notebook für Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Lade Konfiguration und Drucker
        self.load_config()
        self.load_printers()
        
        # Erstelle die Tabs
        self.create_main_tab()
        self.create_settings_tab()
        
        # Erstelle Footer
        self.create_footer()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Konfiguriere die Styles
        style.configure('Main.TFrame', background=self.colors['bg'])
        style.configure('Card.TFrame', background=self.colors['card'])
        style.configure('Card.TLabelframe', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('Card.TLabelframe.Label', background=self.colors['bg'], foreground=self.colors['text'])
        
        style.configure('Custom.TButton',
                       background=self.colors['button'],
                       foreground=self.colors['text'],
                       borderwidth=1,
                       relief='solid',
                       padding=5)
        
        style.map('Custom.TButton',
                 background=[('active', self.colors['button_hover'])])
        
        style.configure('Footer.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['footer_text'])
        
        # Konfiguriere den Root-Hintergrund
        self.root.configure(bg=self.colors['bg'])
        
        style.configure('TNotebook',
                       background=self.colors['bg'],
                       tabmargins=[0, 0, 0, 0])
        
        style.configure('TNotebook.Tab',
                       padding=[10, 5],
                       background=self.colors['bg_light'],
                       foreground=self.colors['text'])
                       
        style.map('TNotebook.Tab',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', self.colors['text'])])

        # Frame Styles
        style.configure('Main.TFrame',
                       background=self.colors['bg'])
        
        style.configure('Card.TFrame',
                       background=self.colors['card'])

        # Label Styles
        style.configure('TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 10))
        
        style.configure('Header.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 24, 'bold'))
        
        style.configure('Section.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Card.TLabel',
                       background=self.colors['card'],
                       foreground=self.colors['text'],
                       font=('Segoe UI', 10))

        # Entry Style
        style.configure('TEntry',
                       fieldbackground=self.colors['input_bg'],
                       foreground=self.colors['text'],
                       insertcolor=self.colors['text'])

        # Combobox Style
        style.configure('TCombobox',
                       fieldbackground=self.colors['input_bg'],
                       background=self.colors['success'],
                       foreground=self.colors['text'],
                       arrowcolor=self.colors['text'])
        
        style.map('TCombobox',
                 fieldbackground=[('readonly', self.colors['input_bg'])],
                 selectbackground=[('readonly', self.colors['input_bg'])])

        # Footer Label Style
        style.configure('Footer.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['footer_text'],
                       font=('Segoe UI', 9))

    def create_main_tab(self):
        self.root.configure(bg=self.colors['bg'])
        
        main_tab = ttk.Frame(self.notebook, style='Main.TFrame')
        self.notebook.add(main_tab, text='Kostenrechner')
        
        main_container = ttk.Frame(main_tab, style='Main.TFrame')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Titel
        ttk.Label(main_container,
                 text="3D Druck Kostenrechner",
                 style='Header.TLabel').pack(pady=(0, 30))
        
        # Content Container
        content = ttk.Frame(main_container, style='Main.TFrame')
        content.pack(fill='both', expand=True)
        
        # Linke Spalte
        left_column = ttk.Frame(content, style='Main.TFrame')
        left_column.pack(side='left', fill='both', expand=True, padx=(0, 20))
        
        # DRUCKER AUSWÄHLEN
        ttk.Label(left_column,
                 text="DRUCKER AUSWÄHLEN",
                 style='Section.TLabel').pack(anchor='w', pady=(0, 10))
        
        printer_frame = ttk.Frame(left_column, style='Card.TFrame')
        printer_frame.pack(fill='x', pady=(0, 20))
        
        combo_frame = ttk.Frame(printer_frame, style='Card.TFrame')
        combo_frame.pack(fill='x', padx=10, pady=10)
        
        self.printer_combo = ttk.Combobox(combo_frame,
                                        textvariable=self.printer_var,
                                        values=self.get_printer_list(),
                                        state='readonly')
        self.printer_combo.pack(side='left', fill='x', expand=True)
        
        ttk.Button(combo_frame,
                  text="Einstellungen",
                  command=lambda: self.notebook.select(1),
                  style='Custom.TButton').pack(side='right', padx=(10, 0))
        
        # DATEN IMPORTIEREN
        ttk.Label(left_column,
                 text="DATEN IMPORTIEREN",
                 style='Section.TLabel').pack(anchor='w', pady=(0, 10))
        
        import_frame = ttk.Frame(left_column, style='Card.TFrame')
        import_frame.pack(fill='x', pady=(0, 20))
        
        import_content = ttk.Frame(import_frame, style='Card.TFrame')
        import_content.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(import_content,
                  text="Aus Orca importieren",
                  command=self.import_from_orca,
                  style='Custom.TButton').pack(fill='x')
        
        self.orca_status = ttk.Label(import_content,
                                   text="",
                                   style='Card.TLabel')
        self.orca_status.pack(pady=(10, 0))
        
        # KOSTEN EINGEBEN
        ttk.Label(left_column,
                 text="KOSTEN EINGEBEN",
                 style='Section.TLabel').pack(anchor='w', pady=(0, 10))
        
        costs_frame = ttk.Frame(left_column, style='Card.TFrame')
        costs_frame.pack(fill='x', pady=(0, 20))
        
        input_frame = ttk.Frame(costs_frame, style='Card.TFrame')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        fields = [
            ("Druckzeit (h)", ""),
            ("Filament Gewicht (g)", ""),
            ("Stromkosten (€/kWh)", ""),
            ("Filament Kosten (€/kg)", ""),
            ("Gewinnmarge (%)", "")
        ]
        
        for i, (text, _) in enumerate(fields):
            frame = ttk.Frame(input_frame, style='Card.TFrame')
            frame.pack(fill='x', pady=(0, 5) if i < len(fields)-1 else 0)
            
            ttk.Label(frame,
                     text=text,
                     style='Card.TLabel').pack(side='left')
            
            entry = ttk.Entry(frame, width=15)
            entry.pack(side='right')
            self.cost_entries[text] = entry
        
        button_frame = ttk.Frame(costs_frame, style='Card.TFrame')
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        ttk.Button(button_frame,
                  text="Berechnen",
                  command=self.calculate_costs,
                  style='Custom.TButton').pack(fill='x')
        
        # Rechte Spalte
        right_column = ttk.Frame(content, style='Main.TFrame')
        right_column.pack(side='left', fill='both', expand=True)
        
        # ERGEBNIS
        ttk.Label(right_column,
                 text="ERGEBNIS",
                 style='Section.TLabel').pack(anchor='w', pady=(0, 10))
        
        results_frame = ttk.Frame(right_column, style='Card.TFrame')
        results_frame.pack(fill='x', pady=(0, 20))
        
        results_content = ttk.Frame(results_frame, style='Card.TFrame')
        results_content.pack(fill='x', padx=10, pady=10)
        
        results = [
            ("Materialkosten", ""),
            ("Stromkosten", ""),
            ("Gesamtkosten", ""),
            ("Endpreis", "")
        ]
        
        for text, _ in results:
            frame = ttk.Frame(results_content, style='Card.TFrame')
            frame.pack(fill='x', pady=2)
            
            ttk.Label(frame,
                     text=text,
                     style='Card.TLabel').pack(side='left')
            
            result = ttk.Label(frame,
                             text="0.00 €",
                             style='Card.TLabel')
            result.pack(side='right')
            self.result_labels[text] = result

    def create_settings_tab(self):
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Einstellungen")

        # Orca Slicer Einstellungen
        orca_settings = ttk.LabelFrame(settings_frame,
                                     text="Orca Slicer",
                                     style='Card.TLabelframe')
        orca_settings.pack(fill='x', padx=10, pady=10)

        path_frame = ttk.Frame(orca_settings, style='Card.TFrame')
        path_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(path_frame, text="Installationspfad:").pack(side='left')
        
        self.orca_path = tk.StringVar(value=self.config.get('orca_path', ''))
        path_entry = ttk.Entry(path_frame, textvariable=self.orca_path)
        path_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        ttk.Button(path_frame,
                  text="Durchsuchen",
                  style='Custom.TButton',
                  command=self.browse_orca_path).pack(side='left')

        # Update Einstellungen
        update_settings = ttk.LabelFrame(settings_frame,
                                       text="Updates",
                                       style='Card.TLabelframe')
        update_settings.pack(fill='x', padx=10, pady=10)

        update_frame = ttk.Frame(update_settings, style='Card.TFrame')
        update_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(update_frame,
                 text=f"Aktuelle Version: {self.version}").pack(side='left')

        ttk.Button(update_frame,
                  text="Nach Updates suchen",
                  style='Custom.TButton',
                  command=self.check_for_updates).pack(side='right')

        # Drucker Verwaltung
        printer_frame = ttk.LabelFrame(settings_frame,
                                     text="Drucker Verwaltung",
                                     style='Card.TLabelframe')
        printer_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Frame für Drucker Liste und Scrollbar
        list_frame = ttk.Frame(printer_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        # Drucker Liste
        self.printer_listbox = tk.Listbox(list_frame,
                                        yscrollcommand=scrollbar.set,
                                        height=6,
                                        selectmode=tk.SINGLE)
        self.printer_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.printer_listbox.yview)

        # Button Frame
        button_frame = ttk.Frame(printer_frame)
        button_frame.pack(fill='x', padx=10, pady=5)

        # Buttons für Drucker Verwaltung
        ttk.Button(button_frame,
                  text="Drucker Hinzufügen",
                  style='Custom.TButton',
                  command=self.add_printer).pack(side='left', padx=5)

        ttk.Button(button_frame,
                  text="Drucker Bearbeiten",
                  style='Custom.TButton',
                  command=self.edit_printer).pack(side='left', padx=5)

        ttk.Button(button_frame,
                  text="Drucker Entfernen",
                  style='Custom.TButton',
                  command=self.remove_printer).pack(side='left', padx=5)

        # Initialisiere die Drucker-Liste
        self.update_printer_lists()

    def load_printers(self):
        try:
            with open('printers.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.printers = [Printer.from_dict(p) for p in data]
        except FileNotFoundError:
            # Erstelle Standard-Drucker
            self.printers = [
                Printer("Ender 3 V2", 150),
                Printer("Bambu X1C", 150),
                Printer("Voron 2.4", 300)
            ]
            self.save_printers()
        self.update_printer_lists()

    def save_printers(self):
        data = [p.to_dict() for p in self.printers]
        with open('printers.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def get_printer_list(self):
        """Gibt eine Liste der Drucker im Format 'Name (Stromverbrauch W)' zurück"""
        return [f"{printer.name} ({printer.power_consumption} W)" for printer in self.printers]

    def get_printer_by_name(self, name):
        """Findet einen Drucker anhand seines Namens"""
        for printer in self.printers:
            if printer.name == name:
                return printer
        return None

    def update_printer_lists(self):
        """Aktualisiert die Drucker-Liste und die Combobox"""
        if hasattr(self, 'printer_listbox'):
            self.printer_listbox.delete(0, tk.END)
            for display_name in self.get_printer_list():
                self.printer_listbox.insert(tk.END, display_name)
        
        if hasattr(self, 'printer_combo'):
            current = self.printer_var.get()
            self.printer_combo['values'] = self.get_printer_list()
            if current and current in self.get_printer_list():
                self.printer_var.set(current)
            elif self.get_printer_list():
                self.printer_var.set(self.get_printer_list()[0])
            else:
                self.printer_var.set('')

    def import_from_orca(self):
        try:
            # Hole den konfigurierten Pfad
            orca_path = self.orca_path.get()
            
            possible_paths = [
                os.path.expanduser("~/AppData/Roaming/OrcaSlicer"),
                "C:/Program Files/OrcaSlicer",
                "C:/Program Files (x86)/OrcaSlicer",
                "D:/Program Files/OrcaSlicer",
            ]
            
            if orca_path and os.path.exists(orca_path):
                possible_paths.insert(0, orca_path)
            
            gcode_file = None
            for base_path in possible_paths:
                if os.path.exists(base_path):
                    for subdir in ['temp', 'cache', 'output']:
                        search_path = os.path.join(base_path, subdir)
                        if os.path.exists(search_path):
                            gcode_files = glob.glob(os.path.join(search_path, '*.gcode'))
                            if gcode_files:
                                gcode_file = max(gcode_files, key=os.path.getmtime)
                                break
                    if gcode_file:
                        break
            
            if not gcode_file:
                self.orca_status.configure(
                    text="⚠️ Keine Orca Dateien gefunden")
                return

            with open(gcode_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            import re
            time_match = re.search(
                r'estimated printing time = .*?(\d+)h\s*(\d+)m', 
                content, 
                re.IGNORECASE
            )
            if time_match:
                hours = float(time_match.group(1))
                minutes = float(time_match.group(2))
                total_hours = hours + (minutes / 60)
                self.cost_entries["Druckzeit (h)"].delete(0, tk.END)
                self.cost_entries["Druckzeit (h)"].insert(0, f"{total_hours:.2f}")
            
            filament_match = re.search(
                r'filament used = (\d+\.?\d*)g', 
                content, 
                re.IGNORECASE
            )
            if filament_match:
                weight = float(filament_match.group(1))
                self.cost_entries["Filament Gewicht (g)"].delete(0, tk.END)
                self.cost_entries["Filament Gewicht (g)"].insert(0, f"{weight:.1f}")
            
            self.orca_status.configure(
                text=f"✓ Erfolgreich importiert aus {os.path.basename(gcode_file)}")
            
        except Exception as e:
            self.orca_status.configure(
                text=f"⚠️ Fehler: {str(e)}")

    def load_config(self):
        """Lade die Konfiguration aus der config.json Datei"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                    self.orca_path.set(self.config.get('orca_path', ''))
        except Exception as e:
            messagebox.showwarning("Warnung", f"Fehler beim Laden der Konfiguration: {str(e)}")
            self.config = {}

    def save_config(self):
        """Speichere die Konfiguration in der config.json Datei"""
        try:
            self.config['orca_path'] = self.orca_path.get()
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Konfiguration: {str(e)}")

    def calculate_costs(self):
        try:
            printer_display = self.printer_var.get()
            if not printer_display:
                messagebox.showerror("Fehler", "Bitte wählen Sie einen Drucker aus!")
                return
            
            printer_name = self.get_printer_name_from_display(printer_display)
            printer = self.get_printer_by_name(printer_name)
            
            if not printer:
                messagebox.showerror("Fehler", "Drucker nicht gefunden!")
                return
            
            try:
                print_time = float(self.cost_entries["Druckzeit (h)"].get())
                filament_weight = float(self.cost_entries["Filament Gewicht (g)"].get())
                filament_cost = float(self.cost_entries["Filament Kosten (€/kg)"].get())
                power_cost = float(self.cost_entries["Stromkosten (€/kWh)"].get())
                profit_margin = float(self.cost_entries["Gewinnmarge (%)"].get())
            except ValueError:
                messagebox.showerror("Fehler", 
                                   "Bitte geben Sie gültige Zahlen ein!")
                return
            
            if print_time <= 0:
                messagebox.showerror("Fehler", 
                                   "Die Druckzeit muss größer als 0 sein!")
                return
            
            if filament_weight <= 0:
                messagebox.showerror("Fehler", 
                                   "Das Filament Gewicht muss größer als 0 sein!")
                return
            
            if profit_margin < 0:
                messagebox.showerror("Fehler", 
                                   "Die Gewinnmarge darf nicht negativ sein!")
                return
            
            power_consumption_kwh = printer.power_consumption * print_time / 1000
            power_costs = power_consumption_kwh * power_cost
            
            filament_costs = (filament_weight * filament_cost) / 1000
            
            # Berechne die Kosten
            material_costs = filament_costs
            electricity_costs = power_costs
            total_costs = material_costs + electricity_costs
            
            # Berechne den Endpreis mit Gewinnmarge
            profit = total_costs * (profit_margin / 100)
            final_price = total_costs + profit
            
            # Formatiere die Ausgabe
            def update_label(label, value):
                label.config(text=f"{value:.2f} €")
            
            # Aktualisiere die Ergebnisse
            update_label(self.result_labels["Materialkosten"], material_costs)
            update_label(self.result_labels["Stromkosten"], electricity_costs)
            update_label(self.result_labels["Gesamtkosten"], total_costs)
            update_label(self.result_labels["Endpreis"], final_price)
            
        except Exception as e:
            messagebox.showerror("Unerwarteter Fehler", f"Ein Fehler ist aufgetreten: {str(e)}")

    def browse_orca_path(self):
        path = filedialog.askdirectory(
            title="Wählen Sie den Orca Slicer Ordner"
        )
        if path:
            self.orca_path.set(path)
            self.save_config()
            messagebox.showinfo("Erfolg", "Orca Slicer Pfad wurde gespeichert!")

    def get_printer_name_from_display(self, display_name):
        """Extrahiert den Druckernamen aus der Anzeige"""
        if '(' in display_name:
            return display_name.split('(')[0].strip()
        return display_name

    def add_printer(self):
        # Erstelle ein neues Fenster für die Eingabe
        add_window = tk.Toplevel(self.root)
        add_window.title("Drucker Hinzufügen")
        add_window.geometry("300x200")

        # Eingabefelder
        ttk.Label(add_window, text="Name:").pack(pady=5)
        name_entry = ttk.Entry(add_window)
        name_entry.pack(pady=5)

        ttk.Label(add_window, text="Stromverbrauch (W):").pack(pady=5)
        power_entry = ttk.Entry(add_window)
        power_entry.pack(pady=5)

        def save_printer():
            name = name_entry.get().strip()
            try:
                power = float(power_entry.get().strip())
            except ValueError:
                messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Zahl für den Stromverbrauch ein.")
                return

            if not name:
                messagebox.showerror("Fehler", "Bitte geben Sie einen Namen ein.")
                return

            if power <= 0:
                messagebox.showerror("Fehler", "Der Stromverbrauch muss größer als 0 sein!")
                return

            # Überprüfe ob der Name bereits existiert
            if self.get_printer_by_name(name):
                messagebox.showerror("Fehler", "Ein Drucker mit diesem Namen existiert bereits.")
                return

            # Füge den neuen Drucker hinzu
            new_printer = Printer(name, power)
            self.printers.append(new_printer)
            self.save_printers()
            self.update_printer_lists()
            add_window.destroy()
            messagebox.showinfo("Erfolg", "Drucker wurde erfolgreich hinzugefügt.")

        # Speichern Button
        ttk.Button(add_window, text="Speichern", command=save_printer).pack(pady=20)

    def edit_printer(self):
        selected_indices = self.printer_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Drucker aus.")
            return

        selected_index = selected_indices[0]
        printer_name = self.printer_listbox.get(selected_index).split(" (")[0]
        printer = self.get_printer_by_name(printer_name)

        if not printer:
            messagebox.showerror("Fehler", "Drucker nicht gefunden.")
            return

        # Erstelle ein neues Fenster für die Bearbeitung
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Drucker Bearbeiten")
        edit_window.geometry("300x200")

        # Eingabefelder
        ttk.Label(edit_window, text="Name:").pack(pady=5)
        name_entry = ttk.Entry(edit_window)
        name_entry.insert(0, printer.name)
        name_entry.pack(pady=5)

        ttk.Label(edit_window, text="Stromverbrauch (W):").pack(pady=5)
        power_entry = ttk.Entry(edit_window)
        power_entry.insert(0, str(printer.power_consumption))
        power_entry.pack(pady=5)

        def save_changes():
            new_name = name_entry.get().strip()
            try:
                new_power = float(power_entry.get().strip())
            except ValueError:
                messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Zahl für den Stromverbrauch ein.")
                return

            if not new_name:
                messagebox.showerror("Fehler", "Bitte geben Sie einen Namen ein.")
                return

            # Überprüfe ob der neue Name bereits existiert (außer bei gleichem Drucker)
            existing_printer = self.get_printer_by_name(new_name)
            if existing_printer and existing_printer != printer:
                messagebox.showerror("Fehler", "Ein Drucker mit diesem Namen existiert bereits.")
                return

            # Aktualisiere die Druckerdaten
            printer.name = new_name
            printer.power_consumption = new_power

            # Speichere die Änderungen
            self.save_printers()
            self.update_printer_lists()
            edit_window.destroy()
            messagebox.showinfo("Erfolg", "Drucker wurde erfolgreich aktualisiert.")

        # Speichern Button
        ttk.Button(edit_window, text="Speichern", command=save_changes).pack(pady=20)

    def remove_printer(self):
        selected_indices = self.printer_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warnung", "Bitte wählen Sie einen Drucker aus.")
            return

        selected_index = selected_indices[0]
        printer_name = self.printer_listbox.get(selected_index).split(" (")[0]
        printer = self.get_printer_by_name(printer_name)

        if not printer:
            messagebox.showerror("Fehler", "Drucker nicht gefunden.")
            return

        if messagebox.askyesno("Drucker löschen", 
                             f"Möchten Sie den Drucker '{printer_name}' wirklich löschen?"):
            self.printers.remove(printer)
            self.save_printers()
            self.update_printer_lists()
            messagebox.showinfo("Erfolg", "Drucker wurde erfolgreich entfernt.")

    def check_for_updates(self):
        """Prüft auf Updates vom GitHub Repository"""
        try:
            # API-URL für das Repository
            api_url = "https://api.github.com/repos/EinsPommes/3D-Printing-Calculator/releases/latest"
            
            # Führe die Anfrage aus
            response = requests.get(api_url, timeout=5)
            response.raise_for_status()  # Wirft einen Fehler bei HTTP-Fehlern
            
            # Parse die Antwort
            latest_release = response.json()
            latest_version = latest_release['tag_name'].lstrip('v')
            
            # Vergleiche Versionen
            if latest_version > self.version:
                message = f"Eine neue Version ({latest_version}) ist verfügbar!\n"
                message += f"Aktuelle Version: {self.version}\n\n"
                message += "Möchten Sie die neue Version herunterladen?"
                
                if messagebox.askyesno("Update verfügbar", message):
                    # Öffne den Browser mit der Release-Seite
                    release_url = latest_release['html_url']
                    webbrowser.open(release_url)
            else:
                messagebox.showinfo("Kein Update verfügbar", 
                    f"Sie verwenden bereits die neueste Version ({self.version}).")
                
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Fehler", 
                "Konnte nicht nach Updates suchen.\nBitte überprüfen Sie Ihre Internetverbindung.")
        except Exception as e:
            messagebox.showerror("Fehler", 
                f"Fehler beim Prüfen auf Updates: {str(e)}")

    def create_footer(self):
        footer = ttk.Frame(self.root, style='Main.TFrame')
        footer.pack(fill='x', padx=10, pady=5)
        
        copyright_label = ttk.Label(footer,
                                  text=self.copyright,
                                  style='Footer.TLabel')
        copyright_label.pack(side='right')

def main():
    root = tk.Tk()
    app = PrintCalculatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
