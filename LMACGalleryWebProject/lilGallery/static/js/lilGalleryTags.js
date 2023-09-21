class LILGalleryTagsController extends SubViewController {
    constructor() {
        super();
        var self = this;
        $(document).ready(function() {
            self.#initTopTagsCloud();
            self.#initAllTags();
        });
    }

    #initTopTagsCloud() {
        $('#lil-top-tags-cloud').tx3TagCloud({
                multiplier: 3
        });
    }

    #initAllTags() {
        $('#lil-gallery-search-selected-tags-button').click(function(clickEvent) {
            var tags = [];

            $("#lil-gallery-selected-tags div").each(function(index, element) {
                tags.push(
                    $(element).data('tag')
                );
            });

            window.location.href = '/lil-gallery/' + tags.join(',') + '?mode=mix';
        });

        $('.lil-gallery-selectable-tag a').click(function(clickEvent){
            clickEvent.preventDefault();
            return true;
        });

        $('.lil-gallery-selectable-tag').click(function(clickEvent) {
            var tag = $(this).data('tag');
            var cssClass = $(this).attr('class').split(/\s/)[1];

            if ($("#lil-gallery-selected-tags div").length < 7) {
                $('#lil-gallery-selected-tags').append(
                    '<div class="lil-gallery-selected-tag ' + cssClass + '" data-tag="' + tag + '">' + tag + '</div>'
                );
                $(this).hide();
            }
        });

        $(document).on('click', '.lil-gallery-selected-tag', function(clickEvent) {
            var element = $(this);
            var tag = element.data('tag');
            element.remove();
            $('.lil-gallery-selectable-tag[data-tag="' + tag + '"').show();
        });
    }
}

overallViewController.addSubViewController(new LILGalleryTagsController());