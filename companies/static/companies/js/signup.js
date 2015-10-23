$('#signupForm').on('submit', function() {
	var email = $("input#email").val();
	if (email.endsWith('princeton.edu')) {
		window.alert('Do not sign up if you have a valid netid.');
		$('#signupForm').trigger("reset");
		return false;
	}
	else return true;
});