import * as Feeds from '../api/feeds';

export default class GlobalFeedPoster {
    constructor(afterSubmitFn) {
        this.token = null;
        this.element = document.createElement('div');
        this.element.style.display = 'none';
        this.element.classList.add(['card']);
        const verbs = ['invite', 'accept', 'reject', 'share', 'unshare', 'join', 'leave', 'request', 'update'];
        const levels = ['alert', 'warning', 'error', 'request'];
        this.afterSubmitFn = afterSubmitFn;

        this.element.innerHTML = `
            <div class='card-header'>
                <b>Global Notification</b> - create a new global notification. Everyone gets to see this.
                <div class="btn btn-primary float-right" data-toggle="collapse" href="#globalFeedInput">
                    <span>
                        <i class="fa fa-toggle-off"></i>
                    </span>
                </div>
            </div>
            <div class='card-body collapse' id="globalFeedInput">
                <div class='form-group mx-sm-3 mb-2'>
                    <label for="verb-select"><b>Verb</b> - this tells the notification what's happening.</label>
                    <select class="form-control custom-select" id="verb-select">
                        ${verbs.map(verb => `<option value="${verb}">${verb}</option>`)}
                    </select>
                </div>
                <div class='form-group mx-sm-3 mb-2'>
                    <label for="object-input"><b>Object</b> - this field sets the notification to what the event is affecting.</label>
                    <input class="form-control" id="object-input" placeholder="Enter object" />
                    <small class="form-text text-muted"></small>
                </div>
                <div class='form-group mx-sm-3 mb-2'>
                    <label for="level-select"><b>Level</b> - this sets the "importance" of a notification, useful for filtering</label>
                    <select class="form-control custom-select" id="level-select">
                        ${levels.map(level => `<option value="${level}">${level}</option>`)}
                    </select>
                </div>
                <div class='form-group mx-sm-3 mb-2'>
                    <label for="context-input"><b>Context keys</b> - these are optional. If present, they will provide a link and specific text for the notification</label>
                    <div class="input-group mb-3">
                        <div class="input-group-prepend">
                            <span class="input-group-text">Text</span>
                        </div>
                        <input type="text" class="form-control" placeholder="Optional text for the notification" id="context-text">
                    </div>
                    <div class="input-group mb-3">
                        <div class="input-group-prepend">
                            <span class="input-group-text">Link</span>
                        </div>
                        <input type="text" class="form-control" placeholder="Link for the notification to link out to" id="context-link">
                    </div>
                </div>
                <button type="submit" class="btn btn-primary mb-2" id="postGlobal">Submit</button>
            </div>`;
        this.bindEvents();
    }

    bindEvents() {
        this.element.querySelector('#postGlobal').onclick = () => {
            let verb = this.element.querySelector('#verb-select').value,
                object = this.element.querySelector('#object-input').value,
                level = this.element.querySelector('#level-select').value,
                contextText = this.element.querySelector('#context-text').value,
                contextLink = this.element.querySelector('#context-link').value;
            Feeds.postGlobalNotification({
                verb: verb,
                object: object,
                level: level,
                context: {
                    text: contextText,
                    link: contextLink
                }
            }, this.token)
                .then(this.afterSubmitFn);
        }
        this.element.querySelector('.card-header .btn').onclick = () => {
            let btnIcon = $(this.element).find('.card-header svg');
            if (btnIcon.attr('data-icon') === 'toggle-off') {
                btnIcon.attr('data-icon', 'toggle-on');
            }
            else {
                btnIcon.attr('data-icon', 'toggle-off');
            }
        }
    }

    activate(token) {
        this.token = token;
        this.element.style.removeProperty('display');
    }

    deactivate() {
        this.token = null;
        this.element.style.display = 'none';
    }
}