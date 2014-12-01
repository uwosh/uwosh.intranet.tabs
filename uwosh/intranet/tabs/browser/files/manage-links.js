
function getUrl(path) {
    return $('base').attr('href') + path;
}

function getChildrenOrder(node) {
    var elements = node.children;
    var order = [];
    for (var i = 0; i < elements.length; i++) {
        var element = elements.item(i);
        order.push(element.id);
    }
    return order;
}

function updateLinks(event, ui) {
    var order = getChildrenOrder(event.target);
    $.post(getUrl('/@@update-link-order'), {'groupId':event.target.id, 'order[]':order});
}

function updateGroups(event, ui) {
    var order = getChildrenOrder(event.target);
    $.post(getUrl('/@@update-group-order'), {'order[]':order});
}

(function($){
$(document).ready(function(){

    //Drag drop 
    $(".sortableLinks").sortable({ update: updateLinks });
    $(".sortableLinks").disableSelection();
    
    $(".sortableGroups").sortable({ update: updateGroups });
    $(".sortableGroups").disableSelection();
    //end drag drop


    //object browser
    //Styling gets all messed up if I do this, but it won't position
    //correctly if I don't!
    //var lf = $("#link-finder").detach()
    //lf.prependTo('body'); // move to top of dom so it gets positioned better
    $("#link-finder").overlay({top: 30});
    $("li.group span.add-link a").click(function(){    
        var group = $(this).parents('.group').find('input[name="group"]').val();
        $('#link-finder input[name="group"]').val(group);
        $("#link-finder").overlay().load();
        return false;
    });
    
    $('#object-tree input[name="form.buttons.add"]').click(function(){
        $("#link-finder").overlay().close();
    });
    
    $('#tree-container').fileTree({ }, function(file) {
        $('#object-tree input[name="form.buttons.add"]')[0].disabled = false;
        $('#object-tree input[name="link"]').val(file);
    });
    //end object browser

    //autocomplete
    function findValue(li) {
        var sValue = null;
    	// if coming from an AJAX call, let's use the UID as the value
    	if( !!li.extra ){ 
    	    sValue = li.extra[0];
    	}else{
    	    sValue = li.selectValue;
    	} 
    	$("#live-search-link-finder input[name='link']").val(sValue);
    	$('#live-search-link-finder input[name="form.buttons.add"]')[0].disabled = false;
    }

    function selectItem(li) {
    	findValue(li);
    }

    function formatItem(row) {
    	return row[0] + "<span class='discreet'> (" + row[2] + ")</span>";
    }
    
    $("#search-links").autocomplete("@@search-links", {
		delay:20,
		minChars:4,
		matchSubset:1,
		matchContains:1,
		cacheLength:10,
		onItemSelect:selectItem,
		onFindValue:findValue,
		formatItem:formatItem,
		autoFill:true
	});
    //end auto complete
	
	
	//suggest links
	$('div#suggested-items div ul li a').click(function(){
	    $.post(getUrl('/@@ajax-add-link'), {
	        group : $('#link-finder input[name="group"]').val(),
	        link : $(this).attr('rel'),
	        type : 'uid'
	    }, function(){
	        $("#link-finder").overlay().close();
	        window.location.reload();
	    });
	    return false;
	});
	
	//add external link
	$("#ajaxed-overlay").overlay({
        onBeforeLoad: function() {
            var wrap = this.getOverlay().find(".pb-ajax");
            var form = $("form#add-external-link");
            wrap.load(form.attr('action') + ' #content > *', form.serialize());
        }
    });
    
	$("form#add-external-link").submit(function(){
	    $("#link-finder").overlay().close();
	    $("#ajaxed-overlay").overlay().load();
	    return false;
	});
	//end add external link

});
})(jQuery);