$(document).ready(function() {
    $(".misusecaseContainer").click(function(){
        // get the misuse_case_id of the clicked misuse case
        var misuse_case_id = $(this).attr("id");

        // Load the usecase corresponding to the selected misuse
        $.ajax({
            url: 'usecases/',
            type: 'GET',
            data: {misuse_case_id: misuse_case_id}, // Send the selected misuse case id

            success: function(result) {
                // If ajax call is successful, reload the fatScrollDiv which containes the use cases
                $('.fatScrollDiv').replaceWith(result);
            },

            error: function(xhr,errmsg,err) {
                // Show error message in the alert
                alert("Oops! We have encountered and error \n" + errmsg);
            }
        });
    });
});
