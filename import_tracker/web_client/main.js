import AssetstoreView from '@girder/core/views/body/AssetstoresView';
import { wrap } from '@girder/core/utilities/PluginUtils';

import importDataButton from './templates/assetstoreButtonsExtension.pug';

wrap(AssetstoreView, 'render', function (render) {
    // Call the underlying render function that we are wrapping
    render.call(this);

    // Inject new button into each assetstore
    const assetstores = this.collection.toArray();
    this.$('.g-assetstore-import-button-container').after(
        (i) => importDataButton({ assetstore: assetstores[i] })
    );
});
