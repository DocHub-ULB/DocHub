/* Copyright 2012, hast. All rights reserved.
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at
 * your option) any later version.
 */

var navbar = function() {
    var state, template = null, height = 130;

    var toggle = function() {
        $('#navbar-bottom').slideToggle(100);
        if (state.visible) {
            $('#content').animate({'padding-top': 70}, 100);
            $('#pull').removeClass("courses-focus");
            $('#pull').addClass("courses");
            state.visible = false;
            $.cookies.set('navbar', state);
        } else {
            $('#content').animate({'padding-top': 84 + height}, 100);
            $('#pull').removeClass("courses");
            $('#pull').addClass("courses-focus");
            state.visible = true;
            $.cookies.set('navbar', state);
        }

        if (typeof viewer_instance !== "undefined")
            viewer_instance.refresh();
    };

    var refresh_padding = function() {
        height = $('#navbar-bottom').height() + 10;
        if (state.visible) {
            $('#pull').removeClass("courses");
            $('#pull').addClass("courses-focus");
            $('#content').css('padding-top', 84 + height);
            if (typeof viewer_instance !== "undefined")
                viewer_instance.refresh();
        } else
            $('#content').css('padding-top', 70);
    };

    var draw = function() {
        $('#navbar-bottom').html(template(state));
        $('.navbar-category').click(load_event);
        refresh_padding();
    };

    var load = function(cat_id) {
        $.getJSON("/json/node/" + cat_id, function(data) {
            state.loaded.push(data);
            console.log(state);
            $.cookies.set('navbar', state);
            draw();
        });
    };

    var load_event = function(event) {
        var list = event.target.parentNode;

        for (var i = 0; i < state.loaded.length; ++i)
            if (state.loaded[i].id == list.getAttribute("data-id"))
                break;

        state.loaded.splice(i + 1, state.loaded.length - i - 1);
        $.cookies.set('navbar', state);
        var nodeid = event.target.getAttribute("data-id");
        if (event.target.getAttribute('data-type') == 'Course')
          window.location = '/zoidberg/course/v/'+nodeid;
        else
          load(nodeid);
    };

    var set_state = function() {
        var source = $.cookies.get('navbar');
        if (source == null) {
            // initial state
            state = {
                loaded: [],
                visible: false,
            };
            load(1);
        } else {
            // read from cookie
            state = source;
            draw();
            if (state.visible == true) {
                $('#navbar-bottom').css('display', 'block');
                $('#pullout').html('up');
                $('#content').css('padding-top', 84 + height);
            }
        }
    };

    $(document).ready(function() {
        $('#pull').click(toggle);
        $('#navbar-search').click(function() {return false;});
        $(window).resize(refresh_padding);
        template = Handlebars.compile(fragments["navbar-list"]);
        set_state();
    });

    return {
        is_down: function() {
            return state.visible;
        },

        get_height: function() {
            return height;
        }
    };
}();
