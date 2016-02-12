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

const COOKIE_NAME = "viewer-preferred-zoom";

var viewer = function(doc) {
    var current_page = 0;
    var current_thumb = 0;
    var current_hilight = -1;
    var zoom = 100;
    var mode = 600;

    var thumb_url = function(numero){
        return doc.pages[numero].url_120 + "#120"
    }

    var url = function(numero, mode) {
        if (mode == 600)
            return doc.pages[numero].url_600 + "#600"
        else
            return doc.pages[numero].url_900 + "#900"
    };

    var set_height = function() {};

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
        var sep = 60;

        $(document).scrollTop($('#page-' + num).offset().top - sep);
    }

    var load_pages = function() {
        var start_page = Math.max(0, current_page - 3);
        var end_page = Math.min(doc.len, current_page + 3);

        for (var i = start_page; i < end_page; ++i)
            if ($('#page-' + i).attr('src') == '/static/images/white.png')
                $('#page-' + i).attr('src', url(i, mode));
    };

    var load_thumbs = function() {
        var start_page = Math.max(0, current_thumb - $('#thumbs').height() /
                                         $('#thumb-1').height() - 2);
        var end_page = Math.min(doc.len, current_thumb + $('#thumbs').height()/
                                         $('#thumb-1').height() + 2);

        for (var i = Math.floor(start_page); i < end_page; ++i)
            if ($('#thumb-' + i).attr('src') === "/static/images/white.png")
                $('#thumb-' + i).attr('src', thumb_url(i));
    };

    var set_current_page = function() {
        var scroll = $(document).scrollTop();

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

    var change_mode = function(m) {
        mode = m;
        $('.page').each(function(i, page) {
            $(page).attr('src', '/static/images/white.png');
        });
        load_pages();
        console.log("mode change")
    };

    var zoom_draw = function(z) {
        console.log(z);
        if (z && z != zoom) {
            zoom = z;
            Cookies.set(COOKIE_NAME, zoom);
            $('#zoom').val(zoom + '%');

            if (zoom >= 125 && mode == 600)
                change_mode(900);
            else if (zoom < 125 && mode == 900)
                change_mode(600);

            $('.page').each(function(i, page) {
                if (zoom == 150) {
                    $(page).height(doc.pages[i].height_900);
                    $(page).width(900);
                } else {
                    $(page).height(doc.pages[i].height_600 * zoom / 100);
                    $(page).width(600 * zoom / 100);
                }
            });

            $('#top-page').width(600 * zoom / 100);
        }
    };

    var zoom_key = function(event) {
        if (event.keyCode == 13) {
            var raw = parseInt($('#zoom').val().replace('%', ''));
            if (!isNaN(raw))
                var z = Math.min(Math.max(25, raw), 500);
            else
                var z = 100;
            zoom_draw(z);
        }
    };

    var zoom_in = function() {
        if(zoom < 300){
            var z = zoom + zoom/9;
            zoom_draw(z);
        }
    };

    var zoom_out = function() {
        if(zoom > 37){
            var z = zoom - zoom/10;
            zoom_draw(z);
        }
    };

    $(document).ready(function() {
        set_height();
        $(window).resize(set_height);
        $(window).scroll(set_current_page);
        $('#thumbs').scroll(set_current_thumb);
        $('.thumb').click(click_thumb);
        $('#zoom').keypress(zoom_key);
        $('#zoom-in').click(zoom_in);
        $('#zoom-out').click(zoom_out);
        load_pages();
        load_thumbs();
        show_thumb_page(0);
        zoom_draw(parseFloat(Cookies.get(COOKIE_NAME)));
    });

    return {
        refresh: function() {
            set_height();
            load_pages();
        }
    };
};


window.viewer = viewer;
