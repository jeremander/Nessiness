function isObject(item) {
  return (item && typeof item === 'object' && !Array.isArray(item));
}

// deep-merges one object into another
function mergeDeep(target, source) {
  for (const key in source) {
    if (isObject(source[key])) {
      if (!target[key]) {
        Object.assign(target, { [key]: {} });
      }
      mergeDeep(target[key], source[key]);
    }
    else {
      Object.assign(target, { [key]: source[key] });
    }
  }
  return target;
}

// gets the full URL for the auth server at the given path
function getAuthUrl(path) {
  return authUrl + path;
}

// awaits a promise with some time limit
async function runWithTimeout(promise, timeout) {
  let timeoutHandle;
  const timeoutPromise = new Promise((_resolve, reject) => {
      timeoutHandle = setTimeout(
          () => reject(new Error('Timeout reached')),
          timeout
      );
  });
  return Promise.race([promise, timeoutPromise]).then(result => {
      clearTimeout(timeoutHandle);
      return result;
  })
}

// fetches an HTTP resource with a timeout (which can be set with the 'timeout' parameter of options)
async function fetchWithTimeout(resource, options = {}) {
  const { timeout = 8000 } = options;
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  const response = await fetch(resource, {
    ...options,
    signal: controller.signal
  });
  clearTimeout(id);
  return response;
}

// given a response from the auth server, converts this to a login state object
function loginStateFromResponse(response, isLogin = true) {
  if (!response) {
    return null;
  }
  let status = response.status;
  const validCodes = [200, 400, 401];
  if (validCodes.includes(status)) {
    return response.json().then((data) => {
      let isLoggedIn = isLogin ? (status == 200) : false;
      return { status, data, isLoggedIn };
    });
  }
  else {
    return null;
  }
}

// gets the current login state of the user, returning null if the user is not logged in (or timeout occurs)
async function fetchUserLoginState() {
  const url = getAuthUrl('/users/me');
  const response = await fetchWithTimeout(url, {timeout: 3000}).catch((err) => {});
  return loginStateFromResponse(response);
}

// gets the current login state of the user stored in localstorage
function getLocalLoginState() {
  let loginStateStr = localStorage.getItem('loginState');
  let loginState = (loginStateStr === null) ? null : JSON.parse(loginStateStr);
  return loginState;
}

// gets the name of the current user, if possible, otherwise returns null
function getCurrentUser() {
  let loginState = getLocalLoginState();
  if (loginState) {
    if (loginState.data) {
      if (loginState.data.user) {
        return loginState.data.user.username;
      }
    }
  }
  return null;
}

// updates the current login state of the user stored in localstorage
function setLocalLoginState(loginState) {
  let localLoginState = getLocalLoginState();
  if ((loginState === null) || (localLoginState === null)) {
    localStorage.setItem('loginState', JSON.stringify(loginState));
  }
  else {
    mergeDeep(localLoginState, loginState);
    // Object.assign(localLoginState, loginState);
    localStorage.setItem('loginState', JSON.stringify(localLoginState));
  }
}

// returns true if a JWT is expired
function tokenIsExpired(token) {
  let expiry = token.exp * 1000;  // expiration time (milliseconds since epoch)
  let currentTimestamp = Date.now();
  return (currentTimestamp >= expiry);
}

// gets a new access token from the auth server
// returns true if the refresh was successful
async function refreshAccessToken(rememberMe) {
  let success = false;
  let loginState = getLocalLoginState();
  if (loginState) {
    let accessToken = loginState.data.access_token;
    if (rememberMe == null) {
      rememberMe = accessToken.remember_me;
    }
    console.log(`Refreshing access token (remember_me = ${rememberMe})...`);
    let url = getAuthUrl('/refresh?remember_me=' + (rememberMe ? '1' : '0'));
    await fetchWithTimeout(url, {method: 'POST', headers: {'Content-Type': 'application/json'}}).then((response) => {
      if (response.status == 200) {
        success = true;
      }
    }).catch((err) => {});
  }
  if (success) {
    let loginState = await fetchUserLoginState();
    console.log(loginState);
    setLocalLoginState(loginState);
    console.log('Successfully refreshed access token.');
  }
  else {
    console.log('Failed to refresh access token.');
  }
  return success;
}

// refreshes the login state of the user
// if the user has a valid access token, stores the token info in local storage
async function refreshUserLoginState() {
  let loginState = getLocalLoginState();
  if (loginState === null) {  // unknown login state, so fetch it from auth server
    console.log('User login status unknown.');
    loginState = await fetchUserLoginState();
  }
  if (loginState) {
    if (loginState.isLoggedIn) {  // user is logged in
      if (tokenIsExpired(loginState.data.access_token)) {
        console.log('Access token is expired.')
        await refreshAccessToken();
        return;
      }
      else {
        console.log('User is logged in.')
        console.log('Login state:', loginState.data);
      }
    }
    else {  // not logged in
      console.log('User is not logged in.')
    }
    setLocalLoginState(loginState);
  }
}

// returns true if the user is currently logged in with a valid access token
function isLoggedIn() {
  let loginState = getLocalLoginState();
  return (loginState != null) && loginState.isLoggedIn && (!tokenIsExpired(loginState.data.access_token));
}

// decorates a function to make it require a login (otherwise, redirects to login page)
async function requiresLogin(func) {
  let loggedIn = isLoggedIn();
  // let loggedIn = true;
  if (!loggedIn) {
    let loginState = getLocalLoginState();
    // if access token is expired, try to refresh it
    if ((loginState != null) && loginState.isLoggedIn && tokenIsExpired(loginState.data.access_token)) {
      let success = await refreshAccessToken();
      if (success) {
        loggedIn = true;
      }
    }
  }
  if (loggedIn) {
    return func();
  }
  else {
    redirectToLogin();
  }
}

// deltes the currently logged in user
async function deleteUser() {
  let url = getAuthUrl('/users/delete-me');
  const response = await fetchWithTimeout(url, {method: 'DELETE', timeout: 3000}).catch((err) => {});
  return response;
}
