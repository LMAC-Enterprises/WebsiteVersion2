
class LMACPollController extends SubViewController {
    #votes = {};

    constructor() {
        super();
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

        for (const [authorperm, vote] of Object.entries(this.#votes)) {
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
                console.log(response);
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
                  console.debug(response);
                  if (response.success === true)
                  {
                        $('#lmac-poll-hive .not-logged-in').hide();
                        $('#lmac-poll-hive .logged-in').show();
                        $('#hive-login-form > input[type="text"]').attr('readonly', 'readonly');
                        $('#lmac-poll-hive .logged-in > .username').html(
                            username
                        );
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

        $('input.vote-slider').on('input', function(changeEvent){
            var sliderValue = $(this).val();
            $(this).parent('.card-footer').children('.vote-percent-display').first().html(sliderValue);
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
