$('.on_click_story_like').click(function(){
  var story_id;
  story_id = $(this).attr("data_story_id");
  jQuery.get('/insane/' + story_id + '/like/', {}, function(created){
    if(created == 1){
      $('#like_count').html(parseInt($('#like_count').html()) + 1);
      $('#like')[0].classList.add('fas');
      $('#like')[0].classList.remove('far');
    }
    else if(created == -1){
      $("#like_dropdown")[0].setAttribute("aria-expanded", "true");
    }
    else{
      $('#like_count').html(parseInt($('#like_count').html()) - 1);
      $('#like')[0].classList.add('far');
      $('#like')[0].classList.remove('fas');
  }
  });
});

$('.on_click_story_comment_like').click(function(){
  var story_comment_id;
  story_comment_id = $(this).attr("data_comment_id");
  var story_id;
  story_id = $(this).attr("data_story_id");
  jQuery.get('/insane/' + story_id + '/like_comment/' + story_comment_id, {},
  function(created){
    if(created == 1){
      $('#like_comment_' + story_comment_id + '_count').html(
        parseInt($('#like_comment_' + story_comment_id + '_count').html()) + 1);
      $('#like_comment_'+story_comment_id)[0].classList.add('fas');
      $('#like_comment_'+story_comment_id)[0].classList.remove('far');
    }
    else if(created == -1){
    $("#comment_like_dropdown"+story_comment_id)[0].setAttribute("aria-expanded", "true");
    alert(story_comment_id);
    }
    else{
      $('#like_comment_' + story_comment_id + '_count').html(
        parseInt($('#like_comment_' + story_comment_id + '_count').html()) - 1);
      $('#like_comment_'+story_comment_id)[0].classList.add('far');
      $('#like_comment_'+story_comment_id)[0].classList.remove('fas');
  }
  });
});
