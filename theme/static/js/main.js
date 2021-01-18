$(document).ready(function () {
  let page_title = $('title')[0].text.split('–')[1];
  if (page_title === undefined) {
    page_title = 'Home';
  }
  else {
    page_title = page_title.trim();
  }
  let links = $('.nav-links .list').find('a');
  for (link of links) {
    let link_name = link.text.trim();
    if (link_name == page_title) {
      $(link).addClass('active-link');
      break;
    }
  }
});