import AssetstoreView from '@girder/core/views/body/AssetstoresView';
import FilesystemImportView from '@girder/core/views/body/FilesystemImportView';
import { wrap } from '@girder/core/utilities/PluginUtils';
import events from '@girder/core/events';
import router from '@girder/core/router';

import importDataButton from './templates/assetstoreButtonsExtension.pug';
import importListView from './views/importList';
import duplicateFilesInput from './templates/duplicateFilesInput.pug';

// Inject button to navigate to imports page in each assetstore in view
wrap(AssetstoreView, 'render', function (render) {
    // Call the underlying render function that we are wrapping
    render.call(this);

    this.$el.find('.g-current-assetstores-container .g-body-title').after(
        '<a class="g-view-imports btn btn-sm btn-primary" href="#assetstore/all_imports"><i class="icon-link-ext"></i>View all past Imports</a>'
    );

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
router.route('assetstore/all_imports', 'importsPage', function () {
    events.trigger('g:navigateTo', importListView);
});

// Add duplicate_files option to Import Asset form
wrap(FilesystemImportView, 'render', function (render) {
    render.call(this);

    this.$('.form-group').last().after(duplicateFilesInput)
})
