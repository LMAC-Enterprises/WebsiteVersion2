(function($) {
    $.QueryString = (function(a) {
        if (a == "") return {};
        var b = {};
        for (var i = 0; i < a.length; ++i)
        {
            var p=a[i].split('=');
            if (p.length != 2) continue;
            b[p[0]] = decodeURIComponent(p[1].replace(/\+/g, " "));
        }
        return b;
    })(window.location.search.substr(1).split('&'))
})(jQuery);


class SubViewController {
    overallViewController;

    init(overallViewController) {
        this.overallViewController = overallViewController
    }

    get overallController() {
        return this.overallViewController;
    }

    onDocumentDirty() {}
}

class OverallViewController {
    subViewControllers = [];
    #urlBeforeUpdate = null;

    init() {
        var self = this;
        window.onload = () => {
            self.initBurgerMenu();
            self.initModal();
            self.initTabs();
            self.initCollapsibleFieldsets();

            for (const subViewController of self.subViewControllers) {
                subViewController.init(self);
            }
        };
    }

    constructor() {
        this.init();
    }

    showBalloonAt(element, html) {
        $(element).showBalloon({
          showDuration: 10,
          hideDuration: 500,
          position: 'top',
          html: true,
          classname: 'balloon-tooltip',
          css: {},
          contents: html,
        });
    }

    showError(errorMessage) {
        $('#error-container').html(
            errorMessage
        ).show();
        $([document.documentElement, document.body]).animate({
                scrollTop: $("#error-container").offset().top
            }, 1000);
    }

    hideErrors() {
        $('#error-container').html(
            ''
        ).hide();
    }

    closeBalloonAt(element) {
        $(element).hideBalloon();
    }

    updateUrlTo(path) {
        this.#urlBeforeUpdate = window.location.pathname;
        window.history.pushState({}, '', path);

    }
    undoUpdatedUrl() {
        if (this.#urlBeforeUpdate == null) {
            return;
        }
        window.history.pushState({}, '', this.#urlBeforeUpdate);
    }

    setDocumentDirty() {
        for (const subViewController of this.subViewControllers) {
            subViewController.onDocumentDirty();
        }
    }

    createCookie(name, value, days) {
        if (days) {
            var date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            var expires = "; expires=" + date.toGMTString();
        }
        else var expires = "";

        document.cookie = name + "=" + value + expires + "; path=/";
    }

    readCookie(name, defaultValue = null) {
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        for (var i = 0; i < ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') c = c.substring(1, c.length);
            if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
        }
        return defaultValue;
    }

    removeCookie(name) {
        this.createCookie(name, "", -1);
    }

    addSubViewController(subViewController) {
        this.subViewControllers.push(subViewController);
    }

    onBurgerMenuButtonClicked() {
        $('.mobile-menu-items').toggleClass('active');
        $('#burger-menu-button').toggleClass('active');
    }

    onModalCloseButtonClicked() {
        $('.modal-content').empty();
        $('#modal-wrapper').hide();
    }

    onTabClicked(element, updatePath = true) {
        var tabsParent = element.parent('.tabs');
        var forTabs = $('.tab-site', '#' + tabsParent.data('for'));

        if (updatePath) {
            this.updateUrlTo(element.data('path'));
        }

        $('.tab', tabsParent).each(function(index, tabElement) {
            if (element.is(tabElement)) {
                if (! $(tabElement).hasClass('active')) {
                    $(tabElement).addClass('active');
                    $('#' + $(tabElement).data('for')).addClass('active');
                }
            }else{
                $(tabElement).removeClass('active');
                $('#' + $(tabElement).data('for')).removeClass('active');
            }
        });
    }

    initCollapsibleFieldsets() {
        $('fieldset.collapsible > legend').on('click', function() {
            $(this).parent().toggleClass('collapsed');
        });
    }

    initBurgerMenu() {
        $('#burger-menu-button').on('click', this.onBurgerMenuButtonClicked);
    }

    initModal() {
        $('.modal-container > .close-button').click(this.onModalCloseButtonClicked);
    }

    initTabs() {
        var self = this;

        $('.tabs > .tab').each(function(index, element) {
            element = $(element);
            if (window.location.pathname == element.data('path')) {
                self.onTabClicked(element);
            }
        });
        $('.tabs > .tab').click(function(clickEvent) {
            clickEvent.preventDefault();
            self.onTabClicked($(this));
            return false;
        });
    }

    startLoadingMode() {
        $('#modal-wrapper').hide();
        $('#load-indicator').show();
    }
    endLoadingMode() {
        $('#load-indicator').hide();
    }

    loadHtmlInto(path, destinationId, csrfToken, data = {}, appendMode = false, limitChildren = 0, doneCallback = null) {
        this.startLoadingMode();

        var self = this;

        var metaData = {
            'csrfmiddlewaretoken': csrfToken,
            'data': data
        }

        $.post(path, metaData)
            .fail(function(jqXHRObject) {
                self.endLoadingMode();
                if (doneCallback != null) {
                    doneCallback(jqXHRObject.status, jqXHRObject.responseText);
                }
            })
            .done(function(receivedData, responseAnswer, responseObject) {
                if (appendMode) {
                    $(destinationId).append(receivedData);
                    var children = $(destinationId).children();
                    var childrenCounted = children.length;
                    if (limitChildren > 0 && childrenCounted > limitChildren) {
                        children.slice(0, childrenCounted - limitChildren).remove();
                    }
                }else{
                    $(destinationId).html(receivedData);
                }

                self.endLoadingMode();
                self.setDocumentDirty();
                self.hideErrors();

                if (doneCallback != null) {
                    doneCallback(200, responseObject);
                }
        });
    }

    loadInModal(path, parameters) {
       this.loadHtmlInto(
           path,
           '#modal-wrapper .modal-content',
           this.readCookie('csrftoken'),
           parameters,
           false,
           0,
           function() {
                $('#modal-wrapper').show();
           }
       );
    }

    sendAjaxCommandRequest(path, command, parameters, doneCallback, failCallback) {
        this.startLoadingMode();

        var self = this;

        var metaData = {
            'csrfmiddlewaretoken': this.readCookie('csrftoken'),
            'data': JSON.stringify({
                'command': command,
                'parameters': parameters
            })
        }

        $.post(path, metaData)
            .fail(function(jqXHRObject) {
                self.endLoadingMode();
                if (doneCallback != null) {
                    doneCallback(jqXHRObject.status, jqXHRObject.responseText);
                }
            })
            .done(function(receivedData) {
                if (doneCallback != null) {
                    doneCallback(200, receivedData);
                }

                self.endLoadingMode();
                self.setDocumentDirty();
        });
    }
}

var overallViewController = new OverallViewController();

class DappLinkSelectorView extends SubViewController {
    dappPrefix = 'https://peakd.com/';

    constructor() {
        super();
    }

    updateDappLinks() {
        var self = this;
        $('.dynamic-dapp-link').each(function(element, index) {
            var path = $(this).data('path');
            if (path.startsWith('https://')) {
                var relativePath = new URL('', path).pathname;
                if (relativePath.startsWith('/')) {
                    relativePath = relativePath.substring(1);
                }
                path = relativePath;
            }


            $(this).attr('href', self.dappPrefix + path);
        });
    }

    setPrefix(prefix, updateCookies = true) {
        if (updateCookies) {
            this.overallController.removeCookie('hiveDappPrefix');
            this.overallController.createCookie('hiveDappPrefix', prefix, 14);
        }
        this.dappPrefix = prefix;
        this.updateDappLinks();
    }

    init(overallController) {
        super.init(overallViewController);

        var self = this;

        $('#dapp-link-box-toggler > a').click(function(e) {
            e.preventDefault();
            $('#dapp-links-wrapper').toggle();
            return false;
        });

        $('#dapp-links-wrapper li.dapp-icon').click(function(e) {
            $('.dapp-icon').removeClass('active');
            $(this).addClass('active');
            self.setPrefix($(this).data('prefix'));
            $('#dapp-links-wrapper').toggle();
        });

        this.setPrefix(this.overallController.readCookie('hiveDappPrefix', self.dappPrefix), false);
        $('#dapp-links-wrapper li.dapp-icon').each(function(index, element){
            if ($(element).data('prefix') == self.dappPrefix) {
                $('.dapp-icon').removeClass('active');
                $(element).addClass('active');
                return false;
            }
        });
    }

    onDocumentDirty() {
        this.updateDappLinks();
    }
}

overallViewController.addSubViewController(new DappLinkSelectorView());