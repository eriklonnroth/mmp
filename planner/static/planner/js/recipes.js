document.addEventListener('alpine:init', () => {
    Alpine.data('recipes', () => ({
        recipes: [
            { id: 1, title: "Spaghetti Carbonara", description: "Classic Italian pasta dish" },
            { id: 2, title: "Chicken Tikka Masala", description: "Creamy and spicy Indian curry" },
            { id: 3, title: "Caesar Salad", description: "Fresh and crispy salad with Caesar dressing" },
            { id: 4, title: "Beef Stroganoff", description: "Hearty Russian beef dish" },
            { id: 5, title: "Vegetable Stir Fry", description: "Quick and healthy Asian-inspired dish" },
            { id: 6, title: "Fish and Chips", description: "Traditional British comfort food" },
            { id: 7, title: "Mushroom Risotto", description: "Creamy Italian rice dish" },
            { id: 8, title: "Greek Salad", description: "Fresh Mediterranean salad" },
            { id: 9, title: "Beef Tacos", description: "Spicy Mexican street food" },
            { id: 10, title: "Margherita Pizza", description: "Classic Neapolitan pizza" },
            { id: 11, title: "Chocolate Brownies", description: "Rich and fudgy dessert" },
            { id: 12, title: "Lemon Garlic Roast Chicken", description: "Juicy and flavorful roasted chicken" },
        ],
        savedRecipes: [],
        mealTypes: ["Breakfast", "Lunch", "Dinner", "Snacks"],
        selectedType: null,
        searchQuery: '',
        
        init() {
            // Load saved recipes from localStorage if available
            const saved = localStorage.getItem('savedRecipes')
            if (saved) {
                this.savedRecipes = JSON.parse(saved)
            }
        },

        get filteredRecipes() {
            return this.recipes.filter(recipe => {
                const matchesSearch = !this.searchQuery || 
                    recipe.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
                    recipe.description.toLowerCase().includes(this.searchQuery.toLowerCase())
                
                const matchesType = !this.selectedType || 
                    recipe.mealType === this.selectedType
                
                return matchesSearch && matchesType
            })
        },

        toggleSavedRecipe(id) {
            const index = this.savedRecipes.indexOf(id)
            if (index === -1) {
                this.savedRecipes.push(id)
            } else {
                this.savedRecipes.splice(index, 1)
            }
            // Save to localStorage
            localStorage.setItem('savedRecipes', JSON.stringify(this.savedRecipes))
        },

        selectType(type) {
            this.selectedType = this.selectedType === type ? null : type
        },
    }))
})
