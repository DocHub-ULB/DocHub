/* Copyright 2012, hast. All rights reserved.
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at
 * your option) any later version.
 */

var nofications = function() {
    var read_notif = function(element) {
        id = element.attr('notif_id');
        $.ajax({
            url: id + "/ajax_read",
            }).done(function() {
                element.parent().remove()
        });
    };

    $(document).ready(function() {
        $('.read_notif').bind( "click", function() {
            read_notif($(this))
        });
    });
}();
