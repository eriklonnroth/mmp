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
        },
        // ... other days
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
        },
        // ... other meal types
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

document.addEventListener('alpine:init', () => {
    Alpine.data('mealPlan', () => ({
        recipes,
        groups: initialData.weekday,  // Start with weekday view
        
        handleMove(recipeId, fromGroupId, toGroupId, newIndex) {
            // Remove recipe only from source group
            const fromGroup = this.groups[fromGroupId];
            if (fromGroup) {
                fromGroup.recipeIds = fromGroup.recipeIds.filter(id => id !== recipeId);
            }

            // Add recipe to target group at the correct position
            const toGroup = this.groups[toGroupId];
            if (toGroup) {
                toGroup.recipeIds.splice(newIndex, 0, recipeId);
            }
        },

        initSortable() {
            // First destroy any existing instances
            document.querySelectorAll('.recipe-list').forEach(el => {
                if (el.sortable) {
                    el.sortable.destroy();
                }
            });

            // Create new instances
            document.querySelectorAll('.recipe-list').forEach(el => {
                el.sortable = new Sortable(el, {
                    group: 'recipes',
                    animation: 150,
                    dataIdAttr: 'data-recipe-id',
                    onEnd: function(evt) {
                        const fromGroupId = evt.from.getAttribute('data-group-id');
                        const toGroupId = evt.to.getAttribute('data-group-id');
                        
                        // Update both groups' arrays
                        if (fromGroupId !== toGroupId) {
                            // Update source group
                            this.groups[fromGroupId].recipeIds = evt.from.sortable.toArray();
                        }
                        
                        // Update destination group
                        this.groups[toGroupId].recipeIds = evt.to.sortable.toArray();
                    }.bind(this)
                });
            });
        },

        groupBy(type) {
            this.groups = initialData[type];  // Simply switch to the correct sub-object
            this.$nextTick(() => {
                this.initSortable();
            });
        },

        init() {
            // Initialize sortable after initial render
            this.$nextTick(() => {
                this.initSortable();
            });

            // Listen for new groups being added
            document.body.addEventListener('htmx:afterSwap', () => {
                this.initSortable();
            });
        }
    }));
});
