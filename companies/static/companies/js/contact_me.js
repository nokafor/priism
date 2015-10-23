$(function() {

    $("input,textarea").jqBootstrapValidation({
        preventSubmit: true,
        submitError: function($form, event, errors) {
            // additional error messages or events
        },
        submitSuccess: function($form, event) {
            event.preventDefault(); // prevent default submit behaviour
            // get values from FORM
            var name = $("input#name").val();
            var email = $("input#email").val();
            var organization = $("input#organization").val();
            var message = $("textarea#message").val();
            var api_user = $("input#api_user").val()
            var api_key = $("input#api_key").val()
            var toEmail = $("input#toEmail").val()
            var firstName = name; // For Success/Failure Message
            // Check for white space in name for Success/Fail message
            if (firstName.indexOf(' ') >= 0) {
                firstName = name.split(' ').slice(0, -1).join(' ');
            }

            var email_body = "You have received a new message from your website contact form. Here are the details:\n\n\nName: " + name + "\n\nEmail: " + email + "\n\nOrganization: " + organization + "\n\nMessage:\n" + message;

            $.ajax({
                type: "POST",
                url: "https://api.sendgrid.com/api/mail.send.json",
                dataType: 'text',
                data: {
                    api_user: api_user,
                    api_key: api_key,
                    to: toEmail,
                    subject: "PRISM Feedback Form",
                    from: email,
                    replyto: email,
                    fromname: "PRISM",
                    text: email_body
                },
                cache: false,
                // For some reason, AJAX is processing these successful events as errors, so I just switched the two messages
                success: function() {
                    // Fail message
                    $('#success').html("<div class='alert alert-danger'>");
                    $('#success > .alert-danger').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                        .append("</button>");
                    $('#success > .alert-danger').append("<strong>Sorry " + firstName + ", it seems that my mail server is not responding. Please try again later!");
                    $('#success > .alert-danger').append('</div>');
                    //clear all fields
                    $('#contactForm').trigger("reset");

                    // // Success message
                    // $('#success').html("<div class='alert alert-success'>");
                    // $('#success > .alert-success').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                    //     .append("</button>");
                    // $('#success > .alert-success')
                    //     .append("<strong>Your message has been sent. </strong>");
                    // $('#success > .alert-success')
                    //     .append('</div>');

                    // //clear all fields
                    // $('#contactForm').trigger("reset");
                },

                // For some reason, AJAX is processing these successful events as errors, so I just switched the two messages
                error: function() {
                    // Success message
                    $('#success').html("<div class='alert alert-success'>");
                    $('#success > .alert-success').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                        .append("</button>");
                    $('#success > .alert-success')
                        .append("<strong>Your message has been sent. </strong>");
                    $('#success > .alert-success')
                        .append('</div>');

                    //clear all fields
                    $('#contactForm').trigger("reset");
                    // // Fail message
                    // $('#success').html("<div class='alert alert-danger'>");
                    // $('#success > .alert-danger').html("<button type='button' class='close' data-dismiss='alert' aria-hidden='true'>&times;")
                    //     .append("</button>");
                    // $('#success > .alert-danger').append("<strong>Sorry " + firstName + ", it seems that my mail server is not responding. Please try again later!");
                    // $('#success > .alert-danger').append('</div>');
                    // //clear all fields
                    // $('#contactForm').trigger("reset");
                },
            })
        },
        filter: function() {
            return $(this).is(":visible");
        },
    });

    $("a[data-toggle=\"tab\"]").click(function(e) {
        e.preventDefault();
        $(this).tab("show");
    });
});


/*When clicking on Full hide fail/success boxes */
$('#name').focus(function() {
    $('#success').html('');
});
