/* Copyright 2012, hast. All rights reserved.
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at
 * your option) any later version.
 */

var navbar = function() {
    var height = 130;
    var visible = false;
    var template = null;

    var toggle = function() {
        $('#navbar-bottom').slideToggle(100);
        if (visible) {
            $('#pullout').html('down');
            $('#content').animate({'padding-top': 70}, 100);
            visible = false;
        } else {
            $('#pullout').html('up');
            $('#content').animate({'padding-top': 90 + height}, 100);
            visible = true;
        }

        if (typeof viewer_instance != undefined)
            viewer_instance.refresh();
    };

    var refresh_padding = function() {
        height = $('#navbar-bottom').height() + 10;
        if (visible) {
            $('#content').css('padding-top', 90 + height);
            if (typeof viewer_instance != undefined)
                viewer_instance.refresh();
        } else
            $('#content').css('padding-top', 70);
    };

    var load = function(node, cat_id) {
        $.getJSON("/json/tree/category/" + cat_id, function(data) {
            $(node).after(template(data));
            $('.navbar-list[data-id=' + cat_id + '] .navbar-category').click(load_event);
            refresh_padding();
        });
    };

    var load_event = function(event) {
        var list = event.target.parentNode;

        for (var elem = list.nextSibling; elem; elem = next) {
            var next = elem.nextSibling;
            if (elem.tagName == "UL")
                $(elem).remove();
        }

        load(list, event.target.getAttribute("data-id"));
    };

    $(document).ready(function() {
        $('#navbar-top').click(toggle);
        $('#navbar-search').click(function() {return false;});
        $(window).resize(refresh_padding);
        template = Handlebars.compile(fragments["navbar-list"]);
        load($("#navbar-start"), 1);
    });
    
    return {
        is_down: function() {
            return visible;
        },

        get_height: function() {
            return height;
        }
    };
}();
