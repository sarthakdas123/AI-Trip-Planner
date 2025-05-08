"""
Alternative itinerary generator that doesn't rely on external APIs.
This can be used as a fallback when the Groq API is not available or not working.
"""

import json
import random
from datetime import datetime, timedelta

class ItineraryGenerator:
    """Generate travel itineraries without external APIs"""
    
    def __init__(self):
        """Initialize with sample data for different destinations"""
        # Load sample activities and attractions for popular destinations
        self.activities = self._load_sample_data()
        
    def _load_sample_data(self):
        """Load sample activities and attractions"""
        return {
            # Generic activities that can be used for any destination
            "generic": {
                "morning": [
                    {"activity": "City Walking Tour", "description": "Explore the city with a local guide", "cost": "$25", "duration": "3 hours"},
                    {"activity": "Museum Visit", "description": "Explore local history and culture", "cost": "$15", "duration": "2 hours"},
                    {"activity": "Local Market", "description": "Shop for local goods and souvenirs", "cost": "$0-30", "duration": "1.5 hours"},
                    {"activity": "Scenic Hike", "description": "Enjoy nature and panoramic views", "cost": "$0", "duration": "3 hours"},
                    {"activity": "Bike Rental", "description": "Explore the area on two wheels", "cost": "$20", "duration": "4 hours"}
                ],
                "lunch": [
                    {"place": "Local Café", "description": "Casual dining with local specialties", "cost": "$15-25"},
                    {"place": "Street Food Market", "description": "Try various local street foods", "cost": "$10-20"},
                    {"place": "Waterfront Restaurant", "description": "Enjoy seafood with a view", "cost": "$20-35"},
                    {"place": "Historic Tavern", "description": "Traditional food in a historic setting", "cost": "$15-30"},
                    {"place": "Food Truck Park", "description": "Various cuisines in a casual setting", "cost": "$10-15"}
                ],
                "afternoon": [
                    {"activity": "Beach Time", "description": "Relax on the sandy shores", "cost": "$0-10", "duration": "3 hours"},
                    {"activity": "Historical Site", "description": "Visit important landmarks", "cost": "$15", "duration": "2 hours"},
                    {"activity": "Boat Tour", "description": "See the area from the water", "cost": "$40", "duration": "1.5 hours"},
                    {"activity": "Shopping District", "description": "Explore local shops and boutiques", "cost": "Varies", "duration": "2 hours"},
                    {"activity": "Art Gallery", "description": "Appreciate local and international art", "cost": "$12", "duration": "1.5 hours"}
                ],
                "dinner": [
                    {"place": "Fine Dining Restaurant", "description": "Upscale local cuisine", "cost": "$50-80"},
                    {"place": "Family-owned Bistro", "description": "Authentic local dishes", "cost": "$25-40"},
                    {"place": "Rooftop Restaurant", "description": "Dinner with a panoramic view", "cost": "$35-60"},
                    {"place": "Seafood Grill", "description": "Fresh seafood specialties", "cost": "$30-50"},
                    {"place": "International Cuisine", "description": "Global flavors in a modern setting", "cost": "$25-45"}
                ],
                "evening": [
                    {"activity": "Live Music Venue", "description": "Enjoy local performers", "cost": "$15-30", "duration": "2 hours"},
                    {"activity": "Night Walking Tour", "description": "See the city lights", "cost": "$25", "duration": "1.5 hours"},
                    {"activity": "Local Bar", "description": "Try local drinks and meet people", "cost": "$20-40", "duration": "2 hours"},
                    {"activity": "Theater Show", "description": "Watch a local performance", "cost": "$35", "duration": "2 hours"},
                    {"activity": "Sunset Viewpoint", "description": "Enjoy the sunset from a scenic spot", "cost": "$0", "duration": "1 hour"}
                ],
                "accommodation": [
                    {"name": "Boutique Hotel", "description": "Charming hotel in a central location", "cost": "$120-180 per night"},
                    {"name": "City Center Apartment", "description": "Self-catering accommodation near attractions", "cost": "$100-150 per night"},
                    {"name": "Beachfront Resort", "description": "Luxury accommodation with ocean views", "cost": "$180-250 per night"},
                    {"name": "Historic Inn", "description": "Stay in a building with character", "cost": "$90-130 per night"},
                    {"name": "Modern Hotel", "description": "Contemporary comfort with amenities", "cost": "$110-160 per night"}
                ]
            },
            
            # Specific activities for popular destinations
            "Paris": {
                "morning": [
                    {"activity": "Eiffel Tower Visit", "description": "Visit the iconic symbol of Paris", "cost": "$25", "duration": "2 hours"},
                    {"activity": "Louvre Museum", "description": "See the Mona Lisa and other masterpieces", "cost": "$17", "duration": "3 hours"},
                    {"activity": "Notre-Dame Cathedral", "description": "Admire the Gothic architecture", "cost": "$0", "duration": "1 hour"},
                    {"activity": "Montmartre Walk", "description": "Explore the artistic neighborhood", "cost": "$0", "duration": "2 hours"},
                    {"activity": "Seine River Cruise", "description": "See Paris from the water", "cost": "$15", "duration": "1 hour"}
                ],
                "lunch": [
                    {"place": "Café de Flore", "description": "Historic café with classic French dishes", "cost": "$25-40"},
                    {"place": "Le Comptoir du Relais", "description": "Bistro with seasonal French cuisine", "cost": "$30-45"},
                    {"place": "L'As du Fallafel", "description": "Famous falafel in the Marais district", "cost": "$10-15"},
                    {"place": "Bouillon Chartier", "description": "Traditional French food at reasonable prices", "cost": "$20-30"},
                    {"place": "Le Petit Marcel", "description": "Cozy café with sandwiches and salads", "cost": "$15-25"}
                ],
                "afternoon": [
                    {"activity": "Champs-Élysées Shopping", "description": "Shop on the famous avenue", "cost": "Varies", "duration": "2 hours"},
                    {"activity": "Musée d'Orsay", "description": "Impressionist art in a former train station", "cost": "$14", "duration": "2 hours"},
                    {"activity": "Luxembourg Gardens", "description": "Relax in the beautiful park", "cost": "$0", "duration": "1.5 hours"},
                    {"activity": "Centre Pompidou", "description": "Modern and contemporary art", "cost": "$14", "duration": "2 hours"},
                    {"activity": "Sainte-Chapelle", "description": "See the stunning stained glass", "cost": "$11", "duration": "1 hour"}
                ],
                "dinner": [
                    {"place": "Le Jules Verne", "description": "Fine dining in the Eiffel Tower", "cost": "$150-250"},
                    {"place": "Chez L'Ami Jean", "description": "Creative Basque cuisine", "cost": "$50-80"},
                    {"place": "Le Petit Cambodge", "description": "Authentic Cambodian food", "cost": "$20-30"},
                    {"place": "Bistrot Paul Bert", "description": "Classic French bistro", "cost": "$40-60"},
                    {"place": "Breizh Café", "description": "Delicious sweet and savory crepes", "cost": "$15-30"}
                ],
                "accommodation": [
                    {"name": "Hôtel Plaza Athénée", "description": "Luxury hotel with Eiffel Tower views", "cost": "$800-1200 per night"},
                    {"name": "Hôtel des Arts Montmartre", "description": "Boutique hotel in artistic neighborhood", "cost": "$150-200 per night"},
                    {"name": "Citadines Les Halles", "description": "Apartment-style accommodation in central location", "cost": "$180-250 per night"},
                    {"name": "Generator Paris", "description": "Modern hostel with private rooms", "cost": "$80-120 per night"},
                    {"name": "Hotel Fabric", "description": "Stylish hotel in former textile factory", "cost": "$200-300 per night"}
                ]
            },
            
            "New York": {
                "morning": [
                    {"activity": "Empire State Building", "description": "Panoramic views from the observation deck", "cost": "$38", "duration": "1.5 hours"},
                    {"activity": "Central Park Walk", "description": "Explore the famous urban park", "cost": "$0", "duration": "2 hours"},
                    {"activity": "Metropolitan Museum of Art", "description": "World-class art collection", "cost": "$25 (suggested)", "duration": "3 hours"},
                    {"activity": "Brooklyn Bridge Walk", "description": "Cross the iconic bridge on foot", "cost": "$0", "duration": "1 hour"},
                    {"activity": "9/11 Memorial & Museum", "description": "Pay respects at this moving site", "cost": "$26", "duration": "2 hours"}
                ],
                "lunch": [
                    {"place": "Katz's Delicatessen", "description": "Famous for pastrami sandwiches", "cost": "$20-30"},
                    {"place": "Chelsea Market", "description": "Food hall with diverse options", "cost": "$15-25"},
                    {"place": "Shake Shack", "description": "Popular burger chain", "cost": "$10-20"},
                    {"place": "Joe's Pizza", "description": "Classic New York slice", "cost": "$3-8"},
                    {"place": "Xi'an Famous Foods", "description": "Hand-pulled noodles and Chinese specialties", "cost": "$10-15"}
                ],
                "afternoon": [
                    {"activity": "Times Square", "description": "Experience the bright lights and energy", "cost": "$0", "duration": "1 hour"},
                    {"activity": "High Line", "description": "Elevated park on former railway", "cost": "$0", "duration": "1.5 hours"},
                    {"activity": "Museum of Modern Art (MoMA)", "description": "Modern and contemporary art", "cost": "$25", "duration": "2 hours"},
                    {"activity": "Fifth Avenue Shopping", "description": "Luxury shopping district", "cost": "Varies", "duration": "2 hours"},
                    {"activity": "Statue of Liberty & Ellis Island", "description": "Visit these historic landmarks", "cost": "$24", "duration": "4 hours"}
                ],
                "dinner": [
                    {"place": "Peter Luger Steak House", "description": "Legendary Brooklyn steakhouse", "cost": "$100-150"},
                    {"place": "Balthazar", "description": "French brasserie in SoHo", "cost": "$50-80"},
                    {"place": "Momofuku Noodle Bar", "description": "David Chang's famous ramen", "cost": "$20-40"},
                    {"place": "Grimaldi's Pizzeria", "description": "Coal brick-oven pizza", "cost": "$20-30"},
                    {"place": "The Halal Guys", "description": "Famous street food cart", "cost": "$8-15"}
                ],
                "accommodation": [
                    {"name": "The Plaza Hotel", "description": "Historic luxury hotel on Central Park", "cost": "$700-1200 per night"},
                    {"name": "Pod 51 Hotel", "description": "Budget-friendly rooms in Midtown", "cost": "$100-150 per night"},
                    {"name": "The Standard, High Line", "description": "Modern hotel overlooking the High Line", "cost": "$300-500 per night"},
                    {"name": "YOTEL New York", "description": "Compact, tech-forward rooms in Hell's Kitchen", "cost": "$150-250 per night"},
                    {"name": "Ace Hotel New York", "description": "Hip hotel with cool lobby scene", "cost": "$250-400 per night"}
                ]
            },
            
            "Tokyo": {
                "morning": [
                    {"activity": "Tsukiji Outer Market", "description": "Explore the famous food market", "cost": "$0 (food extra)", "duration": "2 hours"},
                    {"activity": "Meiji Shrine", "description": "Peaceful shrine in a forest setting", "cost": "$0", "duration": "1.5 hours"},
                    {"activity": "Tokyo Skytree", "description": "Panoramic views from Japan's tallest structure", "cost": "$20", "duration": "2 hours"},
                    {"activity": "Senso-ji Temple", "description": "Tokyo's oldest temple", "cost": "$0", "duration": "1 hour"},
                    {"activity": "Ueno Park", "description": "Large public park with museums", "cost": "$0", "duration": "2 hours"}
                ],
                "lunch": [
                    {"place": "Ichiran Ramen", "description": "Famous tonkotsu ramen chain", "cost": "$10-15"},
                    {"place": "Sushi Dai", "description": "Excellent sushi near the fish market", "cost": "$30-50"},
                    {"place": "Tempura Tsunahachi", "description": "Traditional tempura restaurant", "cost": "$20-40"},
                    {"place": "CoCo Ichibanya", "description": "Popular curry chain", "cost": "$8-15"},
                    {"place": "Ippudo", "description": "Renowned ramen restaurant", "cost": "$10-20"}
                ],
                "afternoon": [
                    {"activity": "Shibuya Crossing", "description": "Experience the famous intersection", "cost": "$0", "duration": "30 minutes"},
                    {"activity": "Harajuku & Takeshita Street", "description": "Youth fashion and culture", "cost": "$0", "duration": "2 hours"},
                    {"activity": "Tokyo National Museum", "description": "Japan's oldest and largest museum", "cost": "$6", "duration": "2 hours"},
                    {"activity": "Akihabara Electric Town", "description": "Electronics and anime district", "cost": "$0", "duration": "2 hours"},
                    {"activity": "Shinjuku Gyoen National Garden", "description": "Beautiful traditional garden", "cost": "$2", "duration": "1.5 hours"}
                ],
                "dinner": [
                    {"place": "Gonpachi", "description": "Inspiration for Kill Bill restaurant scene", "cost": "$30-50"},
                    {"place": "Robot Restaurant", "description": "Unique dinner show experience", "cost": "$80"},
                    {"place": "Kyubey", "description": "High-end sushi restaurant", "cost": "$100-200"},
                    {"place": "Ichiran Ramen", "description": "Famous tonkotsu ramen chain", "cost": "$10-15"},
                    {"place": "Omoide Yokocho", "description": "Narrow alley with tiny eateries", "cost": "$20-40"}
                ],
                "accommodation": [
                    {"name": "Park Hyatt Tokyo", "description": "Luxury hotel featured in Lost in Translation", "cost": "$400-700 per night"},
                    {"name": "Shinjuku Granbell Hotel", "description": "Modern hotel in entertainment district", "cost": "$150-250 per night"},
                    {"name": "Hotel Gracery Shinjuku", "description": "Hotel with Godzilla head on the roof", "cost": "$120-200 per night"},
                    {"name": "UNPLAN Kagurazaka", "description": "Stylish hostel with private rooms", "cost": "$40-100 per night"},
                    {"name": "Tokyu Stay Tsukiji", "description": "Apartment-style rooms near the fish market", "cost": "$100-150 per night"}
                ]
            }
        }
    
    def generate_itinerary(self, destination, start_date, end_date, budget, preferences):
        """Generate a travel itinerary"""
        # Parse dates
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        num_days = (end_date_obj - start_date_obj).days + 1
        
        # Check if we have specific data for this destination
        dest_key = destination
        if destination not in self.activities:
            # Use generic activities if we don't have specific data
            dest_key = "generic"
            print(f"No specific data for {destination}, using generic activities")
        
        # Create the itinerary structure
        itinerary = {
            "destination": destination,
            "duration": num_days,
            "budget": budget,
            "preferences": preferences,
            "days": []
        }
        
        # Generate a day-by-day itinerary
        for i in range(num_days):
            current_date = (start_date_obj + timedelta(days=i)).strftime('%Y-%m-%d')
            
            # Select activities for each part of the day
            # Use a different selection method to ensure variety
            morning_activity = self._select_activity(self.activities[dest_key]["morning"], i, "morning")
            lunch = self._select_activity(self.activities[dest_key]["lunch"], i, "lunch")
            afternoon_activity = self._select_activity(self.activities[dest_key]["afternoon"], i, "afternoon")
            dinner = self._select_activity(self.activities[dest_key]["dinner"], i, "dinner")
            evening_activity = self._select_activity(self.activities[dest_key]["evening"], i, "evening")
            
            # Use the same accommodation for the entire trip
            if i == 0:
                # Select accommodation based on budget
                budget_value = int(budget.replace("$", "").replace(",", ""))
                accommodations = self.activities[dest_key]["accommodation"]
                
                if budget_value < 1000:
                    # Budget trip - select cheaper accommodations
                    accommodation = next((a for a in accommodations if "80" in a["cost"] or "90" in a["cost"] or "100" in a["cost"]), accommodations[0])
                elif budget_value < 3000:
                    # Mid-range trip
                    accommodation = next((a for a in accommodations if "150" in a["cost"] or "180" in a["cost"] or "200" in a["cost"]), accommodations[1])
                else:
                    # Luxury trip
                    accommodation = next((a for a in accommodations if "300" in a["cost"] or "400" in a["cost"] or "500" in a["cost"]), accommodations[2])
                
                # Save for reuse on subsequent days
                selected_accommodation = accommodation
            else:
                accommodation = selected_accommodation
            
            # Add the day to the itinerary
            day = {
                "day": i + 1,
                "date": current_date,
                "morning": [morning_activity],
                "lunch": lunch,
                "afternoon": [afternoon_activity],
                "dinner": dinner,
                "evening": [evening_activity],
                "accommodation": accommodation
            }
            
            # Adjust activities based on preferences if provided
            if preferences:
                self._adjust_for_preferences(day, preferences)
            
            itinerary["days"].append(day)
        
        return itinerary
    
    def _select_activity(self, activities, day_index, time_of_day):
        """Select an activity based on the day index and time of day to ensure variety"""
        # Use different selection methods for different times of day to ensure variety
        if time_of_day == "morning":
            # Cycle through activities
            return activities[day_index % len(activities)]
        elif time_of_day == "lunch" or time_of_day == "dinner":
            # Use a weighted random selection for meals
            weights = [5, 4, 3, 2, 1]  # Prefer earlier items in the list
            return random.choices(activities, weights=weights[:len(activities)])[0]
        else:
            # Use pure random for other activities
            return random.choice(activities)
    
    def _adjust_for_preferences(self, day, preferences):
        """Adjust activities based on user preferences"""
        preferences_lower = preferences.lower()
        
        # Check for specific preferences and adjust activities
        if "food" in preferences_lower or "culinary" in preferences_lower:
            # Add food-related activities
            day["morning"][0]["description"] += " with a focus on local cuisine"
            day["lunch"]["description"] += " - highly recommended for food lovers"
            
        if "history" in preferences_lower or "museum" in preferences_lower:
            # Emphasize historical activities
            if "museum" in day["morning"][0]["activity"].lower() or "historical" in day["morning"][0]["activity"].lower():
                day["morning"][0]["description"] += " - perfect for history enthusiasts"
            else:
                day["morning"][0]["description"] += " with historical context"
                
        if "nature" in preferences_lower or "outdoor" in preferences_lower:
            # Emphasize outdoor activities
            if "park" in day["afternoon"][0]["activity"].lower() or "hike" in day["afternoon"][0]["activity"].lower():
                day["afternoon"][0]["description"] += " - great for nature lovers"
            else:
                day["afternoon"][0]["description"] += " with opportunities to enjoy the outdoors"
                
        if "budget" in preferences_lower or "cheap" in preferences_lower:
            # Emphasize budget-friendly options
            for period in ["morning", "afternoon", "evening"]:
                if isinstance(day[period], list) and day[period]:
                    if "$0" in day[period][0]["cost"] or "$10" in day[period][0]["cost"]:
                        day[period][0]["description"] += " - budget-friendly option"
            
        if "luxury" in preferences_lower or "high-end" in preferences_lower:
            # Emphasize luxury options
            day["dinner"]["description"] += " - perfect for a luxurious experience"
            day["accommodation"]["description"] += " with premium amenities"

# Create a singleton instance
itinerary_generator = ItineraryGenerator()