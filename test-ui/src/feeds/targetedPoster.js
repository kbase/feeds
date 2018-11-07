import * as Feeds from '../api/feeds';
import $ from 'jquery';

export default class TargetedFeedPoster {
    constructor(afterSubmitFn) {
        this.token = null;
        this.element = document.createElement('div');
        this.element.style.display = 'none';
        this.element.classList.add(['card']);
        const verbs = ['invite', 'accept', 'reject', 'share', 'unshare', 'join', 'leave', 'request', 'update'];
        const levels = ['alert', 'warning', 'error', 'request'];
        const sources = ['groups', 'workspace', 'jobs', 'narrative']
        this.afterSubmitFn = afterSubmitFn;

        this.element.innerHTML = `
            <div class='card-header'>
                <b>Targeted Notification</b> - create a new notification targeted at a few users.
                <button class="btn btn-primary float-right" data-toggle="collapse" href="#targetedFeedInput" role="button">
                    <span>
                        <i class="fa fa-toggle-off"></i>
                    </span>
                </button>
            </div>
            <div class='card-body collapse' id="targetedFeedInput">
                <div class='form-group mx-sm-3 mb-2'>
                    <label for="source-input"><b>Source</b> - (temporary during development) - tells the notification what service created it. When complete, this will be inferred by the service's auth credentials.</label>
                    <select class="form-control custom-select" id="source-select">
                        ${sources.map(source => `<option value="${source}">${source}</option>`)}
                    </select>
                </div>
                <div class='form-group mx-sm-3 mb-2'>
                    <label for="actor-input"><b>Actor</b> - this tells the notification who has performed an action</label>
                    <input type="text" class="form-control" placeholder="Enter a userid for the actor" id="actor-input">
                </div>
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
                    <label for="target-input"><b>Target users</b> - optional, but used from services who know what users should see this notification.
                    <input type="text" class="form-control" placeholder="Enter a list of user ids, comma-separated" id="target-input">
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
                <button type="submit" class="btn btn-primary mb-2" id="postNote">Submit</button>
            </div>`;
        this.bindEvents();
    }

    bindEvents() {
        this.element.querySelector('#postNote').onclick = () => {
            let source = this.element.querySelector('#source-select').value,
                actor = this.element.querySelector('#actor-input').value,
                verb = this.element.querySelector('#verb-select').value,
                object = this.element.querySelector('#object-input').value,
                level = this.element.querySelector('#level-select').value,
                contextText = this.element.querySelector('#context-text').value,
                contextLink = this.element.querySelector('#context-link').value,
                target = this.element.querySelector('#target-input').value.split(',');
            Feeds.postNotification({
                source: source,
                actor: actor,
                verb: verb,
                object: object,
                level: level,
                context: {
                    text: contextText,
                    link: contextLink
                },
                target: target
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

            // this.element.querySelector('.card-header svg')..remove('fa-toggle-off');
            // this.element.querySelector('.card-header svg').classList.add('fa-toggle-on');
            // $(this.element).find('.card-header .fa').toggleClass('fa-toggle-off').toggleClass('fa-toggle-on');
        }
        // $('#targetedFeedInput').on('show.bs.collapse', () => {
        // });
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