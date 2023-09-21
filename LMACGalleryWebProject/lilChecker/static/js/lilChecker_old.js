function LILChecker(consoleElement, post) {
	
    var IMAGE_DATA_BLOCK_REGEX = /<table class="lil">[\n]+.*?<\/table>/gs;
    var IMAGE_DATA_ROW_REGEX = /<tr>[\n]+.*?<\/tr>/gs;
    var IMAGE_TITLE_REGEX = /<td class="lil-title">(.+?)<\/td>/gs;
    var IMAGE_TAGS_REGEX = /<td class="lil-tags">(.+?)<\/td>/gs;
    var IMAGE_URL_REGEX = /<td class="lil-image"><img src="(.+?)" width="[0-9]+"\/><\/td>/gs;
	
	var NOT_FOUND = '<span class="LMACLILChecker-not-found">NOT FOUND</span>';
	
	var hivePost = post;
	var imagesFound = [];
	var cons = consoleElement;
	var tablesFound = [];
	
	var self=this;
	
	self.printLog = function(text, messageType = '') {
		
		specialTagPrefix = '';
		specialTagSuffix = '';
		
		if (messageType == 'error') {
			specialTagPrefix = '<span class="LMACLILChecker-error">';
			specialTagSuffix = '</span>';
		}
		
		cons.innerHTML += specialTagPrefix + text + specialTagSuffix;
		cons.innerHTML += "<br/>";
		
		cons.scrollTo(0,cons.scrollHeight);
	};
	self.init = function() {

		cons.innerHTML = ''; 

		if (hivePost.length == 0) {
			self.printLog('ERROR!!! The Hive post is empty.', 'error');
		return false;
		}

		self.printLog('Examining Hive Post...');

		return true;
	} 
	self.validateStructure = function() {

		
		var found = {};
		let tablesMatches = hivePost.matchAll(IMAGE_DATA_BLOCK_REGEX);
		tablesMatches = Array.from(tablesMatches);
 
		tablesMatches.forEach(function(tableElement) {
			tableElement = tableElement[0];
			
			let rowsMatches = hivePost.matchAll(IMAGE_DATA_ROW_REGEX);
			rowsMatches = Array.from(rowsMatches);
			rowsMatches.forEach(function(rowElement) {
				rowElement = rowElement[0];
				
				var titleTagMatches = rowElement.matchAll(IMAGE_TITLE_REGEX);
				titleTagMatches = Array.from(titleTagMatches);
				var title = NOT_FOUND;
				if (! (titleTagMatches.length == 0 || titleTagMatches[0].length < 2)) {
					title = titleTagMatches[0][1];
				}
				
				var tagsTagMatches = rowElement.matchAll(IMAGE_TAGS_REGEX);
				tagsTagMatches = Array.from(tagsTagMatches);
				var tags = NOT_FOUND;
				if (! (tagsTagMatches.length == 0 || tagsTagMatches[0].length < 2)) {
					tags = tagsTagMatches[0][1];
				}
				
				var urlTagMatches = rowElement.matchAll(IMAGE_URL_REGEX);
				urlTagMatches = Array.from(urlTagMatches);
				var url = NOT_FOUND;
				if (! (urlTagMatches.length == 0 || urlTagMatches[0].length < 2)) {
					url = urlTagMatches[0][1];
				}
	 
				found[url] = {
					title: title,
					tags: tags,
					url: url,
				};
			});
		});
	
		
		
		self.printLog('Images found: ' + Object.keys(found).length + '<br/>');
		

		
		self.tablesFound = found;
		
		return true;
	}
	self.findImages = function() {
		self.printLog('LIL tables found:');
	
		var found = false;
		for(var imageKey in self.tablesFound) {
			
			var image = self.tablesFound[imageKey];
			var img = image.url == NOT_FOUND ? '?' : '<img src="https://images.hive.blog/64x0/' + image.url.replace('https://images.hive.blog/0x0/', '') + '" width="64"/>';
			
			self.printLog('Title: ' + image.title + '<br/>Tags: ' + image.tags + '<br/>Image: ' + image.url + '<br/><div class="lilCheckerConsole-image">' + img + '</div><br/><br/>');
			found = true;
		} 
		
		if (!found) {
			self.printLog('Error. No LIL tables found. Please check this post <a href="https://peakd.com/hive-174695/@shaka/the-lmac-summer-special-lets-build-the-lmac-image-library" title="The LMAC Summer Special☀️: Let\'s Build the LMAC Image Library! - On Hive">Click</a> for the correct syntax for posting images to the LIL.<br/>', 'error');
		}

		return true;
	}
}




function checkLILPost() {
	checker = new LILChecker(
		document.getElementById('lilCheckerConsole'), jQuery('#hive-post').val()
	);
	taskList = [checker.init, checker.validateStructure, checker.findImages];
 
	var workerInterval = setInterval(function () {
		 
		var task = taskList.shift();
		if (task == undefined || !task()) {
			clearInterval(workerInterval);
			checker.printLog('The examination is finished!');
			jQuery('#submitToCheck').attr("disabled", false);
		}
	}, 1000);
}


(function($) {
	jQuery('#submitToCheck').click(function() {		
		jQuery('#submitToCheck').attr("disabled", true);
		checkLILPost();		
		return false;
	});
    console.debug('test');
	jQuery('#lil-snippet-copy-button').click(function(e) {

		indicatorElement = jQuery('#lil-snippet-copy-indicator');
		textBox = jQuery('#lil-checker-snippet');
		textBox.focus();
		textBox.select();

		if (typeof document.execCommand !== "undefined") {
 			document.execCommand("copy");
		}else{
			navigator.clipboard.writeText(textBox.val());
		}

		indicatorElement.html('Copied!');
		
		setTimeout(function() {
			indicatorElement.html('');
 
		}, 2000);
		

		return false;
	});
 
})(jQuery);