$('#form').on('submit', function() {
	window.alert('In Function');
	var email = $("input#email").val();
	if (email.endsWith('princeton.edu')) {
		window.alert('Please log in with NetID, using orange button to the left.');
		$('#form').trigger("reset");
		return false;
	}
	else return true;
});