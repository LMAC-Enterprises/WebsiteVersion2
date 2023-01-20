class BeeJobJsComment {
    author = '';
    permlink = '';
    title = '';
    body = '';
    parentPermlink = '';
    parentAuthor = '';
    #beneficiaries = []
    #beeJobJsController = null;

    constructor(beeJobJsController) {
        this.#beeJobJsController = beeJobJsController;
    }

    setBeneficiary(username, percent) {
        this.#beneficiaries.push(
            {
                'account': username,
                'weight': parseInt(percent) * 100,
            }
        );
    }

    get beneficiaries() {
        return this.#beneficiaries;
    }

    save() {
        var self = this;

        window.hive_keychain.requestPost(
            this.author,
            this.title,
            this.body,
            this.parentPermlink,
            this.parentAuthor,
            JSON.stringify({
                format: 'markdown',
                description: 'Final Poll',
                tags: this.tags
            }),
            processedValues.permlink,
            JSON.stringify({
                "author": this.author,
                "permlink":  this.permlink,
                "max_accepted_payout":"100000.000 HBD",
                "percent_hbd":10000,
                "allow_votes":true,
                "allow_curation_rewards":true,
                "extensions":[
                        [0, {
                            "beneficiaries": this.#beneficiaries
                        }]
                    ]
            }), (response) => {
            if (! response.success && response.error != 'user_cancel') {
                self.#beeJobJsController.debug('BeeJobJsComment.save', 'response', response);
                self.overallController.showError(response.message)
                self.overallController.endLoadingMode();
            }else if(! response.success && response.error == 'user_cancel') {

            }else{
                self.#beeJobJsController.debug('BeeJobJsComment.save', 'response', response);
                self.#sendOptionComments(processedValues.commentOptions);
            }
        });
    }
}


class BeeJobJsController {
    #debugMode = false;
    #remoteRPC = null;
    #initialized = false;

    constructor(debugMode = false) {
        this.#debugMode = debugMode;
        var self = this;

        if (this.#debugMode) {
            this.#remoteRPC = 'https://testnet.openhive.network';
        }

        window.addEventListener('DOMContentLoaded', function() {
            self.#init();
        }, true);
    }

    #init() {
        if (window.hive_keychain) {
            window.hive_keychain.requestHandshake(res => {
                $('#lmac-poll-post-submit').removeAttr('disabled');
            });
            this.#initialized = true;
        }
    }

    debug(source, context, data) {
        if (! this.#debugMode) {
            return;
        }

        console.debug(
            `${source} (${context}):\n`,
            data
        );
    }

    get debugMode() {
        return this.#debugMode;
    }

    get initialized() {
        return this.#initialized;
    }

    newComment() {
        if (! this.#initialized) {
            throw Error('BeeJobJsController object not initialized.');
        }

        return new BeeJobJsComment(this);
    }
}


var beeJobJs = new BeeJobJsController(true);

