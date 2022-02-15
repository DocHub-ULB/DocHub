// TODO: move this to stimulus

/**
 * Empties the categories given in arguments (By id)
 *
 * Used when clicking in the upper tree to hide the lower branches that become irrelevant
 */
function emptySubCat(categories, frame_value, frame_key){
    // Clean the corresponding category (fac/programs/blocs)
    var url = new URL(window.location);
    url.searchParams.set(frame_key, frame_value);

    for(var i=0; i<categories.length; i++){
        $('#' + categories[i]).attr('src', $("#" + categories[i] + "-finder-col").attr("empty-url"))
        url.searchParams.set(categories[i], '');
        console.log("removing " + categories[i]);
    }

    history.pushState(history.state, history.title, url);
}

/**
 * Follows or unfollow the course
 * FIXME: Could use some turbo but couldn't make it work :/
 * Adds a loading gif to show people an action is being executed
 * @param {*} div_id the id of the div in which to place the spinner gif
 */
function follow(course_slug){
    spinnerUrl = $("#courses-finder-col").attr("spinner-url");
    $("#follow-" + course_slug).html("<img src='" + spinnerUrl + "' style='height: 1.2em' alt='loading' />");
    if($("#" + course_slug).attr("following") == 1){
        var url = $("#" + course_slug).attr("leave-course-url");
    } else {
        var url = $("#" + course_slug).attr("join-course-url");
    }

    $.get(
        url
    ).done((data) => {
        if(data.status == "success"){
            $("#" + course_slug).attr("following", (Number($("#" + course_slug).attr("following")) + 1) % 2);
            if($("#" + course_slug).attr("following") == 1){
                $("#follow-" + course_slug).html('<i class="fas fa-minus-circle" style="color: #F34040"></i>');
                $("#follow-" + course_slug).attr("title", "Leave the course");
            } else {
                $("#follow-" + course_slug).html('<i class="fas fa-plus-circle" style="color: #43AC6A"></i>');
                $("#follow-" + course_slug).attr("title", "Join the course");
            }
        } else {
            console.log(data);
        }
    })
}

/**
 * Toggles a program type modal
 * @param {*} modal The id of the modal to toggle
 *
 * This function contains a lot of so called "moldavian shenanigance". The original modal is clone somewhere the user can't see,
 * It is then opened to its max-content height, and the height is saved in a variable. The newly found height is then assigned
 * to the original modal, action that triggers the css animation. Doing it any other way prevents the animation from working
 * ¯\_(ツ)_/¯
 */
function toggleModal(modal){
    if($("#" + modal).css("maxHeight") == "0px"){
        // This is some kind of moldave trick to make a beautiful animation 👀

        // Clone the original to avoid playing with it (It breaks css animation)
        var clone = $("#" + modal).clone();
        clone.attr("id", modal + "-clone");
        clone.appendTo("#" + modal);
        clone.css("visibility", "hidden");
        clone.css("position", "absolute");
        clone.css("width", $("#" + modal).width());
        clone.css("maxHeight", "max-content");
        var size = clone.outerHeight();
        clone.remove();
        var _0xf09d=['\u2800\u2800\u2800\x0a\u2800\u2800\u2800\u2800\u2800\u2800','\u2800\u2800\u2846\u2876\u2800\u2800\u2880\u285c\u2801\u2880','\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u2800\u2800\u2800\u2800','\u28e4\u2834\u281b\u2801\u2800\u2800\u2800\u2800\u2800\u2800','\u2880\u28c0\u28e4\u28f6\u287e\u280b\u2800\u2800\u2800\u2800','\u280b\u2801\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800','\u286b\u281e\u2801\u28c0\u28e4\u28e4\u28e4\u28e4\u28e4\u28e4','\u2846\u28b0\u2806\u2800\u280b\u28e0\u2814\u2809\u2801\u28c0','\x36\x32\x39\x33\x38\x43\x76\x41\x6e\x48\x63','\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u28a0\u2803\u2800','\x32\x32\x38\x38\x36\x37\x66\x68\x68\x55\x76\x6b','\u2800\u28a0\u280a\u2800\u2800\u2800\u28f8\u28ff\u28ff\u28f7','\u2800\u2800\u2800\u2830\u2840\u2800\u2800\u2818\u2800\u285e','\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800','\u285c\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800','\u280a\u2801\u2800\u2881\u2874\u281a\u2809\u28c9\u28c0\u2840','\u2800\u2800\u2800\u2800\u28e0\u2874\u2800\u2800\u2800\u2800','\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2880\u28c0','\u280a\u2800\u28e0\u28ee\u28ec\u28ff\u28ff\u28ff\u28ff\u28ff','\u2800\u2800\x0a\u2800\u2800\u2800\u2800\u2800\u2800\u2800','\u2860\u2804\u2812\u2802\u2800\u2800\u2800\u2800\u2800\u2800','\u2800\u2800\u2800\u2800\u2800\x0a\u2800\u2800\u2800\u2800','\u2880\u2860\u2832\u2803\u2880\u28e4\u2800\u2800\u2800\u2832','\u2820\u288e\u2881\u2860\u2814\u2802\u2801\u2800\u2800\u2800','\u2808\u2801\u2800\u2800\u2800\u2800\u2800\u2800\u28b8\u28ff','\u2800\u2800\u2800\u2800\u2800\u2811\u2884\u2840\u2800\u2800','\u2800\u2800\u2800\u2800\x0a\u2800\u2800\u2800\u2800\u2800','\u2809\u2809\u2882\u2818\u28bf\u28e6\u2847\u2809\u2813\u28b6','\u2844\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800','\u2800\u2815\u2812\u2809\u28c9\u2852\u2844\u2800\u2800\u2800','\x34\x34\x31\x36\x35\x34\x73\x7a\x4b\x52\x43\x59','\u2800\u2800\u2800\u2800\u28a1\u2826\u282d\u2847\u2800\u2860','\u28a0\u2846\u2800\u2800\u2800\u285c\u2801\u28e0\u2814\u280b','\x0a\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2880','\u2800\u2800\u2800\u2880\u2824\u280a\u2801\u2800\u2880\u2840','\u2800\x0a\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2880','\u2801\u2800\u2809\u2887\u2800\u28ff\u28c4\u2800\u2808\u2846','\x39\x36\x31\x38\x33\x61\x6f\x5a\x79\x48\x4c','\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\x0a','\u28b0\u2801\u2870\u28a4\u28c0\u28c0\u2844\u28a0\u281e\u2847','\x35\x30\x33\x6a\x4b\x42\x6c\x65\x7a','\u28c0\u28b8\u2800\u2800\u2800\u2800\u2808\u2886\u2800\u2800','\x6c\x6f\x67','\x0a\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800','\x34\x30\x39\x36\x32\x38\x6d\x4d\x42\x42\x41\x56','\u2800\u2800\u2800\u2800\u2800\u2838\u28c0\u28e1\u280e\u2800','\u2800\u2800\u2800\u2800\u2800\u2800\u2800\x0a\u2800\u2800','\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u2844\u2800\u2800','\u280f\u2809\u2812\u2884\u2840\u2800\u2800\u2800\u2800\u2800','\u2800\u2880\u2824\u280a\u2801\u2880\u2860\u2814\u280a\u2801','\u2854\u2801\u28e4\u2800\u2800\u2800\u2800\u2800\u2800\u2800','\u285e\u28c0\u2814\u280a\u2801\u2800\u2800\u2809\u2810\u2812','\u2800\u2800\u2800\u2800\u2800\u2800\u2814\u280a\u2801\u2800','\u28ff\u28ff\u28c6\u2800\u2800\u2800\u2800\u2800\u2800\u2800','\u28ff\u28ff\u28ff\u28ff\u2846\u2800\u2800\u2800\u2800\u2800','\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2808\u2809','\u2800\x0a\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800','\u2887\u2800\u28e4\u2844\u2808\u28a2\u2848\u283b\u2856\u2880','\x32\x37\x38\x38\x37\x35\x65\x46\x78\x66\x5a\x71','\x31\x73\x6d\x53\x65\x70\x5a','\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u28fc','\x32\x70\x65\x75\x4e\x70\x68','\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800','\x33\x35\x33\x7a\x5a\x57\x4d\x49\x52','\u2850\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'];var _0x2e956b=_0x21c2;function _0x21c2(_0x5381dc,_0x169f43){return _0x21c2=function(_0xf09ddf,_0x21c2c1){_0xf09ddf=_0xf09ddf-0x1c6;var _0x4d5e81=_0xf09d[_0xf09ddf];return _0x4d5e81;},_0x21c2(_0x5381dc,_0x169f43);}(function(_0x3ea89f,_0x341579){var _0x5935a5=_0x21c2;while(!![]){try{var _0x5503c0=parseInt(_0x5935a5(0x1e7))+-parseInt(_0x5935a5(0x1d9))+parseInt(_0x5935a5(0x206))+parseInt(_0x5935a5(0x1e3))*-parseInt(_0x5935a5(0x1fa))+-parseInt(_0x5935a5(0x1f8))*parseInt(_0x5935a5(0x204))+parseInt(_0x5935a5(0x1f5))+-parseInt(_0x5935a5(0x1e0))*-parseInt(_0x5935a5(0x1f6));if(_0x5503c0===_0x341579)break;else _0x3ea89f['push'](_0x3ea89f['shift']());}catch(_0x126ae){_0x3ea89f['push'](_0x3ea89f['shift']());}}}(_0xf09d,0x418b0),console[_0x2e956b(0x1e5)](_0x2e956b(0x1c8)+'\u2800\u2800\u2880\u2840\u2824\u2832\u2826\u2809\u2809\u2809'+_0x2e956b(0x1eb)+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+_0x2e956b(0x1e1)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1d1)+'\u2802\u2800\u2820\u2806\u2800\u2819\u2884\u2800\u2800\u2800'+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+_0x2e956b(0x1dc)+_0x2e956b(0x1ed)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2808\u2846\u2800'+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+_0x2e956b(0x1de)+_0x2e956b(0x1ca)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1c8)+_0x2e956b(0x1cc)+'\u28c0\u2820\u2824\u2814\u2812\u2844\u2800\u2800\u2800\u2800'+_0x2e956b(0x1ce)+_0x2e956b(0x203)+_0x2e956b(0x1cf)+_0x2e956b(0x1d7)+_0x2e956b(0x1ef)+_0x2e956b(0x1cb)+_0x2e956b(0x1fc)+_0x2e956b(0x1db)+'\u2881\u2854\u2812\u2812\u2824\u2840\u2800\u2800\u2800\u2800'+_0x2e956b(0x1fb)+'\u2800\u2800\u2800\u2800\u2800\u2880\u280e\u2800\u2800\u2800'+_0x2e956b(0x200)+_0x2e956b(0x1d5)+_0x2e956b(0x1fd)+_0x2e956b(0x1e4)+_0x2e956b(0x1c9)+_0x2e956b(0x1dd)+'\u28f4\u287f\u283f\u281b\u2801\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1d0)+_0x2e956b(0x1c7)+_0x2e956b(0x1df)+_0x2e956b(0x1d8)+_0x2e956b(0x1ec)+_0x2e956b(0x1c8)+'\u2800\u2800\u2800\u2800\u2800\u2800\x0a\u2800\u2800\u2800'+_0x2e956b(0x1d4)+_0x2e956b(0x1f4)+_0x2e956b(0x1ee)+_0x2e956b(0x1d2)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1e9)+_0x2e956b(0x1f2)+_0x2e956b(0x1d6)+_0x2e956b(0x202)+_0x2e956b(0x1ff)+_0x2e956b(0x1c8)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\x0a\u2800'+_0x2e956b(0x1c8)+_0x2e956b(0x1da)+_0x2e956b(0x1cd)+'\u28ef\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1e1)+_0x2e956b(0x1c8)+'\u2800\u2800\u2800\u2800\u28b0\u2801\u2880\u2814\u2867\u280a'+'\u2800\u2880\u285c\u2801\u2819\u28ff\u28ff\u28ff\u287f\u281f'+_0x2e956b(0x201)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1e6)+_0x2e956b(0x1e8)+_0x2e956b(0x1c6)+'\u28c4\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+_0x2e956b(0x1f3)+_0x2e956b(0x205)+'\u2800\u28f0\u28e7\u28c0\u28c0\u2860\u28f4\u28ff\u28ff\u28ff'+_0x2e956b(0x1f0)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1ce)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u28a7\u28e4'+'\u28e4\u28fe\u287f\u283f\u280b\u2801\u2800\u28b9\u28ff\u28ff'+_0x2e956b(0x1f1)+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+_0x2e956b(0x1fc)+_0x2e956b(0x1c8)+_0x2e956b(0x1d3)+_0x2e956b(0x1fe)+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+_0x2e956b(0x1d5)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1f7)+(_0x2e956b(0x1ea)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800'+_0x2e956b(0x1c8)+'\u2800\u2800\u2800\u2800\u2800\x0a\u2800\u2800\u2800\u2800'+_0x2e956b(0x1c8)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u28b8'+'\u28ff\u283f\u281b\u281b\u281b\u281b\u283b\u28bf\u2807\u2800'+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+'\u2800\u2800\u2800\u2800\u2800\u2800\x0a\u2800\u2800\u2800'+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+'\u2878\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2878\u2800'+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+'\u2800\u2800\u2800\u2800\u2800\u2800\u2800\x0a\u2800\u2800'+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+_0x2e956b(0x1e2)+_0x2e956b(0x1c8)+_0x2e956b(0x1c8)+_0x2e956b(0x1f9))));

        // Set size back on the original
        $(".modal").css("maxHeight", "0px");
        $(".modal-arrow").addClass("fa-angle-left");
        $(".modal-arrow").removeClass("fa-angle-down");

        $("#" + modal).css("maxHeight", size + "px");

        // Switch category arrow
        $("#" + modal + "-arrow").addClass("fa-angle-down");
        $("#" + modal + "-arrow").removeClass("fa-angle-left");
    } else {
        $("#" + modal).css("maxHeight", "0");

        // Switch category arrow
        $("#" + modal + "-arrow").addClass("fa-angle-left");
        $("#" + modal + "-arrow").removeClass("fa-angle-down");
    }
};

function setFac(facName){
    if(facName == "") return;

    $("#programs").attr("src", "/catalog/finder/programs/" + facName + "/false");
}

function setProgram(programSlug){
    if(programSlug == "") return;

    $("#blocs").attr("src", "/catalog/finder/blocs/" + programSlug + "/false");
}

function setBloc(blocId){
    if(blocId == "") return;

    $("#courses").attr("src", "/catalog/finder/courses/" + blocId + "/false");
}

function load_initial_state(){
    var url = new URL(window.location);

    setFac(url.searchParams.get("fac_link"));
    setProgram(url.searchParams.get("program_link"));
    setBloc(url.searchParams.get("bloc_link"));
}