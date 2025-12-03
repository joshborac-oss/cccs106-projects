"""Weather Application using Flet v0.28.3 with Search History"""

import flet as ft
from weather_service import WeatherService
from config import Config
import json
from pathlib import Path
from weather_service import WeatherServiceError
import asyncio
from datetime import datetime


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.history_file = Path("search_history.json")
        self.preferences_file = Path("user_preferences.json")
        self.search_history = self.load_history()
        self.preferences = self.load_preferences()
        self.use_celsius = self.preferences.get("use_celsius", True)
        self.current_weather_data = None
        self.setup_page()
        self.build_ui()

    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        # Custom theme Colors
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
        
        self.page.padding = 0
        self.page.scroll = ft.ScrollMode.AUTO
        
        # Window properties
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()


    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )

        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        # Temperature unit toggle
        self.temp_unit_text = ft.Text(
            "°C",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
        self.temp_toggle = ft.Switch(
            value=self.use_celsius,
            active_color=ft.Colors.BLUE_700,
            on_change=self.toggle_temperature_unit,
            tooltip="Toggle °C/°F",
        )
        
        self.temp_unit_container = ft.Row(
            [
                ft.Text("°F", size=14, color=ft.Colors.GREY_600),
                self.temp_toggle,
                ft.Text("°C", size=14, color=ft.Colors.GREY_600),
            ],
            spacing=5,
        )

        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
        # Search history section with expandable dropdown
        self.history_expanded = False
        self.expand_icon = ft.IconButton(
            icon=ft.Icons.EXPAND_MORE,
            tooltip="Show history",
            icon_size=20,
            on_click=self.toggle_history,
        )
        
        self.history_header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.HISTORY, size=20, color=ft.Colors.BLUE_700),
                    ft.Text(
                        "Recent Searches",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Clear history",
                                icon_size=20,
                                on_click=self.clear_history,
                            ),
                            self.expand_icon,
                        ],
                        spacing=0,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=15,
            margin=ft.margin.only(top=10),
            on_click=self.toggle_history,
            ink=True,
        )
        
        # History items list in a scrollable container
        self.history_list = ft.Column(spacing=5)
        
        self.history_dropdown = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [self.history_list],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=10,
                        padding=15,
                    ),
                ],
            ),
            visible=False,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            height=0,
        )
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Title row with theme toggle button
        title_row = ft.Row(
            [
                self.title,
                ft.Row(
                    [
                        self.temp_unit_container,
                        self.theme_button,
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Add all components to page with padding container
        self.page.add(
            ft.Container(
                content=ft.Column(
                    [
                        title_row,
                        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                        self.city_input,
                        self.search_button,
                        self.history_header,
                        self.history_dropdown,
                        ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                        self.loading,
                        self.error_message,
                        self.weather_container,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                padding=20,
                expand=True,
            )
        )
        
        # Update history display
        self.update_history_display()


    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()

    
    def toggle_temperature_unit(self, e):
        """Toggle between Celsius and Fahrenheit."""
        self.use_celsius = self.temp_toggle.value
        self.save_preferences()
        
        # Update display if we have current weather data
        if self.current_weather_data:
            self.page.run_task(self.display_weather, self.current_weather_data)
    
    
    def celsius_to_fahrenheit(self, celsius):
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9/5) + 32
    
    
    def load_preferences(self):
        """Load user preferences from file."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    
    def save_preferences(self):
        """Save user preferences to file."""
        try:
            self.preferences["use_celsius"] = self.use_celsius
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")


    def load_history(self):
        """Load search history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    
    def save_history(self):
        """Save search history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.search_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    
    def add_to_history(self, city: str):
        """Add city to history."""
        # Remove city if it already exists (to avoid duplicates)
        self.search_history = [item for item in self.search_history 
                               if item.get('city', '').lower() != city.lower()]
        
        # Add to beginning of list with timestamp
        self.search_history.insert(0, {
            'city': city,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 searches
        self.search_history = self.search_history[:10]
        
        # Save to file
        self.save_history()
        
        # Update display
        self.update_history_display()
    
    
    def toggle_history(self, e):
        """Toggle history dropdown visibility."""
        self.history_expanded = not self.history_expanded
        
        if self.history_expanded:
            self.expand_icon.icon = ft.Icons.EXPAND_LESS
            self.history_dropdown.visible = True
            self.history_dropdown.height = min(300, len(self.search_history) * 70 + 30)
        else:
            self.expand_icon.icon = ft.Icons.EXPAND_MORE
            self.history_dropdown.height = 0
            # Keep visible=True for animation, will hide after animation completes
        
        self.page.update()
    
    
    def update_history_display(self):
        """Update the history display with current history."""
        # Clear existing history items
        self.history_list.controls.clear()
        
        if not self.search_history:
            self.history_header.visible = False
            self.history_dropdown.visible = False
            self.page.update()
            return
        
        # Show history header
        self.history_header.visible = True
        
        # Add history items
        for item in self.search_history:
            city = item.get('city', '')
            timestamp = item.get('timestamp', '')
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%b %d, %I:%M %p")
            except:
                time_str = ""
            
            # Create history item button
            history_item = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.LOCATION_ON,
                            size=16,
                            color=ft.Colors.BLUE_600,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    city,
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.BLUE_900,
                                ),
                                ft.Text(
                                    time_str,
                                    size=11,
                                    color=ft.Colors.GREY_600,
                                ) if time_str else ft.Container(),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            tooltip="Remove from history",
                            on_click=lambda e, c=city: self.remove_from_history(c),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
                padding=10,
                on_click=lambda e, c=city: self.search_from_history(c),
                ink=True,
            )
            
            self.history_list.controls.append(history_item)
        
        self.page.update()
    
    
    def search_from_history(self, city: str):
        """Search weather for a city from history."""
        self.city_input.value = city
        self.page.update()
        self.page.run_task(self.get_weather)
    
    
    def remove_from_history(self, city: str):
        """Remove a city from search history."""
        self.search_history = [item for item in self.search_history 
                               if item.get('city', '').lower() != city.lower()]
        self.save_history()
        self.update_history_display()
    
    
    def clear_history(self, e):
        """Clear all search history."""
        self.search_history = []
        self.save_history()
        self.update_history_display()
    
    
    def on_search(self, e):
        """Handle search button click."""
        self.page.run_task(self.get_weather)


    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            self.show_error("Please enter a city name")
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            # Fetch weather data
            weather_data = await self.weather_service.get_weather(city)
            
            # Store current weather data for unit conversion
            self.current_weather_data = weather_data
            
            # Add to history (use the actual city name from API response)
            actual_city_name = weather_data.get("name", city)
            self.add_to_history(actual_city_name)
            
            # Display weather
            await self.display_weather(weather_data)
        
        except WeatherServiceError as e:
            # Show user-friendly error message
            self.show_error(str(e))

        except Exception as e:
            self.show_error(str(e))
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    
    def get_weather_alerts(self, data: dict, description: str):
        """Get weather alerts and recommendations based on conditions."""
        alerts = []
        temp_celsius = data.get("main", {}).get("temp", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        wind_speed = data.get("wind", {}).get("speed", 0)
        description_lower = description.lower()
        
        # Temperature alerts
        if temp_celsius >= 35:
            alerts.append({
                "level": "danger",
                "icon": "🔥",
                "title": "Extreme Heat Warning",
                "message": "Very high temperature! Stay hydrated and avoid prolonged sun exposure.",
                "recommendation": "Wear sunscreen, drink plenty of water, and stay in shade."
            })
        elif temp_celsius >= 30:
            alerts.append({
                "level": "warning",
                "icon": "☀️",
                "title": "High Temperature",
                "message": "It's quite hot outside.",
                "recommendation": "Wear light clothing and apply sunscreen."
            })
        elif temp_celsius <= 0:
            alerts.append({
                "level": "danger",
                "icon": "🥶",
                "title": "Freezing Temperature",
                "message": "Temperature below freezing!",
                "recommendation": "Dress in layers, wear warm clothing and watch for ice."
            })
        elif temp_celsius <= 5:
            alerts.append({
                "level": "warning",
                "icon": "❄️",
                "title": "Cold Weather",
                "message": "It's quite cold outside.",
                "recommendation": "Wear warm clothes and a jacket."
            })
        
        # Weather condition alerts
        if "thunder" in description_lower or "storm" in description_lower:
            alerts.append({
                "level": "danger",
                "icon": "⚡",
                "title": "Thunderstorm Alert",
                "message": "Thunderstorm in the area!",
                "recommendation": "Stay indoors and avoid open areas. Unplug electronics."
            })
        elif "rain" in description_lower or "drizzle" in description_lower:
            alerts.append({
                "level": "info",
                "icon": "☔",
                "title": "Rain Expected",
                "message": "Rainy conditions.",
                "recommendation": "Bring an umbrella and wear waterproof clothing."
            })
        elif "snow" in description_lower:
            alerts.append({
                "level": "warning",
                "icon": "🌨️",
                "title": "Snow Alert",
                "message": "Snowy conditions expected.",
                "recommendation": "Drive carefully and dress warmly. Watch for slippery roads."
            })
        
        # Wind alerts
        if wind_speed >= 15:
            alerts.append({
                "level": "warning",
                "icon": "💨",
                "title": "High Wind Warning",
                "message": f"Strong winds at {wind_speed} m/s!",
                "recommendation": "Secure loose objects and be cautious outdoors."
            })
        
        # Humidity alerts
        if humidity >= 80:
            alerts.append({
                "level": "info",
                "icon": "💧",
                "title": "High Humidity",
                "message": f"Humidity at {humidity}%.",
                "recommendation": "It may feel warmer than actual temperature. Stay hydrated."
            })
        
        # Fog/mist alerts
        if "fog" in description_lower or "mist" in description_lower:
            alerts.append({
                "level": "warning",
                "icon": "🌫️",
                "title": "Low Visibility",
                "message": "Foggy conditions reduce visibility.",
                "recommendation": "Drive slowly and use fog lights if driving."
            })
        
        return alerts
    
    def create_alert_banner(self, alert: dict):
        """Create an alert banner with appropriate styling."""
        # Define colors based on alert level
        if alert["level"] == "danger":
            bg_color = ft.Colors.RED_100
            border_color = ft.Colors.RED_700
            text_color = ft.Colors.RED_900
        elif alert["level"] == "warning":
            bg_color = ft.Colors.ORANGE_100
            border_color = ft.Colors.ORANGE_700
            text_color = ft.Colors.ORANGE_900
        else:  # info
            bg_color = ft.Colors.BLUE_100
            border_color = ft.Colors.BLUE_700
            text_color = ft.Colors.BLUE_900
        
        return ft.Container(
            content=ft.Column(
                [
                    # Alert header
                    ft.Row(
                        [
                            ft.Text(alert["icon"], size=24),
                            ft.Text(
                                alert["title"],
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=text_color,
                            ),
                        ],
                        spacing=10,
                    ),
                    # Alert message
                    ft.Text(
                        alert["message"],
                        size=14,
                        color=text_color,
                    ),
                    # Recommendation
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.LIGHTBULB_OUTLINE,
                                    size=16,
                                    color=text_color,
                                ),
                                ft.Text(
                                    alert["recommendation"],
                                    size=13,
                                    color=text_color,
                                    italic=True,
                                    expand=True,
                                ),
                            ],
                            spacing=8,
                        ),
                        bgcolor=ft.Colors.with_opacity(0.5, bg_color),
                        border_radius=8,
                        padding=10,
                        margin=ft.margin.only(top=5),
                    ),
                ],
                spacing=5,
            ),
            bgcolor=bg_color,
            border=ft.border.all(2, border_color),
            border_radius=10,
            padding=15,
            margin=ft.margin.only(bottom=10),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )
    
    def get_weather_theme(self, icon_code: str, description: str):
        """Get theme colors and emoji based on weather condition."""
        description_lower = description.lower()
        
        # Determine weather condition and return theme
        if "clear" in description_lower or "sun" in description_lower:
            return {
                "bg_color": ft.Colors.AMBER_100,
                "card_color": ft.Colors.AMBER_50,
                "emoji": "☀️",
                "accent_color": ft.Colors.ORANGE_700
            }
        elif "cloud" in description_lower and "few" in description_lower:
            return {
                "bg_color": ft.Colors.BLUE_GREY_100,
                "card_color": ft.Colors.BLUE_GREY_50,
                "emoji": "🌤️",
                "accent_color": ft.Colors.BLUE_GREY_700
            }
        elif "cloud" in description_lower:
            return {
                "bg_color": ft.Colors.GREY_300,
                "card_color": ft.Colors.GREY_100,
                "emoji": "☁️",
                "accent_color": ft.Colors.GREY_700
            }
        elif "rain" in description_lower or "drizzle" in description_lower:
            return {
                "bg_color": ft.Colors.BLUE_200,
                "card_color": ft.Colors.BLUE_50,
                "emoji": "🌧️",
                "accent_color": ft.Colors.BLUE_800
            }
        elif "thunder" in description_lower or "storm" in description_lower:
            return {
                "bg_color": ft.Colors.INDIGO_300,
                "card_color": ft.Colors.INDIGO_50,
                "emoji": "⛈️",
                "accent_color": ft.Colors.INDIGO_900
            }
        elif "snow" in description_lower:
            return {
                "bg_color": ft.Colors.CYAN_100,
                "card_color": ft.Colors.CYAN_50,
                "emoji": "❄️",
                "accent_color": ft.Colors.CYAN_700
            }
        elif "mist" in description_lower or "fog" in description_lower or "haze" in description_lower:
            return {
                "bg_color": ft.Colors.BLUE_GREY_200,
                "card_color": ft.Colors.BLUE_GREY_50,
                "emoji": "🌫️",
                "accent_color": ft.Colors.BLUE_GREY_600
            }
        else:
            # Default theme
            return {
                "bg_color": ft.Colors.BLUE_100,
                "card_color": ft.Colors.BLUE_50,
                "emoji": "🌈",
                "accent_color": ft.Colors.BLUE_700
            }
    
    async def display_weather(self, data: dict):
        """Display weather information."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp_celsius = data.get("main", {}).get("temp", 0)
        feels_like_celsius = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        
        # Get weather theme
        theme = self.get_weather_theme(icon_code, description)
        
        # Get weather alerts
        alerts = self.get_weather_alerts(data, description)
        
        # Convert temperature based on user preference
        if self.use_celsius:
            temp = temp_celsius
            feels_like = feels_like_celsius
            unit = "°C"
        else:
            temp = self.celsius_to_fahrenheit(temp_celsius)
            feels_like = self.celsius_to_fahrenheit(feels_like_celsius)
            unit = "°F"
        
        # Build alerts section
        alerts_section = ft.Column(spacing=10)
        if alerts:
            for alert in alerts:
                alerts_section.controls.append(self.create_alert_banner(alert))
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                # Alerts section (at the top)
                alerts_section if alerts else ft.Container(),
                # Weather emoji (large)
                ft.Text(
                    theme["emoji"],
                    size=80,
                ),
                
                # Location
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=theme["accent_color"],
                ),
                
                # Weather description
                ft.Text(
                    description,
                    size=20,
                    italic=True,
                    color=theme["accent_color"],
                ),
                
                # Temperature
                ft.Text(
                    f"{temp:.1f}{unit}",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=theme["accent_color"],
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}{unit}",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),
                
                ft.Divider(),
                
                # Additional info - First row
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%",
                            theme["card_color"],
                            theme["accent_color"]
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s",
                            theme["card_color"],
                            theme["accent_color"]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                
                # Additional info - Second row
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.COMPRESS,
                            "Pressure",
                            f"{data.get('main', {}).get('pressure', 0)} hPa",
                            theme["card_color"],
                            theme["accent_color"]
                        ),
                        self.create_info_card(
                            ft.Icons.CLOUD,
                            "Cloudiness",
                            f"{data.get('clouds', {}).get('all', 0)}%",
                            theme["card_color"],
                            theme["accent_color"]
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Update container with theme colors and smooth transition
        self.weather_container.bgcolor = theme["bg_color"]
        self.weather_container.animate = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
        
        # Animate container appearance
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()

        # Fade in
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()

        self.error_message.visible = False
    
    
    def create_info_card(self, icon, label, value, card_color=ft.Colors.WHITE, accent_color=ft.Colors.BLUE_700):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=accent_color),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=accent_color,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=card_color,
            border_radius=10,
            padding=15,
            width=150,
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
    
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)