//Custom Form Validation Styles from Bootstrap example

(function() {
	'use strict'
	window.addEventListener('load', function() {
		const forms = document.querySelectorAll('.needs-validation');
		// Loop over them and prevent submission
		Array.prototype.filter.call(forms, function(form) {
			form.addEventListener('submit', function(event) {
				if (form.checkValidity() === false) {
					event.preventDefault();
					event.stopPropagation();
				}
				form.classList.add('was-validated');
			}, false);
		});
	}, false);
})();
