# AI Trip Planner

A smart travel planning application that uses AI to generate personalized trip itineraries.

## Frontend Implementation

The frontend has been implemented using:
- HTML
- CSS
- JavaScript
- TailwindCSS for styling

### Directory Structure

```
/static
  /css
    - styles.css (Main CSS file with TailwindCSS imports and custom styles)
  /js
    - main.js (JavaScript functionality for interactive elements)
  /images
    - Various image assets for the application

/templates
  - base.html (Base template with common layout elements)
  - index.html (Homepage)
  - login.html (User login)
  - register.html (User registration)
  - profile.html (User profile)
  - trips.html (List of user trips)
  - new_trip.html (Create new trip form)
  - view_trip.html (Detailed trip view with itinerary)
  - 404.html (Not found error page)
  - 500.html (Server error page)
```

### Features Implemented

1. **User Authentication**
   - Login and registration forms
   - User profile management

2. **Trip Management**
   - Create new trips with destination, dates, budget, and preferences
   - View all trips in a grid layout
   - Detailed trip view with day-by-day itinerary
   - Edit, delete, duplicate, and share trips

3. **Itinerary Display**
   - Day-by-day breakdown of activities
   - Morning, lunch, afternoon, dinner, and evening activities
   - Accommodation suggestions

4. **Booking Management**
   - Add and manage bookings for flights, hotels, etc.
   - Track booking details and confirmation numbers

5. **Weather Integration**
   - Display current weather and forecast for the destination

6. **Responsive Design**
   - Mobile-friendly layout using TailwindCSS
   - Responsive navigation and content display

### How to Run

1. Make sure all required Python packages are installed:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python run.py
   ```

3. Access the application in your browser at:
   ```
   http://localhost:5000
   ```

## Backend Integration

The frontend is integrated with the existing Flask backend, which provides:
- User authentication and session management
- Database operations for trips, bookings, and reviews
- AI-powered itinerary generation using Groq
- Weather data integration

## Future Enhancements

- Add more interactive elements to the itinerary planner
- Implement drag-and-drop functionality for reordering activities
- Add a map view for visualizing the trip locations
- Enhance the booking system with direct integration to booking APIs
- Implement social sharing features for trips