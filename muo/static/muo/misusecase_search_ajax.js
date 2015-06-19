jQuery(function() {

    window.onload=function() {
        // Once the page is loaded, show all the misuse cases by default
        load_misusecases([]);
    };


    $(".misuse-case-container").click(function(){
        // get the misuse_case_id of the clicked misuse case
        var misuse_case_id = $(this).attr("data-value");

        // Remove the selection from the last selected misuse case div
        $('.misuse-case-container.selected').removeClass('selected');

        // Select the current div
        $(this).addClass('selected');

        // Load usecases corresponding to the selected misuse
        load_usecases(misuse_case_id)
    });


    $("#refresh_button").click(function(){
        // Prevent the default django action on button click. Otherwise it'll reload the whole page
        event.preventDefault();

        // Get the selected CWE ids
        var selected_cwes = $('#id_cwes').val();

        // If none of the CWEs are selected, the value of the selected_cwes will be null. I such cases, we need to mimic
        // the default behaviour. We will send an empty array in the ajax request and display all the misuse cases.
        if (selected_cwes == null) {
            selected_cwes = [];
        }

        // Load the misuse cases for the selected cwes
        load_misusecases(selected_cwes)
    });
});


function load_usecases(misuse_case_id) {
    $.ajax({
        url: 'usecases/',
        type: 'POST',
        data: {misuse_case_id: misuse_case_id}, // Send the selected misuse case id

        success: function(result) {
            // If ajax call is successful, reload the fat-scroll-div which contains the use cases
            $('.fat-scroll-div').replaceWith(result);
        },

        error: function(xhr,errmsg,err) {
            // Show error message in the alert
            alert("Oops! We have encountered and error \n" + errmsg);
        }
    });
}


function load_misusecases(cwe_ids) {
    $.ajax({
        url: 'misusecases/',
        type: 'POST',
        data: {cwe_ids: cwe_ids}, // Send the selected CWE ids

        success: function(result) {
            // If ajax call is successful, reload the slim-scroll-div which contains the misuse cases
            $('.slim-scroll-div').replaceWith(result);

            // Select the first misuse case by default
            first_misuse_case_div = $($('.misuse-case-container').get(0));

            first_misuse_case_div.addClass('selected');

            // Get the misuse case id of the first misuse case
            misuse_case_id = first_misuse_case_div.attr("data-value");
            load_usecases(misuse_case_id);
        },

        error: function(xhr,errmsg,err) {
            // Show error message in the alert
            alert("Oops! We have encountered and error \n" + errmsg);
        }
    });
}