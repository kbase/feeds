import * as FeedsAPI from '../api/feeds';
import Feed from './feed';

export default class FeedController {
    constructor() {
        this.token = null;
        this.notes = [];
        this.element = document.createElement('div');
        this.element.style.display = 'none';

        this.header = document.createElement('h2');
        this.header.innerText = "Notification Feed";
        this.header.style.paddingTop = '20px';

        this.globalFeed = new Feed('Global');
        this.userFeed = new Feed();

        this.element.appendChild(this.header);
        this.element.appendChild(this.globalFeed.element);
        this.element.appendChild(this.userFeed.element);
    }

    initialize(displayName, token) {
        this.token = token;
        this.displayName = displayName;
        this.userFeed.setUserName(displayName + "'s");
        this.removeFeed();
        this.refreshFeed();
    }

    removeFeed() {
        this.element.style.display = 'none';
        this.globalFeed.remove();
        this.userFeed.remove();
    }

    refreshFeed() {
        FeedsAPI.getNotifications({}, this.token)
            .then(feed => {
                console.log(feed);
                this.renderFeed(feed.data);
            })
            .catch(err => {
                this.renderError(err);
            });
    }

    renderFeed(feed) {
        this.removeFeed();
        this.globalFeed.updateFeed(feed.global, this.token);
        this.userFeed.updateFeed(feed.user, this.token);
        this.element.style.removeProperty('display');
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