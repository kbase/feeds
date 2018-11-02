import Header from './header';
import TokenInput from './tokenInput';
import FeedPoster from './feeds/poster';
import NotificationFeed from './feeds/notificationFeed';
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import './css/feeds.css';
import { getMyInfo } from './api/auth';

function main() {
    let tokenInfo = null;
    let header = new Header();
    document.body.appendChild(header.element);

    let mainElement = document.createElement('div');
    mainElement.classList.add('feeds-main');
    document.body.appendChild(mainElement);

    let tokenForm = new TokenInput(handleTokenLookup);
    let feedPoster = new FeedPoster();
    let myFeed = new NotificationFeed();

    mainElement.appendChild(tokenForm.element);
    mainElement.appendChild(feedPoster.element);
    mainElement.appendChild(myFeed.element);

    function handleTokenLookup(inputToken) {
        getMyInfo(inputToken)
            .then(info => {
                tokenInfo = info.data;
                tokenForm.renderTokenInfo(tokenInfo);
                feedPoster.activate(inputToken);
                myFeed.renderFeed(inputToken);
            })
            .catch(err => {
                console.log('AN ERROR HAPPENED');
                console.error(err);
                tokenForm.renderTokenError();
                feedPoster.deactivate();
                myFeed.removeFeed();
            });
    }
}

main();