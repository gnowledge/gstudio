var mediaConstraints = {
        audio: true,
        video: {
            optional: [],
            mandatory: webrtcDetectedBrowser == 'firefox'
                && webrtcDetectedVersion < 28 ? {} : {
                maxWidth: 320,
                maxHeight: 240
            }
        }
    },
    pc_config = {
        iceServers:[{
            url: webrtcDetectedBrowser == 'firefox'
                ? 'stun:23.21.150.121'
                : 'stun:stun.l.google.com:19302'
        }]
    },
    pc_constraints = {
        optional: [
            {'DtlsSrtpKeyAgreement': true},
            {'RtpDataChannels': true }
        ]
    },
    sdpConstraints = {
        mandatory: {
            'OfferToReceiveAudio': true,
            'OfferToReceiveVideo': true
        }
    };

$(function() {
    addTurnServers();
    window.chatb = new Chatb(config);
});


function Chatb(config) {
    this.init();
};

Chatb.prototype = {
    init: function() {
        var _this = this;
        this.connected = false;
        this._config = config;
        this._callbacks = [];
        this.users = {};
        this.queue = {};
        this.buttons = {};
        this.settings = new Settings('chatb');

        this.background = '#ddd';
        this.opacity = 0.8;

        this.videos = $('#videos');
        this.local = $('#local')[0];
        this.initOverlay();
        this.renderMenu();
        if (!getUserMedia) {
            this.setStatus('chatb.org only works in a browser with WebRTC support,<br>like the latest version of <a href="http://www.google.com/chrome/">Chrome</a> or <a href="http://getfirefox.com/">Firefox</a>.');
        } else {
            this.connect();
        }
        if (this.settings.get('chat', false)) {
            this.settings.set('chat', false);
            this.toggleChat(true);
        }
    },
    initOverlay: function() {
        var _this = this;

        _this.delay = 3000;
        function show() {
            $('.overlay').animate({opacity: _this.opacity}, 100);
        }
        function hide() {
            if (!_this.overButton) {
                $('.overlay').animate({opacity: 0}, 100);
            }
        }
        this.overlay = $('#overlay');
        this.mousemove = function() {
            if (_this.connected) {
                if (_this.overlayTimeout) {
                    clearTimeout(_this.overlayTimeout);
                } else {
                    show();
                }
                _this.overlayTimeout = setTimeout(function() {
                    hide();
                    _this.overlayTimeout = null;
                }, _this.delay);
            }
        };
        $('body')
            .on({
                mouseenter: function() {
                    if (_this.connected) {
                        show();
                        _this.overlayTimeout = setTimeout(function() {
                            hide();
                            _this.overlayTimeout = null;
                        }, _this.delay);
                    }
                },
                mousemove: this.mousemove
            });
        document.addEventListener('mozfullscreenchange', function() {
            _this.resize();
            _this.buttons.fullscreen.text(document.mozFullScreen ? 'exit fullscreen' : 'enter fullscreen');
        });
        document.addEventListener('webkitfullscreenchange', function() {
            _this.resize();
            _this.buttons.fullscreen.text(document.webkitIsFullScreen ? 'exit fullscreen' : 'enter fullscreen');
            // force a reflow after resize
            setTimeout(function() {
                var video = $('#videos')[0];
                video.style.display='inline-block';
                video.offsetHeight; // no need to store this anywhere, the reference is enough
                video.style.display='block';
            }, 250);
        });


        var toggleHelp = function() {
            var info = $('#info');
                width = parseInt(info.css('width')),
                showInfo = info.css('left') == '-'+width+'px';
            !showInfo && about.show();
            info.animate({left: showInfo ? 0 : -width}, {
                duration: 300,
                complete: function() {
                    showInfo && about.hide();
                }
            });
        };
        var about = this.button('help', toggleHelp).css({
            position: 'fixed',
            top: '2px',
            left: '2px',
        }).appendTo(this.overlay);

        this.button('hide', toggleHelp).css({
            position: 'absolute',
            top: '2px',
            left: '2px',
        }).appendTo($('#info'));
    },
    connect: function() {
        var _this = this,
            host = this._config.wsHost || (
                (document.location.protocol == 'http:' ? 'ws' : 'wss') + '://' + document.location.host
            );

        $(window).on({
            resize: function() { _this.resize() },
            unload: function() {
                if (_this.stream) {
                    _this.stream.stop();
                    _this.stream = null;
                }
                if (_this.video) {
                    _this.video.src = '';
                }
            },
        });
        this.ws = new WebSocket(host + '/_rooms');
        this.ws.onopen = function () {
            window.onhashchange = function() {
                room=document.location.hash.slice(1);
                if (room) {
                    document.title = '#' + room;
                    _this.join(room);
                } else {
                    document.location.href = '#' + _this.randomRoom();
                }
            }
            window.onhashchange();
            _this.getMedia(function() {
                _this.connected = true;
                _this.newInfo();
            });
            $('#chatinput').on('keypress', function(event) {
                //enter
                if (event.keyCode == 13 && !event.shiftKey) {
                    if (this.value.trim().length) {
                        _this.chat(this.value);
                    }
                    this.value = '';
                    event.preventDefault();
                }
            });
            _this.keepalive();
        };
        this.ws.onmessage = function (event) {
            var message = JSON.parse(event.data);
            if (message.type == 'init') {
                _this.id = message.data;
            } else if (message.type == 'info') {
                _this.newInfo(JSON.parse(message.data));
            } else if (message.type == 'chat') {
                _this.chatlog(message.data, message.from);
            } else if (message.from) {
                if (_this.users[message.from]) {
                    _this.users[message.from].processMessage(message);
                } else {
                    _this.queueMessage(message);
                }
            } else {
                _this._callbacks.forEach(function(callback) {
                    callback(message);
                })
            }
        }
        this.ws.onclose = function (event) {
            _this.newInfo({
                name: room,
                users: {}
            });
            setTimeout(function() {
                _this.connect();
            }, 1000);
        };
    },
    getFrame: function(video) {
        var canvas = document.createElement('canvas'),
            context = canvas.getContext('2d'),
            videoAspect;
        canvas.width = canvas.height = 48;
        if (!video || (!video.src && !video.mozSrcObject) || video.videoHeight == 0) {
            context.fillStyle = "#000";
            context.fillRect(0, 0, canvas.width, canvas.height);
        } else {
            videoAspect = video.videoWidth/video.videoHeight;
            if (videoAspect > 1) {
                var height = canvas.height,
                    width = height * videoAspect,
                    left = -(width - canvas.width) / 2,
                    top = 0;
            } else {
                var width = canvas.width,
                    height = width / videoAspect,
                    left = 0,
                    top = -(height - canvas.height) / 2;
            }
            context.drawImage(video, left, top, width, height);
        }
        return canvas.toDataURL();
    },
    getMedia: function(callback) {
        var _this = this;
        if (this.stream) {
            callback && callback();
            return;
        }
        getUserMedia(mediaConstraints,
            function(stream) {
                _this.stream = stream;
                _this.video = $('<video>')
                    .attr({
                        autoplay: true,
                    }).css({
                        opacity: _this.settings.get('video', true) ? 1 : 0

                    }).on({
                        'loadedmetadata': function() {
                            _this.resizeVideo();
                        }
                    })
                    .appendTo(_this.local)[0];
                _this.video.muted = true;
                var audioTrack = stream.getAudioTracks()[0];
                if (audioTrack) {
                    audioTrack.enabled = _this.settings.get('audio', true);
                }
                var videoTrack = stream.getVideoTracks()[0];
                if (videoTrack) {
                    videoTrack.enabled = _this.settings.get('video', true);
                }
                attachMediaStream(_this.video, stream);
                callback && callback();
            },
            function(error) {
                _this.setStatus('Could not access your webcam and microphone.<br>Please reload.');
                console.log('Failed to get access to local media. Error code was ', error);
            }
        );
    },
    keepalive: function() {
        var _this = this;
        if (this.keepaliveInterval) {
            clearInterval(this.keepaliveInterval);
        }
        this.keepaliveInterval = setInterval(function() {
            if (_this.ws && _this.ws.readyState == _this.ws.OPEN) {
                _this.cmd('info', '');
            }
        }, 300000);
    },
    queueMessage: function(message) {
        this.queue[message.from] = this.queue[message.from] || [];
        this.queue[message.from].push(message);
    },
    randomRoom: function() {
        var room = '';
        while(room.length < 14) {
            room +=  String.fromCharCode('A'.charCodeAt(0) + Math.floor(Math.random() * 25));
        }
        return room;
    },
    setStatus: function(text) {
        if (!text) {
            $('#status').html('').hide();
        } else {
            if (text != $('#status').html()) {
                $('#status').html(text).css({opacity: 0}).show();
                var width = $('#status').width(),
                    height = $('#status').height(),
                    statusTop = $('#videos').height()/2 - height/2,
                    statusLeft = $('#videos').width()/2 - width/2;
                $('#status').css({
                    top: statusTop,
                    left: statusLeft,
                }).animate({opacity: 1}, 300);
                $('#status').find('.url').on({
                    click: function() {
                        this.focus();
                        var range = document.createRange();
                        range.selectNodeContents(this);
                        var sel = window.getSelection();
                        sel.removeAllRanges();
                        sel.addRange(range);
                    }
                });
            }
        }
    },
    newInfo: function(info) {
        var _this = this;
        this.info = info || this.info;
        this.numberOfRemoteUsers =  Object.keys(this.info.users).length - 1;
        this.setStatus(
            this.numberOfRemoteUsers > 0
                ? this.connected ? '' : 'Please share your webcam and microphone.'
                : this.numberOfRemoteUsers < 0
                    ? 'connecting to server...'
                    : 'You don\'t have to be alone, tell others to join you at:<br><br><b class="url">' + document.URL + '</b>'
        );

        if (this.connected) {
            Object.keys(this.info.users).forEach(function(id) {
                if (id != _this.id && !_this.users[id]) {
                    _this.users[id] = new User(id, _this, _this.queue[id]);
                    _this.queue[id] = [];
                    _this.resize();
                }
            });
            Object.keys(this.users).forEach(function(id) {
                if (id != _this.id && !_this.info.users[id]) {
                    _this.users[id].remove();
                }
            });
        }
    },
    send: function(message) {
        message = JSON.stringify(message);
        this.ws.send(message);
    },
    cmd: function(action, data) {
        this.send({type: 'cmd', data: JSON.stringify({
            action: action, data: data
        })});
    },
    chat: function(message) {
        this.send({
            type: 'chat', data: message
        });
        this.chatlog(message);
    },
    chatlog: function(message, from) {
        var chat = $('#chat'),
            count,
            width = parseInt(chat.css('width')),
            hidden = chat.css('right') == '-' + width + 'px',
            video = from
                ? this.users[from] ? this.users[from].video : null
                : this.settings.get('video', true) && this.video,
            msg = $('<div>')
                .addClass('message'),
            img = $('<img>')
                .attr({src: this.getFrame(video)})
                .css({
                    position: 'absolute',
                    padding: '2px',
                    'padding-right': '4px'
                })
                .appendTo(msg);

        !from && img.css({
            'padding-right': '2px',
            'padding-left': '4px',
            '-moz-transform': 'scaleX(-1)',
            '-o-transform': 'scaleX(-1)',
            '-webkit-transform': 'scaleX(-1)'
        });

        $('<div>').css({
            'margin-left': '54px'
        }).html(formatMessage(message)).appendTo(msg);
        msg.find('a').attr('target', '_blank');
        this.history.push(msg.html());
        this.settings.set('logs.' + room, this.history);
        this.history.length && this.buttons.clear.show();
        this.chatCount();
        $('#chatlog')
            .append(msg)
            .scrollTop($('#chatlog')[0].scrollHeight);

    },
    loadHistory: function(room) {
        this.history = this.settings.get('logs.' + room, []);
        $('#chatlog').empty();
        this.history.forEach(function(message) {
            var msg = $('<div>')
                .addClass('message')
                .html(message);
            $('#chatlog')
                .append(msg);
            $('#chatlog').scrollTop($('#chatlog')[0].scrollHeight);
        });
        this.history.length && this.buttons.clear.show();
    },
    chatCount: function() {
        var chat = $('#chat'),
            width = parseInt(chat.css('width')),
            hidden = chat.css('right') == '-'+width+'px',
            count;
        count = this.buttons.chat.text().match(/\d+/);
        count = count ? parseInt(count[0]) + 1 : 1;
        if (hidden) {
            this.buttons.chat.removeClass('overlay').text('chat (' + count + ')');
            if (this.buttons.chat.css('opacity') == 0) {
                this.buttons.chat.animate({opacity: this.opacity}, 100);
            }
        }  else {
            this.buttons.chat.text('chat');
        }
    },
    renderMenu: function() {
        var _this = this,
            menu = $('<div>').css({
                right: '2px',
                top: '2px',
                position: 'absolute'
            }),
            audio = this.buttons.audio = this.button(this.settings.get('audio', true)
            ? 'mute' : 'unmute', function() {
                _this.setAudio(audio.text() != 'mute');
            }).appendTo(menu),
            video = this.buttons.video = this.button(this.settings.get('video', true)
            ? 'disable video' : 'enable video', function() {
                _this.setVideo(video.text() != 'disable video');
            }).appendTo(menu),
            fullscreen = this.buttons.fullscreen = this.button(this.settings.get('fullscreen', true)
            ? 'enter fullscreen' : 'exit fullscreen', function() {
                _this.toggleFullscreen();
            }),
            screen = this.buttons.screen = this.button(this.settings.get('screen', true)
            ? 'share screen' : 'stop sharing screen', function() {
                if (_this.screen) {
                    _this.screen.stop();
                } else {
                    _this.shareScreen();
                }
            }), //.appendTo(menu),
            chat = this.buttons.chat = this.button('chat', function() {
                _this.toggleChat();
            });
        webrtcDetectedBrowser == 'chrome'
            && webrtcDetectedVersion >= 33
            && !webrtcDetectedMobile
            // Opera does not support scren sharing and does not throw error
            && !/OPR/.test(navigator.userAgent)
            && screen.appendTo(menu);
        fullscreen.appendTo(menu),
        chat.appendTo(menu);
        this.menu && this.menu.remove();
        this.menu = menu.appendTo(this.overlay);

        var chatmenu = $('#chatmenu').empty();
        this.buttons.clear = this.button('clear', function() {
            _this.history = [];
            _this.settings.set('logs.' + room, _this.history);
            $('#chatlog').empty();
            _this.buttons.clear.hide();
        })
        .css({left: '2px', top: '2px', position: 'absolute'})
        .hide()
        .appendTo(chatmenu);

        this.button('hide', function() {
            _this.toggleChat();
        })
        .css({right: '2px', top: '2px', position: 'absolute'})
        .appendTo(chatmenu);


    },
    button: function(label, click) {
        var _this = this;
        return $('<div>')
            .addClass('target')
            .addClass('overlay')
            .css({
                float: 'left',
                margin: '2px',
                padding: '2px 3px',
                'background-color': this.background,
            })
            .html(label)
            .addClass('target')
            .on({
                click: click,
                mouseenter: function() {
                    _this.overButton = true;
                    if (_this.overlayTimeout) {
                        clearTimeout(_this.overlayTimeout);
                    }
                },
                mouseleave: function() {
                    _this.overButton = false;
                    if (!_this.overlayTimeout) {
                        _this.overlayTimeout = setTimeout(function() {
                            $('.overlay').animate({opacity: 0}, 100);
                            _this.overlayTimeout = null;
                        }, _this.delay);
                    }
                },
            });
    },
    join: function(room) {
        this.cmd('join', room);
        this.newInfo({
            name: room,
            users: {}
        });
        this.loadHistory(room);
    },
    leave: function(room) {
        this.cmd('leave');
    },
    bind: function(/*[type], callback*/) {
        var type, callback;
        if (arguments.length == 2) {
            type = arguments[0];
            callback = arguments[1];
            this._callbacks.push(function(message) {
                if (message.type == type) {
                    callback(message);
                }
            });
        } else {
            this._callbacks.push(arguments[0]);
        }
    },
    resize: function () {
        var _this = this,
            all = Object.keys(this.users),
            height = window.innerHeight,
            width = window.innerWidth,
            rows = all.length > 2 ? 2 : 1,
            perRow = all.length > 1 ? (all.length + all.length % 2) / rows : 1,
            chatWidth = parseInt($('#chat').css('right')) + parseInt($('#chat').css('width'));
        if ((width-chatWidth)/height < 4/3) {
            rows = [perRow, perRow = rows][0];
        }
        if (all.length > 2 && all.length % 2) {
            $(this.local).css({
                width:  (width - chatWidth) / perRow + 'px',
                height: height / rows + 'px',
                right: chatWidth + 'px',
                bottom: 0,
            });
        } else {
            $(this.local).css({
                width: '128px',
                height: '128px',
                bottom: '4px',
                right: (chatWidth + 4) + 'px'
            });
        }
        this.stream && this.resizeVideo(this.local);
        all.forEach(function(id) {
            _this.users[id].resize(100/perRow + '%', 100/rows + '%');
        });
        var width = $('#status').width(),
            height = $('#status').height(),
            statusTop = this.videos.height()/2 - height/2,
            statusLeft = this.videos.width()/2 - width/2;
        $('#status').css({
            top: statusTop,
            left: statusLeft,
        });
    },
    resizeVideo: function() {
        var _this = this,
            width = $(this.local).width(),
            height = $(this.local).height(),
            videoAspect = this.video.videoWidth / this.video.videoHeight,
            boxAspect = width / height;
        if (!this.video) {
            return;
        }
        //Work around Firefox Bug https://bugzilla.mozilla.org/show_bug.cgi?id=926753
        if (webrtcDetectedBrowser == 'firefox'
            && this.video.videoWidth == 0 && this.video.videoHeight == 0) {
            setTimeout(function() {
                if (_this.local.parentElement) {
                    _this.resizeVideo();
                }
            }, 200);
        }
        videoAspect = videoAspect || 300/150;
        $(this.video).css(getVideoCSS(videoAspect, width, height));
    },
    toggleChat: function(fast) {
        var _this = this,
            element = $('#chat'),
            width = parseInt(element.css('width')),
            hidden = element.css('right') == '-'+width+'px',
            target = hidden ? 0 : -width;
        this.settings.set('chat', hidden);
        !hidden && this.buttons.chat
            .text('chat').addClass('overlay');
        element.animate({right: target}, {
            duration: fast ? 0 : 300,
            step: function(now, tween) {
                $('#videos,#overlay').css({right: now + width});
                _this.resize();
                _this.mousemove();
            },
            complete: function() {
                $('#videos,#overlay').css({right: target + width});
                if (hidden) {
                    _this.buttons.chat && _this.buttons.chat.hide();
                } else {
                    _this.buttons.chat && _this.buttons.chat.show();
                }
                _this.resize();
            }
        });
    },
    toggleFullscreen: function() {
        var documentElement = document.body,
            state = 'fullscreen' in document ? 'fullscreen'
                : 'mozFullScreen' in document ? 'mozFullScreen'
                : 'webkitIsFullScreen' in document ? 'webkitIsFullScreen'
                : void 0;
        if (document[state]) {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            }
        } else {
            if (document.body.requestFullscreen) {
                document.body.requestFullscreen();
            } else if (document.body.mozRequestFullScreen) {
                document.body.mozRequestFullScreen();
            } else if (document.body.webkitRequestFullscreen) {
                document.body.webkitRequestFullscreen();
            }
        }
    },
    shareScreen: function(callback) {
        var _this = this;
        getUserMedia({
                video: {
                  mandatory: {
                    maxWidth: 1920,
                    maxHeight: 1080,
                    chromeMediaSource: 'screen'
                  }
                },
            }, function(stream) {
                _this.buttons.screen.text('stop sharing screen');
                _this.screen = stream;
                _this.screen.addTrack(_this.stream.getAudioTracks()[0]);
                _this.screen.getAudioTracks()[0].enabled = _this.settings.get('audio', true);
                _this.screen.onended = function() {
                    _this.screen.stop();
                    _this.screen = null;
                    _this.buttons.screen.text('share screen');
                    var room = _this.info.name;
                    _this.leave();
                    _this.join(room);
                };
                var room = _this.info.name;
                _this.leave();
                _this.join(room);
            }, function(error) {
                console.log('Failed to access screen. Error:', error);
                alert('Screen sharing is still experimental,\nyou have to enable screen capture support"\nat chrome://flags/#enable-usermedia-screen-capture');
            }
        );
    },
    setAudio: function(enable) {
        var audioTrack = this.stream.getAudioTracks()[0],
            screenAudio = this.screen && this.screen.getAudioTracks()[0];
        if (audioTrack) {
            audioTrack.enabled = enable;
        }
        if (screenAudio) {
            screenAudio.enabled = enable;
        }
        this.buttons.audio.html(enable ? 'mute' : 'unmute');
        this.settings.set('audio', enable);
    },
    setVideo: function(enable) {
        var _this = this,
            videoTrack = this.stream.getVideoTracks()[0];
        if (this.screen) {
            videoTrack = _this.screen.getVideoTracks()[0];
        }
        videoTrack.enabled = enable;
        $(this.video).css({
            opacity: enable ? 1 : 0
        })
        enable && setTimeout(function() {
            _this.resizeVideo();
        }, 200);
        this.buttons.video.html(enable ? 'disable video' : 'enable video') ;
        this.settings.set('video', enable);
    }
};

function User(id, parent, messages) {
    this.id = id;
    this._parent = parent;
    this._callbacks = [];
    this.init(messages);
}
User.prototype = {
    init: function(messages) {
        var _this = this;
        var id = this.id;
        this.ui = $('<div>')
            .attr({id: 'remote' + id})
            .addClass('remote').addClass('video')
            .css({
                overflow: 'hidden',
                background: '#eee'
            });
        this.overlay = $('<div>');
        this.message = $('<div>')
            .html('connecting...')
            .css({
                position: 'absolute',
                left: this.ui.width()/2,
                top: this.ui.height()/2,
            })
            .appendTo(this.ui);
        this.video = $('<video>')
            .attr({
                autoplay: true
            }).on({
                'loadedmetadata': function() {
                    _this.resizeVideo();
                }
            })
            .appendTo(this.ui)[0];
        if (messages) {
            messages.forEach(function(message) {
                _this.processMessage(message)
            });
        }
        // only one side should connect
        // to avoid a race condition.
        if (_this.id < _this._parent.id) {
            _this.connect();
        }
        $('#videos').append(this.ui);
    },
    resize: function(width, height) {
        var _this = this;
        this.ui.css({
            width: width,
            height: height,
        });
        this.overlay.css({
            width: width,
            height: height,
        });
        if (this.message) {
            var offset = this.ui.offset();
            this.message.css({
                left: offset.left + this.ui.width()/2 - this.message.width()/2,
                top: offset.top + this.ui.height()/2 - this.message.height()/2,
            });
        }
        this.resizeVideo();
    },
    resizeVideo: function() {
        var _this = this,
            videoAspect,
            width,
            height;
        if (!this.video) {
            return;
        }
        //Work around Firefox Bug https://bugzilla.mozilla.org/show_bug.cgi?id=926753
        if (webrtcDetectedBrowser == 'firefox'
            && this.video.videoWidth == 0 && this.video.videoHeight == 0) {
            $(this.video).one('playing', function() {
                _this.resize(width, height);
            });
        } else {
            videoAspect = this.video.videoWidth / this.video.videoHeight;
        }
        videoAspect = videoAspect || 300/150;
        width = this.ui.width();
        height = this.ui.height();

        $(this.video).css(getVideoCSS(videoAspect, width, height));
    },
    connect: function() {
        //console.log('connect');
        var _this = this;
        var constraints = {optional: [], mandatory: {MozDontOfferDataChannel: true}},
            offer;

        // temporary measure to remove Moz* constraints in Chrome
        if (webrtcDetectedBrowser === 'chrome') {
            for (prop in constraints.mandatory) {
                if (prop.indexOf('Moz') != -1) {
                    delete constraints.mandatory[prop];
                }
            }
        }
        constraints = mergeConstraints(constraints, sdpConstraints);
        if (!this.pc) {
            this.createPeerConnection();
        }
        if (this._parent.screen) {
            this.pc.addStream(this._parent.screen);
        } else {
            this.pc.addStream(this._parent.stream);
        }
        //console.log('not create offer');
        this.pc.createOffer(function(desc) {
            desc.sdp = preferOpus(desc.sdp);
            //console.log('offer', desc);
            _this.pc.setLocalDescription(desc, function() {
                _this.send('offer', desc);
            }, logError);
        }, logError, constraints);
    },
    disconnect: function() {
        //console.log('disconnect');
        if (this.video) {
            //this.video.src = '';
        }
        if (this.stream) {
            this.stream = null;
        }
        if (this.pc) {
            try {
                this.pc.close();
            } catch(e) {}
            this.pc = null;
            delete this.pc;
        }
        this._parent.resize();
    },
    send: function(type, data) {
        //console.log('send from', this._parent.id, 'to', this.id);
        this._parent.send({
            to: this.id,
            type: type,
            data: JSON.stringify(data)
        });
    },
    processMessage: function(message) {
        var _this = this;
        if (message.type == 'offer') {
            offer = JSON.parse(message.data);
            if (_this.pc) {
                this.disconnect();
            }
            this.createPeerConnection();
            if (this._parent.screen) {
                this.pc.addStream(this._parent.screen);
            } else {
                this.pc.addStream(this._parent.stream);
            }
            offer = new RTCSessionDescription(offer);
            this.pc.setRemoteDescription(offer, function() {
                //console.log('create answer');
                function setLocalAndSendMessage(desc) {
                    desc.sdp = preferOpus(desc.sdp);
                    //console.log('answer', desc);
                    _this.pc.setLocalDescription(desc, function() {
                        _this.send('answer', desc);
                    }, logError);
                }
                _this.pc.createAnswer(setLocalAndSendMessage, logError, sdpConstraints);
            }, logError);
        } else if (message.type == 'answer') {
            answer = JSON.parse(message.data);
            //FIXME: why do we get answers without connection?
            if (_this.pc) {
                answer = new RTCSessionDescription(answer);
                _this.pc.setRemoteDescription(answer);
            }
        } else if (message.type == 'icecandidate') {
            candidate = JSON.parse(message.data);
            //console.log('ice', candidate);
            //FIXME: why do we get icecandidates without connection?
            if (_this.pc) {
                candidate = new RTCIceCandidate(candidate);
                _this.pc.addIceCandidate(candidate);
            }
        }
    },
    createPeerConnection: function () {
        var _this = this;
        this.pc = new RTCPeerConnection(pc_config, pc_constraints);
        this.pc.onerror = logError;
        this.pc.onicecandidate = function(event) {
            if (event.candidate) {
                _this.send('icecandidate', event.candidate);
            }
        };
        this.pc.onaddstream = function(event) {
            // console.log('Remote stream added.');
            _this.stream = event.stream;
            attachMediaStream(_this.video, event.stream);
            _this.resizeVideo();
            _this.message.remove();
            _this.message = null;
        };
        this.pc.onremovestream = function(event) {
            // console.log('Remote stream removed.');
            _this.stream = null;
            this.video.src = '';
            if (this.video.mozSrcObject) {
                this.video.mozSrcObject = null;
            }
        }
        /*
        this.pc.onnsignalingstatechange = function(event) {
            console.log(_this.id, 'onsignalingstatechange;', event);
        };
        */
        this.pc.oniceconnectionstatechange = function(event) {
            if (event.target.iceConnectionState == 'disconnected'
                || event.target.iceConnectionState == 'closed') {
                _this.disconnect();
            }
        };
    },
    remove: function() {
        // console.log('remove', this.id);
        var id = this.id;
        if (this.pc) {
            this.disconnect();
        }
        if (this.ui) {
            this.ui.remove();
        }
        delete this._parent.users[id];
        this._parent.resize();
    },
}

Settings = function(namespace) {
    var localStorage;
    this.namespace = namespace;
    try {
        // this will fail if third party cookies/storage is not allowed
        localStorage = window.localStorage || {};
        // FF 3.6 can't assign to or iterate over localStorage
        for (var key in localStorage) {};
    } catch (e) {
        localStorage = {};
    }
    this.backend = localStorage;
};
Settings.prototype = {
    get: function(key, defaultValue) {
        key = this.namespace ? this.namespace + '.' + key : key;
        var value = this.backend[key];
        return value ? JSON.parse(value) : defaultValue;
    },
    set: function(key, value) {
        key = this.namespace ? this.namespace + '.' + key : key;
        this.backend[key] = JSON.stringify(value);
    }
};

function getVideoCSS(videoAspect, width, height) {
    var videoWidth,
        videoHeight,
        marginTop = 0,
        marginLeft = 0;
    //console.log('getVideoCSS', videoAspect, width, height);
    boxAspect = width / height;
    if (videoAspect < boxAspect) {
        videoWidth = width;
        videoHeight = width / videoAspect;
        marginLeft = 0;
        marginTop = -(videoHeight - height) / 2;
        //console.log('crop video top/bottom top:', marginTop, videoAspect, boxAspect);
    } else {
        videoHeight = height;
        videoWidth = height * videoAspect;
        marginLeft = -(videoWidth - width) / 2;
        marginTop = 0;
        //console.log('crop video left/right left:', marginLeft, videoAspect, boxAspect);
    }
    return {
        height: videoHeight + 'px',
        width:  videoWidth + 'px',
        'margin-left': marginLeft + 'px',
        'margin-top': marginTop + 'px',
    }
}
