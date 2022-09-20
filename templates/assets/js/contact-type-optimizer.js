class UnifyEmailContactType {
    _baseOptions = {
        buttonSelector: '#unify-email-contact-type-button',
        toolbarSelector: '#toolbar',
        alertWrapperSelector: '#alert-wrapper',


        loadingText: 'Loading...',
        unknownErrorText: 'Unknown error raised!',
        serverErrorText: 'Optimizing contact types failed:'
    };

    constructor($, options = {}) {
        this.$ = $;
        this.options = {...this._baseOptions, ...options};

        this.triggerButton = null;
        this.triggerButtonOriginalText = '';

        this.toolbar = null;
        this.alertWrapper = null;
    }

    init = () => {
        this.triggerButton = this.$(this.options.buttonSelector);
        this.triggerButton.off('click');
        this.triggerButton.on('click', this.handleOnClick);
        this.triggerButtonOriginalText = this.triggerButton.text();

        this.toolbar = this.$(this.options.toolbarSelector);
        this.alertWrapper = this.$(this.options.alertWrapperSelector);

        if (!this.alertWrapper.length) {
            const alertWrapperId = this.options.alertWrapperSelector.replace('#', '');
            this.toolbar.parent().prepend(`<div id="${alertWrapperId}"></div>`);
            this.alertWrapper = this.$(this.options.alertWrapperSelector);
        }
    };

    handleOnClick = async (e) => {
        e.preventDefault();

        this.setTriggerButtonLoading(true);
        try {
            const response = await this.handleSendRequest();
            const {message} = response;
            this.renderSuccessAlert(
                `<p style="margin-bottom: 0;">${message}</p>`
            );
            this.setTriggerButtonLoading(false);
        } catch (error) {
            this.setTriggerButtonLoading(false);
            const {status, statusText, responseJSON} = error;

            if (!status) {
                this.renderErrorAlert(
                    `<p style="margin-bottom: 0;">${this.options.unknownErrorText}</p>`
                )
                console.error(error);
                return;
            }

            if (status !== 400) {
                const message = `${this.options.serverErrorText} [HTTP ${status}] ${statusText}`;
                this.renderErrorAlert(
                    `<p style="margin-bottom: 0;">${message}</p>`
                );
                return;
            }

            const {message} = responseJSON;
            this.renderErrorAlert(
                `<p style="margin-bottom: 0;">${message}</p>`
            );
        }
    };

    setTriggerButtonLoading = value => {
        this.triggerButton.prop('disabled', value);
        this.triggerButton.text(
            value
                ? this.options.loadingText
                : this.triggerButtonOriginalText
        );
    };

    handleSendRequest = async () => {
        const url = this.triggerButton.attr('href');
        return this.$.ajax({
            url,
            method: 'GET',
            headers: {'X-CsrfToken': UnifyEmailContactType.getCookie('csrftoken')},
            type: 'json',
        });
    };

    renderErrorAlert = (message) => {
        this.alertWrapper.html(
            [
                '<div class="alert alert-danger">',
                message,
                '</div>'
            ].join('\n')
        );
    }

    renderSuccessAlert = (message) => {
        this.alertWrapper.html(
            [
                '<div class="alert alert-success">',
                message,
                '</div>'
            ].join('\n')
        );
    };

    // utils
    static getCookie = (name) => {
        const matches = document.cookie.match(new RegExp(
            "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
        ));
        return matches ? decodeURIComponent(matches[1]) : undefined
    }
}