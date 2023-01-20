class LILGalleryController extends SubViewController {
    csrfToken = '';
    currentSearchTerms = '';
    currentPage = 1;

    constructor(csrfToken) {
        super();

        this.csrfToken = csrfToken;
        this.#initPagination();
    }

    #processSearchTerms(searchTerms, breakDown = false) {
        searchTerms = searchTerms.trim().toLowerCase();

        if (searchTerms.length == 0) {
            return breakDown ? ['all'] : 'all';
        }

        return breakDown ?
                searchTerms.replace(/[^0-9a-z\-\., ]/gi, '').split(/[ ,\s]+/) :
                searchTerms.replace(/[^0-9a-z\-\., ]/gi, '');
    }

    init(overallController) {
        super.init(overallViewController);
        this.#initPagination();
        this.#initSearchForm();
        this.#initOpenImageHandling();
        this.#initDownloadImageHandling();
        this.#initFiveStarRating();
    }

    updateUrl() {
        var mixMode = '';
        if ('mode' in $.QueryString) {
            mixMode = '?mode=mix';
        }
        window.history.pushState({}, '', '/lil-gallery/' + this.currentSearchTerms + '/' + this.currentPage + mixMode);
    }

    onSearchFormSubmit(e) {
        var self = this;
        e.preventDefault();

        this.currentSearchTerms = this.#processSearchTerms($('#lil-gallery-form-search').val());
        this.currentPage = 1;

        this.overallController.loadHtmlInto(
            '/lil-gallery-ajax',
            '#lil-gallery-content',
            $('input[name="csrfmiddlewaretoken"]').val(),
            {
                'searchTerms': this.currentSearchTerms,
                'page': 1
            },
            false,
            20,
            function(status, responseObject) {
                self.updateUrl();
               $('#lil-search-result-info-number').html(responseObject.getResponseHeader('lil-images-amount'));
            }
        );

        return false;
    }

    onLoadButtonClicked(e, direction) {
        var self = this;
        e.preventDefault();
        this.overallController.loadHtmlInto(
            '/lil-gallery-ajax',
            '#lil-gallery-content',
            $('input[name="csrfmiddlewaretoken"]').val(),
            {
                'searchTerms': this.currentSearchTerms,
                'page': this.currentPage + direction
            },
            true,
            50,
            function(status, responseText = '') {
                if (status != 200) {
                    self.overallController.showError(responseText);
                }

                self.currentPage += direction;
                self.updateUrl();
                if (self.currentPage <= 1) {
                    self.currentPage = 1;
                    $('#lil-gallery-load-previous').hide();
                }else{
                    $('#lil-gallery-load-previous').show();
                }
            }
        );

        return false
    }

    onLoadPreviousButtonClicked() {

    }

    #initPagination() {
        var self = this;
        $('#lil-gallery-load-more').click(function(e) { return self.onLoadButtonClicked(e, 1);});
        $('#lil-gallery-load-previous').click(function(e) { return self.onLoadButtonClicked(e, -1);});
    }

    #initSearchForm() {
        var self = this;
        this.currentSearchTerms = this.#processSearchTerms($('#lil-gallery-form-search').val());
        $('#lil-gallery-form').submit(function(e) {return self.onSearchFormSubmit(e);})
    }

    #initOpenImageHandling() {
        var self = this;

        $(document).on('click', '.lil-gallery-image-link', function(e) {
            e.preventDefault();
            self.overallController.loadInModal(
                '/lil-gallery-ajax-image',
                {
                    'imageId': $(this).data('image-id')
                }
            );
            return false;
        });
    }

    #initDownloadImageHandling() {
        var self = this;

        $(document).on('click', '#lil-gallery-image-download-close-button', function(e) {
            $('#lil-gallery-image-download-modal-wrapper').hide();
             self.overallController.closeBalloonAt('#lil-gallery-image-copy-snipped-button');
        });

        $(document).on('click', '#lil-gallery-image-download-button', function(e) {
            $('#lil-gallery-image-download-modal-wrapper').show();
        });

        $(document).on('click', '#lil-gallery-image-final-download-button', function(e) {
            $('#lil-gallery-image-download-modal-wrapper').hide();
        });

        $(document).on('click', '#lil-gallery-image-copy-snipped-button', function(e) {
            navigator.clipboard.writeText(
                $('#lil-gallery-image-download-modal-wrapper textarea').text()
            ).then(
              () => {
                self.overallController.showBalloonAt(
                    '#lil-gallery-image-copy-snipped-button',
                    'Copied to clipboard.'
                );
              },
              () => {
                self.overallController.showBalloonAt(
                    '#lil-gallery-image-copy-snipped-button',
                    'Wasn\'t able to copy snippet to clipboard.'
                );
              }
            );
        });
    }

    #initFiveStarRating() {
        var self = this;

        $(document).on('click', '.lil-rating-star', function(e) {
            var imageId = $(this).data('image-id');
            var ratingRate = $(this).data('rating-rate');
            var starList = $(this).parents('ul.lil-fivestar-list:first');

            self.overallController.sendAjaxCommandRequest(
                '/lil-gallery-ajax-command',
                'doFiveStarVote',
                {
                    'imageId': imageId,
                    'ratingRate': ratingRate
                },
                function(status, receivedData) {
                    starList.children('li').each(function(index, element){
                        var starElement = $('span', element);
                        if (starElement.data('rating-rate') <= ratingRate) {
                            starElement.html('&#128420;'); // SET
                        }else{
                            starElement.html('&#9825;'); // UNSET
                        }
                    })
                },
                function(status, responseText) {
                    self.overallController.showError(responseText);
                }
            );
        });
    }
}

overallViewController.addSubViewController(new LILGalleryController());
