$(document).ready(function(){
  $(".dropdown-menu li a").click(function(){
    $(this).parents(".dropdown").find('.btn').html($(this).text() + ' <span class="caret"></span>');
    $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
    $(this).parents(".dropdown").find('#account_type').val($(this).data('value'));
  });
});