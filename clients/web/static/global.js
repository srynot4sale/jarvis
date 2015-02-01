$(function() {

    /**
     * On page load
     */

    /**
     * Handle "back" events
     */
    window.addEventListener("popstate", function(e) {
        if (e.state && e.state.title) {
            api_call(e.state.title);
        }
    });

    /**
     * Handle "hash change" events
     */
    window.addEventListener("hashchange", function(e) {
        apicall = jarvis_get_apicall_from_url();
        if (apicall) {
            api_call(apicall);
        }
    });

    /**
     * Check if user is on a small screen
     */
    if ($(document).width() < 600) {
        $('body').addClass('mobile');
    }

    /**
     * Setup page markup
     */
    var input = $('<div id="input"></div>');
    var inputtoggle = $('<div id="input-toggle">[+]</div>');
    var output = $('<div id="output"></div>');

    $('#container').append(inputtoggle)
                   .append(input)
                   .append(output);

    /**
     * Setup input toggle
     */
    inputtoggle.click(function() {
        input.toggle();
    });


    /**
     * Setup buttons
     */
    api_call('server menu', function(result) {
        console.log('got menu');

        var res = jarvis_handle_result(result);

        if (!res.success) {
            return;
        }

        var menu = $('<ul class="menu"></ul>');
        for (var i in res.data) {
            var menuitem = $('<li></li>');
            var menulink = jarvis_build_internal_link({path: res.data[i][1], text: res.data[i][0]});
            menu.append(menuitem.append(menulink));
        }

        input.append(menu);
    });

    /**
     * Setup manual api entry box
     */
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


    var default_apicall = 'server connect';

    /**
     * Check if the url indicates a specific action
     */
    url_apicall = jarvis_get_apicall_from_url();
    if (url_apicall) {
        default_apicall = url_apicall;
    }

    api_call(default_apicall);

});



/**
 * Parse hash in URL and retrieve an API call
 */
function jarvis_get_apicall_from_url() {
    if (!window.location.hash || window.location.hash.substr(0, 2) != '#/') {
        return false;
    }

    default_apicall = window.location.hash.substr(2);
    return default_apicall.replace('/', ' ').replace('/', ' ');
}


/**
 * Generate URL from an API call
 */
function jarvis_get_url_from_apicall(apicall) {
    var baseurl = $('body').data('baseurl');
    return baseurl + '#/' + apicall.replace(' ', '/').replace(' ', '/');
}

/**
 * Return internal "link" markup
 */
function jarvis_build_internal_link(config) {
    if (!config.text) {
        config.text = config.path;
    }

    var link = $('<a>');
    link.addClass('internal-link action');
    link.attr('href', jarvis_get_url_from_apicall(config.path));
    link.attr('title', config.path);
    link.data('call', config.path);
    link.html(config.text);
    link.click(function(e) {
        e.preventDefault();
        $(this).blur();
        api_call($(this).data('call'));
    });

    return link;
}


/**
 * Parse request results and return a consistent
 * Javascript object
 */
function jarvis_handle_result(result) {
    console.log('jarvis_handle_result()');
    var res = {}
    res.success = false;

    result = jQuery.parseJSON(result.responseText);

    if (!result) {
        res.result = 'SERVER FAILURE';
        res.message = 'No failure data available';
    } else {
        if (result['state'] != 1) {
            res.result = 'FAILURE';
        } else {
            res.success = true;
        }

        res.message = result['message'];

        if (result['data'] && result['data'].length) {
            if (result['data'] instanceof Array) {
            } else {
                result['data'] = [result['data']];
            }

            res.data = result['data'];
        }

        if (result['actions']) {
            res.actions = result['actions'];
        }

        if (result['notification']) {
            res.notification = result['notification'];
        }

        if (result['redirected']) {
            res.redirected = result['redirected'];
        }
    }

    return res;
}


/**
 * Display a dialog requesting data
 */
function jarvis_dialog(action, callback, params) {
    console.log('jarvis_dialog()');

    var dialog = $('<div class="dialog"></div>');
    var title = action;
    var form = $('<form accept-charset="utf-8"></form>');

    for (var p in params) {
        var param = params[p];
        var original_param = param;
        var value = '';

        // Split out the value
        if (param.indexOf('{{') != -1) {
            value = param.substr(param.indexOf('{{'));
            value = value.substr(2, value.length - 4);
            param = param.substr(0, param.indexOf('{{'));
        }

        var nice = param.replace('%', '').replace('_', ' ');
        var element = $('<div></div>');
        element.append($('<label for="dialog-'+param+'">'+nice+'</label>'));
        element.append($('<input type="text" id="dialog-'+param+'" name="'+param+'" value="'+value+'" />'));
        form.append(element);

        // Remove element from dialog title
        title = title.replace(original_param, '');
    }

    form.prepend($('<h2>'+title+'</h2>'));

    form.append('<input class="bob" type="submit" value="Submit" />');
    dialog.append(form);

    $('.bob', dialog).click(function() {
        for (var p in params) {
            var param = params[p];
            var original_param = param;
            if (param.indexOf('{{') != -1) {
                param = param.substr(0, param.indexOf('{{'));
            }
            action = action.replace(original_param, $('input[name="'+param+'"]', dialog).val());
        }

        $.modal.close();
        api_call(action, callback);
    });

    dialog.modal();
}


/**
 * Update title bar
 */
function jarvis_update_title(title, status = '') {
    var header = $('div.response h3')
    var refresh = jarvis_build_internal_link({path: title, text: title});
    refresh.addClass('refresh title');
    refresh.attr('title', 'Refresh');

    $('.title', header).remove();
    header.prepend(refresh);

    // If response received:
    if (status == 'complete') {
        // Update title bar
        document.title = 'Jarvis - '+title;

        // Update URL
        // (check for support of history API)
        if (!!(window.history && history.pushState)) {
            var url = jarvis_get_url_from_apicall(title);

            // If same as current URL, do not re-add
            if (url != location.href) {
                history.pushState({'title': title}, null, url);
            }
        }
    }
}


/**
 * Make an API call
 */
var api_call = function(action, callback) {
    console.log('api_call('+action+')');

    // Replace the first two spaces
    url = action.replace(' ', '/').replace(' ', '/');

    /**
     * Check if this a dynamic call, e.g. needs input (look for a %xxx)
     */
    var dynamic = /\%[A-Za-z0-9_]+(\{\{.*\}\})?/g;
    var dvars = url.match(dynamic);
    if (dvars) {
        jarvis_dialog(action, callback, dvars);
        return false;
    }

    /**
     * Prepare HTML
     */
    var baseurl = $('body').data('baseurl');

    var exists = $('div.response');
    if (exists.length) {
        exists.remove();
    }

    var output = $('#output');
    var input = $('#input');
    var render = $('<div class="response">');
    render.data('call', url);
    render.addClass('loading');

    var header = $('<h3>');
    render.append(header);
    output.append(render);

    jarvis_update_title(action);

    var title = action;

    // If no callback function defined, then display normally
    if (callback === undefined) {
        var callback = function(result) {
            console.log('default callback');
            input.val('');

            var res = jarvis_handle_result(result);

            res.url = url;
            if (res.redirected) {
                res.action = res.redirected;
            } else {
                res.action = title;
            }

            var list = $('<ol>');
            for (line in res.data) {
                var item = res.data[line][0];
                var li = $('<li>');

                // Make links clickable
                var html = item.replace(/(https?:\/\/[^ ]+)/g, "<a href=\"$1\" target=\"_blank\">$1</a>");

                li.html(html);

                if (res.data[line].length > 1) {
                    var action = res.data[line][1];
                    if (action) {
                        li.addClass('expands');
                        li.addClass('action');
                        li.data('action', action);
                        li.click(function() {
                            api_call($(this).data('action'));
                        });
                    }
                }

                // List item actions (or options)
                if (res.data[line].length > 2) {
                    var options = res.data[line][2];
                    var metacontainer = false;
                    if (options) {
                        var olist = $('<ol class="options">');
                        olist.hover(undefined, function() {
                            $(this).hide();
                        });

                        var olistcontainer = $('<div class="optioncontainer">');
                        var olisttoggle = $('<span class="optiontoggle">^</span>');
                        olisttoggle.hover(function() {
                            $('ol.options').hide();
                            $('ol.options', $(this).parent()).show();
                        });

                        for (var o in options) {
                            // Check if option is metadata
                            var ismetadata = o.match(/^\[(.*)\]$/);

                            if (ismetadata) {
                                var optiontext = o.substr(1, o.length - 2);
                            } else {
                                var optiontext = o;
                            }
                            var option = jarvis_build_internal_link({path: options[o], text: optiontext});

                            if (!ismetadata) {
                                var option = $('<li>').append(option);
                            }

                            option.hover(
                                function() {
                                    $(this).parent().closest('li').addClass('hoveraction');
                                },
                                function() {
                                    $(this).parent().closest('li').removeClass('hoveraction');
                                }
                            );

                            if (ismetadata) {
                                option.addClass('metadata');

                                if (!metacontainer) {
                                    var metacontainer = $('<div>').addClass('metadata');
                                    li.append(metacontainer);
                                }

                                metacontainer.append(option);
                            } else {
                                olist.append(option);
                            }
                        }

                        olistcontainer.prepend(olist);
                        olistcontainer.prepend(olisttoggle);
                        li.prepend(olistcontainer);
                    }
                }

                list.append(li);
            }

            // Page actions
            if (res.actions) {
                for (var action in res.actions) {
                    var a = jarvis_build_internal_link({path: res.actions[action][1], text: res.actions[action][0]});
                    a.addClass('pageaction');
                    header.append(a);
                }
            }

            console.log('update output');
            render.removeClass('loading');

            if (res.result) {
                render.append($('<div class="result">').html(res.result));
                render.addClass('error');
            }

            if (res.notification) {
                var notification = $('<div class="notification">').html(res.notification);
                notification.on('click', function() {
                    $('#output .response').removeClass('notice');
                    $(this).remove();
                });
                render.append(notification);
                render.addClass('notice');
            }

            var message = $('<div class="message">').html(res.message);

            render.append(message);
            render.append(list);

            jarvis_update_title(res.action, 'complete');
        }
    }

    console.log('json call to "'+url+'"');
    $.ajax({
        dataType: "json",
        url: baseurl+'api/'+encodeURIComponent(url),
        data: '',
        complete: callback,
        headers: {'secret': $('body').data('secret')}
    });
}
