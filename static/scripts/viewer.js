/* Copyright 2012, hast. All rights reserved.
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at
 * your option) any later version.
 */

var viewer = function(document) {
    
    var set_height = function() {
        if (navbar.is_down())
            $('#thumbs').height($(window).height() - 165 - navbar.get_height());
        else
            $('#thumbs').height($(window).height() - 145);
    };

    $(document).ready(function() {
        set_height();
        $(window).resize(set_height);
    });

    return {
        refresh: function() {
            set_height();
        }
    };
};
