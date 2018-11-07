import Notification from './notification';

export default class Feed {
    constructor(userName, refreshFn) {
        this.refreshFn = refreshFn;

        this.element = document.createElement('div');
        this.element.classList.add('card');
        this.element.style.marginTop = '20px';
        this.element.innerHTML = `
            <div class="card-header">
                <b><span id="user-feed-name">${userName}</span> notifications</b>
                ${this.renderFilters()}
            </div>
            <div class="card-body"></div>
        `;
        this.ctrlState = {
            seen: false,
            descending: true,
            levelFilter: null,
            sourceFilter: null
        };
        this.bindEvents();
    }

    bindEvents() {
        let ctrls = this.element.querySelector('.card-header div.input-group');
        // toggle eye
        ctrls.querySelector('#seen-btn').onclick = () => {
            let btnIcon = ctrls.querySelector('#seen-btn svg');
            if (btnIcon.getAttribute('data-icon') === 'eye-slash') {
                btnIcon.setAttribute('data-icon', 'eye');
                this.ctrlState.seen = true;
            }
            else {
                btnIcon.setAttribute('data-icon', 'eye-slash');
                this.ctrlState.seen = false;
            }
            this.refresh();
        }

        // toggle order
        ctrls.querySelector('#sort-btn').onclick = () => {
            let btnIcon = ctrls.querySelector('#sort-btn svg');
            if (btnIcon.getAttribute('data-icon') === 'sort-numeric-down') {
                btnIcon.setAttribute('data-icon', 'sort-numeric-up');
                this.ctrlState.descending = false;
            }
            else {
                btnIcon.setAttribute('data-icon', 'sort-numeric-down');
                this.ctrlState.descending = true;
            }
            this.refresh();
        }

        // level filter
        ctrls.querySelector('#level-filter').onchange = (e) => {
            console.log(e);
            if (e.target.selectedIndex === 0) {
                this.ctrlState.levelFilter = null;
            }
            else {
                this.ctrlState.levelFilter = e.target.value;
            }
            this.refresh();
        }

        // source filter
        ctrls.querySelector('#source-filter').onchange = (e) => {
            if (e.target.selectedIndex === 0) {
                this.ctrlState.sourceFilter = null;
            }
            else {
                this.ctrlState.sourceFilter = e.target.value;
            }
            this.refresh();
        }
    }

    refresh() {
        // get filter info from controls
        // run the refresh function
        // update this feed with the results
        console.log(this.ctrlState);
    }

    renderFilters() {
        let levels = ['alert', 'warning', 'error', 'request'],
            services = ['groups', 'workspace', 'jobs', 'narrative'],
            filterHtml = `
                <div class="input-group input-group-sm float-right" style="max-width: 350px">
                    <button class="btn btn-outline-secondary" type="button" id="seen-btn">
                        <i class="far fa-eye"></i>
                    </button>
                    <button class="btn btn-outline-secondary" type="button" id="sort-btn">
                        <i class="fa fa-sort-numeric-down"></i>
                    </button>
                    <select class="custom-select" id="level-filter">
                        <option selected>Filter Level</option>
                        ${levels.map(level => `<option value="${level}">${level}</option>`)}
                    </select>
                    <select class="custom-select" id="source-filter">
                        <option selected>Filter Source</option>
                        ${services.map(service => `<option value="${service}">${service}</option>`)}
                    </select>
                </div>
            `;

        return filterHtml;
    }

    remove() {
        this.element.querySelector('.card-body').innerHTML = '';
    }

    updateFeed(feed, token) {
        this.remove();
        let userFeed = this.element.querySelector('.card-body');
        feed.forEach(note => {
            let noteObj = new Notification(note, token, this.refresh);
            userFeed.appendChild(noteObj.element);
        });
    }

    setUserName(userName) {
        this.userName = userName;
        this.element.querySelector('#user-feed-name').innerHTML = userName;
    }

}