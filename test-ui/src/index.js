import Header from './header';
import TokenInput from './tokenInput';
import GlobalFeedPoster from './feeds/globalPoster';
import TargetedFeedPoster from './feeds/targetedPoster';
import FeedController from './feeds/controller';
import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import '@fortawesome/fontawesome-free/js/all';
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
    let globalPoster = new GlobalFeedPoster(() => {
        myFeed.refreshFeed({});
    });
    let targetedPoster = new TargetedFeedPoster(() => {
        myFeed.refreshFeed({});
    });
    let myFeed = new FeedController();

    mainElement.appendChild(tokenForm.element);
    mainElement.appendChild(globalPoster.element);
    mainElement.appendChild(targetedPoster.element);
    mainElement.appendChild(myFeed.element);

    function handleTokenLookup(inputToken) {
        getMyInfo(inputToken)
            .then(info => {
                console.log(info);
                tokenInfo = info.data;
                tokenForm.renderTokenInfo(tokenInfo);
                globalPoster.activate(inputToken);
                targetedPoster.activate(inputToken);
                myFeed.initialize(tokenInfo.display, inputToken);
            })
            .catch(err => {
                console.log('AN ERROR HAPPENED');
                console.error(err);
                tokenForm.renderTokenError();
                globalPoster.deactivate();
                targetedPoster.deactivate();
                myFeed.removeFeed();
            });
    }
}

main();