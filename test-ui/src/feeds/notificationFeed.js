import * as Feeds from '../api/feeds';
import Notification from './notification';

export default class NotificationFeed {
    constructor() {
        this.token = null;
        this.notes = [];
        this.element = document.createElement('div');
    }

    initialize(token) {
        this.token = token;
        this.removeFeed();
        this.refreshFeed();
    }

    removeFeed() {
        this.element.innerHTML = '';
    }

    refreshFeed() {
        Feeds.getNotifications({token: this.token})
            .then(feed => {
                console.log(feed);
                this.renderFeed(feed.data);
            })
            .catch(err => {
                this.renderError(err);
            });
    }

    renderFeed(feed) {
        this.notes = [];
        feed.user.forEach(note => {
            let feedElem = document.createElement('div');
            this.element.appendChild(feedElem);
            this.notes.push(new Notification(note, feedElem));
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