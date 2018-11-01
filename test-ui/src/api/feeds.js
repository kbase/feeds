/**
 * Basic feeds API.
 */

const feedsUrl = "http://ci.kbase.us/services/feeds/"

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
        method: method,
        cache: 'no-cache',
        headers: {
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': token
        },
        redirect: 'follow',
        referrer: 'no-referrer'
    }
    if (data) {
        request.body = JSON.stringify(data);
    }
    return fetch(feedsUrl + path, request)
        .then(response => response.json());
}

/**
 *
 * @param {object} options
 *  - reverseSort - boolean
 *  - verb - string or int
 *  - level - string or int
 *  - includeSeen - boolean
 *  - token - string, auth token
 */
export function getNotifications (options) {
    if (!options.token) {
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
    let path = 'notifications?' + params.join('&');
    return makeApiCall('GET', path, options.token);
};