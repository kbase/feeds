import * as Feeds from '../api/feeds';

export default class Notification {
    /**
     *
     * @param {object} note
     * has keys: actor, context, created, expires, id, level, object, source, verb
     */
    constructor(note, token, refreshFn) {
        this.note = note;
        this.token = token;
        this.refreshFn = refreshFn;
        this.element = document.createElement('div');
        this.element.classList.add('row', 'alert');
        this.render();
    }

    render() {
        let text = '';
        if (this.note.context && this.note.context.text) {
            text = this.note.context.text;
        }
        this.element.innerHTML = `
            <div class="col-1">${this.renderLevel()}</div>
            <div class="col-10">${this.renderBody()}</div>
            <div class="col-1">${this.renderControl()}</div>
        `;
        this.bindEvents();
    }

    renderBody() {
        let text = `
            <div>${this.renderMessage()}</div>
        `;
        let infoStamp = `
            <small>${this.renderCreated()} - ${this.note.source}</small>
        `;
        return text + infoStamp;
    }

    renderControl() {
        return this.renderSeen();
    }

    renderLevel() {
        let icon = 'fas fa-info';
        switch(this.note.level) {
            case 'error':
                icon = 'fas fa-ban';
                this.element.classList.add('alert-danger');
                break;
            case 'request':
                icon = 'fas fa-question-circle';
                this.element.classList.add('alert-success');
                break;
            case 'warning':
                icon = 'fas fa-exclamation-triangle';
                this.element.classList.add('alert-warning');
                break;
            case 'alert':
            default:
                icon = 'fas fa-info';
                this.element.classList.add('alert-primary');
        }
        return `<span style="font-size: 1.5em;"><i class="${icon}"></i></span>`;
    }

    renderSeen() {
        let icon = "fa fa-times";
        if (this.note.seen) {
            icon = "far fa-eye";
        }
        return `
            <span style="font-size: 1.5em; cursor: pointer;" id="seen-icon">
                <i class="${icon}"></i>
            </span>
        `;
    }

    renderCreated() {
        let date = new Date(this.note.created);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }

    renderSource() {
        return this.note.source;
    }

    renderMessage() {
        if (this.note.context && this.note.context.text) {
            return this.note.context.text;
        }
        else {
            return this.note.actor + ' ' + this.note.verb + ' ' + this.note.object;
        }
    }

    bindEvents() {
        this.element.querySelector('#seen-icon').onclick = () => {
            let action;
            if (this.note.seen) {
                action = Feeds.markUnseen([this.note.id], this.token);
            }
            else {
                action = Feeds.markSeen([this.note.id], this.token);
            }
            action.then(() => { this.refreshFn() } );
        }
    }
}