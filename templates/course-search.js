var searchContent = "";
var selectedTags = [];

var filterChange = function() {
    searchContent = $("[name=document-search]").val();

    selectedTags = [];

    $("[name=document-tags]").children(":selected").each(function(){
        selectedTags.push($(this).val());
    });

    $(".course-row").each(function(){
        $(this).show();

        // Text search
        if(
            searchContent !== "" &&
            $(this).find("h5 > a").text().toLowerCase().indexOf(searchContent.toLowerCase()) < 0 &&
            $(this).find("p").text().toLowerCase().indexOf(searchContent.toLowerCase()) < 0
        ){
            $(this).hide();
        }

        // Keywords
        var tags = $(this).attr("node-keywords").split(" ");
        for(var i=0; i < selectedTags.length; i++){
            if(tags.indexOf(selectedTags[i]) < 0){
                $(this).hide();
                break;
            }
        }
        tags.pop();

        // Type
        var show_type = $("[name=node-type]").find(":selected").val();
        if(show_type !== "tout" && $(this).attr("node-type") !== show_type){
            $(this).hide();
        }

        // Year
        var show_year = $("[name=node-year]").find(":selected").val();
        if(show_year !== "tout" && $(this).attr("node-year") !== show_year){
            $(this).hide();
        }
    });
};

$(document).ready(function(){
    $(".chosen-select").select2();

    $("[name=document-search]").on("keyup",function(){
        if(searchContent != $("[name=document-search]").val()){
            filterChange();
        }
    });
    $("[name=document-tags]").change(function(){
        filterChange();
    });
    $("[name=node-type]").change(function(){
        filterChange();
    });
    $("[name=node-year]").change(function(){
        filterChange();
    });

    filterChange();
});
