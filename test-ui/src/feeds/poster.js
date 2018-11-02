export default class FeedPoster {
    constructor() {
        this.token = null;
        this.element = document.createElement('div');
        this.element.style.display = 'none';
        let inputForm = `
            <div>New Notification input goes here</div>
        `;
        this.element.innerHTML = inputForm;
    }

    activate(token) {
        this.token = token;
        this.element.style.display = 'inline';
    }

    deactivate() {
        this.token = null;
        this.element.style.display = 'none';
    }
}