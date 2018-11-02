import * as Feeds from '../api/feeds';

export default class NotificationFeed {
    constructor() {
        this.token = null;
        this.notes = {};
        this.element = document.createElement('div');
    }

    renderFeed(token) {
        this.token = token;
        this.refreshFeed();
    }

    removeFeed() {
        this.element.innerHTML = '';
    }

    refreshFeed() {
        Feeds.getNotifications({token: this.token})
            .then(feed => {
                console.log(feed);
            })
            .catch(err => {
                this.renderError(err);
            });
    }

    renderError(err) {
        console.log(err);
        console.log(JSON.stringify(err));
        this.element.innerHTML = `
            <div class="alert alert-danger">
                An error occurred while fetching your feed!
            </div>
        `;
    }
}