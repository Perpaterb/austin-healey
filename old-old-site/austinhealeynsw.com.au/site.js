jQuery.extend( jQuery.easing,
{
	easeInQuad: function (x, t, b, c, d) {
		return c*(t/=d)*t + b;
	},
	easeOutQuad: function (x, t, b, c, d) {
		return -c *(t/=d)*(t-2) + b;
	},
	easeInOutQuad: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t + b;
		return -c/2 * ((--t)*(t-2) - 1) + b;
	},
	easeInCubic: function (x, t, b, c, d) {
		return c*(t/=d)*t*t + b;
	},
	easeOutCubic: function (x, t, b, c, d) {
		return c*((t=t/d-1)*t*t + 1) + b;
	},
	easeInOutCubic: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t*t + b;
		return c/2*((t-=2)*t*t + 2) + b;
	},
	easeInQuart: function (x, t, b, c, d) {
		return c*(t/=d)*t*t*t + b;
	},
	easeOutQuart: function (x, t, b, c, d) {
		return -c * ((t=t/d-1)*t*t*t - 1) + b;
	},
	easeInOutQuart: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t*t*t + b;
		return -c/2 * ((t-=2)*t*t*t - 2) + b;
	},
	easeInQuint: function (x, t, b, c, d) {
		return c*(t/=d)*t*t*t*t + b;
	},
	easeOutQuint: function (x, t, b, c, d) {
		return c*((t=t/d-1)*t*t*t*t + 1) + b;
	},
	easeInOutQuint: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return c/2*t*t*t*t*t + b;
		return c/2*((t-=2)*t*t*t*t + 2) + b;
	},
	easeInSine: function (x, t, b, c, d) {
		return -c * Math.cos(t/d * (Math.PI/2)) + c + b;
	},
	easeOutSine: function (x, t, b, c, d) {
		return c * Math.sin(t/d * (Math.PI/2)) + b;
	},
	easeInOutSine: function (x, t, b, c, d) {
		return -c/2 * (Math.cos(Math.PI*t/d) - 1) + b;
	},
	easeInExpo: function (x, t, b, c, d) {
		return (t==0) ? b : c * Math.pow(2, 10 * (t/d - 1)) + b;
	},
	easeOutExpo: function (x, t, b, c, d) {
		return (t==d) ? b+c : c * (-Math.pow(2, -10 * t/d) + 1) + b;
	},
	easeInOutExpo: function (x, t, b, c, d) {
		if (t==0) return b;
		if (t==d) return b+c;
		if ((t/=d/2) < 1) return c/2 * Math.pow(2, 10 * (t - 1)) + b;
		return c/2 * (-Math.pow(2, -10 * --t) + 2) + b;
	},
	easeInCirc: function (x, t, b, c, d) {
		return -c * (Math.sqrt(1 - (t/=d)*t) - 1) + b;
	},
	easeOutCirc: function (x, t, b, c, d) {
		return c * Math.sqrt(1 - (t=t/d-1)*t) + b;
	},
	easeInOutCirc: function (x, t, b, c, d) {
		if ((t/=d/2) < 1) return -c/2 * (Math.sqrt(1 - t*t) - 1) + b;
		return c/2 * (Math.sqrt(1 - (t-=2)*t) + 1) + b;
	},
	easeInElastic: function (x, t, b, c, d) {
		var s=1.70158;var p=0;var a=c;
		if (t==0) return b;  if ((t/=d)==1) return b+c;  if (!p) p=d*.3;
		if (a < Math.abs(c)) { a=c; var s=p/4; }
		else var s = p/(2*Math.PI) * Math.asin (c/a);
		return -(a*Math.pow(2,10*(t-=1)) * Math.sin( (t*d-s)*(2*Math.PI)/p )) + b;
	},
	easeOutElastic: function (x, t, b, c, d) {
		var s=1.70158;var p=0;var a=c;
		if (t==0) return b;  if ((t/=d)==1) return b+c;  if (!p) p=d*.3;
		if (a < Math.abs(c)) { a=c; var s=p/4; }
		else var s = p/(2*Math.PI) * Math.asin (c/a);
		return a*Math.pow(2,-10*t) * Math.sin( (t*d-s)*(2*Math.PI)/p ) + c + b;
	},
	easeInOutElastic: function (x, t, b, c, d) {
		var s=1.70158;var p=0;var a=c;
		if (t==0) return b;  if ((t/=d/2)==2) return b+c;  if (!p) p=d*(.3*1.5);
		if (a < Math.abs(c)) { a=c; var s=p/4; }
		else var s = p/(2*Math.PI) * Math.asin (c/a);
		if (t < 1) return -.5*(a*Math.pow(2,10*(t-=1)) * Math.sin( (t*d-s)*(2*Math.PI)/p )) + b;
		return a*Math.pow(2,-10*(t-=1)) * Math.sin( (t*d-s)*(2*Math.PI)/p )*.5 + c + b;
	},
	easeInBack: function (x, t, b, c, d, s) {
		if (s == undefined) s = 1.70158;
		return c*(t/=d)*t*((s+1)*t - s) + b;
	},
	easeOutBack: function (x, t, b, c, d, s) {
		if (s == undefined) s = 1.70158;
		return c*((t=t/d-1)*t*((s+1)*t + s) + 1) + b;
	},
	easeInOutBack: function (x, t, b, c, d, s) {
		if (s == undefined) s = 1.70158; 
		if ((t/=d/2) < 1) return c/2*(t*t*(((s*=(1.525))+1)*t - s)) + b;
		return c/2*((t-=2)*t*(((s*=(1.525))+1)*t + s) + 2) + b;
	},
	easeInBounce: function (x, t, b, c, d) {
		return c - jQuery.easing.easeOutBounce (x, d-t, 0, c, d) + b;
	},
	easeOutBounce: function (x, t, b, c, d) {
		if ((t/=d) < (1/2.75)) {
			return c*(7.5625*t*t) + b;
		} else if (t < (2/2.75)) {
			return c*(7.5625*(t-=(1.5/2.75))*t + .75) + b;
		} else if (t < (2.5/2.75)) {
			return c*(7.5625*(t-=(2.25/2.75))*t + .9375) + b;
		} else {
			return c*(7.5625*(t-=(2.625/2.75))*t + .984375) + b;
		}
	},
	easeInOutBounce: function (x, t, b, c, d) {
		if (t < d/2) return jQuery.easing.easeInBounce (x, t*2, 0, c, d) * .5 + b;
		return jQuery.easing.easeOutBounce (x, t*2-d, 0, c, d) * .5 + c*.5 + b;
	}
});

/*
|--------------------------------------------------------------------------
| UItoTop jQuery Plugin 1.2 by Matt Varone
| http://www.mattvarone.com/web-design/uitotop-jquery-plugin/
|--------------------------------------------------------------------------
*/
(function($){
	$.fn.UItoTop = function(options) {

 		var defaults = {
    			text: 'To Top',
    			min: 200,
    			inDelay:600,
    			outDelay:400,
      			containerID: 'toTop',
    			containerHoverID: 'toTopHover',
    			scrollSpeed: 1200,
    			easingType: 'linear'
 		    },
            settings = $.extend(defaults, options),
            containerIDhash = '#' + settings.containerID,
            containerHoverIDHash = '#'+settings.containerHoverID;
		
		$('body').append('<a href="#" id="'+settings.containerID+'">'+settings.text+'</a>');
		$(containerIDhash).hide().on('click.UItoTop',function(){
			$('html, body').animate({scrollTop:0}, settings.scrollSpeed, settings.easingType);
			$('#'+settings.containerHoverID, this).stop().animate({'opacity': 0 }, settings.inDelay, settings.easingType);
			return false;
		})
		.prepend('<span id="'+settings.containerHoverID+'"></span>')
		.hover(function() {
				$(containerHoverIDHash, this).stop().animate({
					'opacity': 1
				}, 600, 'linear');
			}, function() { 
				$(containerHoverIDHash, this).stop().animate({
					'opacity': 0
				}, 700, 'linear');
			});
					
		$(window).scroll(function() {
			var sd = $(window).scrollTop();
			if(typeof document.body.style.maxHeight === "undefined") {
				$(containerIDhash).css({
					'position': 'absolute',
					'top': sd + $(window).height() - 50
				});
			}
			if ( sd > settings.min ) 
				$(containerIDhash).fadeIn(settings.inDelay);
			else 
				$(containerIDhash).fadeOut(settings.Outdelay);
		});
};
})(jQuery);


$(document).ready(function() {
	//To Top
	adjustStyle($(this).width());					
	$().UItoTop({ easingType: 'easeOutQuart' });
	
	//FancyBox
	$(".overlayImg").fancybox({
		helpers	: {
			title	: {
				type: 'outside'
			},
			thumbs	: {
				width	: 50,
				height	: 50
			}
		}
	});
		
	//Mobile Menu Slide Toggle	
	$('#navToggle').click(function(){
			$('#navMobile').slideToggle();						   
	});
			
	//MOBILE SCROLL TO TOP
	$("#footerToTop").click(function() {
		  $("html, body").animate({ scrollTop: 0 }, "slow");
		  return false;
	});
	

	
});

$(window).bind("load", function() {
	cartImages();
	stickyFooter();
	galleryImages();
});

$(window).resize(function(){
	adjustStyle($(this).width());								//css loading function
	cartImages();
	stickyFooter();
	galleryImages();
});

//SITE CODE



function stickyFooter(){
	//RESET SIDEBAR AND SITECONTENT TO AUTO TO CLEAR VALUES
	$('.siteContent').css({'height': 'auto'});				
	$('.sidebar').css({'height': 'auto'});	
	
	//SETUP SOME VARS
	var sidebar = $('.sectionFW').last().find('.sidebar');
	var siteContent = $('.sectionFW').last().find('.siteContent');
	var windowHeight = $(window).height();
	var lastHeight = sidebar.outerHeight();	
	var lastSite = siteContent.outerHeight();		
	
	if(lastHeight < lastSite) {	// if siteContent is taller than sidebar make sidebar equal
		sidebar.css({'height': lastSite + 'px'});
	}
	else if(lastHeight > lastSite) {	// if sidebar is taller than siteContent make siteContent equal
		siteContent.css({'height': lastHeight + 'px'});
	}	
	
	var lastHeight = sidebar.outerHeight();				//get new heights
	var lastSite = siteContent.outerHeight();			//get new heights
	var	totalHeight =  $('.siteTop').outerHeight() + $('.siteBottom').outerHeight() + $('#footer').outerHeight();
	var difference = windowHeight - (totalHeight - lastSite);

	
	
	if(windowHeight > totalHeight){
		siteContent.css({'height': difference + 'px'});		
		sidebar.css({'height': difference + 'px'});		
	}	
	
	//ONCE EVERYTHING HAS BEEN RESIZED, MAKE SURE EACH SITECONTENT AND SIDEBAR HEIGHTS MATCH
	$('.container').each(function(){			
		var sidebar = $(this).children('.sidebar').outerHeight();
		var content = $(this).children('.siteContent').outerHeight();
		if(sidebar > content){
			$(this).children('.siteContent').height(sidebar + 'px');
		}
		else if (content > sidebar){
			$(this).children('.sidebar').height(content + 'px');
		}
	});
	
	//RESIZE SHOPPING CART Image
	var productImage = $('.Product-Image-Large').width();
	$('.Product-Image-Large').css({'height': productImage + 'px'});
	
	
}





//SUB MENU
$(document).ready(function () {     		
                $('#nav li').hover(function(){
                $('ul', this).slideDown(400);}, 
				function(){
				$('ul', this).slideUp(400);},
				
				$('#navMobile li').click(function(){
					$('#navMobile li ul').slideUp();
					$('ul', this).slideToggle(100);
					}			)  

);   
});



	function galleryImages(){
		
		$('.contentImg .item a').each(function(){							//for each item
			//set up some vars						   
			var containerWidth = $('.contentImg .item').width();	//get width of container div
			var containerHeight = containerWidth * .8;
			var img = $(this).children(img);						//the current image				
			var imgHeight = img.outerHeight();						//image height
			var imgWidth = img.outerWidth();						//image width
			
			if (imgHeight  > imgWidth){								//if the image is potrait
				img.css({'minWidth' : containerWidth + 'px' });		
			}
			else if (imgWidth  > imgHeight){						//if the image is landscape
				img.css({'minHeight' : containerHeight + 'px' });		
			}	
			else if(imgWidth == imgHeight){							//if the image is square
				img.width(containerWidth);	
			}
			//vertCenter(this);										//vertically center image
		});
	}


//SHOPPING CART THUMBS 
	function cartImages(){
		var containerWidth = $('.Shop-Thumb').width();				//get width of container div
		$('.Shop-Thumb').each(function(){							//for each item
			//set up some vars						   
			var img = $(this).children(img);						//the current image				
			var imgHeight = img.outerHeight();						//image height
			var imgWidth = img.outerWidth();						//image width
			
			if (imgHeight  > imgWidth){								//if the image is potrait
				img.height(containerWidth);	
			}
			else if (imgWidth  > imgHeight){						//if the image is landscape
				img.width(containerWidth);		
			}	
			else if(imgWidth == imgHeight){							//if the image is square
				img.width(containerWidth);	
			}
			vertCenter(this);										//vertically center image
		});
	}

	function vertCenter(divName){
		//vertically center image
		divHeight = $(divName).outerHeight();					//DIV parent height
		$shopImg = $('img', divName);							//Declare that the image is the child of current DIV
		imgHeight = $shopImg.height();							//Get height of img
		imgMargin = divHeight - imgHeight;						//Subtract image height from div height to get remaining px
		$shopImg.css('margin-top', + imgMargin / 2 + "px"); 	
	}	
	
	
