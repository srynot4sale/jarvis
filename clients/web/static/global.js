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
     * Handle "a" keypresses (api call)
     */
    document.addEventListener("keydown", function(e) {
        // Ignore if typing into a form element
        switch (e.target.tagName.toLowerCase()) {
            case 'input':
            case 'textarea':
                return;
        }

        var target = $(e.target);

        // Get "a"
        if (e.keyCode == 65) {
            console.log('Action event');
            $('div.response h3 a.pageaction').focus();
            e.preventDefault();
            return false;
        }

        // Get "q"
        if (e.keyCode == 81) {
            console.log('Query event');
            $('div.response h3 a.title').click();
            e.preventDefault();
            return false;
        }

        // Get "right arrow"
        if (e.keyCode == 39) {
            console.log('Right arrow event');
            if (target.hasClass('pageaction')) {
                console.log('Next page action');
                var found = false;
                $($('a.pageaction').get().reverse()).each(function() {
                    if ($(this).is(':focus')) {
                        found = true;
                        return;
                    }

                    if (found) {
                        $(this).focus();
                        found = false;
                    }
                });
            }
            e.preventDefault();
            return false;
        }

        // Get "left arrow"
        if (e.keyCode == 37) {
            console.log('Right arrow event');
            if (target.hasClass('pageaction')) {
                console.log('Next page action');
                var found = false;
                $('a.pageaction').each(function() {
                    if ($(this).is(':focus')) {
                        found = true;
                        return;
                    }

                    if (found) {
                        $(this).focus();
                        found = false;
                    }
                });
            }
            e.preventDefault();
            return false;
        }
    });

    /**
     * Check if user is on a small screen
     */
    $(window).on('resize', function() {
        if ($(window).width() < 600) {
            $('body').addClass('mobile');
        } else {
            $('body').removeClass('mobile');
        }
    });
    $(window).trigger('resize');

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
     * Setup notifications stack (for Pnotify)
     */
    window.jarvis_notification_stack = {"dir1": "down", "dir2": "left", "context": $('#output')};

    /**
     * Setup input toggle
     */
    inputtoggle.click(function() {
        input.toggle();
    });

    /**
     * Setup logout handler
     */
    input.append($('<div id="logoutcontainer"><a id="logout" class="action" href="/logout">Logout</a></div>'));

    /**
     * Setup buttons
     */
    api_call('server menu', {callback: function(result) {
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
    }});

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

        if (result['context']) {
            res.context = result['context'];
        }
    }

    return res;
}


/**
 * Display a dialog requesting data
 */
function jarvis_dialog(action, options, params) {
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
        element.append($('<label for="dialog-'+param+'">'+nice+'</label><span class="toggle" data-param="'+param+'">[+]</span>'));
        element.append($('<div class="input"><input type="text" id="dialog-'+param+'" name="'+param+'" value="'+value+'" /></div>'));
        form.append(element);

        // Remove element from dialog title
        title = title.replace(original_param, '');
    }

    form.prepend($('<h2>'+title+'</h2>'));

    form.append('<button class="submit" type="submit">Submit</buton>');
    dialog.append(form);

    $('.toggle', dialog).click(function() {
        var toggle = $(this);
        var param = toggle.data('param');
        var input = $('input', toggle.parent());
        var textarea = $('<textarea id="dialog-'+param+'" name="'+param+'"></textarea>');
        textarea.html(input.val());
        input.replaceWith(textarea);
        $("#simplemodal-container").css('height', 'auto');
        $.modal.update();
    });

    $('.submit', dialog).click(function() {
        for (var p in params) {
            var param = params[p];
            var original_param = param;
            if (param.indexOf('{{') != -1) {
                param = param.substr(0, param.indexOf('{{'));
            }
            if ($('input[name="'+param+'"]', dialog).length) {
                var value = $('input[name="'+param+'"]', dialog).val();
            } else {
                var value = $('textarea[name="'+param+'"]', dialog).val();
            }
            action = action.replace(original_param, value);
        }

        $.modal.close();

        // Escape input from now on, otherwise we can't enter data with %'s
        options.escaped = true;
        api_call(action, options);
    });

    // Check for multiline values and if found, toggle textarea
    for (var p in params) {
        var param = params[p];
        if (param.indexOf('\n') != -1) {
            value = param.substr(param.indexOf('{{'));
            value = value.substr(2, value.length - 4);
            param = param.substr(0, param.indexOf('{{'));

            $('.toggle', dialog).each(function() {
                if ($(this).data('param') == param) {
                    $(this).trigger('click');

                    // Reset value as input strips out \n
                    $('textarea', $(this).parent()).html(value);
                }
            });
        }
    }

    dialog.modal();
    $("#simplemodal-container").css('height', 'auto');
    $.modal.update();
}


/**
 * Update title bar
 */
function jarvis_update_title(title, status = '') {
    var header = $('div.response h3')
    header.removeClass('apiinput-enabled');

    var a = $('<a>');
    a.addClass('action title');
    a.attr('title', title);
    a.data('title', title);
    a.html(jarvis_escape(title));

    $('.title', header).remove();
    header.prepend(a);

    a.click(function() {
        /**
        * Setup manual api entry box
        */
        var textbox = $('<input type="text" class="textbox title" value="" />');
        textbox.focus(function(event) {
            $(this).select();
        });

        textbox.keydown(function(event) {
            // Get enter
            if (event.keyCode == 13) {
                // Escape input from now on, otherwise we can't enter data with %'s
                api_call(textbox.val(), {escaped: true});
                jarvis_update_title(textbox.val());
            }
            // Get escape
            if (event.keyCode == 27) {
                jarvis_update_title(title);
            }
        });

        textbox.blur(function(event) {
            jarvis_update_title(title);
        });

        textbox.val(title);
        header.addClass('apiinput-enabled');
        a.replaceWith(textbox);
        textbox.focus();
    });


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
var api_call = function(action, options = {}) {
    console.log('api_call('+action+')');

    // Replace the first two spaces
    url = action.replace(' ', '/').replace(' ', '/');

    /**
     * Check if this a dynamic call, e.g. needs input (look for a %xxx)
     */
    var dynamic = /\%[A-Za-z0-9_]+(\{\{(.|[\r\n])*\}\})?/g;
    var dvars = url.match(dynamic);
    if (dvars && !options.escaped) {
        jarvis_dialog(action, options, dvars);
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
    if (options.callback === undefined) {
        options.callback = function(result) {
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

                // Escape item
                item = jarvis_escape(item);

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
                    var tagcontainer = false;
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
                            // Check if option is tag
                            var istag = o.match(/^\[(.*)\]$/);

                            if (istag) {
                                var optiontext = o.substr(1, o.length - 2);
                            } else {
                                var optiontext = o;
                            }
                            var option = jarvis_build_internal_link({path: options[o], text: jarvis_escape(optiontext)});

                            if (!istag) {
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

                            if (istag) {
                                option.addClass('tagdata');

                                if (!tagcontainer) {
                                    var tagcontainer = $('<div>').addClass('tagdata');
                                    li.append(tagcontainer);
                                }

                                tagcontainer.append(option);
                            } else {
                                olist.append(option);
                            }
                        }

                        olistcontainer.prepend(olist);
                        olistcontainer.prepend(olisttoggle);
                        li.prepend(olistcontainer);
                    }
                }

                // List meta data
                if (res.data[line].length > 3) {
                    if (res.data[line][3]['context']) {
                        li.data('context', res.data[line][3]['context']);
                    }
                }
                list.append(li);
            }

            // Show a message if not data was returned
            if (!res.data) {
                var li = $('<li>');
                li.html('<em>No data returned</em>');
                list.append(li);
            }

            // Page actions
            if (res.actions) {
                for (var action in res.actions) {
                    var a = jarvis_build_internal_link({path: res.actions[action][1], text: jarvis_escape(res.actions[action][0])});
                    a.addClass('pageaction');
                    header.append(a);
                }
            }

            console.log('update output');
            render.removeClass('loading');

            if (res.result) {
                render.append($('<div class="result">').html(jarvis_escape(res.result)));
                render.addClass('error');
            }

            if (res.notification) {
                PNotify.desktop.permission()
                var message = new PNotify({
                    desktop: {
                        desktop: true
                    },
                    type: 'success',
                    title: 'Jarvis',
                    text: res.notification,
                    stack: jarvis_notification_stack
                });
            }

            var message = $('<div class="message">').html(jarvis_escape(res.message));

            render.append(message);
            render.append(list);

            jarvis_update_title(res.action, 'complete');

            // Jump to context if supplied
            if (res.context) {
                var ctx = res.context;

                // Check if matching context found
                $('div.response ol li').each(function() {
                    var match = $(this);
                    if (match.data('context') == ctx) {
                        $('html, body').animate(
                            {
                                scrollTop: match.offset().top - $('div.response h3').outerHeight()
                            },
                            1000
                        );

                        match.effect("highlight", {}, 3000);
                    }
                });
            }
        }
    }

    console.log('json call to "'+url+'"');

    // Escape % signs or things get converted to weird characters
    url = url.replace('%', '%25');

    $.ajax({
        dataType: "json",
        url: baseurl+'api/'+encodeURIComponent(url),
        data: '',
        complete: options.callback
    });
}

function jarvis_escape(text) {
    var escapeMap = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '`': '&#x60;',
        '%': '&#37;'
    };

    function escapeHtml(string) {
        return String(string).replace(/[&<>"'`%]/g, function (s) {
            return escapeMap[s];
        });
    }

    text = escapeHtml(text);
    return text.replace(/\n/g, "<br />");
}
