$(function() {

    var input = $('<div id="input"></div>');
    var output = $('<div id="output"></div>');

    $('body').append(input).append(output);

    var buttons = ['server', 'list'];
    for (var i in buttons) {
        var button = $('<input type="button" class="action" value="'+buttons[i]+'"/>');
        button.click(function() {
            api_call($(this).val()+' default');
        });

        input.append(button);
    }

    var textbox = $('<input type="text" class="textbox" value="" />');
    textbox.keydown(function(event) {
        // Get enter
        if (event.keyCode == 13) {
            api_call(textbox.val());
            textbox.val("");
        }
    });

    input.append(textbox);
    textbox.focus();

    api_call('server connect');

});

var api_call = function(url) {
    console.log('function api_call');

    url = url.replace(' ', '/');
    url = url.replace(' ', '/');

    var baseurl = $('span.base_url').html();

    var callback = function(result) {
        console.log('function callback');
        var output = $('#output');
        var input = $('#input');
        input.val('');

        var res = {}
        res.url = url;

        result = jQuery.parseJSON(result.responseText);

        if (!result) {
            res.result = 'SERVER FAILURE';
            res.message = 'No failure data available';
        }
        else {
            console.log('check state');
            if (result['state'] != 1) {
                res.result = 'FAILURE';
            }

            console.log('check message');
            res.message = result['message'];

            console.log('check data');
            if (result['data'] && result['data'].length) {
                if (result['data'] instanceof Array) {
                } else {
                    result['data'] = [result['data']];
                }

                res.data = result['data'];
            }
        }

        var exists = $('div.response');
        if (exists.length) {
            exists.remove();
        }

        var render = $('<div class="response">');
        render.append($('<h3>').html(res.url));
        if (res.result) {
            render.append($('<div class="result">').html(res.result));
        }

        render.append($('<div class="message">').html(res.message));

        var list = $('<ol>');
        for (line in res.data) {
            var item = res.data[line][0];
            var li = $('<li>').html(item);

            if (res.data[line].length > 1) {
                var action = res.data[line][1];
                if (action) {
                    var span = $('<span class="expand action">&gt;</span>');
                    span.data('action', action);
                    span.click(function() {
                        api_call($(this).data('action'));
                    });

                    li.prepend(span);
                }
            }

            if (res.data[line].length > 2) {
                var options = res.data[line][2];
                if (options) {
                    li.addClass('action');
                    li.click(function() {
                        $('ol.options', $(this)).toggle();
                    });

                    var olist = $('<ol class="options">');
                    for (var o in options) {
                        var option = $('<li class="action">');
                        option.html(o);
                        option.attr('title', options[o]);
                        option.data('action', options[o]);
                        option.click(function() {
                            api_call($(this).data('action'));
                        });

                        olist.append(option);
                    }

                    li.append(olist);
                }
            }

            list.append(li);
        }

        render.append(list);

        console.log('update output');
        output.append(render);
    }

    console.log('make json call');
    $.ajax({
        dataType: "json",
        url: baseurl+url,
        data: '',
        complete: callback,
        headers: {'secret': $('span.secret').html()}
    });
}
