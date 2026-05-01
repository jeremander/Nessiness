const bskyHost = "https://bsky.app";

function parseAtUri(atUri) {
  const match = atUri.match(/^at:\/\/([^/]+)\/([^/]+)\/([^/]+)$/);
  if (!match) {
    return null;
  }
  const [, did, collection, rkey] = match;
  return {did, collection, rkey};
}

(async () => {

  // find the link tag
  const link = document.querySelector('link[rel="site.standard.document"]');
  if (!link) return;
  const atUri = link.getAttribute("href");
  if (!atUri?.startsWith("at://")) return;

  const {did, collection, rkey} = parseAtUri(atUri);

  // fetch the document record with a timeout
  async function fetchWithTimeout(url, ms = 1500) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), ms);
    try {
      const res = await fetch(url, { signal: controller.signal });
      return res.ok ? res.json() : null;
    } catch {
      return null;
    } finally {
      clearTimeout(timer);
    }
  }

  try {

    const pdsUrl = link.dataset.pds;
    if (!pdsUrl) return;

    const article = document.querySelector("article");
    if (!article) return;

    const documentUrl = `${pdsUrl}/xrpc/com.atproto.repo.getRecord` +
      `?repo=${did}&collection=${encodeURIComponent(collection)}&rkey=${encodeURIComponent(rkey)}`;

    const documentData = await fetchWithTimeout(documentUrl, 1500);
    if (!documentData) return;

    const bskyPostRef = documentData.value.bskyPostRef;
    if (!bskyPostRef) return;

    const {did: postDid, rkey: postRkey} = parseAtUri(bskyPostRef.uri);
    const bskyPostUrl = `${bskyHost}/profile/${postDid}/post/${postRkey}`;

    // inject a link to the Bluesky post
    const p = document.createElement("p");
    p.className = "bsky-link";
    p.innerHTML = `<i class="fa-brands fa-bluesky"></i>Comment on <a href="${bskyPostUrl}" target="_blank" rel="noopener">Bluesky</a>`;
    article.appendChild(p);

  } catch {
    // silently fail — this is progressive enhancement
  }
})();
