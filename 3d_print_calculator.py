import json
from typing import Dict, List
import os

class Printer:
    def __init__(self, name: str, power_consumption: float, default_speed: float):
        self.name = name
        self.power_consumption = power_consumption  # in kWh
        self.default_speed = default_speed  # in mm/s

class PrintCalculator:
    def __init__(self):
        self.printers: Dict[str, Printer] = {}
        self.load_printers()

    def load_printers(self):
        """Load printers from JSON file if exists, otherwise create default printers"""
        if os.path.exists('printers.json'):
            with open('printers.json', 'r') as f:
                printer_data = json.load(f)
                for name, data in printer_data.items():
                    self.printers[name] = Printer(
                        name=name,
                        power_consumption=data['power_consumption'],
                        default_speed=data['default_speed']
                    )
        else:
            # Default printers
            self.printers = {
                "Ender 3 V2": Printer("Ender 3 V2", 0.15, 50),
                "X1C": Printer("X1C", 0.25, 120),
                "A1 Mini": Printer("A1 Mini", 0.10, 40),
                "Voron Trident": Printer("Voron Trident", 0.30, 150)
            }
            self.save_printers()

    def save_printers(self):
        """Save printers to JSON file"""
        printer_data = {
            name: {
                'power_consumption': printer.power_consumption,
                'default_speed': printer.default_speed
            }
            for name, printer in self.printers.items()
        }
        with open('printers.json', 'w') as f:
            json.dump(printer_data, f, indent=4)

    def add_printer(self, name: str, power_consumption: float, default_speed: float):
        """Add a new printer to the system"""
        self.printers[name] = Printer(name, power_consumption, default_speed)
        self.save_printers()

    def calculate_costs(self, printer_name: str, print_time: float, filament_weight: float,
                       power_cost: float, filament_cost: float, profit_margin: float) -> Dict[str, float]:
        """Calculate all costs for a print job"""
        printer = self.printers[printer_name]
        
        # Calculate power costs
        power_costs = printer.power_consumption * print_time * power_cost
        
        # Calculate filament costs (convert kg price to g price)
        filament_costs = (filament_weight * filament_cost) / 1000
        
        # Calculate total costs
        total_costs = power_costs + filament_costs
        
        # Calculate final price with profit margin
        final_price = total_costs * (1 + profit_margin / 100)
        
        return {
            'power_costs': round(power_costs, 2),
            'filament_costs': round(filament_costs, 2),
            'total_costs': round(total_costs, 2),
            'final_price': round(final_price, 2)
        }

def main():
    calculator = PrintCalculator()
    
    while True:
        print("\n=== 3D Druck Kostenrechner ===")
        print("\n1. Druckkosten berechnen")
        print("2. Neuen Drucker hinzufügen")
        print("3. Verfügbare Drucker anzeigen")
        print("4. Beenden")
        
        choice = input("\nWählen Sie eine Option (1-4): ")
        
        if choice == "1":
            # Show available printers
            print("\nVerfügbare Drucker:")
            for i, printer in enumerate(calculator.printers.keys(), 1):
                print(f"{i}. {printer}")
            
            # Get printer selection
            printer_index = int(input("\nWählen Sie einen Drucker (Nummer): ")) - 1
            printer_name = list(calculator.printers.keys())[printer_index]
            
            # Get print parameters
            print_time = float(input("Druckzeit (in Stunden): "))
            filament_weight = float(input("Filamentverbrauch (in Gramm): "))
            power_cost = float(input("Stromkosten pro kWh (in €): "))
            filament_cost = float(input("Filamentkosten pro kg (in €): "))
            profit_margin = float(input("Gewinnmarge (in %): "))
            
            # Calculate and display results
            results = calculator.calculate_costs(
                printer_name, print_time, filament_weight,
                power_cost, filament_cost, profit_margin
            )
            
            print("\n=== Kostenübersicht ===")
            print(f"Stromkosten: {results['power_costs']}€")
            print(f"Filamentkosten: {results['filament_costs']}€")
            print(f"Gesamtkosten: {results['total_costs']}€")
            print(f"Endpreis (inkl. {profit_margin}% Marge): {results['final_price']}€")
            
        elif choice == "2":
            name = input("\nName des neuen Druckers: ")
            power_consumption = float(input("Stromverbrauch (in kWh): "))
            default_speed = float(input("Standardgeschwindigkeit (in mm/s): "))
            
            calculator.add_printer(name, power_consumption, default_speed)
            print(f"\nDrucker '{name}' wurde erfolgreich hinzugefügt!")
            
        elif choice == "3":
            print("\nVerfügbare Drucker:")
            for name, printer in calculator.printers.items():
                print(f"\nDrucker: {name}")
                print(f"Stromverbrauch: {printer.power_consumption} kWh")
                print(f"Standardgeschwindigkeit: {printer.default_speed} mm/s")
                
        elif choice == "4":
            print("\nProgramm wird beendet. Auf Wiedersehen!")
            break
        
        else:
            print("\nUngültige Eingabe. Bitte wählen Sie eine Option zwischen 1 und 4.")

if __name__ == "__main__":
    main()
