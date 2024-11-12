document.addEventListener('alpine:init', () => {
    Alpine.data('mealPlan', () => ({
        recipes: window.RECIPES || {},
        groups: window.INITIAL_DATA.weekday || {},
        activeGrouping: 'weekday',
        isEmpty: true,

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
            this.groups = window.INITIAL_DATA[type];
            this.$nextTick(() => {
                this.initSortable();
            });
        },

        init() {
            this.$nextTick(() => {
                this.initSortable();
            });

            document.body.addEventListener('htmx:afterSwap', () => {
                this.initSortable();
            });
        },

        updateGroupName(event) {
            const groupId = event.target.closest('.recipe-group').querySelector('.recipe-list').dataset.groupId;
            if (this.groups[groupId]) {
                this.groups[groupId].name = event.target.innerText;
            }
        },
    }));
});
