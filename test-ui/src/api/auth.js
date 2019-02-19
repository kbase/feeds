const authUrl = 'https://ci.kbase.us/services/auth/';
import axios from 'axios';

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
        url: authUrl + path,
        method: method,
        cache: 'no-cache',
        headers: {
            'Content-type': 'application/json; charset=utf-8',
            'Authorization': token
        },
        redirect: 'follow',
        referrer: 'no-referrer',
        crossDomain: true
    }
    if (data) {
        request.data = data;
    }
    return axios(request);
}

export function getTokenInfo(token) {
    let path = "api/V2/token";
    return makeApiCall('GET', path, token);
}

export function getMyInfo(token) {
    let path = "api/V2/me";
    return makeApiCall('GET', path, token);
}