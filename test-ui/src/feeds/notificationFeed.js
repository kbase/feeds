import * as Feeds from '../api/feeds';

export default class NotificationFeed {
    constructor() {
        this.notes = {};
        this.element = document.createElement('div');
    }

    renderFeed(token) {
        this.element.innerHTML = 'Feed!';
    }

    removeFeed(token) {
        this.element.innerHTML = '';
    }
}