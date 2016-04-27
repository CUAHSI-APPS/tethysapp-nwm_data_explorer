/*jslint
 browser:true, devel:true
 */

/**GLOBAL VARIABLE IMPORTS**/
var $,
    formatDropDown;

(function () {
    "use strict";

    /****************************************
     *******VARIABLES DECLARATIONS***********
     ****************************************/

    /**********General**********/
    var downloadPath,
        /**jQuery Handles**/
        $dropDowns,
        $fileInfoDiv,
        $downloadButton,
        $displayStatus,
        /**Functions**/
        addInitialEventListeners,
        buildArray,
        buildTable,
        clearFileInfo,
        encodeText,
        formatJsonData,
        getQueryType,
        dataQuery,
        isArray,
        isEven,
        processFileData,
        initializeJqueryVariables,
        formatDropDown,
        formatDropdownOptions;

    /*****************************************************
     ***********FUNCTION INITIALIZATION*******************
     *****************************************************/
    addInitialEventListeners = function () {

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
            dataQuery(getQueryType(), selectionPath);
            if (!($fileInfoDiv.is(':empty'))) {
                clearFileInfo();
            }
        });

        $dropDowns.on('select2:unselect', '.contents', function () {
            $('[aria-expanded=true]').parent().parent().remove();
            $(this).next().nextAll().remove();
            if (!($fileInfoDiv.is(':empty'))) {
                clearFileInfo();
            }
        });
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
        $downloadButton.addClass('hidden');
        $fileInfoDiv.resize();
    };

    encodeText = function (a) {
        return $("<div />").text(a).html()
    };

    formatJsonData = function (data) {
        var dataSize,
            dataUnitsSwitchKey,
            dataUnitsSwitch,
            dataUnits;

        //Format the fileSize to appropriate units (originally in bytes)
        dataSize = data.query_data.dataSize;
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
        data.query_data.dataSize = dataSize.toFixed(2).toString() + " " + dataUnits;

        //Format the date (originally in milliseconds)
        if (data.query_data.hasOwnProperty('createdAt')) {
            data.query_data.createdAt = new Date(data.query_data.createdAt).toUTCString();
        }
        if (data.query_data.hasOwnProperty('updatedAt')) {
            data.query_data.updatedAt = new Date(data.query_data.updatedAt).toUTCString();
        }
        if (data.query_data.hasOwnProperty('accessedAt')) {
            data.query_data.accessedAt = new Date(data.query_data.accessedAt).toUTCString();
        }

        //Build a table of the json data and place it in the file info html element
        $fileInfoDiv
            .html(buildTable(data.query_data))
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

    getQueryType = function () {
        if (window.location.pathname.indexOf('files_explorer') !== -1) {
            return 'filesystem';
        }
        return 'irods';
    };

    dataQuery = function (queryType, selectionPath) {
        downloadPath = '';

        $.ajax({
            type: 'GET',
            url: 'get-folder-contents',
            dataType: 'json',
            data: {
                'selection_path': selectionPath,
                'query_type': queryType
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(jqXHR + '\n' + textStatus + '\n' + errorThrown);
            },
            success: function (data) {
                var contents;

                if (!data.hasOwnProperty('success')) {
                    if (data.hasOwnProperty('error')) {
                        alert(data.error);
                    }
                } else {
                    contents = data.query_data.contents;
                    if (contents) { //check to see if the files or folders attributes have data
                        $dropDowns.append(contents); //create the new dropdown box with its file/folder options
                        formatDropDown(); //format the dropdown with file or folder pictures accordingly
                    } else { //if there wasn't any data in the files or folders attributes, the selection was a file
                        processFileData(data, selectionPath, queryType);
                    }
                }
            }
        });
    };

    isArray = function (a) {
        return "[object Array]" === Object.prototype.toString.call(a);
    };
    
    isEven = function (a) {
        return 0 === a % 2;
    };

    processFileData = function (data, selectionPath, fileSource) {
        if (fileSource === 'filesystem') {
            downloadPath = '/static/nwm_data_explorer/temp_files/' + data.query_data.dataName;
        } else {
            downloadPath = 'http://shawncrawley:shawncrawley@nfie.hydroshare.org:8080/irods-rest/rest/fileContents' +
                selectionPath.slice(0, selectionPath.indexOf('?'));
        }

        try {
            $downloadButton.off('click');
        } catch (e) {
            console.log(e);
        }

        $downloadButton.on('click', function () { //create a new click event to initialize the downloadPath variable
            window.open(downloadPath);
        });
        //show the appropriate buttons
        $downloadButton.removeClass('hidden');

        formatJsonData(data);
    };

    initializeJqueryVariables = function () {
        $dropDowns = $('#drop-down');
        $fileInfoDiv = $('#file-info');
        $downloadButton = $('#download-button');
        $displayStatus = $('#display-status');
    };

    formatDropDown = function () {
        $('.contents:last-child').select2({
            placeholder: "Select a file/folder",
            allowClear: true,
            minimumResultsForSearch: 7,
            templateResult: formatDropdownOptions,
            templateSelection: formatDropdownOptions
        });
    };

    formatDropdownOptions = function (state) {
        if (!state.id) {
            return state.text;
        }
        if ($(state.element).attr('data-path').indexOf("?folder") !== -1) {
            return $('<span><img src="/static/nfie_irods_explorer/images/dir_icon.svg" class="drop-down-icon" /> ' + state.text + '</span>');
        }
        return $('<span><img src="/static/nfie_irods_explorer/images/file_icon.svg" class="drop-down-icon" /> ' + state.text + '</span>');
    };


    /*************************
     RUN ONCE DOCUMENT IS READY
     *************************/
    $(function () {
        var $title = $('#title'),
            $subtitle = $('#subtitle');
        initializeJqueryVariables();
        addInitialEventListeners();
        if (window.location.pathname.indexOf('files_explorer') !== -1) {
            $title.text('Filesystem Explorer');
            $subtitle.text('Browse the National Water Model data stored on the server');
            dataQuery('filesystem', '/projects/water/nwm/nwm_sample?folder');
        } else {
            $title.text('iRODS Explorer');
            $subtitle.text('Browse the National Water Model data stored in iRODS');
            dataQuery('irods', '/nfiehydroZone/home/public/nwm_sample?folder');
        }
    });
}());