function validateForm() {
    // alert("Checkpoint");
    var form = document.getElementById('scheduleForm');
    if (!anyChecked(form)) return false;
    // alert("Checkpoint 1");
    // var is_checked = anyChecked(form);
    // alert("Checkpoint");
    // return is_checked;
    checkCastSize(form);
    return true;
    
    // var is_checked = false;
    // for (var x = 0; x < inputs.length; x++) {
    //     if (inputs[x].type == 'checkbox' && inputs[x].checked) {
    //         alert(inputs[x].value);
    //     } 
    // }
}

function anyChecked(form) {
	var inputs = form.getElementsByTagName('input');
	var is_checked = false;
	for (var x = 0; x < inputs.length; x++) {
		if (inputs[x].type == 'checkbox') {
			is_checked = inputs[x].checked;
			if (is_checked) break;
		}
	}

	if (!is_checked) alert('You must select at least one field before continuing');

	return is_checked;
}

function checkCastSize(form) {
	var inputs = form.getElementsByTagName('input');
	var labels = form.getElementsByTagName('label');

	for (var x = 0; x < inputs.length; x++) {
		if (inputs[x].type == 'checkbox' && inputs[x].checked) {
			var a = labels[x].getElementsByTagName('a');
			alert(a[0].innerHTML);
		}
	}
}