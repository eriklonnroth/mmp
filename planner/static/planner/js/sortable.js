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
                    delay: 50,
                    delayOnTouchOnly: true,
                    animation: 150,
                    filter: '.add-mpr-button',
                    onEnd: function(evt) {
                        const mprId = evt.item.getAttribute('data-recipe-id');
                        const newGroupId = evt.to.getAttribute('data-group-id');
                        
                        htmx.ajax('POST', `/action_update_mpr/${mprId}/${newGroupId}/`, {
                            swap: 'none'
                        });
                    },
                });
            });
        },
    }));
});
