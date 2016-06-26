var config = {
    mode: "fixed_servers",
    rules: {
      singleProxy: {
        scheme: "https",
        host: "%PROXY_HOST%",
        port: %PROXY_PORT%
      }
    }
  };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%PROXY_USERNAME%",
            password: "%PROXY_PASSWORD%"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
);
