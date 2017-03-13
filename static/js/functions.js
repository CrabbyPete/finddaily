$(function() {
	var breakpoint = $('#logo img').width();

	$.checkbox();
	$.radio();
	$('select.stylized').chosen().change(function(evt,params){ 
														var href = params['selected'];
														window.location = href;
		                                            });


	$('select.makes').chosen().change(function(evt,params){ 
		var make = params['selected'];
		var url = $(this).attr('href')+make;
		$.get(url,function(data){
			var html = $('select.models').html()
			$('select.models').html(data);
			$('select.models').trigger("chosen:updated");
		});
    });
	
	
	$('select.models').chosen().change(function(evt,params){
		var url = $(this).attr('href') + params['selected'];
		$.get(url,function(data){
			var html = $('select.models').html()
			$('select.trims').html(data);
			$('select.trims').trigger("chosen:updated");
		});

    });
	
	$('select.trims').chosen();
	
 
	$('[data-popup]').colorbox({
		scrolling: false,
		opacity: .45,
		initialWidth: 50,
		initialHeight: 50
	});

	$(document)
	.on('focusin', '.field', function() {
		if(this.title==this.value) {
			this.value = '';
		}
	})
	.on('focusout', '.field', function(){
		if(this.value=='') {
			this.value = this.title;
		}
	})
	.on('click', '.ico-help', function(e) {
		$(this).toggleClass('active');

		e.preventDefault();
	})
	.on('click', '.edit, .save', function(e) {
		var $parent = $(this).parents('div:eq(0)');
		var $class = $(this).attr('class');
		
		$parent.toggleClass('editing');
		if ( $class == 'save' ) {
			$('.options').submit();
		}
	
		e.preventDefault();
	})
	.on('click', '#listing .settings-link', function(e) {
		if(!$('.settings-dd').is(':animated')) {
			$(this).toggleClass('active');
			$('.settings-dd').slideToggle(500);
		}

		e.preventDefault();
	})
	.on('click', '.btns .delete',function() {
		var href = $(this).attr('href');
		var parent = $(this).parents('#line');
		parent.remove();
		$.get(href);
	})
	
	.on('click', '.settings .cancel', function() {
		$('.settings-dd').slideUp(500);
		$('.settings-link').removeClass('active');
	})
	.on('click', '#colorbox .cancel, #colorbox .note', function(e) {
		if ( $(this).attr('class') == 'note' )
			$('.notes').submit();
		
		$.colorbox.close();

		e.preventDefault();
	})
	.on('click', '#mobile-nav .toggle', function(e) {
		if(!$('#mobile-nav > ul').is(':animated')) {
			$('#mobile-nav > ul').slideToggle(400);
		}

		e.preventDefault();
	})

	$('html').on('click', function(e) {
		if(!$(e.target).parents('#mobile-nav').length && $('#mobile-nav > ul').is(':visible')) {
			$('#mobile-nav > ul').slideUp(400);
		}
	})

	$(window)
	.on('load', function() {
		if($('.text-fader').length) {
			$('.text-fader').flexslider({
				slideshowSpeed: 7000,
				animationSpeed: 600,
				controlNav: false,
				directionNav: false,
				smoothHeight: true,
				touch: false
			});
		}
	})
	.on('resize', function() {
		breakpoint = $('#logo img').width();

		switch(breakpoint) {
			case 124:
			do_resize()
			break;

			case 150:
			do_resize()
			break;

			default:
			//do nothing
			break;
		}
	});

	function do_resize() {
		if($('#colorbox').is(':visible')) {
			var div_wid = $('#cboxLoadedContent > div').outerWidth();
			$.colorbox.resize({
				innerWidth: div_wid
			});
		}
	}
});