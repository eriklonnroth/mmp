const groupingsData = JSON.parse(document.getElementById('groupings').textContent);
const recipesData = JSON.parse(document.getElementById('recipes').textContent);

document.addEventListener('alpine:init', () => {
    Alpine.data('mealPlan', () => ({
        recipes: recipesData,
        groups: groupingsData.weekday,
        groupings: groupingsData,
        activeGrouping: 'weekday',
        isEmpty: true,

        init() {
            this.$nextTick(() => {
                this.initSortable();
            });
        },

        initSortable() {
            const recipeLists = document.querySelectorAll('.recipe-list');
            recipeLists.forEach(el => {
                Sortable.create(el, {
                    group: 'recipes',
                    animation: 150,
                    filter: '.add-recipe-btn',
                });
            });
        },

        groupBy(type) {
            this.activeGrouping = type;
            this.groups = this.groupings[type];
            this.$nextTick(() => {
                this.initSortable();
            });
        },

        updateGroupName(event) {
            const groupId = event.target.closest('.meal-group').querySelector('.recipe-list').dataset.groupId;
            if (this.groups[groupId]) {
                this.groups[groupId].name = event.target.innerText;
            }
        },

        confirmRemoveRecipe(event, recipeName) {
            if (confirm(`Remove ${recipeName}?`)) {
                const recipeItem = event.target.closest('.recipe-item');
                if (recipeItem) {
                    recipeItem.remove();
                }
            }
        },
    }));
});
