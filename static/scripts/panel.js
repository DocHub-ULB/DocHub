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
            var button = e.target;
            var panel = $("#" + $(button).attr("data-target"));
            var action = $(button).attr("data-action");
            
            if (panel != undefined) {
                if (action == "show") {
                    $(button).removeClass("border-bottom");
                    $(button).attr("data-action", "mask");
                    $(panel).slideDown(100);
                    console.log($(panel).next().children("thead > tr > th"));
                    $(panel).next().removeClass("rounded");
                    $(panel).next().removeClass("rounded");
                } else {
                    $(button).addClass("border-bottom");
                    $(button).attr("data-action", "show");
                    $(panel).slideUp(100);
                    $(panel).next().addClass("rounded");
                    $(panel).next().addClass("rounded");
                }
            }
        });
    });

    return {};
}();
