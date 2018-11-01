import Header from './header';
import Controls from './controls';
import NotificationFeed from './feeds/notificationFeed';
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './css/feeds.css';
import * as Feeds from './api/feeds';
import { getTokenInfo, getMyInfo } from './api/auth';

function main() {
    let token = null;
    let header = new Header();
    document.body.appendChild(header.element);

    let mainElement = document.createElement('div');
    mainElement.classList.add('feeds-main');
    document.body.appendChild(mainElement);

    let controls = new Controls(handleTokenLookup);
    let myFeed = new NotificationFeed();

    mainElement.appendChild(controls.element);
    mainElement.appendChild(myFeed.element);

    function handleTokenLookup(inputToken) {
        getMyInfo(inputToken)
            .then(info => {
                token = info.data;
                controls.renderTokenInfo(token);
                myFeed.renderFeed(token);
            })
            .catch(err => {
                console.log('AN ERROR HAPPENED');
                console.error(err);
                controls.renderTokenError();
                myFeed.removeFeed();
            });
    }
}

main();