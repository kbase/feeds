export default class Header {
    constructor() {
        this.element = document.createElement('div');
        this.render();
    }

    render() {
        this.element.innerHTML = `
            <div class='navbar navbar-dark bg-dark'>
                <a href='#' class='navbar-brand'>
                    KBase Feeds Test UI -- NOT FOR PRODUCTION. The real thing won't look like this. Calm down.
                </a>
            </div>
        `;
    }
}