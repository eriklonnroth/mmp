const initialData = {
    weekday: {
        monday: {
            id: 'monday',
            name: 'Monday',
            recipeIds: ['overnight-oats', 'greek-yogurt', 'pasta-carbonara']
        },
        tuesday: {
            id: 'tuesday',
            name: 'Tuesday',
            recipeIds: ['chicken-korma', 'quinoa-salad', 'beef-stir-fry']
        }
    },
    mealType: {
        breakfast: {
            id: 'breakfast',
            name: 'Breakfast',
            recipeIds: ['overnight-oats', 'greek-yogurt', 'pancakes', 'french-toast']
        },
        lunch: {
            id: 'lunch',
            name: 'Lunch',
            recipeIds: ['quinoa-salad', 'chicken-sandwich', 'lentil-soup']
        }
    }
};

const recipes = {
    'overnight-oats': { id: 'overnight-oats', name: 'Overnight Oats (for 2)' },
    'greek-yogurt': { id: 'greek-yogurt', name: 'Greek Yogurt Bowl (for 1)' },
    'pasta-carbonara': { id: 'pasta-carbonara', name: 'Pasta Carbonara (for 3)' },
    'chicken-korma': { id: 'chicken-korma', name: 'Chicken Korma (for 4)' },
    'quinoa-salad': { id: 'quinoa-salad', name: 'Quinoa Salad (for 4)' },
    'beef-stir-fry': { id: 'beef-stir-fry', name: 'Beef Stir Fry (for 3)' },
    'smoothie-bowl': { id: 'smoothie-bowl', name: 'Smoothie Bowl (for 2)' },
    'chicken-sandwich': { id: 'chicken-sandwich', name: 'Chicken Sandwich (for 2)' },
    'fish-curry': { id: 'fish-curry', name: 'Fish Curry (for 4)' },
    'pancakes': { id: 'pancakes', name: 'Pancakes (for 3)' },
    'french-toast': { id: 'french-toast', name: 'French Toast (for 4)' },
    'lentil-soup': { id: 'lentil-soup', name: 'Lentil Soup (for 6)' }
};

// plan.js
document.addEventListener('DOMContentLoaded', () => {
    function initSortable() {
        document.querySelectorAll('.recipe-list').forEach(el => {
            Sortable.create(el, {
                group: 'recipes',
                animation: 150,
                ghostClass: 'bg-blue-50',
                dragClass: 'opacity-50',
                filter: '.add-recipe-btn',

                onAdd: (evt) => {
                    // Hide the "+ Add recipe" button when items exist
                    evt.to.querySelector('.add-recipe-btn').classList.add('hidden');
                },

                onRemove: function(evt) {
                    // Alpine.js will handle the visibility automatically
                }
            });
        });
    }

    // Initial setup
    initSortable();

    // Reinitialize Sortable after HTMX swaps
    document.body.addEventListener('htmx:afterSwap', initSortable);
});