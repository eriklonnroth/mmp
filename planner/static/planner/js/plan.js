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
            const recipeLists = document.querySelectorAll('.mpr-list');
            recipeLists.forEach(el => {
                Sortable.create(el, {
                    group: 'mprs',
                    animation: 150,
                    filter: '.add-mpr-button',
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
    }));
});
