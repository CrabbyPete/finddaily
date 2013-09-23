// jQuery checkbox & radio buttons

jQuery.fn.checkbox = function() {
	return this.each(function() {
		var $this = jQuery(this);
		if(!$this.parents('.custom-checkbox').length) {
			var wrap_tag = 'div';

			if(!$this.parents('label').length) {
				wrap_tag = 'label';
			}

			$this.wrap('<div class="custom-checkbox" />').parent().append('<img src="/static/css/images/checkbox.png" width="13" height="41" />');

			if($this.is(':checked')) {
				$this.parent().addClass('checked');
			}
		}

		jQuery(document).on('change', 'input[type="checkbox"]', function() {
			var $this = jQuery(this);
			if($this.is(':checked')) {
				$this.parent().addClass('checked');
			} else {
				$this.parent().removeClass('checked');
			}
		});
	});
}
jQuery.fn.radio = function() {
	return this.each(function() {
		var $this = jQuery(this);
		if(!$this.parents('.custom-radio').length) {
			$this.wrap('<div class="custom-radio" />').parent().append('<img src="/static/css/images/radio.png" width="15" height="47" />');

			if($this.is(':checked')) {
				$this.parent().addClass('checked');
			}
		}

		jQuery(document).on('change', 'input[type="radio"]', function() {
			var $this = jQuery(this);
			var rad_name = $this.attr('name');
			if($this.is(':checked')) {
				jQuery('input[name="' + rad_name + '"]').each(function() {
					jQuery(this).parent().removeClass('checked');
				});
				$this.parent().addClass('checked');
			}
		});
	});
}


jQuery.checkbox = function() {
	jQuery('input[type="checkbox"]').checkbox();
}
jQuery.radio = function() {
	jQuery('input[type="radio"]').radio();
}