/* Copyright 2012, hast. All rights reserved.
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at
 * your option) any later version.
 */

Number.prototype.pad = function(l) {
    var n = Math.abs(this);
    var zeros = Math.max(0, l - Math.floor(n).toString().length );
    var padding = Math.pow(10, zeros).toString().substr(1);
    return padding + n;
}

var viewer = function(doc) {
    var current_page = 0;
    var current_thumb = 0;
    var current_hilight = -1;

    var url = function(numero, width) {
        var l = 'n';
        if (width < 300)
            l = 'm';
        else if (width > 750)
            l = 'b';

        return '/static/documents/' + doc.slug + '/' + doc.id.pad(4) + 
               '_' + numero.pad(4) + '_' + l + '.jpg';
    };

    var set_height = function() {
        if (navbar.is_down())
            $('#thumbs').height($(window).height() - 120 - navbar.get_height());
        else
            $('#thumbs').height($(window).height() - 106);
    };

    var set_current_hilight = function(thumb) {
        if (current_hilight != thumb) {
            $('#thumb-' + current_hilight).removeClass('hilight');
            $('#thumb-' + thumb).addClass('hilight');
            current_hilight = thumb;
        }
    };

    var show_thumb_page = function(page) {
        if (page == 0)
            var scroll = 0;
        else
            var scroll = 10;

        for (var i = 0; page && i < page && i < doc.len; ++i)
            scroll += ($('#thumb-' + i).height() + 34);
        $('#thumbs').scrollTop(scroll);
        set_current_hilight(i);
    };

    var scroll_to_page = function(num) {
        if (navbar.is_down())
            var sep = 75 + navbar.get_height();
        else
            var sep = 60;

        $(document).scrollTop($('#page-' + num).offset().top - sep);
    }

    var load_pages = function() {
        var start_page = Math.max(0, current_page - 2);
        var end_page = Math.min(doc.len, current_page + 2);

        for (var i = start_page; i < end_page; ++i)
            if ($('#page-' + i).attr('src') === "/static/images/white.png")
                $('#page-' + i).attr('src', url(i, 600));
    };

    var load_thumbs = function() {
        var start_page = Math.max(0, current_thumb - $('#thumbs').height() /
                                         $('#thumb-1').height() - 2);
        var end_page = Math.min(doc.len, current_thumb + $('#thumbs').height()/
                                         $('#thumb-1').height() + 2);

        for (var i = Math.floor(start_page); i < end_page; ++i)
            if ($('#thumb-' + i).attr('src') === "/static/images/white.png")
                $('#thumb-' + i).attr('src', url(i, 120));
    };

    var set_current_page = function() {
        var scroll = $(document).scrollTop();
        if (navbar.is_down())
            scroll -= 94 - navbar.get_height();
        else
            scroll -= 90;
        for (var i = 0; i < doc.len && scroll > 0; ++i)
            scroll -= ($('#page-' + i).height() + 12);
        if (current_page != Math.max(0, i - 1)) {
            current_page = Math.max(0, i - 1);
            show_thumb_page(current_page);
            load_pages();
        }
    };

    var set_current_thumb = function() {
        var scroll = $('#thumbs').scrollTop();
        for (var i = 0; i < doc.len && scroll > 0; ++i)
            scroll -= ($('#thumb-' + i).height() + 34);
        if (current_thumb != Math.max(0, i - 1)) {
            current_thumb = Math.max(0, i - 1);
            load_thumbs();
        }
    };

    var click_thumb = function(event) {
        thumb = $(event.target).attr('data-num');
        show_thumb_page(thumb);
        scroll_to_page(thumb);
    };

    $(document).ready(function() {
        set_height();
        $(window).resize(set_height);
        $(window).scroll(set_current_page);
        $('#thumbs').scroll(set_current_thumb);
        $('.thumb').click(click_thumb);
        load_pages();
        load_thumbs();
    });

    return {
        refresh: function() {
            set_height();
            load_pages();
        }
    };
};
