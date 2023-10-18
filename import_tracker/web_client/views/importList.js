import $ from 'jquery';
import moment from 'moment';

import AssetstoreModel from '@girder/core/models/AssetstoreModel';
import { AssetstoreType } from '@girder/core/constants';
import View from '@girder/core/views/View';
import router from '@girder/core/router';
import { restRequest } from '@girder/core/rest';

import importListTemplate from '../templates/importList.pug';
import '../stylesheets/importList.styl';

var importList = View.extend({
    events: {
        'click .re-import-btn': function (e) {
            const index = Number($(e.currentTarget).attr('index'));
            const importEvent = this.imports[index];
            if (importEvent === undefined) {
                return;
            }

            // Re-perform import
            const assetstore = new AssetstoreModel({ _id: importEvent.assetstoreId });
            const destType = importEvent.params.destinationType;
            const destId = importEvent.params.destinationId;

            assetstore.off('g:imported').on('g:imported', function () {
                router.navigate(destType + '/' + destId, { trigger: true });
            }, this).on('g:error', function (resp) {
                this.$('.g-validation-failed-message').text(resp.responseJSON.message);
            }, this);

            assetstore.once('g:fetched', () => {
                if (assetstore.get('type') === AssetstoreType.DICOMWEB) {
                    assetstore.dicomwebImport(importEvent.params);
                } else {
                    assetstore.import(importEvent.params);
                }
            }).fetch();
        },
        'click .re-import-edit-btn': function (e) {
            const index = Number($(e.currentTarget).attr('index'));
            const importEvent = this.imports[index];
            if (importEvent === undefined) {
                return;
            }

            // Navigate to re-import page
            const navigate = (assetstoreId, importId) => {
                const assetstore = new AssetstoreModel({ _id: assetstoreId });
                assetstore.once('g:fetched', () => {
                    if (assetstore.get('type') === AssetstoreType.DICOMWEB) {
                        // Avoid adding previous import data for DICOMweb imports by navigating to blank import
                        // TODO: Add DICOMweb-specific re-import view
                        router.navigate(`dicomweb_assetstore/${assetstoreId}/import`, { trigger: true });
                    } else {
                        router.navigate(`assetstore/${assetstoreId}/re-import/${importId}`, { trigger: true });
                    }
                }).fetch();
            };

            const assetstoreId = importEvent.assetstoreId;
            const importId = importEvent._id; // Only individual imports have an _id
            if (importId) {
                navigate(assetstoreId, importId);
                return;
            }

            // If the importEvent aggregated 'unique' imports, we need to find a matching importId
            restRequest({
                url: `assetstore/${assetstoreId}/imports`,
                data: { unique: false }
            }).done((results) => {
                const importId = results.filter((i) =>
                    i.params.importPath === importEvent.params.importPath &&
                    i.params.destinationId === importEvent.params.destinationId &&
                    i.params.destinationType === importEvent.params.destinationType
                )[0]._id;

                navigate(assetstoreId, importId);
            });
        }
    },

    initialize:
        function ({ id, unique }) {
            this._unique = unique;
            this._assetstoreId = id;
            this.imports = [];

            const route = id ? `${id}/imports` : 'all_imports';
            restRequest({
                url: `assetstore/${route}`,
                data: { unique: unique || false }
            }).done((result) => {
                this.imports = result;
                this.checkAssetstores();
            });
        },

    checkAssetstores() {
        restRequest({
            url: 'assetstore',
            data: { limit: 0 }
        }).done((result) => {
            const assetstores = result.map((a) => a._id);
            this.assetstoreExists = this.imports.map((i) => assetstores.includes(i.assetstoreId));
            this.render();
        });
    },

    render() {
        this.$el.html(importListTemplate({
            imports: this.imports,
            assetstoreExists: this.assetstoreExists,
            moment: moment,
            unique: this._unique,
            assetstoreId: this._assetstoreId
        }));
        this.$el.tooltip();

        return this;
    }
});

export default importList;
