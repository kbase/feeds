export default class Notification {
    /**
     *
     * @param {object} note
     * has keys: actor, context, created, expires, id, level, object, source, verb
     */
    constructor(note) {
        this.note = note;
        this.element = document.createElement('div');
        this.element.classList.add('row');
        this.render();
    }

    render() {
        let text = '';
        if (this.note.context && this.note.context.text) {
            text = this.note.context.text;
        }
        this.element.innerHTML = `
            <div class="col-1">${this.renderLevel()}</div>
            <div class="col-1">${this.renderSeen()}</div>
            <div class="col-2">${this.renderCreated()}</div>
            <div class="col-1">${this.renderSource()}</div>
            <div class="col-7">${this.renderMessage()}</div>
        `;
    }

    renderLevel() {
        let icon = 'fas fa-info';
        switch(this.note.level) {
            case 'error':
                icon = 'fas fa-ban';
                break;
            case 'request':
                icon = 'fas fa-question-circle';
                break;
            case 'warning':
                icon = 'fas fa-exclamation-triangle';
                break;
            case 'alert':
            default:
                icon = 'fas fa-info';
        }
        return `<span><i class="${icon}"></i></span>`;
    }

    renderSeen() {
        if (!this.note.seen) {
            return '<span><i class="far fa-eye"></i></span>';
        }
        return '';
    }

    renderCreated() {
        let date = new Date(this.note.created);
        return date.toLocaleDateString() + '<br>' + date.toLocaleTimeString();
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
}