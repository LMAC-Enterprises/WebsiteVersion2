class LMACPollCreateController extends SubViewController {
    constructor() {
        super();
    }

    #processFormValues() {
        var nominees = '';
        var beneficiaries = [];
        var commentOptions = [];
        var author = $('#lmac-poll-post-author').val();
        var body = $('#lmac-poll-post-body').val();
        var tags = $('#lmac-poll-post-tags').val().split(/[^a-zA-Z0-9]/i).filter(element => element);

        if (! tags.includes('lmacpoll')) {
            tags.push('lmacpoll');
        }

        $('.post-beneficiary-container').each(function(index, element) {
            var username = $('.post-beneficiary-username', element).val();
            var percent = $('.post-beneficiary-percent', element).val();

            if (username.length == 0 || percent.length == 0) {
                return true;
            }

            beneficiaries.push(
                {
                    'account': username,
                    'weight': parseInt(percent) * 100,
                }
            );
        });

        $('.post-nominee-container').each(function(index, element) {
            var username = $('.post-nominee-username', element).val();
            var authorPerm = $('.post-nominee-authorperm', element).val();
            var imageUrl = $('.post-nominee-image-url', element).val();

            if (username.length == 0 || authorPerm.length == 0 || imageUrl.length == 0) {
                return true;
            }

            if (! authorPerm.startsWith('/')) {
                authorPerm = '/' + authorPerm;
            }

            nominees += '---\n\n@' + username + ': [-> Original post](/' + authorPerm + ')\n\n'
            nominees += '![](' + imageUrl + ')\n\n'
            commentOptions.push(username);
        });

        body = body.replace('{nominees}', nominees);
        body = body.replace('{author}', author);

        return {
            'author': author,
            'category': $('#lmac-poll-post-category').val(),
            'title': $('#lmac-poll-post-title').val(),
            'body': body,
            'tags': tags,
            'commentOptions': commentOptions,
            'beneficiaries': beneficiaries,
            'permlink': $('#lmac-poll-post-permlink').val()
        };
    }

    #sendOptionComments(commentOptions) {
        var workerInterval = window.setInterval(function () {
            commentOption = commentOptions.pop();
            if (commentOption === undefined) {
                window.clearInterval(workerInterval);
                console.debug(workerInterval);
                return;
            }

            console.debug(commentOption);
        },
            300
        );
    }

    #submitPoll(processedValues) {

        this.overallController.startLoadingMode();
        var self = this;

        window.hive_keychain.requestPost(
            processedValues.author,
            processedValues.title,
            processedValues.body,
            processedValues.category,
            '',
            JSON.stringify({
                format: 'markdown',
                description: 'Final Poll',
                tags: processedValues.tags
            }),
            processedValues.permlink,
            JSON.stringify({
                "author": processedValues.author,
                "permlink":  processedValues.permlink,
                "max_accepted_payout":"100000.000 HBD",
                "percent_hbd":10000,
                "allow_votes":true,
                "allow_curation_rewards":true,
                "extensions":[
                        [0, {
                            "beneficiaries":processedValues.beneficiaries
                        }]
                    ]
            }), (response) => {
          console.log(response);
            if (! response.success && response.error != 'user_cancel') {
                self.overallController.showError(response.message)
                self.overallController.endLoadingMode();
            }else{
                self.#sendOptionComments(processedValues.commentOptions);
            }
        });
    }

    init(overallController) {
        super.init(overallViewController);

        if (window.hive_keychain) {
            window.hive_keychain.requestHandshake(res => {
                $('#lmac-poll-post-submit').removeAttr('disabled');
            });
            var keychain = window.hive_keychain;
        }

        var self = this;

        $('#lmac-poll-post-add-beneficiary').click(function(clickEvent) {
            clickEvent.preventDefault();

            $('.post-beneficiaries-wrapper').append('<div class="post-beneficiary-container">\n<input class="post-beneficiary-username" type="text" value="" placeholder="username" />\n<input class="post-beneficiary-percent" type="text" value="" placeholder="0" />\n<label>&percnt;</label>\n<button class="delete-beneficiary">Delete template</button>\n</div>');

            return false;
        });

        $(document).on('click', '.delete-beneficiary', function(clickEvent) {
            clickEvent.preventDefault();

            $(this).parent('.post-beneficiary-container').remove();

            return false;
        });

        $('#lmac-poll-post-add-nominee').click(function(clickEvent) {
            clickEvent.preventDefault();

            $('.post-nominees-wrapper').append('<div class="post-nominee-container"><div class="form-row"><label class="fixed-span-150">Author username:</label><input class="post-nominee-username" type="text" value="" maxlength="32" placeholder="username" /></div><div class="form-row"><label class="fixed-span-150">Author-Permlink:</label><input class="post-nominee-authorperm" type="text" value="" maxlength="256" placeholder="@author/permlink" /></div><div class="form-row"><label class="fixed-span-150">Image url:</label><input class="post-nominee-image-url" type="text" value="" maxlength="256" placeholder="https://images.hive.blog/p/HXJDKQWLJD.png" /></div><button class="delete-nominee">Delete nominee</button></div>');

            return false;
        });

        $(document).on('click', '.delete-nominee', function(clickEvent) {
            clickEvent.preventDefault();

            $(this).parent('.post-nominee-container').remove();

            return false;
        });

        $('#lmac-poll-post-export').click(function(clickEvent){
            clickEvent.preventDefault();

            var processedValues = self.#processFormValues();

            try {
              navigator.clipboard.writeText(processedValues.body);
              self.overallController.showBalloonAt('#lmac-poll-post-export', 'Successfully exported.');
            } catch (err) {
              self.overallController.showBalloonAt('#lmac-poll-post-export', 'Exporting failed.');
            }

            return false;
        });

        $('#lmac-poll-post-submit').click(function(clickEvent){
            clickEvent.preventDefault();

            var processedValues = self.#processFormValues();

            self.#submitPoll(processedValues);

            return false;
        });
    }
}

overallViewController.addSubViewController(new LMACPollCreateController());