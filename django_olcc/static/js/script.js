(function($) {
    $(document).ready(function() {
        var form = $('#find-stores');

        // Hide the submit button
        form.find('input[type=submit]').hide();

        // Submit the form on change
        form.find('select:first').each(function() {
            $(this).change(function() {
                form.submit();
                return false;
            });
        });
    });
})(jQuery);
