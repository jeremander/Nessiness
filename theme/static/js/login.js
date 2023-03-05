// refreshes the page based on the current login state
function refreshLoginDisplay() {
  if (isLoggedIn()) {
    try {
      let loginState = getLocalLoginState();
      let username = loginState.data.user.username;
      let link = '/profile';
      $('.user-greeting').html(`Hello, <a class="username" href="${link}" onclick="loadProfile()"><b>${username}</b></a>!`);
    }
    catch {
      console.log('Could not get username.');
    }
    finally {
      $('.login-link').hide();
      $('.logout-link').show();
    }
  }
  else {
    $('.user-greeting').html('');
    $('.login-link').show();
    $('.logout-link').hide();
  }
}

function clearInvalid(form) {
  $(form).find('input').removeClass('is-invalid');
  $(form).find('.invalid-feedback').remove();
  $(form).find('.error-msg').html('');
}

function clearForm(form) {
  clearInvalid(form);
  for (input of $(form).find('input')) {
    if (input.type != 'submit') {
      $(input).val('');
    }
  }
}

function signupToggle() {
  $('#login-box').hide();
  $('#signup-box').show();
  clearForm($('#login-form'));
}

function loginToggle() {
  $('#signup-box').hide();
  $('#login-box').show();
  clearForm($('#signup-form'));
}

function redirectToLogin(elt) {
  if (!isLoggedIn()) {
    if (elt) {
      elt.preventDefault();
    }
    redirectToRoute('/login', true);
  }
}

$('#login-form').submit((elt) => {
  elt.preventDefault();
  clearInvalid(elt.target);
  const rememberMe = $(elt.target).find('#remember-me').prop('checked');
  let formData = new FormData(elt.target);
  const loginUrl = getAuthUrl('/login?remember_me=' + rememberMe.toString());
  fetchWithTimeout(loginUrl, {method: 'POST', body: formData, timeout: 5000}).catch((err) => {
    return new Response(JSON.stringify({detail: 'Network error'}), {status: 400});
  }).then(loginStateFromResponse).then((loginState) => {
    // store the login state
    setLocalLoginState(loginState);
    if (!loginState) {
      alert('Network error');
    }
    else if (loginState.status == 400) {  // server error
      alert(loginState.data.detail);
    }
    else if (loginState.status == 401) {  // authentication error
      let inputs = $(elt.target).find('input');
      $(inputs[1]).addClass('is-invalid');
      let err = loginState.data.detail;
      $(inputs[1]).parent().append(`<div class="invalid-feedback">${err}.</div>`);
    }
    else if (loginState.status == 200) {
      // if a redirect URL is present, redirect back there
      let locUrl = new URL(window.location.href);
      let redirectUrl = locUrl.searchParams.get('redirect');
      if (!redirectUrl) {
        redirectUrl = '/';
      }
      window.location.replace(redirectUrl);
    }
    else {
      alert('Unknown error occurred.');
    }
  });
});

$('.logout-link').click((elt) => {
  elt.preventDefault();
  const logoutUrl = getAuthUrl('/logout');
  fetchWithTimeout(logoutUrl, {method: 'POST', timeout: 3000}).then((response) => {
    return loginStateFromResponse(response, false);
  }).then((loginState) => {
    setLocalLoginState(loginState);
    console.log('User is logged out.');
    console.log('Login state:', loginState.data);
  }).catch(() => {
    console.log('Could not connect to server for logout.');
    setLocalLoginState(null);
  }).finally(() => {
    redirectToLogin();
  });
});

$('#signup-form').submit((elt) => {
  elt.preventDefault();
  clearInvalid(elt.target);
  let url = getAuthUrl('/users/create?welcome=true');
  let inputs = $(elt.target).find('input');
  let body = JSON.stringify({username: inputs[0].value, email: inputs[1].value, password: inputs[2].value});
  fetch(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body}).then((response) => {
    return response.json().then((data) => {
      return {status: response.status, data}
    });
  }).catch((err) => {
    return new Response(JSON.stringify({detail: 'Network error'}), {status: 400});
  }).then((obj) => {
    if (obj.status == 400) {  // network error
      alert('Network error');
    }
    else if (obj.status == 409) {  // conflict (user/email already exists)
      let err = obj.data.detail;
      let tokens = err.split(' ');
      let i = (tokens[2] == 'username') ? 0 : 1;
      let token = (i == 0) ? 'Username' : 'Email';
      $(inputs[i]).addClass('is-invalid');
      $(inputs[i]).parent().append(`<div class="invalid-feedback">${token} already exists.</div>`);
    }
    else if (obj.status == 422) {  // invalid email address
      $(inputs[1]).addClass('is-invalid');
      $(inputs[1]).parent().append('<div class="invalid-feedback">Invalid email address.</div>');
    }
    else if (obj.status == 200) {  // signup successful
      let email = inputs[1].value;
      $('#signup-modal').modal('hide');
      setFlashMessageContent('signup-success', `Account created successfully!<br><br>Sent email to <b>${email}</b>`);
      flashMessage('signup-success');
      loginToggle();
    }
    else {
      alert('Unknown error occurred.')
    }
  });
});

$('#signup-toggle').click(signupToggle);

$('#login-toggle').click(loginToggle);

$('#password-reset-modal').on('hidden.bs.modal', () => {
  clearForm($('#password-reset-request-form'));
});

$('#password-reset-request-form').submit((elt) => {
  elt.preventDefault();
  $('#password-reset-modal').modal('hide');
  let email = $(elt.target).find('input[type="email"]')[0].value;
  let url = getAuthUrl(`/users/change-password-request?email=${email}`);
  fetchWithTimeout(url).then((response) => {
    if (response.status == 200) {
      setFlashMessageContent('password-reset-requested', 'If account exists, a password reset email was sent to the address provided.');
      flashMessage('password-reset-requested', 5000);
    }
    else {
      alert('Unknown error occurred.')
    }
  }, () => {
    alert('Network error');
  });
});

$('#password-reset-form').submit((elt) => {
  elt.preventDefault();
  clearInvalid(elt.target);
  // check that password reset token is valid before loading the page
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  let inputs = $(elt.target).find('input');
  if (urlParams.has('email') && urlParams.has('token')) {
    const url = getAuthUrl('/users/change-password-submit' + queryString);
    let body = JSON.stringify({username: inputs[0].value, email: urlParams.get('email'), password: inputs[1].value});
    fetchWithTimeout(url, {method: 'POST', headers: {'Content-Type': 'application/json'}, body}).then((response) => {
      if (response.status == 200) {
        $(elt.target).find('.error-msg').html('');
        addFlashMessage('password-reset-success', 'Successfully changed password.')
        redirectToRoute('/login', false);
      }
      else {
        response.json().then((data) => {
          $(elt.target).find('.error-msg').html(data.detail);
        });
      }
    });
  }
});