//LOAD CSS	
function adjustStyle(width) {		
		width = parseInt(width);
		if (width < 600) {
			$("#size-stylesheet").attr("href", "small.css");
		} else if ((width >= 601) && (width < 760)) {
			$("#size-stylesheet").attr("href", "medium.css");
		} else {
		   $("#size-stylesheet").attr("href", "style.css");
		}	
}
