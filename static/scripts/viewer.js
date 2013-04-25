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
    var zoom = 100;
    var mode = 'n';

    var url = function(numero, width) {
        if (width < 300)
            m = 'm';
        else
            m = mode;

        return '/static/documents/'+doc.parentid+'/' + doc.id.pad(6) +
              '_' + numero.pad(6) + '_' + m + '.jpg';
        //return '/static/documents/' + doc.slug + '/' + doc.id.pad(4) +
        //       '_' + numero.pad(4) + '_' + m + '.jpg';
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
            if ($('#page-' + i).attr('src') == '/static/images/white.png')
                $('#page-' + i).attr('src', url(i, 600 * zoom / 100));
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

    var change_mode = function(m) {
        mode = m;
        $('.page').each(function(i, page) {
            $(page).attr('src', '/static/images/white.png');
        });
        load_pages();
    };

    var zoom_draw = function(z) {
        if (z != zoom) {
            zoom = z;
            $('#zoom').val(zoom + '%');

            if (zoom >= 125 && mode == 'n')
                change_mode('b');
            else if (zoom < 125 && mode == 'b')
                change_mode('n');

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
        /*
        if (zoom < 100)
            var z = zoom + 10;
        else if (zoom < 475)
            var z = zoom + 25;
        else
            var z = 500;
        */
        var z = zoom + zoom/9;
        zoom_draw(z);
    };

    var zoom_out = function() {
        /*
        if (zoom <= 35)
            var z = 25;
        else if (zoom <= 100)
            var z = zoom - 10;
        else
            var z = zoom - 25;
        */
        var z = zoom - zoom/10;
        zoom_draw(z);
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
    });

    return {
        refresh: function() {
            set_height();
            load_pages();
        }
    };
};
