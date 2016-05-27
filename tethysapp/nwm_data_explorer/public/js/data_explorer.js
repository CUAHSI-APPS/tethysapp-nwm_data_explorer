/*jslint
 browser:true, devel:true
 */

/**GLOBAL VARIABLE IMPORTS**/
var $,
    formatDropDown,
    filtersList,
    lastQuerySelectionPath,
    currentDirPath,
    fsPath = '/projects/water/nwm/nwm_sample?folder',
    // fsPath = '/projects/water/nwm/data?folder',
    irodsPath = '/nwmZone/home/nwm/data?folder';

(function () {
    'use strict';
    /****************************************
     *******VARIABLES DECLARATIONS***********
     ****************************************/

    /**jQuery Handles**/
    var $dropDowns,
        $fileInfoDiv,
        $btnDownload,
        $btnDownloadAll,
        $downloadAll,
        /**Functions**/
        addInitialEventListeners,
        alertUserOfError,
        buildArray,
        buildTable,
        clearFileInfo,
        createSelect2Objects,
        encodeText,
        formatFileMetadata,
        modifyDownloadBtn,
        processDataQueryResponse,
        updateFiltersList,
        getQueryType,
        prepareDownloadAllButton,
        queryData,
        isArray,
        isEven,
        addFileMetadataToUI,
        initializeJqueryVariables,
        formatDropDown,
        formatDropdownOptions;

    /*****************************************************
     ***********FUNCTION INITIALIZATION*******************
     *****************************************************/
    addInitialEventListeners = function () {

        $btnDownloadAll.on('click', function () {
            var downloadUrl;
            $('.contents').last().find('option').each(function (i, obj) {
                if (i > 0) {
                    var fileName = $(obj).attr('data-filename');
                    fileName = fileName.replace('?file', '');
                    downloadUrl = 'download-file?selection_path=' + encodeURIComponent(currentDirPath + '/' + fileName);
                    window.open(downloadUrl);
                }
            });
        });

        $('.slct-filter').on('select2:select', function (e) {
            var selections = $(this).val();
            var allIndex = selections.indexOf('all');
            if (e.params.data.id === 'all' || ($(this).attr('id') === 'slct-types' && selections.length === 4 && allIndex === -1) || ($(this).attr('id') === 'slct-hours-init' && selections.length === 24 && allIndex === -1)) {
                $(this).val(['all']).trigger("change");
            } else if (selections.length > 1 && allIndex !== -1) {
                selections.splice(allIndex, 1);
                $(this).val(selections).trigger("change");
            }
        });

        $('#btn-filter-options').on('click', function () {
            if ($(this).hasClass('contracted')) {
                $(this)
                    .removeClass('contracted')
                    .addClass('expanded');
                $('#filter-options').slideDown();
            } else {
                $(this)
                    .removeClass('expanded')
                    .addClass('contracted');
                $('#filter-options').slideUp();
            }
        });

        $('#btn-apply-filters').on('click', function () {
            var selectedTypes = $('#slct-types').val();
            var selectedHours = $('#slct-hours-init').val();
            var selectedMembers = $('#slct-longrange-member').val();
            if (selectedTypes === null || selectedHours === null || selectedMembers === null) {
                alert('A filter input field was left blank. Filters not applied');
            } else {
                updateFiltersList();
                $('.contents').last().nextAll().remove();
                clearFileInfo();
                queryData(getQueryType(), lastQuerySelectionPath);
            }
        });

        window.addEventListener('beforeunload', function () {
            $.ajax({
                url: 'delete-temp-files',
                async: false
            });
        });

        $dropDowns.on('select2:select', '.contents', function (e) {
            var numElements,
                selectionPath;

            numElements = $(this).nextAll().length;
            if (numElements !== 1) {
                $(this).next().nextAll().remove();
            }
            selectionPath = $(e.params.data.element).attr('data-path');
            lastQuerySelectionPath = selectionPath;
            queryData(getQueryType(), selectionPath);
            clearFileInfo();
        });

        $dropDowns.on('select2:unselect', '.contents', function () {
            $('[aria-expanded=true]').parent().parent().remove();
            $(this).next().nextAll().remove();
            clearFileInfo();
        });
    };

    alertUserOfError = function () {
        alert('Sorry! An error ocurred.');
    };

    buildArray = function (a) {
        var e = document.createElement("table"),
            d, b, c = !1,
            n = !1,
            l = {},
            g = -1,
            m = 0,
            k,
            td_class;
        k = "";
        if (0 === a.length) return "<div></div>";
        d = e.insertRow(-1);
        for (var f = 0; f < a.length; f++)
            if ("object" !== typeof a[f] || isArray(a[f])) n ||
            (g += 1, n = !0, b = d.insertCell(g), l.empty = g, b.innerHTML = "<div class='td_head'>&nbsp;</div>");
            else
                for (var h in a[f]) k = "-" + h, k in l || (c = !0, g += 1, b = d.insertCell(g), l[k] = g, b.innerHTML = "<div class='td_head'>" + encodeText(h) + "</div>");
        c || e.deleteRow(0);
        m = g + 1;
        for (f = 0; f < a.length; f++)
            if (d = e.insertRow(-1), td_class = isEven(f) ? "td_row" : "td_row_odd", "object" !== typeof a[f] || isArray(a[f]))
                if ("object" === typeof a[f] && isArray(a[f]))
                    for (g = l.empty, c = 0; c < m; c++) b = d.insertCell(c), b.className = td_class, k = c === g ? '<table style="width:100%">' + $(buildArray(a[f]), !1).html() + "</table>" : " ", b.innerHTML = "<div class='" + td_class + "'>" + encodeText(k) + "</div>";
                else
                    for (g = l.empty, c = 0; c < m; c++) b = d.insertCell(c), k = c === g ? a[f] : " ", b.className = td_class, b.innerHTML = "<div class='" + td_class + "'>" + encodeText(k) + "</div>";
            else {
                for (c = 0; c < m; c++) b =
                    d.insertCell(c), b.className = td_class, b.innerHTML = "<div class='" + td_class + "'>&nbsp;</div>";
                for (h in a[f]) c = a[f], k = "-" + h, g = l[k], b = d.cells[g], b.className = td_class, "object" !== typeof c[h] || isArray(c[h]) ? "object" === typeof c[h] && isArray(c[h]) ? b.innerHTML = '<table style="width:100%">' + $(buildArray(c[h]), !1).html() + "</table>" : b.innerHTML = "<div class='" + td_class + "'>" + encodeText(c[h]) + "</div>" : b.innerHTML = '<table style="width:100%">' + $(buildTable(c[h]), !1).html() + "</table>"
            }
        return e
    };

    buildTable = function (a) {
        var e = document.createElement("table"),
            d, b;
        if (isArray(a)) return buildArray(a);
        for (var c in a) {
            "object" !== typeof a[c] || isArray(a[c]) ? "object" === typeof a[c] && isArray(a[c]) ?
                (d = e.insertRow(-1), b = d.insertCell(-1), b.colSpan = 2, b.innerHTML = '<div class="td_head">' +
                    encodeText(c) + '</div><table style="width:100%">' + $(buildArray(a[c]), !1).html() + "</table>") :
                (d = e.insertRow(-1), b = d.insertCell(-1), b.innerHTML = "<div class='td_head'>" + encodeText(c) +
                    "</div>", d = d.insertCell(-1), d.innerHTML = "<div class='td_row'>" +
                    encodeText(a[c]) + "</div>") : (d = e.insertRow(-1), b = d.insertCell(-1), b.colSpan = 2, b.innerHTML = '<div class="td_head">' +
                encodeText(c) + '</div><table style="width:100%">' + $(buildTable(a[c]), !1).html() + "</table>");
        }
        return e
    };

    clearFileInfo = function () {
        $fileInfoDiv.empty();
        $btnDownload.addClass('hidden');
        $downloadAll.addClass('hidden');
        $fileInfoDiv.resize();
    };

    createSelect2Objects = function () {
        $('.slct-filter').select2({
            width: '100%',
            placeholder: "Please make a selection",
            allowClear: true,
            minimumResultsForSearch: Infinity
        });
    };

    encodeText = function (a) {
        return $("<div />").text(a).html()
    };

    formatFileMetadata = function (data) {
        var dataSize,
            dataUnitsSwitchKey,
            dataUnitsSwitch,
            dataUnits;

        //Format the fileSize to appropriate units (originally in bytes)
        dataSize = data.dataSize;
        dataUnitsSwitchKey = 0;
        while (dataSize > 999) {
            dataSize /= 1000;
            dataUnitsSwitchKey += 1;
        }
        dataUnitsSwitch = function (dataUnitsSwitchKey) {
            var options = {
                0: 'bytes',
                1: 'kB',
                2: 'MB',
                3: 'GB',
                4: 'TB',
                5: 'PB'
            };
            return options[dataUnitsSwitchKey];
        };
        dataUnits = dataUnitsSwitch(dataUnitsSwitchKey);
        data.dataSize = dataSize.toFixed(2).toString() + " " + dataUnits;

        //Format the date (originally in milliseconds)
        if (data.hasOwnProperty('createdAt')) {
            data.createdAt = new Date(data.createdAt).toUTCString();
        }
        if (data.hasOwnProperty('updatedAt')) {
            data.updatedAt = new Date(data.updatedAt).toUTCString();
        }
        if (data.hasOwnProperty('accessedAt')) {
            data.accessedAt = new Date(data.accessedAt).toUTCString();
        }

        return data;
    };

    getQueryType = function () {
        if (window.location.pathname.indexOf('files_explorer') !== -1) {
            return 'filesystem';
        }
        return 'irods';
    };

    // prepareDownloadAllButton = function () {
    //     var selectionFiles = [];
    //     var downloadUrl;
    //
    //     $('.contents').last().find('option').each(function (i, obj) {
    //         if (i > 0) {
    //             var fileName = $(obj).attr('data-filename');
    //             fileName = fileName.replace('?file', '');
    //             selectionFiles.push(fileName);
    //         }
    //     });
    //     downloadUrl = 'download-files?selection_dir=' + encodeURIComponent(currentDirPath) + '&files=' + encodeURIComponent(selectionFiles.join(','));
    //     $btnDownloadAll
    //         .attr('href', downloadUrl)
    //         .removeClass('hidden');
    // };

    queryData = function (queryType, selectionPath) {
        $.ajax({
            type: 'GET',
            url: 'get-folder-contents',
            dataType: 'json',
            data: {
                'selection_path': selectionPath,
                'query_type': queryType,
                'filters_list': filtersList.length === 0 ? undefined : filtersList.join(',')
            },
            error: alertUserOfError,
            success: function (response) {
                processDataQueryResponse(response, selectionPath, queryType);
            }
        });
    };

    isArray = function (a) {
        return "[object Array]" === Object.prototype.toString.call(a);
    };

    isEven = function (a) {
        return 0 === a % 2;
    };

    processDataQueryResponse = function (response, selectionPath, queryType) {
        var contents;

        if (!response.hasOwnProperty('success')) {
            if (response.hasOwnProperty('error')) {
                alertUserOfError(response.error);
            }
        } else {
            currentDirPath = selectionPath.replace('?folder', '');
            contents = response.query_data.contents;
            if (contents) {
                // The selection was a folder/directory
                $dropDowns.append(contents);
                formatDropDown();
                if (!response.query_data.contains_folder && filtersList.length > 0 && $('.contents').last().find('option').length > 1) {
                    $downloadAll.removeClass('hidden');
                    // prepareDownloadAllButton();
                }
            } else {
                // The selection was a file
                addFileMetadataToUI(response.query_data);
                modifyDownloadBtn(selectionPath, queryType);
            }
        }
    };

    updateFiltersList = function (initial) {
        var $selectHours = $('#slct-hours-init');
        var $selectTypes = $('#slct-types');
        var $selectMembers = $('#slct-longrange-member');

        var addValsToFilterList = function ($slct) {
            var selectedValsList = $slct.val();
            if (selectedValsList.indexOf('all') === -1) {
                selectedValsList.forEach(function (val) {
                    filtersList.push(val);
                });
            }
        };

        filtersList = [];

        if (!initial) {
            addValsToFilterList($selectTypes);
            addValsToFilterList($selectHours);
            addValsToFilterList($selectMembers);
        }
    };

    addFileMetadataToUI = function (data) {
        $fileInfoDiv
            .html(buildTable(formatFileMetadata(data)))
            .prepend('<h3>File metadata:</h3>')
            .resize();

        //Format the table data headers with spaces and capitalization
        $('.td_head').each(function () {
            var i,
                thisText,
                loopTotal,
                newText;

            thisText = $(this).text();
            loopTotal = thisText.length;
            for (i = 0; i < loopTotal; i++) {
                if (/[^A-z]/.test(thisText.charAt(0))) {
                    thisText = thisText.slice(1);
                }
                if (/[A-Z]/.test(thisText.charAt(i))) {
                    thisText = thisText.slice(0, i) + " " + thisText.slice(i);
                    i++;
                }
            }
            newText = thisText.charAt(0).toUpperCase() + thisText.slice(1) + ":";
            $(this).text(newText);
        });

        //remove any attributes that are empty
        $('.td_row').each(function () {
            if (!($(this).html())) {
                $(this).parent().parent().remove();
            }
        });
    };

    modifyDownloadBtn = function (selectionPath, fileSource) {
        var downloadUrl;

        if (fileSource === 'filesystem') {
            downloadUrl = 'download-file?selection_path=' + encodeURIComponent(selectionPath);
        } else {
            downloadUrl = 'http://nwm-reader:nwmreader@nfie.hydroshare.org:8080/irods-rest/rest/fileContents' +
                selectionPath.slice(0, selectionPath.indexOf('?'));
        }

        $btnDownload.attr({'href': downloadUrl})
            .removeClass('hidden');
    };

    initializeJqueryVariables = function () {
        $dropDowns = $('#drop-down');
        $fileInfoDiv = $('#file-info');
        $btnDownload = $('#btn-download-one');
        $btnDownloadAll = $('#btn-download-all');
        $downloadAll = $('#download-all');
    };

    formatDropDown = function () {
        $('.contents:last-child').select2({
            placeholder: "Select a file/folder",
            allowClear: true,
            minimumResultsForSearch: Infinity,
            templateResult: formatDropdownOptions,
            templateSelection: formatDropdownOptions
        });
    };

    formatDropdownOptions = function (state) {
        if (!state.id) {
            return state.text;
        }
        if ($(state.element).attr('data-path').indexOf('?folder') !== -1) {
            return $('<span><img src="/static/nfie_irods_explorer/images/dir_icon.svg" class="drop-down-icon" /> ' + state.text + '</span>');
        }
        return $('<span><img src="/static/nfie_irods_explorer/images/file_icon.svg" class="drop-down-icon" /> ' + state.text + '</span>');
    };


    /*************************
     RUN ONCE DOCUMENT IS READY
     *************************/
    $(function () {
        var $title = $('#title'),
            $subtitle = $('#subtitle'),
            $link;

        initializeJqueryVariables();
        addInitialEventListeners();
        updateFiltersList(true);
        if (window.location.pathname.indexOf('files_explorer') !== -1) {
            $title.text('Filesystem Explorer');
            $subtitle.text('Browse the National Water Model data stored on the server');
            queryData('filesystem', fsPath);
            lastQuerySelectionPath = fsPath;
            $link = $('#link-filesystem');
        } else {
            $title.text('iRODS Explorer');
            $subtitle.text('Browse the National Water Model data stored in iRODS');
            queryData('irods', irodsPath);
            lastQuerySelectionPath = irodsPath;
            $link = $('#link-irods');
        }
        $link.addClass('active');
        createSelect2Objects();
    });
}());