/* Copyright 2012, hast. All rights reserved.
 *
 * This program is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or (at
 * your option) any later version.
 */

var panel_master = function() {
    $(document).ready(function() {
        $('.panel-button').click(function(e) {
            $('#upload').slideDown();
        });
    });

    return {};
}();
