// const authUrl = "https://nessiness-auth.herokuapp.com";
const authUrl = "http://localhost:5000";

function refreshLoginDisplay() {
  let username = localStorage.getItem('nessiness-username');
  if (username === null) {
    $('.user-greeting').html('');
  }
  else {
    $('.user-greeting').html(`Hello, <b>${username}</b>!`);
    $('.login-link').hide();
  }
}

function clearInvalid(form) {
  $(form).find('input').removeClass('is-invalid');
  $(form).find('.invalid-feedback').remove();
}

function clearForm(form) {
  clearInvalid(form);
  for (input of $(form).find('input')) {
    if (input.type != 'submit') {
      $(input).val('');
    }
  }
}

$('#login-modal').on('hide.bs.modal', function (e) {
  clearForm($(e.target).find('#login-form'));
});

$('#signup-modal').on('hide.bs.modal',  function(e) {
  clearForm($(e.target).find('#signup-form'));
});

$('#login-form').submit(function(elt) {
  clearInvalid(elt.target);
  let formData = new FormData(elt.target);
  let xhr = new XMLHttpRequest();
  let url = authUrl + '/token';
  xhr.open('POST', url, true);
  xhr.onreadystatechange = function() {
    if (xhr.readyState == 4) {
      if (xhr.status == 401) {  // authentication error
        let inputs = $(elt.target).find('input');
        $(inputs[1]).addClass('is-invalid');
        $(inputs[1]).parent().append('<div class="invalid-feedback">Invalid username or password.</div>');
      }
      else if (xhr.status == 200) {
        let response = JSON.parse(xhr.responseText);
        localStorage.setItem('nessiness-username', response.username);
        refreshUsername();
        $('#login-modal').modal('hide');
      }
      else {
        alert('Unknown error occurred.');
      }
    }
  };
  xhr.send(formData);
  return false;
});

$('#signup-form').submit(function(elt) {
  clearInvalid(elt.target);
  let obj = {};
  let inputs = $(elt.target).find('input');
  obj['username'] = inputs[0].value;
  obj['email'] = inputs[1].value;
  obj['password'] = inputs[2].value;
  let body = JSON.stringify(obj);
  let xhr = new XMLHttpRequest();
  let url = authUrl + '/users/create?welcome=true';
  xhr.open('POST', url, true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4) {
      let response = JSON.parse(xhr.responseText);
      if (xhr.status == 409) {  // user or email already exists
        let msg = response.detail;
        let tokens = msg.split(' ');
        let i = (tokens[2] == 'username') ? 0 : 1;
        let token = (i == 0) ? 'Username' : 'Email';
        $(inputs[i]).addClass('is-invalid');
        $(inputs[i]).parent().append(`<div class="invalid-feedback">${token} already exists.</div>`);
      }
      else if (xhr.status == 422) {  // invalid email address
        $(inputs[1]).addClass('is-invalid');
        $(inputs[1]).parent().append('<div class="invalid-feedback">Invalid email address.</div>');
      }
      else if (xhr.status == 200) {
        let email = inputs[1].value;
        $('#signup-modal').modal('hide');
        $('#signup-success .success-msg').html(`Account created successfully!<br><br>Sent email to <b>${email}</b>`);
        $('#signup-success').fadeIn('fast', function() {
          $(this).delay(5000).fadeOut('slow');
        });
      }
      else {
        alert('Unknown error occurred.')
      }
    }
  };
  xhr.send(body);
  return false;
});
