import AssetstoreModel from '@girder/core/models/AssetstoreModel';
import View from '@girder/core/views/View';

import router from '@girder/core/router';
import events from '@girder/core/events';
import { restRequest } from '@girder/core/rest';

const goBack = (assetstoreId) => {
    router.navigate(
        `assetstore/${assetstoreId}/import`,
        { trigger: true, replace: true }
    );
};

var reImportView = View.extend({
    initialize({ assetstoreId, importId }) {
        this.importId = importId;
        this.assetstoreId = assetstoreId;
        this.type = '';

        restRequest({
            url: `assetstore/import/${importId}`,
            error: null
        }).done((assetstoreImport) => {
            if (!assetstoreImport) {
                goBack(this.assetstoreId);
                return;
            }

            this.import = assetstoreImport;

            // collect assetstore type info and render
            const assetstore = new AssetstoreModel({ _id: assetstoreId });
            assetstore.once('g:fetched', () => {
                this.type = assetstore.get('type') === 0 ? 'filesystem' : 's3';
                this.render();
            }).fetch();
        }).fail(() => {
            events.trigger('g:alert', {
                icon: 'cancel',
                text: 'Unable to fetch base import information. Redirected to empty import page',
                type: 'danger'
            });
            goBack(this.assetstoreId);
        });
    },

    render() {
        const params = this.import.params;
        const destId = params.destinationId;
        const destType = params.destinationType;
        const excludeExisting = params.excludeExisting ? 'true' : 'false';

        this.$(`#g-${this.type}-import-path`).val(params.importPath);
        this.$(`#g-${this.type}-import-dest-type`).val(destType);
        this.$(`#g-${this.type}-import-dest-id`).val(destId);
        this.$(`#g-${this.type}-import-leaf-items`).val(params.leafFoldersAsItems);
        this.$(`#g-${this.type}-import-exclude-existing`).val(excludeExisting);

        restRequest({
            url: `resource/${destId}/path`,
            method: 'GET',
            data: { type: destType },
            error: null
        }).done((path) => {
            this.$(`#g-${this.type}-import-dest-id`).val(`${destId} (${path})`);
        }).fail(() => {
            this.$(`#g-${this.type}-import-dest-id`).val('');
        });

        return this;
    }
});

export default reImportView;
