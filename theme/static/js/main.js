$(document).ready(function () {
  // determine the page title
  let page_title = $('title')[0].text.split('–')[1];
  if (page_title === undefined) {
    page_title = 'Home';
  }
  else {
    page_title = page_title.trim();
  }

  refreshUserLoginState().then(() => {
    refreshLoginDisplay(); // display cached username
    $('#signup-box').hide();
  });

  // determine which link on navbar is active
  let links = $('.nav-links .list').find('a');
  let found_link = false;
  for (link of links) {
    let link_name = link.text.trim();
    if (link_name == page_title) {
      $(link).addClass('active-link');
      found_link = true;
      break;
    }
  }
  if (!found_link) {
    $(links[0]).addClass('active-link');
  }

  // flash message about just-deleted user
  let deletedUser = localStorage.getItem('deletedUser');
  if (deletedUser) {
    $('#delete-account-success .flash-alert-content').html(`Successfully deleted account for <b>${deletedUser}</b>.`);
    localStorage.removeItem('deletedUser');
    flashAlert('#delete-account-success');
  }

  // $(function () {
  //   $("[rel='tooltip']").tooltip({selector: "[title]"});
  // });

});