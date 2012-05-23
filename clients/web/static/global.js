$(function() {

    var input = $('<textarea style="border: 0; width: 100%; height: 100%;"></textarea>');

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

});

var api_call = function(url) {
    console.log('function api_call');

    var baseurl = $('span.base_url').html();

    var callback = function(result) {
        console.log('function callback');
        var input = $('textarea');

        var text = '';

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
            if (result['data']) {
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
    $.getJSON(baseurl+url, '', callback);
}
