export default class Notification {
    /**
     *
     * @param {object} note
     * @param {Node} element
     * has keys: actor, context, created, expires, id, level, object, source, verb
     */
    constructor(note, element) {
        this.note = note;
        this.element = element;
        this.render();
    }

    render() {
        this.element.innerHTML = this.note.id + ' ' + this.note.actor;
    }
}