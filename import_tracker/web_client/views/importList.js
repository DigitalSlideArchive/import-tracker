import $ from 'jquery';
import moment from 'moment';

import AssetstoreModel from '@girder/core/models/AssetstoreModel';
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
            }, this).import(importEvent.params);
        },
        'click .re-import-edit-btn': function (e) {
            const index = Number($(e.currentTarget).attr('index'));
            const importEvent = this.imports[index];
            if (importEvent === undefined) {
                return;
            }

            const assetstoreId = importEvent.assetstoreId;
            const importId = importEvent._id;

            router.navigate(`assetstore/${assetstoreId}/re-import/${importId}`, { trigger: true });
        }
    },

    initialize:
        function ({ id, unique }) {
            this._unique = unique;
            this._assetstoreId = id;
            if (id) {
                this.assetstoreId = id;
                this.imports = [];
                restRequest({
                    url: `assetstore/${id}/imports`,
                    data: { unique: unique || false }
                }).done((result) => {
                    this.imports = result;
                    this.checkAssetstores();
                });
            } else {
                this.imports = [];
                restRequest({
                    url: `assetstore/all_imports`,
                    data: { unique: unique || false }
                }).done((result) => {
                    this.imports = result;
                    this.checkAssetstores();
                });
            }
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
