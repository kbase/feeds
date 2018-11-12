/**
 * Basic feeds API.
 */
import axios from 'axios';
const feedsUrl = 'https://ci.kbase.us/services/feeds/';
// const feedsUrl = 'http://localhost:5000/';

/**
 *
 * @param {string} method
 * @param {string} path
 * @param {string} token
 * @param {object} options
 */
function makeApiCall (method, path, token, data) {
    // remove the first slash, if present
    if (path.startsWith('/')) {
        path = path.substring(1);
    }
    method = method.toLocaleUpperCase();
    if (!['GET', 'POST', 'PUT', 'DELETE'].includes(method)) {
        throw new Error('Method ' + method + ' not usable');
    }
    let request = {
        url: feedsUrl + path,
        method: method,
        cache: 'no-cache',
        headers: {
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': token
        },
        redirect: 'follow',
        referrer: 'no-referrer',
        maxRedirects: 5
    }
    if (data) {
        request.data = data;
    }
    return axios(request);
}

/**
 *
 * @param {object} options
 *  - reverseSort - boolean
 *  - verb - string or int
 *  - level - string or int
 *  - includeSeen - boolean
 * @param {string} token - auth token
 */
export function getNotifications (options, token) {
    if (!token) {
        throw new Error('Auth token required');
    }
    let params = [];
    if (options.reverseSort) {
        params.push('rev=1');
    }
    if (options.verb) {
        params.push('v=' + options.verb);
    }
    if (options.level) {
        params.push('l=' + options.level);
    }
    if (options.includeSeen) {
        params.push('seen=1');
    }
    let path = 'api/V1/notifications?' + params.join('&');
    return makeApiCall('GET', path, token);
};

/**
 *
 * @param {object} data
 * - verb
 * - object
 * - level
 * - context (keys text, link)
 * - token
 */
export function postNotification (data, token) {
    let path = 'api/V1/notification';
    return makeApiCall('POST', path, token, data);
}

export function postGlobalNotification (data, token) {
    let path = 'api/V1/notification/global';
    return makeApiCall('POST', path, token, data);
}

export function markSeen(noteIds, token) {
    let path = 'api/V1/notifications/see';
    return makeApiCall('POST', path, token, {note_ids: noteIds});
}

export function markUnseen(noteIds, token) {
    let path = 'api/V1/notifications/unsee';
    return makeApiCall('POST', path, token, {note_ids: noteIds});
}