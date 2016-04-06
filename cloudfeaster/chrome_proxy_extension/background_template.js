var config = {
    mode: "fixed_servers",
    rules: {
      singleProxy: {
        scheme: "https",
        host: "%PROXY_HOST%",
        port: parseInt(%PROXY_PORT%)
      }
    }
  };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
    };
}

chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {urls: ["<all_urls>"]},
        ['blocking']
);
