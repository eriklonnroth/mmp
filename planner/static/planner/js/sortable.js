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
                        const toGroupId = evt.to.dataset.groupId;
                        const fromGroupId = evt.from.dataset.groupId;
    
                        const toOrder = Array.from(evt.to.children).map(el => el.dataset.mprId);
                        const fromOrder = Array.from(evt.from.children).map(el => el.dataset.mprId);

                        console.log('toGroupId', toGroupId);
                        console.log('fromGroupId', fromGroupId);
                        console.log('toOrder', toOrder);
                        console.log('fromOrder', fromOrder);
                        
                        const values = {
                            to_group: toGroupId,
                            from_group: fromGroupId,
                            to_order: toOrder.join(',')
                        };
                        
                        if (fromOrder.length > 0) {
                            values.from_order = fromOrder.join(',');
                        }
                    
                        htmx.ajax('POST', '/action_move_mpr/', {
                            values: values,
                            swap: 'none'
                        });
                    }
                });
            });
        },
    }));
});
