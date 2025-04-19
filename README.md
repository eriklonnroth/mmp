# Make My Meal Plan

A Django-based meal planning application that helps users create personalized meal plans, manage recipes, and generate smart shopping lists.

## Features

- **User Profiles**: Create profiles with dietary preferences and restrictions
- **Recipe Management**: Search existing recipes or generate new ones with AI assistance
- **Meal Planning**: Organize recipes into customizable meal plans by weekday or meal type
- **Smart Shopping Lists**: Generate consolidated shopping lists from your meal plans
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- Python 3.x
- Django
- HTMX for interactive UI components
- Alpine.JS for client-side interactivity
- TailwindCSS for styling
- Anthropic API integration for AI-powered recipe generation

## Installation

1. Clone the repository
2. Set up a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Configure environment variables (create a `.env` file)
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key
   ANTHROPIC_API_KEY=your_api_key
   ```
5. Run migrations
   ```
   python manage.py migrate
   ```
6. Create a superuser
   ```
   python manage.py createsuperuser
   ```
7. Start the development server
   ```
   python manage.py runserver
   ```

## Usage

1. Create a user profile with your dietary preferences
2. Search or generate recipes based on your preferences
3. Add recipes to your collection
4. Create meal plans by organizing recipes by day or meal type
5. Generate shopping lists from your meal plans
6. Use the checkbox feature to track items as you shop

## Development

- Run tests: `python manage.py test`

## License

MIT License 