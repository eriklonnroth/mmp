document.addEventListener('alpine:init', () => {
    Alpine.data('sortableContainer', () => ({

        init() {
            this.$nextTick(() => {
                this.initSortable();
            });
        },

        initSortable() {
            const mprs = document.querySelectorAll('.mpr-list');
            mprs.forEach(el => {
                Sortable.create(el, {
                    group: 'mprs',
                    animation: 150,
                    filter: '.add-mpr-button',
                });
            });
        },
    }));
});
