import AssetstoreView from '@girder/core/views/body/AssetstoresView';
import { wrap } from '@girder/core/utilities/PluginUtils';
import events from '@girder/core/events';
import router from '@girder/core/router';

import importDataButton from './templates/assetstoreButtonsExtension.pug';
import importListView from './views/importList';

// Inject button to navigate to imports page in each assetstore in view
wrap(AssetstoreView, 'render', function (render) {
    // Call the underlying render function that we are wrapping
    render.call(this);

    // Inject new button into each assetstore
    const assetstores = this.collection.toArray();
    this.$('.g-assetstore-import-button-container').after(
        (i) => importDataButton({ importsPageLink: `#assetstore/${assetstores[i].id}/imports` })
    );
});

// Setup router to assetstore imports view
router.route('assetstore/:id/imports', 'importsPage', function (id) {
    events.trigger('g:navigateTo', importListView, { id });
});
