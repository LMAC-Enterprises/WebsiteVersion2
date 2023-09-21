
class LMACPollController extends SubViewController {
    #votes = {};

    constructor() {
        super();
    }

    #reloadDelayed(delay) {
        var self = this;
        this.overallController.startLoadingMode();

        window.setTimeout(function() {
            self.#acquireUserVotes($('#hive-login-form > input[type="text"]').val())
        }, delay);
    }

    #setVote(author, permlink, voteValue) {
        this.#votes[author + '/' + permlink] = {
            'author': author,
            'permlink': permlink,
            'weight': voteValue * 100
        };
    }

    #sendVotesViaKeychain() {
        var operations = [];
        var username = $('#hive-login-form > input[type="text"]').val();
        var self = this;

        for (const [authorperm, vote] of Object.entries(this.#votes)) {
            if (vote['weight'] <= 0) {
                continue;
            }
            operations.push([
                'vote',
                {
                    voter: username,
                    author: vote['author'],
                    permlink: vote['permlink'],
                    weight: vote['weight']
                }
            ]);
        }

        window.hive_keychain.requestBroadcast(
            username,
            operations,
            'Posting',
            (response) => {
                self.#reloadDelayed(5000);
            }
        );
    }

    #getCurrentPollPostPermlink() {
        var segments = window.location.pathname.split('/');

        return segments[2] + '/' + segments[3];
    }

    #acquireUserVotes(username) {
        var username = $('#hive-login-form > input[type="text"]').val();
        var self = this;

        this.overallController.sendAjaxCommandRequest(
            '/lmac-poll-ajax-command',
            'loadUserVotes',
            {
                'username': username,
                'pollPostPermlink': self.#getCurrentPollPostPermlink(),
            },
            function(status, receivedData) {
                for (let permlink in receivedData['votes']) {
                    $('.vote-slider[data-comment-permlink="' + permlink + '"]').val(receivedData['votes'][permlink]).trigger('input');
                }
                self.overallController.endLoadingMode();
            },
            function(status, responseText) {
                self.overallController.showError(responseText);
            }
        );

    }

    #initHiveLogin() {

        if (window.hive_keychain) {
            window.hive_keychain.requestHandshake(res => {
                $('#hive-login-keychain-login-button').removeAttr('disabled');
            });
            var keychain = window.hive_keychain;
        }

        var self = this;

        $('#hive-login-keychain-login-button').click(function(clickEvent){
              var username = $('#hive-login-form > input[type="text"]').val();
              keychain.requestSignBuffer(username, username + Date.now(), "Posting", (response) => {
                  if (response.success === true)
                  {
                        $('#lmac-poll-hive .not-logged-in').hide();
                        $('#lmac-poll-hive .logged-in').show();
                        $('#hive-login-form > input[type="text"]').attr('readonly', 'readonly');
                        $('#lmac-poll-hive .logged-in > .username').html(
                            username
                        );
                        self.#acquireUserVotes(username);
                  }else{
                        $('#lmac-poll-hive .not-logged-in').show();
                        $('#lmac-poll-hive .logged-in').hide();
                        self.overallController.showError('Login failed.');
                  }
            }, null, 'Authenticate');
        });

        $('#hive-login-keychain-send-button').click(function(clickEvent){
            self.#sendVotesViaKeychain();
            return false;
        });

        $('#lmac-poll-hive .logged-in .logout').click(function(clickEvent) {
            clickEvent.preventDefault();

            $('#hive-login-form > input[type="text"]').removeAttr('readonly');
            $('#lmac-poll-hive .not-logged-in').show();
            $('#lmac-poll-hive .logged-in').hide();

            return false;
        });
    }

    #initVotingMechanism() {

        var self = this;

        $('input.vote-percent-display').on('input', function(changeEvent){
            var value = parseInt($(this).val());
            if (value < 0) {
                value = 0;
            }
            if (value > 100) {
                value = 100;
            }

            var voteSlider = $(this).parent('.card-footer').children('.vote-slider');

            voteSlider.val(value);
            $(this).parent('.card-footer').children('.vote-percent-display').first().val(value);

            self.#setVote(
                 voteSlider.data('comment-author'),
                 voteSlider.data('comment-permlink'),
                 value
            );
        });


        $('input.vote-slider').on('input', function(changeEvent){
            var sliderValue = $(this).val();
            $(this).parent('.card-footer').children('.vote-percent-display').first().val(sliderValue);
            self.#setVote(
                 $(this).data('comment-author'),
                 $(this).data('comment-permlink'),
                sliderValue
            );
        });
    }

    init(overallController) {
        super.init(overallViewController);

        this.#initVotingMechanism();
        this.#initHiveLogin();
    }
}

overallViewController.addSubViewController(new LMACPollController());
