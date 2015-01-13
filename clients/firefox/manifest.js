var baseurl = '{{ escape(BASEURL) }}';

function getManifest() {
  return {
    "name": "Jarvis Firefox Service",
    "origin": baseurl,
    "iconURL": baseurl+"static/img/favicon.ico",

    "markURL": baseurl+"firefox/status.html?url=%{url}&title=%{title}&note=%{text}",

    // should be available for display purposes
    "description": "Jarvis Firefox Service",
    "author": "Aaron Barnes",
    "homepageURL": baseurl,

    "version": 0.1
  }
}
