import $ from 'jquery';

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
        }
    },

    initialize:
        function ({ id }) {
            if(id){
            this.assetstoreId = id;
            this.imports = [];
            restRequest({
                url: `assetstore/${id}/imports`,
                method: 'GET'
            }).done((result) => {
                this.imports = result;
                this.render();
            });
        }else{
            this.imports = [];
            restRequest({
                url: `assetstore/all_imports`,
                method: 'GET'
            }).done((result) => {
                this.imports = result;
                this.render();
            });
        }

    },

    render: function () {
        this.$el.html(importListTemplate({ imports: this.imports }));

        return this;
    }
});

export default importList;
