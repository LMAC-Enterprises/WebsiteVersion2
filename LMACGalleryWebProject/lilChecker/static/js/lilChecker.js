class LILCheckerController extends SubViewController {
    #IMAGE_DATA_BLOCK_REGEX = new RegExp('<table class=\"lil\">([\n]+.*?)<\/table>', 'gs');
    #IMAGE_DATA_ROW_REGEX = /<tr>[\n]+.*?<\/tr>/gs;
    #IMAGE_TITLE_REGEX = /<td class="lil-title">(.+?)<\/td>/gs;
    #IMAGE_TAGS_REGEX = /<td class="lil-tags">(.+?)<\/td>/gs;
    #IMAGE_URL_REGEX = /<td class="lil-image"><img src="(.+?)" width="[0-9]+"\/><\/td>/gs;
    #FALLBACK_IMAGE_URL = '/static/images/lil-checker-fallback-image.png';

	#NOT_FOUND = '<span class="LMACLILChecker-not-found">NOT FOUND</span>';

    #cons;
	#imagesFound = [];
	#tablesFound = [];

    constructor() {
        super();
    }

    init(overallController) {
        super.init(overallViewController);

        var self = this;

        this.#cons = jQuery('#lil-checker-console');
        jQuery('#lil-checker-submit-to-check').click(function() {self.checkPost()});
    }

	#printLog(text, messageType = '') {

		var specialTagPrefix = '';
		var specialTagSuffix = '';
		var self = this;

		if (messageType == 'error') {
			specialTagPrefix = '<span class="LMACLILChecker-error">';
			specialTagSuffix = '</span>';
		}

		this.#cons.append(specialTagPrefix + text + specialTagSuffix + "<br/>");

	};

	#formatImage(title, tags, url, error) {
	    return `<div class="lil-checker-preview"><img class="lil-checker-preview-image" src="${url}" alt="Image not loadable."/><p>Title: ${title}<br />Tags: ${tags}</p><p class="LMACLILChecker-error">${error}</p></div>`;
	}

   #isValidUrl(string) {
        try {
        var url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch (err) {
            return false;
        }
    }

	checkPost() {
        var hivePost = jQuery('#lil-checker-markdown').val();

		if (hivePost.length == 0) {
			this.#printLog('ERROR!!! Can\'t check empty markdown.', 'error');
		    return false;
		}

		this.#cons.html('$ Checking Markdown...<br /><br />');

        var self = this;
		var found = {};
		let tablesMatches = hivePost.matchAll(this.#IMAGE_DATA_BLOCK_REGEX);
		tablesMatches = Array.from(tablesMatches);
		if (tablesMatches.length == 0) {
		    this.#printLog('$ Error No images found!!!', 'error');
		    return;
		}

		var imagesFound = 0;

		tablesMatches.forEach(function(tableElement) {
			tableElement = tableElement[0];

			let rowsMatches = hivePost.matchAll(self.#IMAGE_DATA_ROW_REGEX);
			rowsMatches = Array.from(rowsMatches);
			rowsMatches.forEach(function(rowElement) {
				rowElement = rowElement[0];
				var error = '';

				var titleTagMatches = rowElement.matchAll(self.#IMAGE_TITLE_REGEX);
				titleTagMatches = Array.from(titleTagMatches);
				var title = self.#NOT_FOUND;
				if (! (titleTagMatches.length == 0 || titleTagMatches[0].length < 2)) {
					title = titleTagMatches[0][1];
				}

				if (title.length > 128) {
				    error = 'Please, use a shorter title.<br/>';
				}

				var tagsTagMatches = rowElement.matchAll(self.#IMAGE_TAGS_REGEX);
				tagsTagMatches = Array.from(tagsTagMatches);
				var tags = self.#NOT_FOUND;
				if (! (tagsTagMatches.length == 0 || tagsTagMatches[0].length < 2)) {
					tags = tagsTagMatches[0][1];
				}
				if (! tags.includes(',')) {
				    error += 'Better separate tags by commas.<br/>';
				}
				if (tags.length > 200) {
				    error += 'Please, use fewer or shorter tags.<br/>';
				}

				var urlTagMatches = rowElement.matchAll(self.#IMAGE_URL_REGEX);
				urlTagMatches = Array.from(urlTagMatches);
				var url = '';
				if (! (urlTagMatches.length == 0 || urlTagMatches[0].length < 2)) {
					url = urlTagMatches[0][1];
					if (! self.#isValidUrl(url)) {
					    url = self.#FALLBACK_IMAGE_URL;
					    error += 'Image URL not valid!<br/>';
					}else{
					    url = 'https://images.hive.blog/0x90/' + url;
					}
				}
                imagesFound++;
				self.#printLog(self.#formatImage(title, tags, url, error));
			});
        });
        self.#printLog('Found ' + imagesFound + ' images.');
        this.#cons.scrollTop(this.#cons.prop("scrollHeight"));
	}
}


overallViewController.addSubViewController(new LILCheckerController());