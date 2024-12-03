document.addEventListener('alpine:init', () => {
    Alpine.data('mealPlan', () => ({

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
    }));
});
