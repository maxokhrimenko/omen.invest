from typing import Dict, Callable
from ..controllers.portfolio_controller import PortfolioController

class MainMenu:
    def __init__(self, controller: PortfolioController):
        self._controller = controller
        self._menu_options = {
            "1": ("Load Portfolio", self._controller.load_portfolio),
            "2": ("Analyze Portfolio", self._controller.analyze_portfolio),
            "3": ("Analyze Tickers", self._controller.analyze_tickers),
            "4": ("Compare Tickers", self._controller.compare_tickers),
            "5": ("Generate Report", self._controller.generate_report),
            "6": ("Settings", self._controller.show_settings),
            "7": ("Warehouse Metrics", self._controller.show_warehouse_metrics),
            "0": ("Exit", self._exit)
        }
    
    def show(self) -> None:
        """Display menu and handle user interactions."""
        print("🚀 Welcome to Portfolio Analysis Tool!")
        
        while True:
            self._display_menu()
            choice = input("\nEnter your choice: ").strip()
            
            if choice in self._menu_options:
                _, action = self._menu_options[choice]
                try:
                    action()
                    if choice == "0":
                        break
                    self._wait_for_continue()
                except KeyboardInterrupt:
                    print("\n\n⚠️  Operation cancelled by user.")
                    self._wait_for_continue()
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")
                    self._wait_for_continue()
            else:
                print("❌ Invalid choice. Please try again.")
                self._wait_for_continue()
    
    def _display_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "="*60)
        print("📈 PORTFOLIO ANALYSIS TOOL".center(60))
        print("="*60)
        
        for key, (description, _) in self._menu_options.items():
            icon = self._get_menu_icon(key)
            print(f"{icon} {key}. {description}")
        
        print("="*60)
    
    def _get_menu_icon(self, key: str) -> str:
        """Get icon for menu item."""
        icons = {
            "1": "📁",
            "2": "📊", 
            "3": "📈",
            "4": "🔬",
            "5": "📋",
            "6": "⚙️",
            "7": "🏪",
            "0": "🚪"
        }
        return icons.get(key, "📌")
    
    def _wait_for_continue(self) -> None:
        """Wait for user to press Enter to continue."""
        try:
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            pass
    
    def _exit(self) -> None:
        """Exit the application."""
        print("\n🙏 Thank you for using Portfolio Analysis Tool!")
        print("💡 Remember: Past performance doesn't guarantee future results.")
        print("📊 Always diversify your investments and consult financial advisors.")
        print("\n👋 Goodbye!")
