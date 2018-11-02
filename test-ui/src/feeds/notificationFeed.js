import * as Feeds from '../api/feeds';
import Notification from './notification';

export default class NotificationFeed {
    constructor() {
        this.token = null;
        this.notes = [];
        this.element = document.createElement('div');
        this.element.style.display = 'none';

        this.header = document.createElement('h2');
        this.header.innerText = "Notification Feed";

        this.globalCard = document.createElement('div');
        this.globalCard.classList.add('card');
        this.globalCard.innerHTML = `
            <div class="card-header">Global notifications</div>
            <div class="card-body"></div>
        `;

        this.userCard = document.createElement('div');
        this.userCard.classList.add('card');
        this.userCard.innerHTML = `
            <div class="card-header">
                <span id="user-feed-name"></span>'s notifications
            </div>
            <div class="card-body"></div>
        `;

        this.element.appendChild(this.header);
        this.element.appendChild(this.globalCard);
        this.element.appendChild(this.userCard);
    }

    initialize(displayName, token) {
        this.token = token;
        this.displayName = displayName;
        this.removeFeed();
        this.refreshFeed();
    }

    removeFeed() {
        this.element.style.display = 'none';
        this.globalCard.querySelector('.card-body').innerHTML = '';
        this.userCard.querySelector('.card-body').innerHTML = '';
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
        let globalBody = this.globalCard.querySelector('.card-body');
        let globalFeed = document.createElement('div');
        globalFeed.classList.add('container');
        globalBody.appendChild(globalFeed);

        let userBody = this.userCard.querySelector('.card-body');
        let userFeed = document.createElement('div');
        userFeed.classList.add('container');
        userBody.appendChild(userFeed);

        feed.global.forEach(note => {
            let noteObj = new Notification(note);
            this.notes.push(noteObj);
            globalFeed.appendChild(noteObj.element);
        });

        this.userCard.querySelector('#user-feed-name').innerHTML = this.displayName;
        feed.user.forEach(note => {
            let noteObj = new Notification(note);
            this.notes.push(noteObj);
            userFeed.appendChild(noteObj.element);
        });
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