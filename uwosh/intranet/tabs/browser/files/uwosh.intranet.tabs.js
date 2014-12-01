
(function($){
$(document).ready(function(){
    
    $('a#add-group').prepOverlay({
        subtype:'ajax',
        urlmatch:'$',urlreplace:' #content > *'
    });
    
    $('a#add-tab').prepOverlay({
        subtype:'ajax',
        urlmatch:'$',urlreplace:' #content > *'
    });
    
    $('a.delete').prepOverlay({
        subtype:'ajax',
        urlmatch:'$',urlreplace:' #content > *'
    });
    
    $('a#rename-group').prepOverlay({
        subtype:'ajax',
        urlmatch:'$',urlreplace:' #content > *'
    });

});    
})(jQuery);
