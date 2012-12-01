/* Copyright 2012, hast. All rights reserved.
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at
 * your option) any later version.
 */

var viewer = function(doc) {
    var current_page = 0;

    var url = function(numero) {
        return '/static/documents/' + doc.slug + '/0001_000' + numero + '_n.jpg';
    };

    var set_height = function() {
        if (navbar.is_down())
            $('#thumbs').height($(window).height() - 165 - navbar.get_height());
        else
            $('#thumbs').height($(window).height() - 145);
    };

    var load = function() {
        var start_page = Math.max(0, current_page - 2);
        var end_page = Math.min(doc.len - 1, current_page + 2);
        console.log("load from " + doc.len + " to " + end_page);
        for (var i = start_page; i < end_page; ++i) {
            console.log("load : " + url(i));
            $('#page-' + i).attr('src', url(i));
        }
    };

    console.log(doc);
    console.log(doc.len);
    $(document).ready(function() {
        set_height();
        load();
        $(window).resize(set_height);
    });

    return {
        refresh: function() {
            set_height();
            load();
        }
    };
};
