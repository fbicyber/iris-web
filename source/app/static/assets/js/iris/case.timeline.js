var tm_filter = null;
var selector_active;
var current_timeline;
var g_event_id = null;
var g_event_desc_editor = null;

// Current global search term applied to the timeline table (lowercased, debounced on keyup).
var g_timeline_search_term = '';
// event_raw can be huge (full log/artifact dumps) - cap how much of it is indexed for search so typing stays responsive.
var TIMELINE_SEARCH_RAW_CHAR_CAP = 4000;

function handle_ed_paste(event, editor_instance) {
    let filename = null;
    const { items } = event.originalEvent.clipboardData;
    for (let i = 0; i < items.length; i += 1) {
        const item = items[i];

        if (item.kind === 'string') {
            item.getAsString(function (s) {
                filename = $.trim(s.replace(/\t|\n|\r/g, '')).substring(0, 40);
            });
        }

        if (item.kind === 'file') {
            const blob = item.getAsFile();

            if (blob !== null) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    notify_success('The file is uploading in background. Don\'t leave the page');

                    if (filename === null) {
                        filename = random_filename(25);
                    }

                    upload_interactive_data(e.target.result, filename, function (data) {
                        url = data.data.file_url + case_param();
                        event.preventDefault();
                        editor_instance.insertSnippet(`\n![${filename}](${url} =40%x40%)\n`);
                    });
                };
                reader.readAsDataURL(blob);
            } else {
                notify_error('Unsupported direct paste of this item. Use datastore to upload.');
            }
        }
    }
}

function bind_event_editor_paste(editor_instance) {
    $('#event_description').off('paste.handle_ed_paste').on('paste.handle_ed_paste', (event) => {
        event.preventDefault();
        handle_ed_paste(event, editor_instance);
    });
}

function refresh_event_image_preview(editor_instance) {
    if (!editor_instance) {
        return;
    }

    const raw_content = editor_instance.getValue() || '';
    const image_matches = [...raw_content.matchAll(/!\[([^\]]*)\]\(([^)]+)\)/g)];
    const preview_container = $('#event_image_preview_container');
    const preview_content = $('#event_image_preview_content');

    if (image_matches.length === 0) {
        preview_content.empty();
        preview_container.hide();
        return;
    }

    let html = '';
    for (const match of image_matches) {
        const alt_text = sanitizeHTML((match[1] || 'attachment').trim());
        const url_part = (match[2] || '').trim();
        const image_url = sanitizeHTML(url_part.split(' =')[0].trim());
        if (!image_url) {
            continue;
        }
        html += `<img src="${image_url}" alt="${alt_text}" class="img-fluid mb-2 mr-2 border rounded" style="max-height:220px;">`;
    }

    if (html.length === 0) {
        preview_content.empty();
        preview_container.hide();
        return;
    }

    preview_content.html(html);
    preview_container.show();
}

function bind_event_image_preview(editor_instance) {
    refresh_event_image_preview(editor_instance);
    editor_instance.getSession().on('change', function () {
        refresh_event_image_preview(editor_instance);
    });
}

function strip_markdown_images(text) {
    if (typeof text !== 'string') {
        return text;
    }

    return text
        .replace(/!\[[^\]]*]\([^)]+\)/g, '')
        .replace(/\n{3,}/g, '\n\n')
        .trim();
}

/*
 * Builds a single lowercased, length-capped string of the "extra" fields that aren't bound to a visible
 * column (description, raw log, linked IOCs, UUID) so they can be matched by the global search bar.
 * Computed once per event when the data is loaded, not on every table draw/search keystroke.
 */
function build_event_search_blob(evt) {
    let parts = [];

    if (evt.event_content) {
        parts.push(evt.event_content);
    }

    if (evt.event_raw) {
        parts.push(evt.event_raw.substring(0, TIMELINE_SEARCH_RAW_CHAR_CAP));
    }

    if (evt.event_uuid) {
        parts.push(evt.event_uuid);
    }

    if (evt.iocs && evt.iocs.length > 0) {
        evt.iocs.forEach(function (ioc) {
            if (ioc.name) {
                parts.push(ioc.name);
            }
            if (ioc.description) {
                parts.push(ioc.description);
            }
        });
    }

    return parts.join(' \u0000 ').toLowerCase();
}

/*
 * Plain-text (no HTML) list of an asset IP field, used for anything other than on-screen display:
 * global search, sort, and export - all of which choke on the raw assets array / HTML markup.
 */
function extract_ips_from_assets(assets, ip_field) {
    if (!assets || assets.length === 0) {
        return '';
    }

    return assets
        .map(function (asset) { return asset[ip_field]; })
        .filter(function (ip) { return ip != null && ip !== ''; })
        .join(', ');
}

function enable_timeline_column_resize(tableSelector, dataTable) {
    const table = $(tableSelector);
    const minWidth = 60;

    table.find('thead th').each(function(index) {
        const th = $(this);
        if (th.find('.col-resizer').length) {
            return;
        }

        th.css('position', 'relative');

        const resizer = $('<div class="col-resizer"></div>');
        resizer.css({
            position: 'absolute',
            right: '0',
            top: '0',
            height: '100%',
            width: '6px',
            cursor: 'col-resize',
            'user-select': 'none'
        });

        th.append(resizer);

        resizer.on('mousedown', function(e) {
            e.preventDefault();

            const startX = e.pageX;
            const startWidth = th.outerWidth();
            const nextTh = th.next('th');
            const startNextWidth = nextTh.length ? nextTh.outerWidth() : null;

            $('body').css('cursor', 'col-resize');

            $(document)
                .on('mousemove.colresize', function(ev) {
                    const delta = ev.pageX - startX;
                    const newWidth = Math.max(minWidth, startWidth + delta);

                    th.css('width', newWidth + 'px');
                    $(dataTable.column(index).nodes()).css('width', newWidth + 'px');

                    if (nextTh.length && startNextWidth !== null) {
                        const newNextWidth = Math.max(minWidth, startNextWidth - delta);
                        nextTh.css('width', newNextWidth + 'px');
                        $(dataTable.column(index + 1).nodes()).css('width', newNextWidth + 'px');
                    }
                })
                .on('mouseup.colresize', function() {
                    $(document).off('.colresize');
                    $('body').css('cursor', '');
                    dataTable.columns.adjust();
                });
        });
    });
}

function edit_in_event_desc() {
    if($('#container_event_desc_content').is(':visible')) {
        $('#container_event_description').show(100);
        $('#container_event_desc_content').hide(100);
        $('#event_edition_btn').hide(100);
        $('#event_preview_button').hide(100);
    } else {
        $('#event_preview_button').show(100);
        $('#event_edition_btn').show(100);
        $('#container_event_desc_content').show(100);
        $('#container_event_description').hide(100);
    }
}

/* Fetch a modal that allows to add an event */
function add_event(parent_event_id = null) {
    url = 'timeline/events/add/modal' + case_param();
    $('#modal_add_event_content').load(url, function (response, status, xhr) {
        hide_minimized_modal_box();
        if (status !== "success") {
             ajax_notify_error(xhr, url);
             return false;
        }

        g_event_desc_editor = get_new_ace_editor('event_description', 'event_desc_content', 'target_event_desc',
                            function() {
                                $('#last_saved').addClass('btn-danger').removeClass('btn-success');
                                $('#last_saved > i').attr('class', "fa-solid fa-file-circle-exclamation");
                            }, null);

        g_event_desc_editor.setOption("minLines", "10");
        bind_event_editor_paste(g_event_desc_editor);
        bind_event_image_preview(g_event_desc_editor);
        let headers = get_editor_headers('g_event_desc_editor', null, 'event_edition_btn');
        $('#event_edition_btn').append(headers);
        edit_in_event_desc();

        let parent_selector = $('#parent_event_id');

        // Add empty option
        let option = $('<option>');
        option.attr('value', '');
        option.text('No parent event');
        parent_selector.append(option);

        // Add all events to the parent selector
        for (let idx in current_timeline) {
            let event = current_timeline[idx];
            let option = $('<option>');
            option.attr('value', event.event_id);
            option.text(`${event.event_title}`);
            parent_selector.append(option);
        }

        parent_selector.selectpicker({
            liveSearch: true,
            size: 10,
            width: '100%',
            title: 'Select a parent event',
            style: 'btn-light',
            noneSelectedText: 'No event selected',
        });

        if (parent_event_id != null) {
            parent_selector.selectpicker('val', parent_event_id);
            parent_selector.selectpicker("refresh");
        }

        let assets = $('#event_assets');
        let iocs = $('#event_iocs');

        assets = initialize_field_select2(assets);
        iocs = initialize_field_select2(iocs);

        $('#submit_new_event').on("click", function () {
            clear_api_error();
            var data_sent = $('#form_new_event').serializeObject();
            data_sent['event_date'] = `${$('#event_date').val()}T${$('#event_time').val()}`;
            data_sent['event_in_summary'] = $('#event_in_summary').is(':checked');
            data_sent['event_in_graph'] = $('#event_in_graph').is(':checked');
            data_sent['event_sync_iocs_assets'] = $('#event_sync_iocs_assets').is(':checked');
            data_sent['event_tags'] = $('#event_tags').val();
            data_sent['event_assets'] = $('#event_assets').val();
            data_sent['event_iocs'] = $('#event_iocs').val();
            data_sent['event_tz'] = $('#event_tz').val();
            data_sent['event_content'] = g_event_desc_editor.getValue();
            data_sent['parent_event_id'] = $('#parent_event_id').val() || null;

            ret = get_custom_attributes_fields();
            has_error = ret[0].length > 0;
            attributes = ret[1];

            if (has_error){return false;}

            // proceed to update the event with the new asset and IOC IDs
            data_sent['event_assets'] = $('#event_assets').val();
            data_sent['event_iocs'] = $('#event_iocs').val();

            data_sent['custom_attributes'] = attributes;

            // automatically calls time_converter here and submit the converted timestamp
            const start_convert_val = $('#event_date_convert_input').val();
            const time_convert_promise = (start_convert_val && start_convert_val.trim().length > 0)
                ? time_converter()
                : Promise.resolve();

            time_convert_promise.then(function () {
                const end_convert_val = $('#end_event_date_convert_input').val();
                if (end_convert_val && end_convert_val.trim().length > 0) {
                    return end_time_converter();
                }
                return Promise.resolve();
            }).then(function () {
                data_sent['event_date'] = `${$('#event_date').val()}T${$('#event_time').val()}`;
                data_sent['event_tz'] = $('#event_tz').val();

                if (!$('#end_event_date').val()) {
                    notify_error('End Event Time is required.');
                    return false;
                }
                set_end_event_fields(data_sent);

                post_request_api('timeline/events/add', JSON.stringify(data_sent), true)
                    .done((data) => {
                        if (notify_auto_api(data)) {
                            window.location.hash = data.data.event_id;
                            apply_filtering();
                            $('#modal_add_event').modal('hide');
                        }
                    });

            }).catch(function (error) {
                return false;
            });
        });

        $('#modal_add_event').modal({ show: true });
        $('#event_title').focus();
    });
}

/**
 * Initializes the select2 dropdown for a specific field (asset or ioc)
 * allowing the user to add new field by typing.
 *
 * @param {jQuery} fields_object - The jQuery object representing the select2 element
 */
function initialize_field_select2(fields_object) {
    fields_object.select2({
        tags: true,
        tokenSeparators: [','],
        createTag: function(params) {
            let term = $.trim(params.term);

            return { id: term, text: term, newTag: true };
        },
        templateResult: function(data) {
            // Display field name in the dropdown
            return data.text;
        },
        templateSelection: function(data) {
            // Display field name in the selection
            return data.text;
        }
    });

    // temporary list of field names that were added
    let temp_field_names_list = [];

    fields_object.on('select2:select', function(e) {
        let fields_obj_name = fields_object.attr("name");
        var field_name_data = e.params.data;
        if (field_name_data.newTag == true) {
            temp_field_names_list.push(field_name_data.text);
        }
        if (fields_obj_name == "event_assets") {
            add_asset_from_event(temp_field_names_list, fields_object);
        }
        else if (fields_obj_name == "event_iocs") {
            add_ioc_from_event(temp_field_names_list, fields_object);
        }

        // reset the temp list to avoid adding duplicates
        temp_field_names_list = [];
    });

    return fields_object
}

/**
 * Automatically add new assets from the event modal
 * @param asset_names_list: list of strings, asset names that user inputs
 * @param event_assets: the jQuery object representing the select2 dropdown for event's assets
 */
function add_asset_from_event(asset_names_list, event_assets) {
    return add_items_from_event(asset_names_list, event_assets, 'assets/add', asset_data_template);
}

/**
 * Automatically add new IOCs from the event modal
 * @param ioc_names_list: list of strings, IOCs names that user inputs
 * @param event_iocs: the jQuery object representing the select2 dropdown for event's IOCs
 */
function add_ioc_from_event(ioc_names_list, event_iocs) {
    return add_items_from_event(ioc_names_list, event_iocs, 'ioc/add', ioc_data_template);
}

/**
 * Helper function to add items (assets or IOCs) from an event modal
 * @param {Array} names_list - List of names (assets or IOCs)
 * @param {jQuery} fields_object - The jQuery object of the select2 field
 * @param {string} api_url - The API endpoint to post the data to ('assets/add' or 'ioc/add')
 * @param {Object} data_template - The data structure template for the item (asset or ioc)
 * @returns {Promise} - Resolves when all items are added
 */
function add_items_from_event(names_list, fields_object, api_url, data_template) {
    let new_item_ids_list = [];

    // create promises for each item (asset or ioc)
    let item_creation_promises = names_list.map((item_name) => {
        return new Promise((resolve, reject) => {
            let data = {
                ...data_template, // copy the attributes of the post data template into the new object
                csrf_token: $('#csrf_token').val(),
                custom_attributes: get_custom_attributes_fields()[1]
            };

            // map item_name to the correct field based on the endpoint (asset or ioc)
            if (api_url === 'assets/add') {
                data.asset_name = item_name;
            } else if (api_url === 'ioc/add') {
                data.ioc_value = item_name;
            }

            // add the new item to the specified API endpoint (assets or IOCs)
            post_request_api(api_url, JSON.stringify(data), true)
                .done((data) => {
                    if (data.status == 'success') {
                        let item_id;

                        if (api_url === 'assets/add') {
                            item_id = data.data.asset_id;
                        } else if (api_url === 'ioc/add') {
                            item_id = data.data.ioc_id;
                        } else {
                            reject(`Invalid API endpoint ${api_url}.`);
                            return;
                        }

                        new_item_ids_list.push(item_id);

                        // add the new item to the fields_object (select2 dropdown), select2 adds the name, but the jQuery object needs the item ID
                        fields_object.find('option').each(function () {
                            let current_value = $(this).val();
                            if (current_value == item_name) {
                                // remove the string item name, and replace with the ID

                                $(this).remove();
                                let newOption = new Option(item_name, item_id, true, true);
                                fields_object.append(newOption);
                            }
                        });

                        // trigger select2 to refresh the dropdown with the new options
                        fields_object.trigger('change');
                        resolve();
                    } else {
                        reject(`Error saving item: ${data.message}`);
                    }
                })
                .fail((error) => {
                    reject(error);
                });
        });
    });

    return Promise.all(item_creation_promises);
}

function save_event() {
    $('#submit_new_event').click();
}


function select_timezone(){
   /**
    * Allow user to choose local timezone from dropdown
    * Call POST to /timeline/select-timezone"
    */

    $('#timezone').on("change", function(){
        let selected_timezone = $(this).val();
        post_request_api("timeline/select-timezone", JSON.stringify(selected_timezone), true)
        .done((data) => {
            if(notify_auto_api(data)) {
                // console.log("successfully post data for select timezone", data.data.timezone);
                // dynamically update the Local header name
                $('#local_timezone_header').text("Local, UTC" + data.data.offset);

                // refresh and auto update the table
                get_or_filter_tm();
            }
        });
    });
}


function duplicate_event(id) {
    window.location.hash = id;
    clear_api_error();

    post_request_api("timeline/events/duplicate/" + id)
    .done((data) => {
        if(notify_auto_api(data)) {
            if ("data" in data && "event_id" in data.data)
            {
                window.location.hash = data.data.event_id;
            }
            apply_filtering();
        }

        // open the new event
        edit_event(data.data.event_id)
    });

}
function update_event(event_id) {
    const start_convert_val = $('#event_date_convert_input').val();
    const time_convert_promise = (start_convert_val && start_convert_val.trim().length > 0)
        ? time_converter()
        : Promise.resolve();

    time_convert_promise.then(function() {
        const end_convert_val = $('#end_event_date_convert_input').val();
        if (end_convert_val && end_convert_val.trim().length > 0) {
            return end_time_converter();
        }
        return Promise.resolve();
    }).then(function() {
        if (!$('#end_event_date').val()) {
            notify_error('End Event Time is required.');
            return false;
        }
        update_event_ext(event_id, true);
    });
}

function update_event_ext(event_id, do_close) {

    if (event_id === undefined || event_id === null) {
        event_id = g_event_id;
    }

    window.location.hash = event_id;
    clear_api_error();
    var data_sent = $('#form_new_event').serializeObject();
    data_sent['event_date'] = `${$('#event_date').val()}T${$('#event_time').val()}`;
    data_sent['event_in_summary'] = $('#event_in_summary').is(':checked');
    data_sent['event_in_graph'] = $('#event_in_graph').is(':checked');
    data_sent['event_sync_iocs_assets'] = $('#event_sync_iocs_assets').is(':checked');
    data_sent['event_tags'] = $('#event_tags').val();
    data_sent['event_assets'] = $('#event_assets').val();
    data_sent['event_iocs'] = $('#event_iocs').val();
    data_sent['event_tz'] = $('#event_tz').val();
    data_sent['event_content'] = g_event_desc_editor.getValue();
    data_sent['parent_event_id'] = $('#parent_event_id').val() || null;

    ret = get_custom_attributes_fields();
    has_error = ret[0].length > 0;
    attributes = ret[1];

    if (has_error){return false;}

    data_sent['custom_attributes'] = attributes;

    // proceed to update the event with the new asset and IOC IDs
    data_sent['event_assets'] = $('#event_assets').val();
    data_sent['event_iocs'] = $('#event_iocs').val();
    set_end_event_fields(data_sent);

    post_request_api('timeline/events/update/' + event_id, JSON.stringify(data_sent), true)
        .done(function (data) {
            if (notify_auto_api(data)) {
                apply_filtering();
                if (do_close !== undefined && do_close === true) {
                    $('#modal_add_event').modal('hide');
                }

                $('#submit_new_event').text("Saved").addClass('btn-outline-success')
                    .removeClass('btn-outline-danger').removeClass('btn-outline-warning');
                $('#last_saved').removeClass('btn-danger').addClass('btn-success');
                $('#last_saved > i').attr('class', "fa-solid fa-file-circle-check");
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            console.log("Error during update event:", jqXHR, textStatus, errorThrown);
        });
}

/* Delete an event from the timeline */
function delete_event(event_id = null, skip_prompt = false) {
    var event_id_set = new Set();

    if (event_id !== undefined && event_id !== null && event_id !== '') {
        event_id_set.add(event_id.toString());
    } else {
        var selected_rows = $(".timeline-selected");

        // selected rows from timeline tabular
        var table_selected_rows = Table.rows('.selected').data();
        event_id_set = get_selected_rows_event_ids(selected_rows, table_selected_rows);
    }

    event_id_set.forEach(event_id => {
    window.location.hash = event_id;
    (skip_prompt ? Promise.resolve(true) : do_deletion_prompt("You are about to delete event #" + event_id))
    .then((doDelete) => {
        if (doDelete) {
            post_request_api("timeline/events/delete/" + event_id)
            .done(function(data) {
                if(notify_auto_api(data)) {
                    apply_filtering();
                    $('#modal_add_event').modal('hide');
                }
            });
        }
    });
})
}

/* Edit an event from the timeline thanks to its ID */
function edit_event(id) {
  url = '/case/timeline/events/' + id + '/modal' + case_param();
  window.location.hash = id;
  $('#modal_add_event_content').load(url, function (response, status, xhr) {
        hide_minimized_modal_box();
        if (status !== "success") {
             ajax_notify_error(xhr, url);
             return false;
        }

        g_event_id = id;
        g_event_desc_editor = get_new_ace_editor('event_description', 'event_desc_content', 'target_event_desc',
                            function() {
                                $('#last_saved').addClass('btn-danger').removeClass('btn-success');
                                $('#last_saved > i').attr('class', "fa-solid fa-file-circle-exclamation");
                            }, null);
        g_event_desc_editor.setOption("minLines", "6");
        bind_event_editor_paste(g_event_desc_editor);
        bind_event_image_preview(g_event_desc_editor);
        preview_event_description(true);
        headers = get_editor_headers('g_event_desc_editor', null, 'event_edition_btn');
        $('#event_edition_btn').append(headers);
        edit_in_event_desc();

        let parent_selector = $('#parent_event_id');

        // Add empty option
        let option = $('<option>');
        option.attr('value', '');
        option.text('No parent event');
        parent_selector.append(option);

        let target_idx = 0;
        // Add all events to the parent selector and remove the current event
        for (let idx in current_timeline) {
            let event = current_timeline[idx];

            if (event.event_id === id) {
                target_idx = event.parent_event_id;
                continue;
            }

            let option = $('<option>');
            option.attr('value', event.event_id);
            option.text(`${event.event_title}`);
            parent_selector.append(option);
        }

        parent_selector.selectpicker({
            liveSearch: true,
            size: 10,
            width: '100%',
            title: 'Select a parent event',
            style: 'btn-light',
            noneSelectedText: 'No event selected',
        });

        if (target_idx!= null) {
            parent_selector.selectpicker('val', target_idx);
            parent_selector.selectpicker("refresh");
        }

        let assets = $('#event_assets');
        let iocs = $('#event_iocs');

        assets = initialize_field_select2(assets);
        iocs = initialize_field_select2(iocs);

        load_menu_mod_options_modal(id, 'event', $("#event_modal_quick_actions"));
        $('#modal_add_event').modal({show:true});
  });
}

function preview_event_description(no_btn_update) {
    if(!$('#container_event_description').is(':visible')) {
        event_desc = g_event_desc_editor.getValue();
        converter = get_showdown_convert();
        html = converter.makeHtml(do_md_filter_xss(event_desc));
        event_desc_html = do_md_filter_xss(html);
        $('#target_event_desc').html(event_desc_html);
        $('#container_event_description').show();
        if (!no_btn_update) {
            $('#event_preview_button').html('<i class="fa-solid fa-eye-slash"></i>');
        }
        $('#container_event_desc_content').hide();
    }
    else {
        $('#container_event_description').hide();
         if (!no_btn_update) {
            $('#event_preview_button').html('<i class="fa-solid fa-eye"></i>');
        }

        $('#event_preview_button').html('<i class="fa-solid fa-eye"></i>');
        $('#container_event_desc_content').show();
    }
}

function is_timeline_compact_view() {
    var x = localStorage.getItem('iris-tm-compact');
    if (typeof x !== 'undefined') {
        if (x === 'true') {
            return true;
        }
    }
    return false;
}

function toggle_compact_view() {
    var x = localStorage.getItem('iris-tm-compact');
    if (typeof x === 'undefined') {
        localStorage.setItem('iris-tm-compact', 'true');
        location.reload();
    } else {
        if (x === 'true') {
            localStorage.setItem('iris-tm-compact', 'false');
            location.reload();
        } else {
             localStorage.setItem('iris-tm-compact', 'true');
            location.reload();
        }
    }
}


function is_timeline_tree_view() {
    var x = localStorage.getItem('iris-tm-tree');
    if (typeof x !== 'undefined') {
        if (x === 'true') {
            return true;
        }
    }
    return false;
}


function toggle_tree_view() {
    var x = localStorage.getItem('iris-tm-tree');
    if (typeof x === 'undefined') {
        localStorage.setItem('iris-tm-tree', 'true');
        location.reload();
    } else {
        if (x === 'true') {
            localStorage.setItem('iris-tm-tree', 'false');
            location.reload();
        } else {
             localStorage.setItem('iris-tm-tree', 'true');
            location.reload();
        }
    }
}

function toggle_selector() {
    //activating selector toggle
    if(selector_active == false) {
        selector_active = true;

        //blend in conditional buttons to perform actions on selected rows - e.g. select graph, summary, color
        $(".btn-conditional").show(250);
        //highligh the selection button
        $("#selector-btn").addClass("btn-active");
        //$("#selector-btn").load();
        //remove data toggle attribute to disable expand feature
        $("[id^=dropa_]").removeAttr('data-toggle');

        //create click handler for timeline events
        $(".timeline li .timeline-panel").on('click', function(){
            if($(this).hasClass("timeline-selected")) {
                $(this).removeClass("timeline-selected");
            } else {
                $(this).addClass("timeline-selected");
            }
        });

        $(".timeline li .timeline-panel-t").on('click', function(){
            if($(this).hasClass("timeline-selected")) {
                $(this).removeClass("timeline-selected");
            } else {
                $(this).addClass("timeline-selected");
            }
        });

    }

    //deactivating selector toggle
    else if(selector_active == true) {
        selector_active = false;
        $(".btn-conditional").hide(250);
        $(".btn-conditional-2").hide(250);
        $("#selector-btn").removeClass("btn-active");
        //restore the collapse feature
        $("[id^=dropa_]").attr('data-toggle','collapse');
        $(".timeline-selected").removeClass("timeline-selected");

        $(".timeline li .timeline-panel").off('click');
        apply_filtering();
    }
}

function toggle_colors() {
    // console.log("toggling colors");
    var color_buttons = $(".btn-conditional-2");
    color_buttons.slideToggle(250, function () {
        if ($(this).is(':visible')) {
            $(this).css('display', 'inline-flex');
        }
    });
}

function get_selected_rows_event_ids(selected_rows, table_selected_rows){
    /**
     *  Gather all selected rows from timeline table and old timeline list
     *  Get the event ids of the selected rows
     *
     *  Return: a Set() of selected rows's event ids
     */

    // a Set of event ids from all selected rows
    // doing this to ensure it is backward friendly --> if people want to use the old events list, functionality will still work
    var event_id_set = new Set();

    // adding event ids from TABLE selected rows to the set, it should NOT add duplicates
    table_selected_rows.each(function(evt){
        event_id_set.add(evt.event_id.toString());
    });

    // adding event ids from selected rows to the set, it should NOT add duplicates
    selected_rows.each(function(index){
        var object = selected_rows[index];
        var event_id = object.getAttribute('id').replace("event_","");
        event_id_set.add(event_id);
    });

    return event_id_set;
}

function events_set_attribute(attribute, color) {

    var attribute_value;

    var selected_rows = $(".timeline-selected");

    // selected rows from timeline tabular
    var table_selected_rows = Table.rows('.selected').data();


    switch(attribute) {
        case "event_in_graph":
            break;
        case "event_in_summary":
            break;
        case "event_color":
            attribute_value = color;
            var color_buttons = $(".btn-conditional-2");
            color_buttons.slideToggle(250);
            break;
        default:
            console.log("invalid argument given");
            return false;
    }

    // if no rows are selected both in table and old list, return
    if(table_selected_rows.length <= 0 && selected_rows.length <= 0){
        console.log("no rows selected, returning");
        return true;
    }

    var event_id_set = get_selected_rows_event_ids(selected_rows, table_selected_rows);

    var index = 0;  // will be used to keep track of where in event_id_set for the loop below
    event_id_set.forEach(function(evt_id){
        var original_event;

        // get event data
        get_request_api("timeline/events/" + evt_id)
        .done((data) => {
            original_event = data.data;
            if(notify_auto_api(data, true)) {

                //change attribute to selected value
                if(attribute === 'event_in_graph' || attribute === 'event_in_summary'){
                    attribute_value = original_event[attribute];
                    original_event[attribute] = !attribute_value;
                } else if(attribute === 'event_color') {
                    // attribute value already set to color L240
                    original_event[attribute] = attribute_value;
                }

                //add csrf token to request
                original_event['csrf_token'] = $("#csrf_token").val();
                delete original_event['event_comments_map'];

                // because of the way the backend handles timestamps
                // set it this way to prevent the UTC timestamps from being changed unintentionally
                original_event.event_date = original_event.event_date_wtz
                original_event.event_tz = "-0000"
                if (original_event.event_end_date_wtz) {
                    original_event.event_end_date = original_event.event_end_date_wtz
                    original_event.event_end_tz = "-0000"
                }

                //send updated event to API
                post_request_api('timeline/events/update/' + evt_id, JSON.stringify(original_event), true)
                .done(function(data) {
                    notify_auto_api(data);
                    if (index === event_id_set.size - 1) {
                        // if we are at the last element of the set, show the updated view of the rows

                        get_or_filter_tm(function() {  // update the old event lists selected row, indicate that the rows are selected
                            selected_rows.each(function() {
                                var event_id = this.getAttribute('id')
                                $('#' + event_id).addClass("timeline-selected");
                            });
                        });

                        // IF selected_rows isnt used anymore, just call get_or_filter_tm()
                    }
                    index++;
                });
            }
        });
    });
}

function events_bulk_delete() {
    var selected_rows = $(".timeline-selected");
    // selected rows from timeline tabular
    var table_selected_rows = Table.rows('.selected').data();

    if(table_selected_rows.length <= 0 && selected_rows.length <= 0){
        console.log("no rows selected, returning");
        return true;
    }

    var event_id_set = get_selected_rows_event_ids(selected_rows, table_selected_rows);

    swal({
        title: "Are you sure?",
        text: "You are about to delete " + event_id_set.size + " events.\nThere is no coming back.",
        icon: "warning",
        buttons: true,
        dangerMode: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete them'
    })
    .then((willDelete) => {
        if (willDelete) {
            var index = 0;
            event_id_set.forEach(function(evt_id){

                post_request_api("timeline/events/delete/" + evt_id)
                .done(function(data) {
                    notify_auto_api(data);
                    if (index === event_id_set.size - 1) {
                        get_or_filter_tm();
                    }
                    index++;
                });
            });
        } else {
            swal("Pfew, that was close");
        }
    });
}

function toggleSeeMore(element) {
    let ariaExpanded = element.getAttribute('aria-expanded');
    if (ariaExpanded === 'false') {
        element.innerHTML = '&gt; See less';
    } else {
        element.innerHTML = '&gt; See more';
    }
}

function buildEvent(event_data, compact, comments_map, tree, tesk, tmb, idx, reap, converter) {
    let evt = event_data;
    let dta =  evt.event_date.toString().split('T');
    let tags = '';
    let cats = '';
    let tmb_d = '';
    let style = '';
    let asset = '';

    if (evt.event_id in comments_map) {
        nb_comments = comments_map[evt.event_id].length;
    } else {
        nb_comments = '';
    }

    if(evt.category_name && evt.category_name != 'Unspecified') {
         if (!compact) {
             tags += `<span class="badge badge-light float-right ml-1 mt-2">${sanitizeHTML(evt.category_name)}</span>`;
         } else {
             if (evt.category_name != 'Unspecified') {
                 cats += `<span class="badge badge-light float-right ml-1 mt-1 mr-2 mb-1">${sanitizeHTML(evt.category_name)}</span>`;
             }
         }
    }

    if (evt.iocs != null && evt.iocs.length > 0) {
        for (let ioc in evt.iocs) {
            let span_anchor = $('<span>');
            span_anchor.addClass('badge badge-warning-event float-right ml-1 mt-2');
            span_anchor.attr('data-toggle', 'popover');
            span_anchor.attr('data-trigger', 'hover');
            span_anchor.attr('style', 'cursor: pointer;');
            span_anchor.attr('data-content', 'IOC - ' + evt.iocs[ioc].description);
            span_anchor.attr('title', evt.iocs[ioc].name);
            span_anchor.text(evt.iocs[ioc].name)
            span_anchor.html('<i class="fa-solid fa-virus-covid mr-1"></i>' + span_anchor.html());
            tags += span_anchor[0].outerHTML;
        }
    }

    if (evt.event_tags != null && evt.event_tags.length > 0) {
        sp_tag = evt.event_tags.split(',');
        for (tag_i in sp_tag) {
                tags += get_tag_from_data(sp_tag[tag_i], 'badge badge-light ml-1 float-right mt-2');
            }
    }

    let entry = '';
    let inverted = 'timeline';
    let timeline_style = tree ? '-t' : '';

    /* Do we have a border color to set ? */
    if (tesk) {
        style += "timeline-odd"+ timeline_style;
        tesk = false;
    } else {
        style += "timeline-even" + timeline_style;
        tesk = true;
    }

    let style_s = "";
    if (evt.event_color) {
            style_s = `style='border-left: 2px groove ${sanitizeHTML(evt.event_color)};'`;
    }

    if (!tree) {
        inverted += '-inverted';
    } else {
        if (tesk) {
            inverted += '-inverted';
        }
    }


    /* For every assets linked to the event, build a link tag */
    if (evt.assets != null) {
        for (let ide in evt.assets) {
            let cpn =  evt.assets[ide]["ip"] + ' - ' + evt.assets[ide]["description"]
            cpn = sanitizeHTML(cpn)
            let span_anchor = $('<span>');
            span_anchor.attr('data-toggle', 'popover');
            span_anchor.attr('data-trigger', 'hover');
            span_anchor.attr('style', 'cursor: pointer;');
            span_anchor.attr('data-content', cpn);
            span_anchor.attr('title', evt.assets[ide]["name"]);
            span_anchor.text(evt.assets[ide]["name"]);

            if (evt.assets[ide]["compromised"]) {
                span_anchor.addClass('badge badge-warning-event float-right ml-1 mt-2');
            } else {
                span_anchor.addClass('badge badge-light float-right ml-1 mt-2');
            }

            asset += span_anchor[0].outerHTML;
        }
    }

    let ori_date = '<span class="ml-3"></span>';
    if (evt.event_date_wtz != evt.event_date) {
        ori_date += `<i class="fas fa-info-circle mr-1" title="Locale date time ${evt.event_date_wtz}${evt.event_tz}"></i>`
    }

    if(evt.event_in_summary) {
        ori_date += `<i class="fas fa-newspaper mr-1" title="Showed in summary"></i>`
    }

    if(evt.event_in_graph) {
        ori_date += `<i class="fas fa-share-alt mr-1" title="Showed in graph"></i>`
    }


    let day = dta[0];
    // Transform the date to the user's system format. day is in the format YYYY-MM-DD. We want our date in the user's host format, without the minutes and seconds.
    // First parse the date to a Date object
    let date = new Date(day);
    // Then use the toLocaleDateString method to get the date in the user's host format
    day = date.toLocaleDateString();

    let hour = dta[1].split('.')[0];

    let mtop_day = '';

    if (!tmb.includes(day) && evt.parent_event_id == null) {
        tmb.push(day);
        tmb_d = `<li class="time-badge${timeline_style} badge badge-dark" id="time_${idx}"><small class="">${day}</small><br/></li>`;

        idx += 1;
        mtop_day = 'mt-4';
    }

    let title_parsed = match_replace_ioc(sanitizeHTML(evt.event_title), reap);
    let raw_content = do_md_filter_xss(evt.event_content); // Raw markdown content
    // do_md_filter_xss only sanitizes the markdown SOURCE (tag-oriented), so a markdown
    // link with no literal HTML tags (e.g. [x](javascript:...)) survives it and only
    // becomes dangerous once showdown converts it to an <a href="javascript:...">. The
    // !compact branch below re-sanitizes its own converted output with filterXSS, but
    // the compact branch used to render this value directly - filter it here as a safe
    // default so the compact path is covered too.
    let formatted_content = filterXSS(converter.makeHtml(raw_content)); // Convert markdown to HTML

    const wordLimit = 30; // Define your word limit

    if (!compact) {
        let paragraphs = raw_content.split('\n\n');
        let short_content, long_content;

        if (paragraphs.join(' ').split(' ').length > wordLimit || paragraphs.length > 2) {
            let temp_content = '';
            let i = 0;
            let wordCount = 0;

            // Loop until the content length is more than wordLimit or paragraph count is more than 2
            while(wordCount <= wordLimit && i < 2 && i < paragraphs.length){
                let words = paragraphs[i].split(' ');
                if (wordCount + words.length > wordLimit && wordCount != 0) {
                    break;
                }
                temp_content += paragraphs[i] + '\n\n';
                wordCount += words.length;
                i++;
            }

            short_content = converter.makeHtml(temp_content); // Convert markdown to HTML
            short_content = match_replace_ioc(filterXSS(short_content), reap);
            temp_content = paragraphs.slice(i).join('\n\n');
            long_content = converter.makeHtml(temp_content); // Convert markdown to HTML
            long_content = match_replace_ioc(filterXSS(long_content), reap);

            formatted_content = short_content + `<div class="collapse" id="collapseContent-${evt.event_id}">
            ${long_content}
            </div>
            <a class="btn btn-link btn-sm" data-toggle="collapse" href="#collapseContent-${evt.event_id}" role="button" aria-expanded="false" aria-controls="collapseContent" onclick="toggleSeeMore(this)">&gt; See more</a>`;
        } else {
            let content_parsed = converter.makeHtml(raw_content); // Convert markdown to HTML
            content_parsed = filterXSS(content_parsed);
            formatted_content = match_replace_ioc(content_parsed, reap);
        }
    }

    let shared_link = buildShareLink(evt.event_id);

    let flag = '';
    if (evt.event_is_flagged) {
        flag = `<i class="fas fa-flag text-warning" title="Flagged"></i>`;
    } else {
        flag = `<i class="fa-regular fa-flag" title="Not flagged"></i>`;
    }

    if (compact) {
        entry = `<li class="${inverted} ${mtop_day}" title="Event ID #${evt.event_id}" data-datetime="${evt.event_date}" >
                <div class="timeline-panel${timeline_style} ${style}" ${style_s}  id="event_${evt.event_id}">
                    <div class="timeline-heading">
                        <div class="btn-group dropdown float-right">
                            ${cats}
                            <button type="button" class="btn btn-light btn-xs" onclick="edit_event(${evt.event_id})" title="Edit">
                                <span class="btn-label">
                                    <i class="fa fa-pen"></i>
                                </span>
                            </button>
                            <button type="button" class="btn btn-light btn-xs" onclick="flag_event(${evt.event_id})" title="Flag">
                                <span class="btn-label">
                                    ${flag}
                                </span>
                            </button>
                            <button type="button" class="btn btn-light btn-xs" onclick="comment_element(${evt.event_id}, 'timeline/events')" title="Comments">
                                <span class="btn-label">
                                    <i class="fa-solid fa-comments"></i><span class="notification" id="object_comments_number_${evt.event_id}">${nb_comments}</span>
                                </span>
                            </button>
                            <button type="button" class="btn btn-light btn-xs dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
                                <span class="btn-label">
                                    <i class="fa fa-cog"></i>
                                </span>
                            </button>
                            <div class="dropdown-menu" role="menu" x-placement="bottom-start" style="position: absolute; transform: translate3d(0px, 32px, 0px); top: 0px; left: 0px; will-change: transform;">
                                    <a href= "#" class="dropdown-item" onclick="copy_object_link(${evt.event_id});return false;"><small class="fa fa-share mr-2"></small>Share</a>
                                    <a href= "#" class="dropdown-item" onclick="copy_object_link_md('event', ${evt.event_id});return false;"><small class="fa-brands fa-markdown mr-2"></small>Markdown Link</a>
                                    <a href= "#" class="dropdown-item" onclick="duplicate_event(${evt.event_id});return false;"><small class="fa fa-clone mr-2"></small>Duplicate</a>
                                    <div class="dropdown-divider"></div>
                                    <a href= "#" class="dropdown-item text-danger" onclick="delete_event();"><small class="fa fa-trash mr-2"></small>Delete</a>
                            </div>
                        </div>
                        <div class="collapsed" id="dropa_${evt.event_id}" data-toggle="collapse" data-target="#drop_${evt.event_id}" aria-expanded="false" aria-controls="drop_${evt.event_id}" role="button" style="cursor: pointer;">
                            <span class="text-muted text-sm float-left mb--2"><small>${formatTime(evt.event_date, { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'})}</small></span>
                            <a class="text-dark text-sm ml-3" href="${shared_link}" onclick="edit_event(${evt.event_id});return false;">${title_parsed}</a>
                        </div>
                    </div>
                    <div class="timeline-body text-faded" >
                        <div id="drop_${evt.event_id}" class="collapse" aria-labelledby="dropa_${evt.event_id}" style="">
                            <div class="card-body">
                            ${formatted_content}
                            </div>
                            <div class="bottom-hour mt-2">
                                <span class="float-right">${tags}${asset} </span>
                            </div>
                        </div>
                    </div>
                </div>
            </li>`
    } else {
        entry = `<li class=${inverted} title="Event ID #${evt.event_id}" >
                <div class="timeline-panel${timeline_style} ${style}" ${style_s} id="event_${evt.event_id}">
                    <div class="timeline-heading">
                        <div class="btn-group dropdown float-right">

                            <button type="button" class="btn btn-light btn-xs" onclick="edit_event(${evt.event_id})" title="Edit">
                                <span class="btn-label">
                                    <i class="fa fa-pen"></i>
                                </span>
                            </button>
                            <button type="button" class="btn btn-light btn-xs" onclick="add_event(${evt.event_id})" title="Add child event">
                                <span class="btn-label">
                                   <i class="fa-brands fa-hive"></i>
                                </span>
                            </button>
                            <button type="button" class="btn btn-light btn-xs" onclick="flag_event(${evt.event_id})" title="Flag">
                                <span class="btn-label">
                                    ${flag}
                                </span>
                            </button>
                            <button type="button" class="btn btn-light btn-xs" onclick="comment_element(${evt.event_id}, 'timeline/events')" title="Comments">
                                <span class="btn-label">
                                    <i class="fa-solid fa-comments"></i><span class="notification" id="object_comments_number_${evt.event_id}">${nb_comments}</span>
                                </span>
                            </button>
                            <button type="button" class="btn btn-light btn-xs dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
                                <span class="btn-label">
                                    <i class="fa fa-cog"></i>
                                </span>
                            </button>
                            <div class="dropdown-menu" role="menu" x-placement="bottom-start" style="position: absolute; transform: translate3d(0px, 32px, 0px); top: 0px; left: 0px; will-change: transform;">
                                    <a href= "#" class="dropdown-item" onclick="copy_object_link(${evt.event_id});return false;"><small class="fa fa-share mr-2"></small>Share</a>
                                    <a href= "#" class="dropdown-item" onclick="copy_object_link_md('event', ${evt.event_id});return false;"><small class="fa-brands fa-markdown mr-2"></small>Markdown Link</a>
                                    <a href= "#" class="dropdown-item" onclick="duplicate_event(${evt.event_id});return false;"><small class="fa fa-clone mr-2"></small>Duplicate</a>
                                    <div class="dropdown-divider"></div>
                                    <a href= "#" class="dropdown-item text-danger" onclick="delete_event();"><small class="fa fa-trash mr-2"></small>Delete</a>
                            </div>
                        </div>
                        <div class="row mb-2">
                            <a class="timeline-title" href="${shared_link}" onclick="edit_event(${evt.event_id});return false;">[${hour}] ${title_parsed}</a>
                        </div>
                    </div>
                    <div class="timeline-body text-faded" >
                        <span>${formatted_content}</span>

                        <div class="bottom-hour mt-2">
                            <div class="row">
                                <div class="col d-flex">
                                    <span class="text-muted text-sm align-self-end float-left mb--2"><small class="bottom-hour-i"><i class="flaticon-stopwatch mr-2"></i>${formatTime(evt.event_date, { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'})}${ori_date}</small></span>
                                </div>

                                <div class="col">
                                    <span class="float-right">${tags}${asset} </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </li>`
    }
    return [entry, tmb_d];
}

function build_timeline(data) {
    let compact = is_timeline_compact_view();
    let tree = is_timeline_tree_view();
    var is_i = false;
    current_timeline = data.data.tim;
    let tmb = [];

    let reid = 0;

    $('#time_timeline_select').empty();

    var standard_filters = [
                {value: 'asset:', score: 10, meta: 'Match assets name of events'},
                {value: 'asset_id:', score: 10, meta: 'Match assets ID of events'},
                {value: 'startDate:', score: 10, meta: 'Match end date of events'},
                {value: 'endDate:', score: 10, meta: 'Match end date of events'},
                {value: 'tag:', score: 10, meta: 'Match tag of events'},
                {value: 'description:', score: 10, meta: 'Match description of events'},
                {value: 'flag', score: 10, meta: 'Match flagged events'},
                {value: 'category:', score: 10, meta: 'Match category of events'},
                {value: 'title:', score: 10, meta: 'Match title of events'},
                {value: 'source:', score: 10, meta: 'Match source of events'},
                {value: 'raw:', score: 10, meta: 'Match raw data of events'},
                {value: 'ioc', score: 10, meta: "Match ioc value in events"},
                {value: 'ioc_id', score: 10, meta: "Match ioc ID in events"},
                {value: 'event_id', score: 10, meta: "Match event ID in events"},
                {value: 'AND ', score: 10, meta: 'AND operator'}
              ]

    for (let rid in data.data.assets) {
        standard_filters.push(
             {value: data.data.assets[rid][0], score: 1, meta: data.data.assets[rid][1]}
        );
    }

    for (let rid in data.data.categories) {
        standard_filters.push(
             {value: data.data.categories[rid], score: 1, meta: "Event category"}
        );
    }

    tm_filter.setOptions({
          enableBasicAutocompletion: [{
            getCompletions: (editor, session, pos, prefix, callback) => {
              callback(null, standard_filters);
            },
          }],
          enableLiveAutocompletion: true,
    });

    let tesk = false;
    let reap = [];
    let ioc_list = data.data.iocs;
    for (ioc in ioc_list) {
        let ioc_len = ioc_list[ioc]['ioc_value'].length;
        if (ioc_len === 0 || ioc_len > 64) {
            console.log('Ignoring IOC with length 0 or > 64')
            continue;
        }
        let capture_start = "(^|;|:|||>|<|[|]|(|)|\s|\>)(";
        let capture_end = ")(;|:|||>|<|[|]|(|)|\s|>|$|<br/>)";
        // When an IOC contains another IOC in its description, we want to avoid to replace that particular pattern
        var avoid_inception_start = "(?!<span[^>]*?>)" + capture_start;
        var avoid_inception_end = "(?![^<]*?<\/span>)" + capture_end;
        var re = new RegExp(avoid_inception_start
               + escapeRegExp(sanitizeHTML(ioc_list[ioc]['ioc_value']))
               + avoid_inception_end
               ,"g");
        let replacement = `$1<span class="text-warning-high ml-1 link_asset" data-toggle="popover" style="cursor: pointer;" data-trigger="hover" data-content="${escapeHtml(ioc_list[ioc]['ioc_description'])}" title="IOC">${sanitizeHTML(ioc_list[ioc]['ioc_value'])}</span>`;
        reap.push([re, replacement]);
    }
    let idx = 0;

    let converter = get_showdown_convert();
    let child_events = Object();

    for (let index in data.data.tim) {
        let evt =  data.data.tim[index];
        let eki = buildEvent(evt, compact, data.data.comments_map, tree, tesk, tmb, idx, reap, converter);
        tesk = !tesk;

        is_i = false;
        let entry = eki[0];
        let tmb_d = eki[1];

        if (evt.parent_event_id != null) {
            if (!(evt.parent_event_id in child_events)) {
                child_events[evt.parent_event_id] = [];
            }
            child_events[evt.parent_event_id].push(entry);
            tesk = !tesk;

        } else {
            $('#timeline_list').append(tmb_d);
            $('#timeline_list').append(entry);
        }

    }


    if (tree) {
        $('#timeline_list').addClass('timeline-t');
    } else {
        $('#timeline_list').removeClass('timeline-t');
    }

    for (let parent_id in child_events) {
        let parent_event = $('#event_' + parent_id);

        let parent_event_class = parent_event.parent().attr('class');
        let parent_class = parent_event.attr('class');

        // Reverse the order of the child events list
        child_events[parent_id] = child_events[parent_id].reverse();

        // Add button on parent to toggle child events
        let button = $('<button>');
        button.attr('type', 'button');
        button.attr('class', 'btn btn-light btn-xs mt-2');
        button.attr('onclick', `toggle_child_events_of_event(${parent_id});`);
        button.attr('title', 'Toggle child events');
        button.html('<span class="btn-label"><i class="fa fa-chevron-down"></i></span>');

        parent_event.find('.timeline-body').append(button);

        for (let child_html in child_events[parent_id]) {

            let child = $(child_events[parent_id][child_html]);

            child.attr('class', parent_event_class);
            child.addClass('timeline-child');
            child.addClass('timeline-child-' + parent_id);

            child.find('div:first').attr('class', parent_class);

            let child_date = child.find('.bottom-hour').find('small').text();
            let parent_date = parent_event.find('.bottom-hour').find('small').text();
            child_date = Date.parse(child_date);
            parent_date = Date.parse(parent_date);

            if (child_date < parent_date) {
                child.find('.bottom-hour-i').append('<span class="ml-2"><i class="fas fa-exclamation-triangle text-warning" title="Child event datetime is earlier than parent event"></i></span>')
            }

            child.insertAfter(parent_event.parent());
        }

    }

    //match_replace_ioc(data.data.iocs, "timeline_list");
    $('[data-toggle="popover"]').popover();

    if (data.data.tim.length === 0) {
       $('#card_main_load').append('<h3 class="ml-mr-auto text-center" id="no_events_msg">No events in current view</h3>');
       $('#timeline_list').hide();
    } else {
        $('#timeline_list').show();
        $('#no_events_msg').remove('h3');
    }

    set_last_state(data.data.state);
    hide_loader();

    if (location.href.indexOf("#") != -1) {
        var current_url = window.location.href;
        var id = current_url.substr(current_url.indexOf("#") + 1);
        if ($('#event_'+id).offset() != undefined) {
            $('.content').animate({ scrollTop: $('#event_'+id).offset().top - 180 });
            $('#event_'+id).addClass('fade-it');
        }
    }

    // re-enable onclick event on timeline if selector_active is true
    if(selector_active == true) {
        $(".timeline li .timeline-panel").on('click', function(){
            if($(this).hasClass("timeline-selected")) {
                $(this).removeClass("timeline-selected");
            } else {
                $(this).addClass("timeline-selected");
            }
        });
    }
}

function toggle_child_events() {
    let child_events = $('.timeline-child');
    if (child_events.is(':visible')) {
        child_events.hide();
        // Find the button of the parent event, excluding the child events themselves
        for (let i = 0; i < child_events.length; i++) {
            let child_event = child_events[i];
            let parent_event = $(child_event).prev();
            if (parent_event.hasClass('timeline-child')) {
                continue;
            }
            let btn = parent_event.find('button:last');
            if (btn.html().indexOf('fa-chevron-down') !== -1) {
                btn.html('<span class="btn-label"><i class="fa fa-chevron-right"></i> Child events</span>');
            }
        }


    } else {
        child_events.show();
        for (let i = 0; i < child_events.length; i++) {
            let child_event = child_events[i];
            let parent_event = $(child_event).prev();
            if (parent_event.hasClass('timeline-child')) {
                continue;
            }
            let btn = parent_event.find('button:last');
            if (btn.html().indexOf('fa-chevron-right') !== -1) {
                btn.html('<span class="btn-label"><i class="fa fa-chevron-down"></i></span>');
            }
        }
    }
}

function toggle_child_events_of_event(event_id) {
    let child_events = $('.timeline-child-' + event_id);
    let event = $('#event_' + event_id);

    if (child_events.is(':visible')) {
        child_events.hide();
        let btn = $('#event_' + event_id).find('button:last');
        if (btn.html().indexOf('fa-chevron-down') !== -1) {
            btn.html('<span class="btn-label"><i class="fa fa-chevron-right"></i> Child events</span>');
        }
    } else {
        child_events.show();
        let btn = $('#event_' + event_id).find('button:last');
        if (btn.html().indexOf('fa-chevron-right') !== -1) {
            btn.html('<span class="btn-label"><i class="fa fa-chevron-down"></i></span>');
        }
    }
}

function escapeRegExp(text) {
    return text.replace(/[-[\]{}()*+?.,\\^$|#\s]/g, '\\$&');
}

function match_replace_ioc(entry, reap) {

    for (rak in reap) {
        entry = entry.replace(reap[rak][0], reap[rak][1]);
    }
    return entry;
}

function to_page_up() {
  document.body.scrollTop = 0; // For Safari
  document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
}

function to_page_down() {
    // Get last element ID of the timeline
    let last_element_id = $('.timeline li:last > div').attr('id').replace('event_', '');

    // Scroll to the last element
    $('html').animate({ scrollTop: $('#event_'+last_element_id).offset().top - 80 });
}

function show_time_converter(){
    $('#event_date_convert').show();
    $('#event_date_convert_input').focus();
    $('#event_date_inputs').hide();
}

function hide_time_converter(){
    $('#event_date_convert').hide();
    $('#event_date_inputs').show();
    $('#event_date').focus();
}

function show_end_time_converter(){
    $('#end_event_date_convert').show();
    $('#end_event_date_convert_input').focus();
    $('#end_event_date_inputs').hide();
}

function hide_end_time_converter(){
    $('#end_event_date_convert').hide();
    $('#end_event_date_inputs').show();
    $('#end_event_date').focus();
}

function flag_event(event_id){
    post_request_api('timeline/events/flag/'+event_id)
    .done(function(data) {
        if (notify_auto_api(data)) {
            uiFlagEvent(event_id, data.data.event_is_flagged)
        }
    });
}

function uiFlagEvent(event_id, is_flagged) {
    if (is_flagged === true) {
        $('#event_'+event_id).find('.fa-flag').addClass('fas text-warning').removeClass('fa-regular');
    } else {
        $('#event_'+event_id).find('.fa-flag').addClass('fa-regular').removeClass('fas text-warning');
    }
}

function uiRemoveEvent(event_id) {
    $('#event_'+event_id).remove();
}

function uiUpdateEvent(event_id, event_data) {
    let last_event_id = 0;
    for (let index in current_timeline){
        let list_date = new Date(current_timeline[index].event_date);
        let evt_date = new Date(event_data.event_date);

        if (list_date < evt_date) {
            last_event_id = current_timeline[index].event_id;
        }
    }
    if (last_event_id !== 0) {
        let updated_event = $(`#event_${event_id}`).html();
        $(`#event_${event_id}`).remove();
        $(`#event_${last_event_id}`).after(updated_event);
    }
}

/**
 * Converts a user-input date string and updates related fields
 * Returns a Promise that resolves when the
 * update completes successfully or rejects on failure
 *
 * @returns {Promise<void>} A Promise that resolves when the conversion and UI update succeed
 */
function time_converter() {
    return new Promise(function(resolve, reject) {
        let date_val = $('#event_date_convert_input').val();

        var data_sent = {
            date_value: date_val,
            csrf_token: $('#csrf_token').val()
        };

        post_request_api('timeline/events/convert-date', JSON.stringify(data_sent))
            .done(function(data) {
                if (notify_auto_api(data)) {
                    $('#event_date').val(data.data.date);
                    $('#event_time').val(data.data.time);
                    $('#event_tz').val(data.data.tz);
                    // If end time is empty, default it to the converted start time
                    const end_date_val = $('#end_event_date').val();
                    const end_convert_val = $('#end_event_date_convert_input').val();
                    if ((!end_date_val || end_date_val.length === 0) && (!end_convert_val || end_convert_val.trim().length === 0)) {
                        $('#end_event_date').val(data.data.date);
                        $('#end_event_time').val(data.data.time);
                        $('#end_event_tz').val(data.data.tz);
                        $('#end_event_date_convert_input').val(`${data.data.date}T${data.data.time}`);
                    }
                    hide_time_converter();
                    $('#convert_warning_feedback').text(data.data.msg);
                    $('#convert_bad_feedback').text('');
                    resolve();
                } else {
                    reject("API response was not successful.");
                }
            })
            .fail(function() {
                $('#convert_bad_feedback').text('Unable to find a matching pattern for the date.');
                reject("Failed to convert date.");
            });
    });
}

function set_end_event_fields(data_sent) {
    const end_date = $('#end_event_date').val();
    const end_time = $('#end_event_time').val();
    const end_tz = $('#end_event_tz').val();

    if (end_date && end_date.length > 0) {
        data_sent['event_end_date'] = `${end_date}T${end_time}`;
        data_sent['event_end_tz'] = end_tz;
    } else {
        data_sent['event_end_date'] = null;
        data_sent['event_end_tz'] = null;
    }
}

function end_time_converter() {
    return new Promise(function(resolve, reject) {
        let date_val = $('#end_event_date_convert_input').val();

        var data_sent = {
            date_value: date_val,
            csrf_token: $('#csrf_token').val()
        };

        post_request_api('timeline/events/convert-date', JSON.stringify(data_sent))
            .done(function(data) {
                if (notify_auto_api(data)) {
                    $('#end_event_date').val(data.data.date);
                    $('#end_event_time').val(data.data.time);
                    $('#end_event_tz').val(data.data.tz);
                    hide_end_time_converter();
                    $('#end_convert_warning_feedback').text(data.data.msg);
                    $('#end_convert_bad_feedback').text('');
                    resolve();
                } else {
                    reject("API response was not successful.");
                }
            })
            .fail(function() {
                $('#end_convert_bad_feedback').text('Unable to find a matching pattern for the date.');
                reject("Failed to convert date.");
            });
    });
}

function goToSharedLink(){
    if (location.href.indexOf("#") != -1) {
        var current_url = window.location.href;
        var id = current_url.substr(current_url.indexOf("#") + 1);
        if ($('#event_'+id).offset() != undefined) {
            return;
        }
   }
   shared_id = getSharedLink();
   if (shared_id) {
        $('html, body').animate({ scrollTop: $('#event_'+shared_id).offset().top - 80 });
        $('#event_'+shared_id).addClass('fade-it');
    }
}

function timelineToCsv(){
    csv_data = "event_date(UTC),event_title,event_description,event_tz,event_date_wtz,event_end_date,event_end_tz,event_end_date_wtz,event_category,event_tags,linked_assets,linked_iocs\n";
    for (index in current_timeline) {
        item = current_timeline[index];
        content = item.event_content.replace(/"/g, '\"');
        content_parsed = content.replace(/(\r?\n)+/g, ' - ');
        title = item.event_title.replace(/"/g, '\"');
        tags = item.event_tags.replace(/"/g, '\"');
        assets = "";
        for (k in item.assets) {
            asset = item.assets[k].name.replace(/"/g, '\"');
            assets += `${asset};`;
        }
        iocs = "";
        for (k in item.iocs) {
            ioc = item.iocs[k].name.replace(/"/g, '\"');
            iocs += `${ioc};`;
        }
        csv_data += `"${item.event_date}","${title}","${content_parsed}","${item.event_tz}","${item.event_date_wtz}","${item.event_end_date || ''}","${item.event_end_tz || ''}","${item.event_end_date_wtz || ''}","${item.category_name}","${tags}","${assets}","${iocs}"\n`;
    }
    download_file("iris_timeline.csv", "text/csv", csv_data);
}

function timelineToCsvWithUI(){
    csv_data = "event_date(UTC),event_title,event_description,event_tz,event_date_wtz,event_end_date,event_end_tz,event_end_date_wtz,event_category,event_tags,linked_assets,linked_iocs,created_by,creation_date\n";
    for (index in current_timeline) {

        item = current_timeline[index];
        content = item.event_content.replace(/"/g, '\"');
        content_parsed = content.replace(/(\r?\n)+/g, ' - ');
        title = item.event_title.replace(/"/g, '\"');
        tags = item.event_tags.replace(/"/g, '\"');
        assets = "";
        for (k in item.assets) {
            asset = item.assets[k].name.replace(/"/g, '\"');
            assets += `${asset};`;
        }
        iocs = "";
        for (k in item.iocs) {
            ioc = item.iocs[k].name.replace(/"/g, '\"');
            iocs += `${ioc};`;
        }
        csv_data += `"${item.event_date}","${title}","${content_parsed}","${item.event_tz}","${item.event_date_wtz}","${item.event_end_date || ''}","${item.event_end_tz || ''}","${item.event_end_date_wtz || ''}","${item.category_name}","${tags}","${assets}","${iocs}","${item.user}","${item.event_added}"\n`;
    }
    download_file("iris_timeline.csv", "text/csv", csv_data);
}

function timelineToExcel() {
    let workbook = new ExcelJS.Workbook();
    let worksheet = workbook.addWorksheet('Timeline');

    worksheet.columns = [
        { header: 'event_id', key: 'event_id'},
        { header: 'event_date', key: 'event_date'},
        { header: 'event_tz', key: 'event_tz'},
        { header: 'event_end_date', key: 'event_end_date'},
        { header: 'event_end_tz', key: 'event_end_tz'},
        { header: 'event_title', key: 'event_title' },
        { header: 'event_category', key: 'event_category' },
        { header: 'event_content', key: 'event_content' },
        { header: 'event_raw', key: 'event_raw' },
        { header: 'event_source', key: 'event_source' },
        { header: 'event_assets', key: 'event_assets' },
        { header: 'event_iocs', key: 'event_iocs' },
        { header: 'event_tags', key: 'event_tags' },
    ];

    for (index in current_timeline) {
        let event = current_timeline[index];
        let row_assets = "";
        if (event.assets.length > 0 && event.assets != undefined)
        {
            event.assets.forEach((asset) => {
                row_assets += asset.name;
                row_assets += ";";
            });
        }
        let row_iocs = "";
        if (event.iocs.length > 0 && event.iocs != undefined) {
            row_iocs = "";
            event.iocs.forEach((ioc) => {
                row_iocs += ioc.name;
                row_iocs += ";";
            });
        }
        let row_tags = event.event_tags.replace(",", "|");
        worksheet.addRow({ event_id: event.event_id, event_date: event.event_date_wtz, event_tz: "+00:00",
                        event_title: event.event_title, event_category: event.category_name, event_content: event.event_content,
                        event_raw: event.event_raw, event_source: event.event_source, event_assets: row_assets, event_iocs: row_iocs, event_tags: row_tags });
    }
    // Unfreeze every column except event_id
    for(let col_idx = 1; col_idx <= worksheet.columnCount; col_idx++)
    {
        let col = worksheet.getColumn(col_idx);
        if (col._header != "event_id")
        {
            col.protection = { locked: false, lockText: false };
        }
    }
    // Freeze headers
    let header_row = worksheet.getRow(1);
    header_row.protection = { locked: true, lockText: true };

    // Resize column width to largest value + a buffer
    worksheet.columns.forEach(column => {
        let lengths = column.values.map(v => v.toString().length);
        let maxLength = Math.max(...lengths.filter(v => typeof v === 'number'));
        column.width = maxLength+1;
    });

    // add Assets tab to Excel export
    let assets_worksheet = workbook.addWorksheet('Assets');
    // full_assets is defined in common.js, to be accessible across different tabs
    addAssetsTabToExcel(assets_worksheet, full_assets);

    // add IOCs tab to Excel export
    let iocs_worksheet = workbook.addWorksheet('IOCs');
    // full_iocs is defined in common.js, to be accessible across different tabs
    addIocsTabToExcel(iocs_worksheet, full_iocs);

    // format filename: case_[caseid]_timeline_[ISO UTC date].xlsx
    let caseid = get_caseid();
    date = get_current_datetime_iso();
    filename = "case_" + caseid + "_timeline_" + date + ".xlsx";

    workbook.xlsx.writeBuffer().then(function (data) {
        const blob = new Blob([data],
            { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const url = window.URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = filename;
        anchor.click();
        window.URL.revokeObjectURL(url);
    });
}


function timelineToExcelWithUI() {
    let workbook = new ExcelJS.Workbook();
    let worksheet = workbook.addWorksheet('Timeline');

    worksheet.columns = [
        { header: 'event_id', key: 'event_id' },
        { header: 'event_date', key: 'event_date' },
        { header: 'event_tz', key: 'event_tz' },
        { header: 'event_end_date', key: 'event_end_date'},
        { header: 'event_end_tz', key: 'event_end_tz'},
        { header: 'event_title', key: 'event_title' },
        { header: 'event_category', key: 'event_category' },
        { header: 'event_content', key: 'event_content' },
        { header: 'event_raw', key: 'event_raw' },
        { header: 'event_source', key: 'event_source' },
        { header: 'event_assets', key: 'event_assets' },
        { header: 'event_iocs', key: 'event_iocs' },
        { header: 'event_tags', key: 'event_tags' },
        { header: "created_by", key: "created_by"},
        { header: "creation_date", key: "creation_date"},
    ];

    for (index in current_timeline) {
        let event = current_timeline[index];
        let row_assets = "";
        if (event.assets.length > 0 && event.assets != undefined) {
            event.assets.forEach((asset) => {
                row_assets += asset.name;
                row_assets += ";";
            });
        }
        let row_iocs = "";
        if (event.iocs.length > 0 && event.iocs != undefined) {
            row_iocs = "";
            event.iocs.forEach((ioc) => {
                row_iocs += ioc.name;
                row_iocs += ";";
            });
        }
        let row_tags = event.event_tags.replace(",", "|");
        worksheet.addRow({ event_id: event.event_id, event_date: event.event_date_wtz, event_tz: "+00:00",
                        event_title: event.event_title, event_category: event.category_name, event_content: event.event_content,
                        event_raw: event.event_raw, event_source: event.event_source, event_assets: row_assets, event_iocs: row_iocs,
                        event_tags: row_tags, created_by: event.user, creation_date: event.event_added });
    }
    // Unfreeze every column except event_id and user_info
    for (let col_idx = 1; col_idx <= worksheet.columnCount; col_idx++) {
        let col = worksheet.getColumn(col_idx);
        if(col._header != "event_id" && col._header != "created_by" && col._header != "creation_date")
        {
            col.protection = { locked: false, lockText: false };
        }
    }
    // Freeze headers
    let header_row = worksheet.getRow(1);
    header_row.protection = { locked: true, lockText: true };

    // Resize column width to largest value + a buffer
    worksheet.columns.forEach(column => {
        let lengths = column.values.map(v => v.toString().length);
        let maxLength = Math.max(...lengths.filter(v => typeof v === 'number'));
        column.width = maxLength + 1;
    });


    // add Assets tab to Excel export
    let assets_worksheet = workbook.addWorksheet('Assets');
    // full_assets is defined in common.js, to be accessible across different tabs
    addAssetsTabToExcel(assets_worksheet, full_assets);

    // add IOCs tab to Excel export
    let iocs_worksheet = workbook.addWorksheet('IOCs');
    // full_iocs is defined in common.js, to be accessible across different tabs
    addIocsTabToExcel(iocs_worksheet, full_iocs);

    // format filename: case_[caseid]_timeline_[ISO UTC date].xlsx
    let caseid = get_caseid();
    date = get_current_datetime_iso();
    filename = "case_" + caseid + "_timeline_" + date + ".xlsx";

    workbook.xlsx.writeBuffer().then(function (data) {
        const blob = new Blob([data],
            { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const url = window.URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = filename;
        anchor.click();
        window.URL.revokeObjectURL(url);
    });
}


let parsed_filter = {};
let keywords = ['asset', 'asset_id', 'tag', 'title', 'description', 'ioc', 'ioc_id',
        'raw', 'category', 'source', 'flag', 'startDate', 'endDate', 'event_id'];

function parse_filter(str_filter, keywords) {
  for (var k = 0; k < keywords.length; k++) {
  	keyword = keywords[k];
    items = str_filter.split(keyword + ':');

    ita = items[1];

    if (ita === undefined) {
    	continue;
    }

    item = split_bool(ita);

    if (item != null) {
      if (!(keyword in parsed_filter)) {
        parsed_filter[keyword] = [];
      }
      if (!parsed_filter[keyword].includes(item)) {
        parsed_filter[keyword].push(item.trim());
        console.log('Got '+ item.trim() + ' as ' + keyword);
      }

      if (items[1] != undefined) {
        str_filter = str_filter.replace(keyword + ':' + item, '');
        if (parse_filter(str_filter, keywords)) {
        	keywords.shift();
        }
      }
    }
  }
  return true;
}

function filter_timeline() {
    current_path = location.protocol + '//' + location.host + location.pathname;
    new_path = current_path + case_param() + '&filter=' + encodeURIComponent(tm_filter.getValue());
    window.location = new_path;
}

function reset_filters() {
    current_path = location.protocol + '//' + location.host + location.pathname;
    new_path = current_path + case_param();
    window.location = new_path;
}

function apply_filtering(post_req_fn, reset_pos = false) {
    keywords = ['asset', 'asset_id', 'tag', 'title', 'description', 'ioc', 'ioc_id',
        'raw', 'category', 'source', 'flag', 'startDate', 'endDate', 'event_id'];

    parsed_filter = {};
    parse_filter(tm_filter.getValue(), keywords);
    filter_query = encodeURIComponent(JSON.stringify(parsed_filter));

    const content = document.querySelector('.content');
    var scrollPos = reset_pos ? 0: content.scrollTop;
    console.log(scrollPos);

    $('#timeline_list').empty();
    show_loader();
    get_request_data_api("/case/timeline/advanced-filter",{ 'q': filter_query })
    .done((data) => {
        if(notify_auto_api(data, true)) {
            build_timeline(data);
            if(post_req_fn !== undefined) {
                post_req_fn();
            }
            // add list of events to timeline tabular
            events_list = data.data.tim;
            events_list.forEach(function (evt) {
                evt._search_blob = build_event_search_blob(evt);
            });
            const page_info = Table.page.info();
            const display_start = page_info ? page_info.start : 0;
            Table.clear();
            Table.rows.add(events_list);

            // TODO: make cells editable here, if needed

            if (Table.settings && Table.settings().length > 0) {
                Table.settings()[0]._iDisplayStart = display_start;
            }
            Table.columns.adjust().draw(false);
            load_menu_mod_options('event', Table, delete_event, [{
                type: 'option',
                title: 'Duplicate',
                multi: false,
                iconClass: 'fa fa-clone',
                action: function(rows) {
                    let row = rows[0];
                    duplicate_event(row.event_id);
                }
            }]);
            $('[data-toggle="popover"]').popover();
            Table.responsive.recalc();
            $(document)
                .off('click', '.event_details_link')
                .on('click', '.event_details_link', function(event) {
                    event.preventDefault();
                    let event_id = $(this).data('event_id');
                    edit_event(event_id);
                });

            set_last_state(data.data.state);
            content.scrollTo(0, scrollPos);
            hide_loader();
        }
        goToSharedLink();
    });
}

function getFilterFromLink(){
    queryString = window.location.search;
    urlParams = new URLSearchParams(queryString);

    if (urlParams.get('filter') !== undefined) {
        return urlParams.get('filter')
    }
    return null;
}

function get_or_filter_tm(post_req_fn, reset_pos=false) {
    filter = getFilterFromLink();
    if (filter) {
        tm_filter.setValue(filter);
        apply_filtering(post_req_fn, reset_pos);
    } else {
        apply_filtering(post_req_fn, reset_pos);
    }
}

function show_timeline_filter_help() {
    $('#modal_help').load('/case/timeline/filter-help/modal' + case_param(), function (response, status, xhr) {
        if (status !== "success") {
             ajax_notify_error(xhr, '/case/timeline/filter-help/modal');
             return false;
        }
        $('#modal_help').modal('show');
    });
}

/* BEGIN_RS_CODE */
function fire_upload_excel_events() {
    $('#modal_upload_excel_events').modal('show');
}

function upload_csv_events() {
    const api_path =  '/case/timeline/events/csv_upload';
    const modal_dlg = '#modal_upload_csv_events'
    const file_input = '#input_upload_csv_events'

    var file = $(file_input).get(0).files[0];

    var reader = new FileReader();
    reader.onload = function (e) {
        let fileData = e.target.result
        let data = new Object();
        data['csrf_token'] = $('#csrf_token').val();
        data['CSVData'] = fileData;

        post_request_api(api_path, JSON.stringify(data), true)
        .done((data) => {

            if (notify_auto_api(data)) {
                apply_filtering();
                $(modal_dlg).modal('hide');
                swal("Got news for you", data.message, "success");
            } else {
                //alert( JSON.stringify(data.data,null,2));
                swal("Got bad news for you", data.message, "error");
            }
        })

    };
    reader.readAsText(file)

    return false;
}

function upload_excel_events(){
    const api_path =  '/case/timeline/events/excel_upload';
    const modal_dlg = '#modal_upload_excel_events'
    const file_input = '#input_upload_excel_events'

    var file = $(file_input).get(0).files[0];

    var reader = new FileReader();
    reader.onload = function (e) {
        let fileData = e.target.result
        let data = new Object();
        data['csrf_token'] = $('#csrf_token').val();
        //need to convert the buffer to an Array object for JSON.stringify to work
        data['excel_data'] = Array.from(new Uint8Array(fileData));

        post_request_api(api_path, JSON.stringify(data), true)
        .done((data) => {
            var str = '<ul style="list-style-type: none; padding: 0;">'
            data.data.forEach(function(item) {
                str += '<li>'+ item + '</li>';
            });
            str += '</ul> <i>Recoverable errors can be solved by fixing the error in your file and reuploading.</i>';

            let msg = document.createElement('div')
            msg.innerHTML = str

            if (notify_auto_api(data)) {
                apply_filtering();
                $(modal_dlg).modal('hide')
                swal({
                    title: "Upload done. Any rows with errors are displayed below",
                    icon: "success",
                    content: msg,
                })
            } else {
                swal({
                    title: "That didn't work :(",
                    icon: "error",
                    content: msg,
                })
            }
        })

    };
    //read in excel file as bytes
    reader.readAsArrayBuffer(file)

    return false;
}


function handleCollabNotifications(collab_data) {
   if (collab_data.action_type === "flagged") {
       uiFlagEvent(collab_data.object_id, true);
   }
   else if (collab_data.action_type === "un-flagged") {
       uiFlagEvent(collab_data.object_id, false);
   }
   else if (collab_data.action_type === "deletion") {
       uiRemoveEvent(collab_data.object_id);
   }
   // else if (collab_data.action_type === 'updated') {
   //     uiUpdateEvent(collab_data.object_id,
   //         collab_data.object_data)
   // }
}

function generate_events_sample_csv(){
    csv_data = "event_date,event_tz,event_end_date,event_end_tz,event_title,event_category,event_content,event_raw,event_source,event_assets,event_iocs,event_tags\n"
    csv_data += '"2023-03-26T03:00:30.000","+00:00","2023-03-26T03:10:30.000","+00:00","An event","Unspecified","Event description","raw","source","","","defender|malicious"\n'
    csv_data += '"2023-03-26T03:00:35.000","+00:00","","","An event","Legitimate","Event description","raw","source","","","defender|malicious"\n'
    download_file("sample_events.csv", "text/csv", csv_data);
}

function generate_events_sample_excel(){
    let workbook = new ExcelJS.Workbook();
    let worksheet = workbook.addWorksheet('Timeline');

    worksheet.columns = [
        { header: 'event_id', key: 'event_id' },
        { header: 'event_date', key: 'event_date' },
        { header: 'event_tz', key: 'event_tz' },
        { header: 'event_end_date', key: 'event_end_date' },
        { header: 'event_end_tz', key: 'event_end_tz' },
        { header: 'event_title', key: 'event_title' },
        { header: 'event_category', key: 'event_category' },
        { header: 'event_content', key: 'event_content' },
        { header: 'event_raw', key: 'event_raw' },
        { header: 'event_source', key: 'event_source' },
        { header: 'event_assets', key: 'event_assets' },
        { header: 'event_iocs', key: 'event_iocs' },
        { header: 'event_tags', key: 'event_tags' },
    ];

    worksheet.addRow({ event_id: "", event_date: "2023-03-26T03:00:30.000", event_tz: "+00:00", event_end_date: "2023-03-26T03:10:30.000", event_end_tz: "+00:00", event_title: "An event", event_category: "Unspecified", event_content: "Event description", event_raw: "raw", event_source: "source", event_assets: "", event_iocs: "abc;123;def;456;", event_tags: "defender|malicious" });

    // Unfreeze every column except event_id
    for (let col_idx = 2; col_idx <= worksheet.columnCount; col_idx++) {
        let col = worksheet.getColumn(col_idx);
        col.protection = { locked: false, lockText: false };
    }
    // Freeze headers
    let header_row = worksheet.getRow(1);
    header_row.protection = { locked: true, lockText: true };

    // Resize column width to largest value + a buffer
    worksheet.columns.forEach(column => {
        let lengths = column.values.map(v => v.toString().length);
        let maxLength = Math.max(...lengths.filter(v => typeof v === 'number'));
        column.width = maxLength + 1;
    });

    workbook.xlsx.writeBuffer().then(function (data) {
        const blob = new Blob([data],
            { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
        const url = window.URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = "sample_events.xlsx";
        anchor.click();
        window.URL.revokeObjectURL(url);
    });
}

/* END_RS_CODE */

/* Page is ready, fetch the assets of the case */
$(document).ready(function(){

    selector_active = false;

    tm_filter = ace.edit("timeline_filtering",
    {
        autoScrollEditorIntoView: true,
        minLines: 1,
        maxLines: 5
    });
    tm_filter.setTheme("ace/theme/tomorrow");
    tm_filter.session.setMode("ace/mode/json");
    tm_filter.renderer.setShowGutter(false);
    tm_filter.setShowPrintMargin(false);
    tm_filter.renderer.setScrollMargin(10, 10);
    tm_filter.setOption("displayIndentGuides", true);
    tm_filter.setOption("indentedSoftWrap", true);
    tm_filter.setOption("showLineNumbers", false);
    tm_filter.setOption("placeholder", "Filter timeline");
    tm_filter.setOption("highlightActiveLine", false);
    tm_filter.commands.addCommand({
                        name: "Do filter",
                        bindKey: { win: "Enter", mac: "Enter" },
                        exec: function (editor) {
                                  filter_timeline();
                        }
    });
    $('#time_timeline_select').on('change', function(e){
        id = $('#time_timeline_select').val();
        $('html, body').animate({ scrollTop: $('#time_'+id).offset().top - 180 });
    });

    /****** changes start here  *******/

    /* add filtering fields for each column of table of the page (must be done before datatable initialization) */
    // $.each($.find("table"), function(index, element){
    //     addFilterFields($(element).attr("id"));
    // });

    Table = $("#timeline_tabular").DataTable({
        dom: '<"container-fluid"<"row"<"col"l><"col"f><"col text-right"p>>>rt<"container-fluid"<"row"<"col"i><"col"p>>>',
        aaData: [],
        fixedHeader: {
            headerOffset: 47  // make header sticky only to top of the inner page
        },
        stateSave: true,
        autoWidth: false,
        aoColumns: [
            {
                "data": "event_date",  // LOCAL
                "width": "11%",
                "render": function(data, type) {
                    if (!data) {
                        return data;
                    }

                    if (type === 'display') {
                        return data.split(".")[0];
                    }

                    // Keep milliseconds for accurate sort ordering.
                    return data;
                }
            },
            {
                "data": "event_date_wtz",  // UTC
                "width": "11%",
                "render": function(data, type) {
                    if (!data) {
                        return data;
                    }

                    if (type === 'display') {
                        return data.split(".")[0];
                    }

                    // Keep milliseconds for accurate sort ordering.
                    return data;
                }
            },
            {
                "data": "event_added",  // Create Date
                "visible": false,
                "width": "11%",
                "render": function(data, type) {
                    if (!data) {
                        return data;
                    }

                    if (type === 'display') {
                        return data.split(".")[0];
                    }

                    return data;
                }
            },
            {
                "data": "event_title",  // Event Title
                "width": "30%",
                "render": function(data, type, row, meta) {
                    if (type === 'display' && data != null) {
                        let datak = '';

                        // format event description
                        let displayEventDesc = strip_markdown_images(row['event_content']);
                        displayEventDesc = cleanHTMLTags(displayEventDesc);
                        displayEventDesc = ellipsis_field_raw(displayEventDesc, 900);
                        let dataContent = parse_json_string(displayEventDesc);

                        let shareLink = buildShareLink(row['event_id']);

                        // build hyperlink for event title, show event description when hover over
                        let anchor = $('<a>')
                            .attr('href', shareLink)
                            .attr('data-event_id', row['event_id'])
                            .attr('title', `Event ID #${row['event_id']}`)
                            .attr('data-toggle', 'popover')
                            .attr('data-trigger', 'hover')
                            .attr('data-content', dataContent)
                            .css('cursor', 'pointer')
                            .addClass('event_details_link');

                        if (isWhiteSpace(data) || data === null) {
                            datak = '#' + row['event_id'];
                            anchor.text(datak);
                        } else {
                            datak = ellipsis_field(data, 200);
                            anchor.html(datak);
                        }

                        return anchor.prop('outerHTML');
                    }
                    return data;
                }
            },
            {
                "data": "event_in_summary",  // Add to Summary
                "width": "6%",
                "render": function(data, type) {
                    if (type === 'display') {
                        return data ? 'Y' : 'N';
                    }
                    return data;
                }
            },
            {
                "data": 'assets',  // Host
                "width": "10%",
                "render": function(data){
                    // parse host data from assets

                    if(data.length == 0) {
                        return '';
                    }
                    else {
                        var asset_link = '';

                        // display each asset name on a line, hyperlink to route back to Assets
                        data.forEach(function(asset){
                            data_asset_name = sanitizeHTML(asset.name);
                            data_asset_name = ellipsis_field_raw(data_asset_name, 30);

                            share_link = "/case/assets" + case_param();
                            asset_link += '<a href="'+ share_link + '">' + data_asset_name + '</a>';
                            asset_link += "<br/>";
                        });
                        data = asset_link;
                    }
                    return data;
                }
            },
            {
                "data": 'event_source',  // Artifact Path
                "width": "10%",
                "render": function(data){
                    // parse event source as artifact path
                    if (data == null || data == ""){
                        return "";
                    }
                    else {
                        data = ellipsis_field_raw(sanitizeHTML(data), 30);
                        return data;
                    }
                }
            },
            {
                "data": 'assets',  // Internal IP
                "width": "8%",
                "render": function(data, type, row, meta){
                    if (data == null) {
                        return '';
                    }

                    // search/sort/export all need plain text, not the raw assets array or display HTML
                    if (type !== 'display') {
                        return extract_ips_from_assets(data, 'ip');
                    }

                    // parse internal IP data from assets
                    if(data.length == 0) {
                        return '';
                    }
                    else {
                        var asset_link = '';

                        // display each asset IP on a line, hyperlink to route back to Assets
                        data.forEach(function(asset){
                            var ips = "";
                            if(asset.ip == "" || asset.ip == null) {
                                asset_link += '';
                            }
                            else {
                                // only hyperlink if IP is a non-empty value

                                let de = (asset.ip).split(',');
                                for (let ip in de) {
                                    individual_ip = sanitizeHTML(de[ip]);
                                    ips += get_ip_from_data(individual_ip, 'badge badge-light ml-2');
                                }
                                share_link = "/case/assets" + case_param();
                                asset_link += '<a href="' + share_link + '">' + ips + '</a>' + '<br/>';
                            }

                        });
                        return asset_link + '';
                    }
                }
            },
            {
                "data": 'assets',  // External IP
                "width": "8%",
                "render": function(data, type, row, meta){
                    if (data == null) {
                        return '';
                    }

                    // search/sort/export all need plain text, not the raw assets array or display HTML
                    if (type !== 'display') {
                        return extract_ips_from_assets(data, 'ext_ip');
                    }

                    // parse external IP data from assets
                    if(data.length == 0) {
                        return '';
                    }
                    else {
                        var asset_link = '';

                        // display each asset IP on a line, hyperlink to route back to Assets
                        data.forEach(function(asset){
                            var ips = "";
                            if(asset.ext_ip == "" || asset.ext_ip == null) {
                                asset_link += '';
                            }
                            else {
                                // only hyperlink if IP is a non-empty value

                                let de = (asset.ext_ip).split(',');
                                for (let ip in de) {
                                    individual_ip = sanitizeHTML(de[ip]);
                                    ips += get_ip_from_data(individual_ip, 'badge badge-light ml-2');
                                }
                                share_link = "/case/assets" + case_param();
                                asset_link += '<a href="' + share_link + '">' + ips + '</a>' + '<br/>';
                            }

                        });
                        return asset_link;
                    }
                }
            },
            {
                "data": "category_name",  // Event Category
                "visible": false,
                "width": "9%",
                "render": function(data) {
                    return data;
                }
            },
            {
                "data": "event_tags",  // Tags
                "visible": false,
                "width": "8%",
                "render": function(data, type) {
                    if (type === 'display' && data != null  ) {
                        tags = "";
                        de = data.split(',');
                        for (tag in de) {
                          individual_tag = sanitizeHTML(de[tag]);
                          if (individual_tag == ""){
                            individual_tag = null;
                          }
                          else {
                            individual_tag = ellipsis_field_raw(individual_tag, 20);
                          }
                          tags += get_tag_from_data(individual_tag, 'badge badge-light ml-2');
                        }
                        return tags;
                    }
                    return data;
                }
            },
            {
                "data": 'user',  // Reported By
                "visible": false,
                "width": "8%",
                "render": function(data){
                    return sanitizeHTML(data);
                }
            },

        ],
        createdRow: function(row, data){
            // update row color based on user's selection
            $('td', row).css('background-color', data.event_color);
        },
        filter: true,
        info: true,
        ordering: true,
        processing: true,
        retrieve: true,
        pageLength: 100,
        lengthMenu: [[10, 25, 50, 100, 250, 500, 1000, -1], [10, 25, 50, 100, 250, 500, 1000, "All"]],
        // order: [[ 2, "asc" ]],
        buttons: [
        ],
        responsive: {
            details: {
                display: $.fn.dataTable.Responsive.display.childRow,
                renderer: $.fn.dataTable.Responsive.renderer.tableAll()
            }
        },
        orderCellsTop: true,
        initComplete: function () {
            tableFiltering(this.api(), 'timeline_tabular', []);
            $('div.dataTables_filter', this.api().table(). container()).attr('id', 'datatable_search_bar');
            this.api().search('').draw();
        },
        // add ability to select multiple rows
        select: {
            style: 'os'
        }
    });

    // Extend the global search bar to also match description, raw log, IOCs and UUID (none of which are
    // bound to a visible column). Returns true (row kept) whenever there's no active search term, so
    // sorting/paging/adding rows doesn't pay the extra scan cost - only an actual search does.
    $.fn.dataTable.ext.search.push(function (settings, searchData, index, rowData) {
        if (settings.nTable.id !== 'timeline_tabular' || !g_timeline_search_term) {
            return true;
        }

        if (searchData.join(' ').toLowerCase().indexOf(g_timeline_search_term) !== -1) {
            return true;
        }

        return !!(rowData._search_blob && rowData._search_blob.indexOf(g_timeline_search_term) !== -1);
    });

    enable_timeline_column_resize('#timeline_tabular', Table);

    $("#timeline_tabular").css("font-size", 12);

    Table.on( 'responsive-resize', function ( e, datatable, columns ) {
            hide_table_search_input( columns );
    });


    // change row status to 'selected'
    Table.on('click', 'tbody tr', function (e) {
        e.currentTarget.classList.toggle('selected');
    });

    // apply search - debounced so large raw-log content isn't rescanned on every keystroke
    var timeline_search_debounce = null;
    $('#datatable_search_bar').keyup(function(){
        var search_val = $(this).val();
        clearTimeout(timeline_search_debounce);
        timeline_search_debounce = setTimeout(function () {
            g_timeline_search_term = search_val.trim().toLowerCase();
            Table.draw();
        }, 250);
    })

    // prevent redirect to case #1 by default
    $('#datatable_search_bar').on("keypress", function(e){
        if (e.which == 13) {
            e.preventDefault();
        }
    })

    // utils buttons
    var buttons = new $.fn.dataTable.Buttons(Table, {
        buttons: [
           { "extend": 'csvHtml5', "text":'<i class="fas fa-cloud-download-alt"></i>',"className": 'btn btn-link text-white'
           , "titleAttr": 'Download as Excel', "exportOptions": { "columns": ':visible', 'orthogonal':  'export' } } ,
           { "extend": 'copyHtml5', "text":'<i class="fas fa-copy"></i>',"className": 'btn btn-link text-white'
           , "titleAttr": 'Copy', "exportOptions": { "columns": ':visible', 'orthogonal':  'export' } },
           { "extend": 'colvis', "text":'<i class="fas fa-eye-slash"></i>',"className": 'btn btn-link text-white'
           , "titleAttr": 'Toggle columns' }
       ]
       }).container().appendTo($('#tables_button'));

    get_or_filter_tm();

    // get all case assets here for excel export
    get_case_assets_from_external();

    // get all case iocs here for excel export
    get_case_iocs_from_external();

    // allow user to update timezone at any time
    select_timezone();

    setInterval(function() { check_update('timeline/state'); }, 3000);

    collab_case.on('case-obj-notif', function(data) {
        let js_data = JSON.parse(data);
        if (js_data.object_type === 'events') {
            handleCollabNotifications(js_data);
        }
    });

});

// Export functions for testing (only in Node.js/Jest environment)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        strip_markdown_images,
        is_timeline_compact_view,
        is_timeline_tree_view,
        escapeRegExp,
        getFilterFromLink,
        parse_filter,
        set_end_event_fields,
        get_selected_rows_event_ids,
        toggleSeeMore,
        refresh_event_image_preview,
        time_converter,
        end_time_converter,
        add_items_from_event,
        add_asset_from_event,
        add_ioc_from_event
    };
}
