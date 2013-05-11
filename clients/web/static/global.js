$(function() {

    var input = $('<div id="input"></div>');
    var output = $('<div id="output"></div>');

    $('body').append(input).append(output);

    var buttons = [['home', 'server connect'], ['server', 'server default'], ['list', 'list default']];
    for (var i in buttons) {
        var button = $('<input type="button" class="action" data-call="'+buttons[i][1]+'" value="'+buttons[i][0]+'"/>');
        button.click(function() {
            api_call($(this).data('call'));
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

    // Replace the first two spaces
    url = url.replace(' ', '/');
    url = url.replace(' ', '/');

    var baseurl = $('span.base_url').html();

    var exists = $('div.response');
    if (exists.length) {
        exists.remove();
    }

    var output = $('#output');
    var input = $('#input');
    var render = $('<div class="response">');
    render.data('call', url);
    render.addClass('loading');

    var header = $('<h3>').html(url);
    var refresh = $('<span class="refresh action" title="refresh">&crarr;</span>');
    refresh.click(function() {
        api_call(url);
    });

    header.prepend(refresh);
    render.append(header);

    output.append(render);

    var callback = function(result) {
        console.log('function callback');
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

        console.log('update output');
        render.removeClass('loading');

        if (res.result) {
            render.append($('<div class="result">').html(res.result));
        }

        render.append($('<div class="message">').html(res.message));
        render.append(list);
    }

    console.log('make json call to '+url);
    $.ajax({
        dataType: "json",
        url: baseurl+url,
        data: '',
        complete: callback,
        headers: {'secret': $('span.secret').html()}
    });
}
