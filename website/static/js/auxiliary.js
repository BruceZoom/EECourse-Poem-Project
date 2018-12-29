function imageUploadChanged(id) {
    document.getElementById(id).value = "图片已上传，请提交！";
}

jQuery(document).ready(function () {
  $body = (window.opera) ? (document.compatMode == "CSS1Compat" ? $('html') : $('body')) : $('html,body');
});

function slide_to_top () {
    jQuery('#back-to-top').click(function(){
      console.log("jump");
    $body.animate({scrollTop: jQuery('#nav-header').offset().top}, 1000);
    return false;
  });
}
