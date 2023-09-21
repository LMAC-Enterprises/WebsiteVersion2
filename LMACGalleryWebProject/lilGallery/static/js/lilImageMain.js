class LILImageController extends SubViewController {
    constructor(csrfToken) {
        super();

        this.csrfToken = csrfToken;
    }

    init(overallController) {
        super.init(overallViewController);
        this.#initDownloadImageHandling();
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

}

overallViewController.addSubViewController(new LILImageController());
