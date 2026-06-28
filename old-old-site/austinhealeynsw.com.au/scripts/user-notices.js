function getPageLength() {
	var test1 = document.body.scrollHeight;
	var test2 = document.body.offsetHeight;
	var totalPageLength;
	
	if (test1 > test2) { // all but Explorer Mac
		totalPageLength = document.body.scrollHeight;
	} else { // Explorer Mac; would also work in Explorer 6 Strict, Mozilla and Safari
		totalPageLength = document.body.offsetHeight;
	}
	
	return totalPageLength;
}

function populateNotice(noticeColour, noticeTitle, noticeContent) {
	document.getElementById("_noticeTitleArea").style.backgroundColor = noticeColour;
	document.getElementById("_noticeTitle").innerHTML = noticeTitle;
	document.getElementById("_noticeContent").innerHTML = noticeContent; 
		
	showNotice('userNoticeArea', noticeContent.length);
}

function showNotice(whichNotice, noticeCheck) {
	var w, h, pageLength;
	
	// only show notice if it's not already showing
	if (document.getElementById(whichNotice) && noticeCheck > 0) {
		if (window.innerWidth !== undefined && window.innerHeight !== undefined) { 
			w = window.innerWidth;
			h = window.innerHeight;
		} else {  
			w = document.documentElement.clientWidth;
			h = document.documentElement.clientHeight;
		}

		// show page mask
		pageLength = getPageLength();

		if (h > getPageLength()) {
			pageLength = h;
		}
		
		document.getElementById('userNoticeMask').style.height = pageLength + 'px';
		document.getElementById('userNoticeMask').style.display = 'block';
		
		document.getElementById(whichNotice).style.position = 'fixed';
		document.getElementById(whichNotice).style.display = 'block';
		
		adjustZindex(whichNotice, '+'); 	
		
		// center large notices vertically but put smaller ones near the topdocument.getElementById(whichNotice).offsetHeight
		if (document.getElementById(whichNotice).offsetHeight < 300) {
			document.getElementById(whichNotice).style.top = '200px';
		} else {
			document.getElementById(whichNotice).style.top = ((h - document.getElementById(whichNotice).offsetHeight) / 2) + 'px';
		}
		
		document.getElementById(whichNotice).style.left = ((w - document.getElementById(whichNotice).offsetWidth) / 2) + 'px'; 
	} 
}

function hideNotice(whichNotice, alsoHideMask) {
	// if it exists, glide the current notice gently off screen
	if (document.getElementById(whichNotice)) {
		if (whichNotice == 'filterProcessing') {
			document.getElementById('filterProcessing').style.display = 'none';
		}
		
		var topPosition = document.getElementById(whichNotice).style.top.replace('px','');
		var noticeHeight = document.getElementById(whichNotice).offsetHeight;
		
		var id = setInterval(rePosition, 5);
		
		function rePosition() {
			if (topPosition + noticeHeight < 0) {
				clearInterval(id);
				
				document.getElementById(whichNotice).style.top = '-1000px';
				document.getElementById(whichNotice).style.left = '-1000px';
				document.getElementById(whichNotice).style.display = 'none';		
				
				// hide mask if it isn't already hidden
				if (alsoHideMask || document.getElementById('userNoticeArea').style.display != 'none') {
					document.getElementById('userNoticeMask').style.display = 'none'; 
				}
				
				adjustZindex(whichNotice, '-'); 	
			} else {
				topPosition -= 10;
				
				document.getElementById(whichNotice).style.top = topPosition + 'px';
			} 
		}
	}
	
	// hide all browser forms
	var browserFormsList = document.getElementsByClassName('_singleBrowserForm');
	
	for (var l = 0; l < browserFormsList.length; l++) {
		browserFormsList[l].style.display = 'none';
	}	
}

function centreNotice() {
	var w, h, noticeList;
	
	if (document.getElementById('userNoticeMask') && document.getElementById('userNoticeMask').style.display == 'block') {
		if (window.innerWidth !== undefined && window.innerHeight !== undefined) { 
			w = window.innerWidth;
			h = window.innerHeight;
		} else {  
			w = document.documentElement.clientWidth;
			h = document.documentElement.clientHeight;
		}	
		
		noticeList = document.getElementsByClassName('_userNoticeForm');
		
		for (var c = 0; c < noticeList.length; c++) {
			noticeList[c].style.left = ((w - noticeList[c].offsetWidth) / 2) + 'px';
		}
	}
}

function showDeleteForm(deleteWhat, itemLabel, itemID) {
	document.getElementById("_noticeTitleArea").style.backgroundColor = 'red';

	if (deleteWhat.length > 0 && itemID.length == 64) {
		var xmlhttp = new XMLHttpRequest();
		
		xmlhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200 && this.responseText.length > 0) {
				var formContent = this.responseText.split('<!>');

				document.getElementById("_noticeTitle").innerHTML = formContent[0];
				document.getElementById("_noticeContent").innerHTML = formContent[1]; 
				
				showNotice('userNoticeArea',1);
			}
		};

		xmlhttp.open("GET", siteBase + 'requests/_delete-item.php?item=' + deleteWhat + '&label=' + itemLabel + '&id=' + itemID + '&ret=' + encodeURI(window.location.href), true);
		xmlhttp.send();	
	}
}

function showAddMemberForm() {
	document.getElementById("_noticeTitleArea").style.backgroundColor = 'black';
	document.getElementById("_noticeTitle").innerHTML = 'Add a member';

	var xmlhttp = new XMLHttpRequest();
	
	xmlhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200 && this.responseText.length > 0) {
			document.getElementById("_noticeContent").innerHTML = this.responseText; 
			
			showNotice('userNoticeArea',1);
		}
	};

	xmlhttp.open("GET", siteBase + 'requests/_add-member.php', true);
	xmlhttp.send();	
}

function adjustZindex(whichItem, whichDirection) {
	// cycle through pop up user notices (includes browser forms) 
	allUserNotices = document.getElementsByClassName('_userNoticeForm');

	var frontZindex = 0;
	var frontItem = '';
	
	for (n = 0; n < allUserNotices.length; n++) {
		if (allUserNotices[n].style.display == 'block' && parseInt(allUserNotices[n].style.zIndex) > frontZindex) {
			frontZindex = parseInt(allUserNotices[n].style.zIndex);
			frontItem = allUserNotices[n].id;
		}
	}

	frontZindex += 10000;

	if (whichDirection == '+') {
		document.getElementById(whichItem).style.zIndex = frontZindex;
		
		putMaskBehind = whichItem;
	} else {
		putMaskBehind = frontItem;
	}
	
	if (document.getElementById(putMaskBehind)) {
		document.getElementById('userNoticeMask').style.zIndex = parseInt(document.getElementById(putMaskBehind).style.zIndex) - 1;
	}
}

// detect ESC key to hide notices
document.onkeydown = function(evt) {
    evt = evt || window.event;
	
    if (evt.keyCode == 27) {
		var noticeList = document.getElementsByClassName('_userNoticeForm');
		
		for (var n = 0; n < noticeList.length; n++) {
			if (noticeList[n] && noticeList[n].style.display == 'block') {
				hideNotice(noticeList[n].id, true);
			}
		}
    }
};

	