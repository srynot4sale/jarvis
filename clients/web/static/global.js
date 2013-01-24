$(function() {

    var input = $('<textarea id="input"></textarea>');

    $('body').append(input);


    input.keydown(function(event) {
        // Get enter
        if (event.keyCode == 13) {
            console.log('"ENTER" keypress');

            // Get last line of textarea
            var last = input.val().split('\n').pop();

            console.log('User entered: '+last);
            var result = api_call(last);
        }
    });

    input.focus();

});

var api_call = function(url) {
    console.log('function api_call');

    var baseurl = $('span.base_url').html();

    var callback = function(result) {
        console.log('function callback');
        var input = $('textarea');

        var text = '';

        result = jQuery.parseJSON(result.responseText);

        if (!result) {
            text += 'Result: SERVER FAILURE\n';
            text += 'Message: No failure data available\n';
        }
        else {
            console.log('check state');
            if (result['state'] != 1) {
                text += 'Result: FAILURE\n';
            }

            console.log('check message');
            text += 'Message: '+result['message']+'\n';

            console.log('check data');
            if (result['data'] && result['data'].length) {
                text += 'Data:\n';
                if (result['data'] instanceof Array) {
                } else {
                    result['data'] = [result['data']];
                }

                for (line in result['data']) {
                    text += '  ' + result['data'][line]+'\n';
                }
            }
        }

        text += '\n';

        console.log('update textarea');
        input.val(input.val() + text);
        input.scrollTop = input.scrollHeight; // Scrolls to bottom
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
